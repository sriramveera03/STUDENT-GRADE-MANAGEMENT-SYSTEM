import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'school.db')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            father_name TEXT,
            mobile_number TEXT,
            school_name TEXT,
            class TEXT,
            address TEXT,
            dob TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS student_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            assessment_type TEXT NOT NULL,
            marks REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE (student_id, subject_id, assessment_type)
        )
    ''')

    cur.execute("INSERT OR IGNORE INTO teachers (username, password) VALUES ('admin', 'admin123')")
    cur.execute("INSERT OR IGNORE INTO teachers (username, password) VALUES ('teacher1', 'password123')")

    subjects = [('Telugu', 'TEL'), ('English', 'ENG'), ('Hindi', 'HIN'), ('Maths', 'MAT'), ('Science', 'SCI'), ('Social', 'SOC')]
    for name, code in subjects:
        cur.execute("INSERT OR IGNORE INTO subjects (name, code) VALUES (?, ?)", (name, code))

    # 40 students
    students_data = [
        ('1001', 'Reddy Ram', 'Reddy Srinivas', '9876543210', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '12, MG Road, Hyderabad', '2007-05-10'),
        ('1002', 'Naidu Raja', 'Naidu Venkatesh', '9876543211', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '45, Tank Bund, Secunderabad', '2007-08-21'),
        ('1003', 'Sharma Priya', 'Sharma Ramesh', '9876543212', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '78, Jubilee Hills, Hyderabad', '2007-03-15'),
        ('1004', 'Reddy Anjali', 'Reddy Prasad', '9876543213', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '23, Banjara Hills, Hyderabad', '2007-11-02'),
        ('1005', 'Koppula Sairam', 'Koppula Satyanarayana', '9876543214', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '56, Kukatpally, Hyderabad', '2007-08-19'),
        ('1006', 'Syed Ahmed', 'Syed Ibrahim', '9876543215', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '89, Ameerpet, Hyderabad', '2007-12-10'),
        ('1007', 'Devi Pavitra', 'Devi Mahesh', '9876543216', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '34, Madhapur, Hyderabad', '2007-07-30'),
        ('1008', 'Varma Avikshit', 'Varma Suresh', '9876543217', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '67, Gachibowli, Hyderabad', '2007-10-09'),
        ('1009', 'Reddy Arjun', 'Reddy Krishna', '9876543218', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '90, Kondapur, Hyderabad', '2007-01-15'),
        ('1010', 'Kumar Kiran', 'Kumar Narayana', '9876543219', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '11, Begumpet, Hyderabad', '2007-02-18'),
        ('1011', 'Varma Rahul', 'Varma Rajesh', '9876543220', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '44, Somajiguda, Hyderabad', '2007-03-22'),
        ('1012', 'Reddy Varun', 'Reddy Venkata Rao', '9876543221', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '77, Himayatnagar, Hyderabad', '2007-04-10'),
        ('1013', 'Reddy Sai', 'Reddy Srinivasa Rao', '9876543222', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '22, Abids, Hyderabad', '2007-05-12'),
        ('1014', 'Naidu Vishal', 'Naidu Subbarao', '9876543223', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '55, Nampally, Hyderabad', '2007-06-05'),
        ('1015', 'Sharma Nikhil', 'Sharma Mahendra', '9876543224', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '88, Dilsukhnagar, Hyderabad', '2007-07-19'),
        ('1016', 'Kumar Teja', 'Kumar Gopal', '9876543225', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '33, LB Nagar, Hyderabad', '2007-09-14'),
        ('1017', 'Reddy Aditya', 'Reddy Raghava', '9876543226', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '66, Uppal, Hyderabad', '2007-10-21'),
        ('1018', 'Kumar Manoj', 'Kumar Shankar', '9876543227', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '99, Tarnaka, Hyderabad', '2007-11-03'),
        ('1019', 'Teja Charan', 'Teja Ramesh', '9876543228', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '10, Malkajgiri, Hyderabad', '2007-12-17'),
        ('1020', 'Sharma Rohit', 'Sharma Suresh', '9876543229', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '43, Kompally, Hyderabad', '2007-06-25'),
        # 20 new students
        ('1021', 'Patel Vivek', 'Patel Ramakrishna', '9876543230', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '15, Miyapur, Hyderabad', '2007-04-03'),
        ('1022', 'Rao Deepika', 'Rao Venkataramana', '9876543231', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '28, Chandanagar, Hyderabad', '2007-09-11'),
        ('1023', 'Singh Akash', 'Singh Dharmendra', '9876543232', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '51, Patancheru, Hyderabad', '2007-01-29'),
        ('1024', 'Gupta Sneha', 'Gupta Rajendra', '9876543233', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '74, Bachupally, Hyderabad', '2007-07-07'),
        ('1025', 'Chowdary Lakshmi', 'Chowdary Venkat', '9876543234', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '37, Nizampet, Hyderabad', '2007-02-14'),
        ('1026', 'Yadav Suresh', 'Yadav Ramesh', '9876543235', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '60, Pragathi Nagar, Hyderabad', '2007-08-08'),
        ('1027', 'Mishra Pooja', 'Mishra Shiv Kumar', '9876543236', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '83, Lingampally, Hyderabad', '2007-03-30'),
        ('1028', 'Nair Arjun', 'Nair Surendran', '9876543237', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '16, KPHB Colony, Hyderabad', '2007-11-16'),
        ('1029', 'Verma Ananya', 'Verma Deepak', '9876543238', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '39, Bowenpally, Secunderabad', '2007-06-22'),
        ('1030', 'Pillai Arun', 'Pillai Krishnamurthy', '9876543239', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '62, Trimulgherry, Secunderabad', '2007-10-05'),
        ('1031', 'Bhat Kavya', 'Bhat Narayana', '9876543240', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '85, Maredpally, Secunderabad', '2007-05-18'),
        ('1032', 'Iyer Rithvik', 'Iyer Subramanian', '9876543241', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '18, Karkhana, Secunderabad', '2007-09-25'),
        ('1033', 'Mehta Divya', 'Mehta Prakash', '9876543242', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '41, Sainikpuri, Secunderabad', '2007-04-12'),
        ('1034', 'Joshi Harsha', 'Joshi Balasubramanyam', '9876543243', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '64, AS Rao Nagar, Hyderabad', '2007-12-01'),
        ('1035', 'Kaur Simran', 'Singh Gurpreet', '9876543244', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '87, Nagole, Hyderabad', '2007-07-27'),
        ('1036', 'Pandey Rohit', 'Pandey Santosh', '9876543245', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '20, Hayathnagar, Hyderabad', '2007-01-08'),
        ('1037', 'Desai Meghna', 'Desai Pramod', '9876543246', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '43, Vanasthalipuram, Hyderabad', '2007-08-31'),
        ('1038', 'Rao Tarun', 'Rao Sridhar', '9876543247', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '66, Saroornagar, Hyderabad', '2007-03-09'),
        ('1039', 'Krishnan Aditi', 'Krishnan Gopalan', '9876543248', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '89, Bandlaguda, Hyderabad', '2007-10-19'),
        ('1040', 'Saxena Vikram', 'Saxena Anil', '9876543249', 'LITTLE FLOWER PRIMARY AND HIGH SCHOOL', '10th', '12, Attapur, Hyderabad', '2007-06-14'),
    ]

    for s in students_data:
        cur.execute('''INSERT OR IGNORE INTO students 
                      (roll_number, name, father_name, mobile_number, school_name, class, address, dob) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', s)

    marks_data = {
        '1001': {'Telugu': 97, 'English': 90, 'Hindi': 74, 'Maths': 85, 'Science': 92, 'Social': 67},
        '1002': {'Telugu': 70, 'English': 60, 'Hindi': 74, 'Maths': 65, 'Science': 72, 'Social': 87},
        '1003': {'Telugu': 79, 'English': 90, 'Hindi': 76, 'Maths': 95, 'Science': 62, 'Social': 87},
        '1004': {'Telugu': 80, 'English': 70, 'Hindi': 94, 'Maths': 85, 'Science': 72, 'Social': 97},
        '1005': {'Telugu': 86, 'English': 79, 'Hindi': 74, 'Maths': 65, 'Science': 92, 'Social': 87},
        '1006': {'Telugu': 96, 'English': 89, 'Hindi': 94, 'Maths': 85, 'Science': 92, 'Social': 77},
        '1007': {'Telugu': 92, 'English': 98, 'Hindi': 95, 'Maths': 82, 'Science': 90, 'Social': 78},
        '1008': {'Telugu': 82, 'English': 88, 'Hindi': 92, 'Maths': 72, 'Science': 60, 'Social': 88},
        '1009': {'Telugu': 78, 'English': 85, 'Hindi': 80, 'Maths': 90, 'Science': 88, 'Social': 75},
        '1010': {'Telugu': 65, 'English': 72, 'Hindi': 70, 'Maths': 68, 'Science': 74, 'Social': 80},
        '1011': {'Telugu': 88, 'English': 91, 'Hindi': 85, 'Maths': 95, 'Science': 90, 'Social': 87},
        '1012': {'Telugu': 70, 'English': 75, 'Hindi': 68, 'Maths': 72, 'Science': 66, 'Social': 74},
        '1013': {'Telugu': 92, 'English': 89, 'Hindi': 94, 'Maths': 96, 'Science': 91, 'Social': 90},
        '1014': {'Telugu': 60, 'English': 65, 'Hindi': 58, 'Maths': 70, 'Science': 62, 'Social': 68},
        '1015': {'Telugu': 85, 'English': 83, 'Hindi': 78, 'Maths': 88, 'Science': 84, 'Social': 80},
        '1016': {'Telugu': 74, 'English': 77, 'Hindi': 69, 'Maths': 81, 'Science': 75, 'Social': 79},
        '1017': {'Telugu': 89, 'English': 84, 'Hindi': 86, 'Maths': 90, 'Science': 88, 'Social': 85},
        '1018': {'Telugu': 67, 'English': 73, 'Hindi': 71, 'Maths': 76, 'Science': 70, 'Social': 72},
        '1019': {'Telugu': 91, 'English': 93, 'Hindi': 89, 'Maths': 94, 'Science': 92, 'Social': 90},
        '1020': {'Telugu': 76, 'English': 81, 'Hindi': 79, 'Maths': 84, 'Science': 73, 'Social': 77},
        # New students marks
        '1021': {'Telugu': 83, 'English': 87, 'Hindi': 80, 'Maths': 91, 'Science': 85, 'Social': 78},
        '1022': {'Telugu': 94, 'English': 92, 'Hindi': 88, 'Maths': 97, 'Science': 93, 'Social': 91},
        '1023': {'Telugu': 68, 'English': 71, 'Hindi': 65, 'Maths': 73, 'Science': 69, 'Social': 76},
        '1024': {'Telugu': 89, 'English': 86, 'Hindi': 82, 'Maths': 88, 'Science': 87, 'Social': 84},
        '1025': {'Telugu': 75, 'English': 78, 'Hindi': 72, 'Maths': 80, 'Science': 76, 'Social': 81},
        '1026': {'Telugu': 62, 'English': 67, 'Hindi': 63, 'Maths': 69, 'Science': 64, 'Social': 70},
        '1027': {'Telugu': 91, 'English': 94, 'Hindi': 90, 'Maths': 95, 'Science': 92, 'Social': 89},
        '1028': {'Telugu': 77, 'English': 80, 'Hindi': 74, 'Maths': 82, 'Science': 79, 'Social': 83},
        '1029': {'Telugu': 86, 'English': 88, 'Hindi': 84, 'Maths': 90, 'Science': 87, 'Social': 85},
        '1030': {'Telugu': 58, 'English': 63, 'Hindi': 55, 'Maths': 66, 'Science': 60, 'Social': 64},
        '1031': {'Telugu': 93, 'English': 96, 'Hindi': 91, 'Maths': 98, 'Science': 94, 'Social': 92},
        '1032': {'Telugu': 72, 'English': 75, 'Hindi': 70, 'Maths': 78, 'Science': 73, 'Social': 77},
        '1033': {'Telugu': 87, 'English': 89, 'Hindi': 85, 'Maths': 92, 'Science': 88, 'Social': 86},
        '1034': {'Telugu': 64, 'English': 68, 'Hindi': 61, 'Maths': 72, 'Science': 66, 'Social': 69},
        '1035': {'Telugu': 90, 'English': 93, 'Hindi': 88, 'Maths': 94, 'Science': 91, 'Social': 89},
        '1036': {'Telugu': 69, 'English': 72, 'Hindi': 67, 'Maths': 75, 'Science': 71, 'Social': 73},
        '1037': {'Telugu': 84, 'English': 87, 'Hindi': 82, 'Maths': 89, 'Science': 85, 'Social': 83},
        '1038': {'Telugu': 78, 'English': 81, 'Hindi': 76, 'Maths': 83, 'Science': 80, 'Social': 79},
        '1039': {'Telugu': 95, 'English': 97, 'Hindi': 93, 'Maths': 99, 'Science': 96, 'Social': 94},
        '1040': {'Telugu': 71, 'English': 74, 'Hindi': 69, 'Maths': 77, 'Science': 72, 'Social': 75},
    }

    assessment_types = ['UNIT1', 'UNIT2', 'PREFINAL1', 'PREFINAL2', 'FINAL1', 'FINAL2']

    for roll, subjects_marks in marks_data.items():
        cur.execute("SELECT id FROM students WHERE roll_number=?", (roll,))
        student_row = cur.fetchone()
        if not student_row:
            continue
        student_id = student_row[0]

        for subj_name, marks in subjects_marks.items():
            cur.execute("SELECT id FROM subjects WHERE name=?", (subj_name,))
            subj_row = cur.fetchone()
            if not subj_row:
                continue
            subject_id = subj_row[0]

            for atype in assessment_types:
                cur.execute('''INSERT OR IGNORE INTO student_assessments 
                              (student_id, subject_id, assessment_type, marks) 
                              VALUES (?, ?, ?, ?)''', (student_id, subject_id, atype, marks))

    conn.commit()
    conn.close()
    print("Database initialized successfully with 40 students!")


if __name__ == "__main__":
    init_db()
