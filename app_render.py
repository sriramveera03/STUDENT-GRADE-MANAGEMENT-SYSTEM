import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash, g
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secretkey123')

DATABASE = os.path.join(os.path.dirname(__file__), 'school.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def dict_from_row(row):
    return dict(row) if row else None


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template("index.html")


# ---------------- STUDENT LOGIN PAGE ----------------
@app.route('/student_login')
def student_login():
    return render_template("student_login.html")


# ---------------- STUDENT LOGIN LOGIC ----------------
@app.route('/student_login', methods=['POST'])
def student_login_post():
    roll_number = request.form['roll_number']
    dob = request.form['dob']

    cur = get_db().cursor()
    cur.execute("SELECT * FROM students WHERE roll_number=? AND dob=?", (roll_number, dob))
    student = dict_from_row(cur.fetchone())

    if student:
        session['student_id'] = student['id']
        return redirect(url_for('student_dashboard', id=student['id']))
    else:
        flash("Invalid roll number or date of birth. Please try again.")
        return redirect(url_for('student_login'))


# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student/<int:id>')
def student_dashboard(id):
    if 'student_id' not in session or session['student_id'] != id:
        return redirect(url_for('home'))

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = dict_from_row(cur.fetchone())

    if not student:
        return redirect(url_for('home'))

    cur.execute("""
        SELECT
            subj.id AS subject_id,
            subj.name AS subject_name,
            MAX(CASE WHEN sa.assessment_type = 'UNIT1' THEN sa.marks END) AS unit1,
            MAX(CASE WHEN sa.assessment_type = 'UNIT2' THEN sa.marks END) AS unit2,
            MAX(CASE WHEN sa.assessment_type = 'PREFINAL1' THEN sa.marks END) AS prefinal1,
            MAX(CASE WHEN sa.assessment_type = 'PREFINAL2' THEN sa.marks END) AS prefinal2,
            MAX(CASE WHEN sa.assessment_type = 'FINAL1' THEN sa.marks END) AS final1,
            MAX(CASE WHEN sa.assessment_type = 'FINAL2' THEN sa.marks END) AS final2
        FROM subjects AS subj
        LEFT JOIN student_assessments AS sa
            ON sa.subject_id = subj.id AND sa.student_id = ?
        GROUP BY subj.id, subj.name
        ORDER BY subj.id
    """, (id,))
    subjects = [dict_from_row(row) for row in cur.fetchall()]

    cur.execute("""
        SELECT COALESCE(SUM(marks), 0) AS total_marks, COALESCE(AVG(marks), 0) AS average_marks
        FROM student_assessments WHERE student_id = ?
    """, (id,))
    stats = dict_from_row(cur.fetchone())

    total = float(stats["total_marks"]) if stats else 0.0
    average = round(float(stats["average_marks"]), 2) if stats else 0.0

    if average >= 90:
        grade = "A+"
    elif average >= 75:
        grade = "A"
    elif average >= 60:
        grade = "B"
    elif average >= 50:
        grade = "C"
    else:
        grade = "Fail"

    return render_template("student.html", student=student, subjects=subjects, total=total, average=average, grade=grade)


# ---------------- DOWNLOAD PDF ----------------
@app.route('/download_pdf/<int:id>')
def download_pdf(id):
    if 'student_id' not in session or session['student_id'] != id:
        return redirect(url_for('home'))

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = dict_from_row(cur.fetchone())

    if not student:
        return redirect(url_for('home'))

    cur.execute("""
        SELECT subj.name AS subject_name,
            MAX(CASE WHEN sa.assessment_type = 'UNIT1' THEN sa.marks END) AS unit1,
            MAX(CASE WHEN sa.assessment_type = 'UNIT2' THEN sa.marks END) AS unit2,
            MAX(CASE WHEN sa.assessment_type = 'PREFINAL1' THEN sa.marks END) AS prefinal1,
            MAX(CASE WHEN sa.assessment_type = 'PREFINAL2' THEN sa.marks END) AS prefinal2,
            MAX(CASE WHEN sa.assessment_type = 'FINAL1' THEN sa.marks END) AS final1,
            MAX(CASE WHEN sa.assessment_type = 'FINAL2' THEN sa.marks END) AS final2
        FROM subjects AS subj
        LEFT JOIN student_assessments AS sa ON sa.subject_id = subj.id AND sa.student_id = ?
        GROUP BY subj.id, subj.name ORDER BY subj.id
    """, (id,))
    subjects = [dict_from_row(row) for row in cur.fetchall()]

    cur.execute("SELECT COALESCE(SUM(marks), 0) AS total_marks, COALESCE(AVG(marks), 0) AS average_marks FROM student_assessments WHERE student_id = ?", (id,))
    stats = dict_from_row(cur.fetchone())

    total = float(stats["total_marks"]) if stats else 0.0
    average = round(float(stats["average_marks"]), 2) if stats else 0.0

    if average >= 90:
        grade = "A+"
    elif average >= 75:
        grade = "A"
    elif average >= 60:
        grade = "B"
    elif average >= 50:
        grade = "C"
    else:
        grade = "Fail"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>LITTLE FLOWER PRIMARY AND HIGH SCHOOL</b>", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("<b>EXAMINATION - MARKS MEMO</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.5 * inch))

    dob_str = student['dob'] if isinstance(student['dob'], str) else student['dob']
    details = [
        ["Roll Number", student['roll_number']],
        ["Name", student['name']],
        ["School", student['school_name'] or ''],
        ["Date of Birth", dob_str],
    ]
    detail_table = Table(details, colWidths=[2.5 * inch, 3 * inch])
    detail_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(detail_table)
    elements.append(Spacer(1, 0.5 * inch))

    header = ["Subject", "Unit 1", "Unit 2", "Prefinal 1", "Prefinal 2", "Final 1", "Final 2"]
    rows = [header]
    for row in subjects:
        rows.append([
            row["subject_name"],
            row["unit1"] if row["unit1"] is not None else "",
            row["unit2"] if row["unit2"] is not None else "",
            row["prefinal1"] if row["prefinal1"] is not None else "",
            row["prefinal2"] if row["prefinal2"] is not None else "",
            row["final1"] if row["final1"] is not None else "",
            row["final2"] if row["final2"] is not None else "",
        ])
    rows.append(["", "", "", "", "", "Total", total])
    rows.append(["", "", "", "", "", "Average", average])
    rows.append(["", "", "", "", "", "Grade", grade])

    marks_table = Table(rows, colWidths=[1.5*inch, 0.7*inch, 0.7*inch, 0.9*inch, 0.9*inch, 0.7*inch, 0.7*inch])
    marks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))
    elements.append(marks_table)
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(f"Issue Date: {date.today()}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename={student['roll_number']}_Result.pdf"
    return response


# ---------------- TEACHER LOGIN ----------------
@app.route('/teacher_login')
def teacher_login():
    return render_template("teacher_login.html")


@app.route('/teacher_login', methods=['POST'])
def teacher_login_post():
    username = (request.form.get('username') or "").strip()
    password = (request.form.get('password') or "").strip()

    cur = get_db().cursor()
    cur.execute("SELECT * FROM teachers WHERE username=?", (username,))
    teacher = dict_from_row(cur.fetchone())

    if teacher and teacher.get("password") and str(teacher["password"]).strip() == password:
        session['teacher_id'] = teacher['id']
        return redirect(url_for('teacher_dashboard'))

    flash("Invalid username or password. Try admin/admin123 or teacher1/password123.")
    return redirect(url_for('teacher_login'))


# ---------------- TEACHER DASHBOARD ----------------
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'teacher_id' not in session:
        return redirect(url_for('home'))

    cur = get_db().cursor()
    cur.execute("SELECT id, roll_number, name FROM students")
    students = cur.fetchall()

    return render_template("teacher.html", students=students)


# ---------------- PRINT ALL STUDENTS ----------------
@app.route('/print_all_students')
def print_all_students():
    if 'teacher_id' not in session:
        return redirect(url_for('home'))

    cur = get_db().cursor()
    cur.execute("SELECT * FROM students ORDER BY roll_number")
    students = [dict_from_row(row) for row in cur.fetchall()]

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(11*inch, 8.5*inch))
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>LITTLE FLOWER PRIMARY AND HIGH SCHOOL</b>", styles['Title']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("<b>ALL STUDENTS DETAILS</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.3 * inch))

    data = [["Roll No", "Name", "Father Name", "Mobile", "Class", "DOB", "Address"]]
    for s in students:
        data.append([
            s.get('roll_number', '-'),
            s.get('name', '-'),
            s.get('father_name', '-') or '-',
            s.get('mobile_number', '-') or '-',
            s.get('class', '-') or '-',
            s.get('dob', '-') or '-',
            (s.get('address', '-') or '-')[:30],
        ])

    table = Table(data, colWidths=[0.8*inch, 1.3*inch, 1.3*inch, 1.1*inch, 0.7*inch, 1*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b3d91')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f6f9')]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Total Students: {len(students)}", styles['Normal']))
    elements.append(Paragraph(f"Generated on: {date.today().strftime('%d-%m-%Y')}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=All_Students_Details.pdf'
    return response


# ---------------- STUDENT DETAILS (TEACHER ONLY) ----------------
@app.route('/student_details/<int:id>')
def student_details(id):
    if 'teacher_id' not in session:
        return redirect(url_for('home'))

    cur = get_db().cursor()
    cur.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = dict_from_row(cur.fetchone())

    if not student:
        return redirect(url_for('teacher_dashboard'))

    return render_template("student_details.html", student=student)


# ---------------- UPDATE STUDENT ----------------
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    if 'teacher_id' not in session:
        return redirect(url_for('home'))

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = dict_from_row(cur.fetchone())

    if not student:
        return redirect(url_for('teacher_dashboard'))

    cur.execute("SELECT id, name FROM subjects ORDER BY id")
    subjects = [dict_from_row(row) for row in cur.fetchall()]

    assessment_types = ["UNIT1", "UNIT2", "PREFINAL1", "PREFINAL2", "FINAL1", "FINAL2"]

    if request.method == 'POST':
        name = request.form.get('name', '')
        father_name = request.form.get('father_name', '') or None
        mobile_number = request.form.get('mobile_number', '') or None
        class_name = request.form.get('class', '') or None
        address = request.form.get('address', '') or None

        cur.execute("UPDATE students SET name=?, father_name=?, mobile_number=?, class=?, address=? WHERE id=?",
                    (name, father_name, mobile_number, class_name, address, id))

        for subj in subjects:
            subject_id = subj["id"]
            for assessment in assessment_types:
                field_name = f"marks_{subject_id}_{assessment}"
                raw_value = request.form.get(field_name)

                if raw_value is None or str(raw_value).strip() == "":
                    continue

                try:
                    marks = float(raw_value)
                except ValueError:
                    continue

                cur.execute("SELECT id FROM student_assessments WHERE student_id=? AND subject_id=? AND assessment_type=?",
                            (id, subject_id, assessment))
                existing = cur.fetchone()

                if existing:
                    cur.execute("UPDATE student_assessments SET marks=? WHERE id=?", (marks, existing[0]))
                else:
                    cur.execute("INSERT INTO student_assessments (student_id, subject_id, assessment_type, marks) VALUES (?, ?, ?, ?)",
                                (id, subject_id, assessment, marks))

        db.commit()
        return redirect(url_for('teacher_dashboard'))

    cur.execute("SELECT subject_id, assessment_type, marks FROM student_assessments WHERE student_id = ?", (id,))
    assessment_rows = cur.fetchall()

    assessments = {}
    for row in assessment_rows:
        sid = row[0]
        atype = row[1]
        assessments.setdefault(sid, {})[atype] = row[2]

    def _grade(avg):
        if avg >= 90: return "A+"
        if avg >= 75: return "A"
        if avg >= 60: return "B"
        if avg >= 50: return "C"
        return "Fail"

    subject_stats = {}
    for subj in subjects:
        sid = subj["id"]
        subj_assess = assessments.get(sid, {})
        vals = [float(subj_assess.get(t, 0) or 0) for t in assessment_types]
        total = sum(vals)
        avg = total / 6 if vals else 0
        subject_stats[sid] = {"total": round(total, 2), "percentage": round(avg, 2), "grade": _grade(avg)}

    return render_template("update.html", student=student, subjects=subjects, assessments=assessments,
                           assessment_types=assessment_types, subject_stats=subject_stats)


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/vision_mission')
def vision_mission():
    return render_template("vision_mission.html")


@app.route('/school_timings')
def school_timings():
    return render_template("school_timings.html")


@app.route('/contact_us')
def contact_us():
    return render_template("contact_us.html")


if __name__ == "__main__":
    app.run(debug=True)
