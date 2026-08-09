# EduTrak 🎓

**EduTrak** is a comprehensive data analytics portal designed for educational institutions to monitor student performance, engagement, and behavior. It provides interactive dashboards for both administrators and students, enabling data-driven decision-making.

## 🚀 Key Features
- **Dynamic Dataset Management**: Admins can upload and manage multiple datasets.
- **Automated Preprocessing**: Intelligent handling of missing values (Nulls) during dataset uploads.
- **Smart Insights**: Automated analysis of charts to provide actionable feedback.
- **Role-Based Access**: Specialized dashboards for Admins/Instructors and Students.
- **Predictive Analytics**: A trained RandomForestClassifier (`train_dropout_model.py`) predicts each student's dropout probability in real time from their engagement profile, with a live "AI Risk Predictor" tool and feature-importance chart in the Risk & Engagement page.

## 🛠️ Tech Stack
- **Frontend/UI**: Streamlit
- **Backend Logic**: Python
- **Database**: SQLite3
- **Data Analysis**: Pandas, NumPy
- **Machine Learning**: scikit-learn (RandomForestClassifier), joblib
- **Visualization**: Matplotlib, Seaborn

## 📋 Prerequisites
- Python 3.8 or higher installed on your system.

## ⚙️ Project Setup

### 1. Clone or Extract the Project
Ensure all project files are in a single directory.

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the Database
Before running the app for the first time, you must set up the database and load the initial datasets:
```bash
python database_setup.py
```
This will create `edutrak.db` and populate it with the default behavior and engagement data.

### 5. Train the Dropout Risk Model
This trains and saves the ML model used by the "AI Risk Predictor" tool (only needs to be run once, or again if you change the engagement data):
```bash
python train_dropout_model.py
```
This will print evaluation metrics (accuracy, ROC-AUC, cross-validation) and save `dropout_model.pkl`.

### 6. Run the Application
```bash
streamlit run app.py
```

## 🔐 Default Credentials
You can use these accounts to explore the platform:
- **Admin**: `admin` / `admin`
- **Student**: `student` / `student`
*(You can also create new accounts using the Sign Up feature in the sidebar)*

---
**Project developed by Atharva Maurya (Student @ BBDU) - 2026**
