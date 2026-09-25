from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

CSV_FILE = "student_performance.csv"


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# ADD / ANALYZE STUDENT
# --------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    name = request.form["name"]

    python_marks = int(request.form["python"])
    sql_marks = int(request.form["sql"])
    statistics_marks = int(request.form["statistics"])

    average = round(
        (python_marks + sql_marks + statistics_marks) / 3,
        2
    )

    # Performance
    if average >= 85:
        performance = "Excellent"
    elif average >= 70:
        performance = "Good"
    elif average >= 50:
        performance = "Average"
    else:
        performance = "Needs Improvement"

    # Grade
    if average >= 90:
        grade = "A+"
    elif average >= 80:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 50:
        grade = "D"
    else:
        grade = "F"

    student = {
        "Student": name,
        "Python": python_marks,
        "SQL": sql_marks,
        "Statistics": statistics_marks,
        "Average": average,
        "Performance": performance,
        "Grade": grade
    }

    df_new = pd.DataFrame([student])

    # Create or append CSV
    if os.path.exists(CSV_FILE):

        df_old = pd.read_csv(CSV_FILE)

        # Make sure old CSV has Grade column
        if "Grade" not in df_old.columns:

            df_old["Grade"] = df_old["Average"].apply(
                calculate_grade
            )

        df = pd.concat(
            [df_old, df_new],
            ignore_index=True
        )

        df.to_csv(
            CSV_FILE,
            index=False
        )

    else:

        df_new.to_csv(
            CSV_FILE,
            index=False
        )

    return render_template(
        "result.html",
        name=name,
        python=python_marks,
        sql=sql_marks,
        statistics=statistics_marks,
        average=average,
        performance=performance,
        grade=grade
    )


# --------------------------------------------------
# GRADE CALCULATION
# --------------------------------------------------

def calculate_grade(average):

    if average >= 90:
        return "A+"
    elif average >= 80:
        return "A"
    elif average >= 70:
        return "B"
    elif average >= 60:
        return "C"
    elif average >= 50:
        return "D"
    else:
        return "F"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data():

    if os.path.exists(CSV_FILE):

        df = pd.read_csv(CSV_FILE)

        if "Grade" not in df.columns:

            df["Grade"] = df["Average"].apply(
                calculate_grade
            )

        return df

    return pd.DataFrame(
        columns=[
            "Student",
            "Python",
            "SQL",
            "Statistics",
            "Average",
            "Performance",
            "Grade"
        ]
    )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    df = load_data()

    total_students = len(df)

    if total_students > 0:

        overall_average = round(
            df["Average"].mean(),
            2
        )

        top_student = df.loc[
            df["Average"].idxmax()
        ].to_dict()

    else:

        overall_average = 0

        top_student = {
            "Student": "No Data",
            "Average": 0,
            "Grade": "-",
            "Performance": "-"
        }

    students = df.to_dict(
        orient="records"
    )

    return render_template(
        "dashboard.html",
        total_students=total_students,
        overall_average=overall_average,
        top_student=top_student,
        students=students
    )


# --------------------------------------------------
# VIEW ALL STUDENTS
# --------------------------------------------------

@app.route("/students")
def students():

    df = load_data()

    student_list = df.to_dict(
        orient="records"
    )

    return render_template(
        "students.html",
        students=student_list,
        total_students=len(df)
    )


# --------------------------------------------------
# TOP PERFORMER
# --------------------------------------------------

@app.route("/top-performer")
def top_performer():

    df = load_data()

    if len(df) > 0:

        top = df.loc[
            df["Average"].idxmax()
        ].to_dict()

    else:

        top = {
            "Student": "No Data",
            "Python": 0,
            "SQL": 0,
            "Statistics": 0,
            "Average": 0,
            "Performance": "-",
            "Grade": "-"
        }

    return render_template(
        "top_performer.html",
        top=top
    )


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

@app.route("/analytics")
def analytics():

    df = load_data()

    if len(df) > 0:

        python_average = round(
            df["Python"].mean(),
            2
        )

        sql_average = round(
            df["SQL"].mean(),
            2
        )

        statistics_average = round(
            df["Statistics"].mean(),
            2
        )

        performance_counts = (
            df["Performance"]
            .value_counts()
            .to_dict()
        )

        grade_counts = (
            df["Grade"]
            .value_counts()
            .to_dict()
        )

        student_names = df["Student"].tolist()

        student_averages = df["Average"].tolist()

    else:

        python_average = 0
        sql_average = 0
        statistics_average = 0

        performance_counts = {}
        grade_counts = {}

        student_names = []
        student_averages = []

    return render_template(
        "analytics.html",
        python_average=python_average,
        sql_average=sql_average,
        statistics_average=statistics_average,
        performance_counts=performance_counts,
        grade_counts=grade_counts,
        student_names=student_names,
        student_averages=student_averages
    )


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# --------------------------------------------------
# DOWNLOAD CSV
# --------------------------------------------------

@app.route("/download")
def download():

    if os.path.exists(CSV_FILE):

        return send_file(
            CSV_FILE,
            as_attachment=True,
            download_name="student_performance_report.csv"
        )

    return "No student data available."


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)