import sqlite3
import pandas as pd
import joblib
import os
import hashlib
import secrets

def get_db_connection():
    return sqlite3.connect('edutrak.db')

# ─────────────────────────────────────────
#  IDENTIFIER VALIDATION (SQL-injection guard)
# ─────────────────────────────────────────
# table_name / col values below get interpolated into SQL strings because SQLite can't
# bind identifiers (table/column names) as query parameters the way it binds values.
# The mitigation is an allow-list: check the name against what actually exists in the
# database (sqlite_master / PRAGMA table_info) before ever putting it in a query string.
# A name that isn't a real table/column can't pass validation, so it can't carry a
# SQL fragment through — the same principle as parameterizing values, applied to
# identifiers instead.

def _valid_table_names():
    """Every real table name currently in the DB."""
    with get_db_connection() as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {r[0] for r in rows}

def _assert_valid_table(table_name):
    if table_name not in _valid_table_names():
        raise ValueError(f"Unknown table: {table_name!r}")
    return table_name

def _valid_column_names(table_name):
    """Columns of table_name. Caller must validate table_name with _assert_valid_table
    first — PRAGMA doesn't support bound parameters either, so an unvalidated table_name
    here would just move the same injection risk one call earlier."""
    with get_db_connection() as conn:
        rows = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    return {r[1] for r in rows}

def _assert_valid_column(table_name, col):
    if col not in _valid_column_names(table_name):
        raise ValueError(f"Unknown column {col!r} in table {table_name!r}")
    return col

# ─────────────────────────────────────────
#  ML DROPOUT RISK PREDICTION
# ─────────────────────────────────────────

_MODEL_BUNDLE = None  # cached in-memory after first load

def load_dropout_model(path='dropout_model.pkl'):
    """Load the trained dropout-risk model bundle (cached). Returns None if not trained yet."""
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        if not os.path.exists(path):
            return None
        _MODEL_BUNDLE = joblib.load(path)
    return _MODEL_BUNDLE

def predict_dropout_risk(student_input: dict):
    """
    student_input: dict with keys for all numeric + categorical features used in training
    (see NUMERIC_FEATURES / CATEGORICAL_FEATURES in train_dropout_model.py).
    Returns (probability, risk_label) e.g. (0.82, "High Risk"), or (None, None) if the
    model hasn't been trained yet (run: python train_dropout_model.py).
    """
    bundle = load_dropout_model()
    if bundle is None:
        return None, None
    model = bundle['model']
    cols = bundle['numeric_features'] + bundle['categorical_features']
    row = pd.DataFrame([{c: student_input.get(c) for c in cols}])
    proba = float(model.predict_proba(row)[0][1])
    if proba >= 0.6:
        label = "High Risk"
    elif proba >= 0.3:
        label = "Medium Risk"
    else:
        label = "Low Risk"
    return proba, label

def get_dropout_feature_importance(top_n=8):
    """Top-N global feature importances from the trained model, as a pandas Series."""
    bundle = load_dropout_model()
    if bundle is None:
        return None
    return bundle['feature_importances'].head(top_n)

def get_dropout_model_metrics():
    """Held-out accuracy / ROC-AUC / cross-val ROC-AUC recorded at training time."""
    bundle = load_dropout_model()
    if bundle is None:
        return None
    return bundle['metrics']

def predict_dropout_risk_batch(df):
    """
    Vectorised dropout-risk prediction for a whole class at once (used by the Risk List
    filter, instead of calling predict_dropout_risk() in a per-row loop).
    df must already contain student_id/Student_ID plus every numeric_features +
    categorical_features column the model was trained on (see NUMERIC_FEATURES /
    CATEGORICAL_FEATURES in train_dropout_model.py).
    Returns a copy of df with 'risk_probability' and 'risk_label' columns added,
    or None if the model isn't trained yet, or the dataset is missing required columns
    (e.g. a custom-uploaded engagement dataset with fewer columns than the training set).
    """
    bundle = load_dropout_model()
    if bundle is None:
        return None
    cols = bundle['numeric_features'] + bundle['categorical_features']
    missing = [c for c in cols if c not in df.columns]
    if missing:
        return None
    model = bundle['model']
    proba = model.predict_proba(df[cols])[:, 1]
    out = df.copy()
    out['risk_probability'] = proba
    out['risk_label'] = pd.cut(
        proba, bins=[-0.01, 0.3, 0.6, 1.01], labels=["Low Risk", "Medium Risk", "High Risk"]
    )
    return out

# ─────────────────────────────────────────
#  INTERVENTION / OUTREACH LOG
# ─────────────────────────────────────────

def ensure_interventions_table():
    """Create the interventions table if it doesn't exist yet. Safe to call on every app start."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                flagged_by TEXT NOT NULL,
                note TEXT,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        """)
        conn.commit()

def create_intervention(student_id, flagged_by, note, priority='Medium'):
    """Log a new outreach flag for a student."""
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO interventions (student_id, flagged_by, note, priority) VALUES (?, ?, ?, ?)",
            (str(student_id), flagged_by, note, priority)
        )
        conn.commit()

def get_interventions(status_filter='All'):
    """Fetch the outreach log, optionally filtered by status ('Open' / 'Resolved' / 'All')."""
    with get_db_connection() as conn:
        if status_filter == 'All':
            return pd.read_sql("SELECT * FROM interventions ORDER BY created_at DESC", conn)
        return pd.read_sql(
            "SELECT * FROM interventions WHERE status = ? ORDER BY created_at DESC",
            conn, params=[status_filter]
        )

def update_intervention_status(intervention_id, new_status):
    """Mark an intervention Resolved (stamps resolved_at) or Reopened (clears it)."""
    with get_db_connection() as conn:
        if new_status == 'Resolved':
            conn.execute(
                "UPDATE interventions SET status = ?, resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_status, intervention_id)
            )
        else:
            conn.execute(
                "UPDATE interventions SET status = ?, resolved_at = NULL WHERE id = ?",
                (new_status, intervention_id)
            )
        conn.commit()

# ─────────────────────────────────────────
#  STUDENT-SPECIFIC FUNCTIONS (New / Fixed)
# ─────────────────────────────────────────

def get_student_behavior(student_id, table_name='behavior'):
    """Fetch all behavior columns for one student."""
    _assert_valid_table(table_name)
    with get_db_connection() as conn:
        query = f'SELECT * FROM "{table_name}" WHERE Student_ID = ?'
        df = pd.read_sql(query, conn, params=[str(student_id)])
        if df.empty:
            # try int match
            query2 = f'SELECT * FROM "{table_name}" WHERE CAST(Student_ID AS TEXT) = ?'
            df = pd.read_sql(query2, conn, params=[str(student_id)])
        return df

def get_student_engagement(student_id, table_name='engagement'):
    """Fetch all engagement columns for one student."""
    _assert_valid_table(table_name)
    with get_db_connection() as conn:
        query = f'SELECT * FROM "{table_name}" WHERE student_id = ?'
        df = pd.read_sql(query, conn, params=[str(student_id)])
        if df.empty:
            query2 = f'SELECT * FROM "{table_name}" WHERE CAST(student_id AS TEXT) = ?'
            df = pd.read_sql(query2, conn, params=[str(student_id)])
        return df

def get_class_stats(table_name, metric_cols):
    """Return mean, min, max for given columns (pandas-based, safe for special col names)."""
    _assert_valid_table(table_name)
    for c in metric_cols:
        _assert_valid_column(table_name, c)
    with get_db_connection() as conn:
        # Quote each column name to handle special chars like (%)
        cols_quoted = ', '.join([f'"{c}"' for c in metric_cols])
        df = pd.read_sql(f'SELECT {cols_quoted} FROM "{table_name}"', conn)
    result = {}
    for c in metric_cols:
        result[f'avg_{c}'] = float(df[c].mean())
        result[f'min_{c}'] = float(df[c].min())
        result[f'max_{c}'] = float(df[c].max())
    return result

def get_percentile(student_val, table_name, col):
    """What % of students scored <= student_val in this column."""
    try:
        _assert_valid_table(table_name)
        _assert_valid_column(table_name, col)
        with get_db_connection() as conn:
            df = pd.read_sql(f'SELECT "{col}" FROM "{table_name}"', conn)
        total = len(df)
        if total == 0:
            return 0
        below = (df[col] <= float(student_val)).sum()
        return round((below / total) * 100, 1)
    except Exception:
        return 0

def get_top_students(table_name, col, limit=5):
    """Top N students by a column."""
    _assert_valid_table(table_name)
    _assert_valid_column(table_name, col)
    limit = int(limit)  # also guards the LIMIT clause, which can't be parameterized either
    with get_db_connection() as conn:
        return pd.read_sql(
            f'SELECT * FROM "{table_name}" ORDER BY "{col}" DESC LIMIT {limit}', conn)

# ─────────────────────────────────────────
#  EXISTING FUNCTIONS (kept + improved)
# ─────────────────────────────────────────

def learning_intensity(student_id=None, table_name='behavior'):
    _assert_valid_table(table_name)
    with get_db_connection() as conn:
        query = f'SELECT Student_ID, [Course_Completion_Rate(%)], Daily_Learning_Hours FROM "{table_name}"'
        df = pd.read_sql(query, conn)
        df = df[df['Daily_Learning_Hours'] > 0].copy()
        df['intensity'] = df['Course_Completion_Rate(%)'] / df['Daily_Learning_Hours']
        if student_id:
            s = df[df['Student_ID'].astype(str) == str(student_id)]
            return s['intensity'].iloc[0] if not s.empty else None
        return df['intensity'].mean()

def engagement_efficiency(student_id=None, table_name='engagement'):
    _assert_valid_table(table_name)
    with get_db_connection() as conn:
        query = f'SELECT student_id, final_grade, engagement_score FROM "{table_name}"'
        df = pd.read_sql(query, conn)
        df = df[df['engagement_score'] > 0].copy()
        df['efficiency'] = df['final_grade'] / df['engagement_score']
        if student_id:
            s = df[df['student_id'].astype(str) == str(student_id)]
            return s['efficiency'].iloc[0] if not s.empty else None
        return df[['student_id', 'efficiency']]

def submission_power(table_name='engagement'):
    _assert_valid_table(table_name)
    with get_db_connection() as conn:
        df = pd.read_sql(f'SELECT final_grade, assignments_submitted FROM "{table_name}"', conn)
        med = df['assignments_submitted'].median()
        return {
            "more_than_median": df[df['assignments_submitted'] > med]['final_grade'].mean(),
            "less_than_equal_median": df[df['assignments_submitted'] <= med]['final_grade'].mean(),
            "median_value": med
        }

def get_class_averages(behavior_table='behavior', engagement_table='engagement'):
    eff_df = engagement_efficiency(table_name=engagement_table)
    return {
        "avg_intensity": learning_intensity(table_name=behavior_table),
        "avg_efficiency": eff_df['efficiency'].mean() if isinstance(eff_df, pd.DataFrame) else 0,
        "avg_grade": submission_power(table_name=engagement_table)["more_than_median"]
    }

def get_behavior_data(table_name='behavior'):
    _assert_valid_table(table_name)
    with get_db_connection() as conn:
        return pd.read_sql(f'SELECT * FROM "{table_name}"', conn)

def get_engagement_data(table_name='engagement'):
    _assert_valid_table(table_name)
    with get_db_connection() as conn:
        return pd.read_sql(f'SELECT * FROM "{table_name}"', conn)

def get_available_datasets():
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM datasets ORDER BY upload_date DESC", conn)

def save_new_dataset(df, name, dataset_type):
    if dataset_type not in ('behavior', 'engagement'):
        return False, f"Invalid dataset type: {dataset_type!r}"
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna("Unknown")
    import time
    table_name = f"ds_{dataset_type}_{int(time.time())}"
    try:
        with get_db_connection() as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.cursor().execute(
                "INSERT INTO datasets (name, type, table_name) VALUES (?, ?, ?)",
                (name, dataset_type, table_name))
            conn.commit()
        return True, table_name
    except Exception as e:
        return False, str(e)

def hash_password(password, salt=None):
    """
    PBKDF2-HMAC-SHA256 with a random per-user salt (stdlib only — hashlib + secrets,
    no new dependency). Returns 'salt$hash', both hex, ready to store in users.password.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100_000)
    return f"{salt}${dk.hex()}"

def verify_password(password, stored):
    """Check a plaintext password against a stored 'salt$hash' string.
    Returns False (not an error) for a legacy plaintext row that hasn't been migrated
    yet — authenticate_user() handles that case separately."""
    if '$' not in stored:
        return False
    salt, _ = stored.split('$', 1)
    return secrets.compare_digest(hash_password(password, salt), stored)

def create_user(username, password, role):
    try:
        with get_db_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hash_password(password), role))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    """
    Looks up the user by username, then verifies the password in Python (can't compare
    a hash to the raw password in SQL). Existing rows created before this fix still have
    the old plaintext password — those are verified with a direct match and then
    transparently rehashed and saved, so default/legacy logins (e.g. admin/admin) keep
    working without needing a separate migration script.
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT username, password, role FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if row is None:
            return None
        uname, stored, role = row
        if '$' in stored:
            return (uname, role) if verify_password(password, stored) else None
        # legacy plaintext row — verify directly, then migrate to a hash on success
        if stored == password:
            conn.execute("UPDATE users SET password = ? WHERE username = ?",
                         (hash_password(password), uname))
            conn.commit()
            return (uname, role)
        return None

def user_exists(username):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
        return cur.fetchone() is not None