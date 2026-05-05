# from flask import Flask, render_template, request, redirect, session
# import sqlite3
# from utils.qr_generator import generate_qr
# from datetime import date
# from flask import request
# from datetime import datetime
# import json



# app = Flask(__name__)
# app.secret_key = "smart_attendance_secret"

# def get_db():
#     return sqlite3.connect("database/attendance.db")

# @app.route("/", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         conn = get_db()
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT id, role FROM users WHERE email=? AND password=?",
#             (email, password)
#         )
#         user = cursor.fetchone()
#         conn.close()

#         if user:
#             session["user_id"] = user[0]
#             session["role"] = user[1]

#             if user[1] == "student":
#                 return redirect("/student")
#             else:
#                 return redirect("/faculty")

#         return "<h3>Invalid Credentials</h3>"

#     return render_template("login.html")

# @app.route("/student")
# def student_dashboard():
#     if session.get("role") != "student":
#         return redirect("/")
#     return render_template("student_dashboard.html")


# @app.route("/faculty")
# def faculty_dashboard():
#     if session.get("role") != "faculty":
#         return redirect("/")
#     return render_template("faculty_dashboard.html")


# @app.route("/generate_qr")
# def generate_qr_route():
#     if session.get("role") != "faculty":
#         return redirect("/")

#     conn = get_db()
#     cursor = conn.cursor()

#     # Create a new session
#     cursor.execute("""
#         INSERT INTO sessions (faculty_id, subject, session_date, created_at)
#         VALUES (?, ?, ?, ?)
#     """, (
#         session["user_id"],
#         "Regular Class",
#         date.today().isoformat(),
#         datetime.now().isoformat()
#     ))

#     session_id = cursor.lastrowid
#     conn.commit()
#     conn.close()

#     generate_qr(session_id)

#     return render_template("faculty_dashboard.html", qr=True)


# @app.route("/scan_qr")
# def scan_qr():
#     if session.get("role") != "student":
#         return redirect("/")
#     return render_template("scan_qr.html")


# @app.route("/mark_attendance", methods=["POST"])
# def mark_attendance():
#     if session.get("role") != "student":
#         return redirect("/")

#     try:
#         qr_data = request.form["qrdata"]
#         data = json.loads(qr_data)
#         session_id = data["session_id"]
#     except:
#         return "❌ Invalid QR Code"

#     student_id = session["user_id"]

#     conn = get_db()
#     cursor = conn.cursor()

#     # Check if already marked for this session
#     cursor.execute("""
#         SELECT id FROM attendance
#         WHERE student_id = ? AND session_id = ?
#     """, (student_id, session_id))

#     if cursor.fetchone():
#         conn.close()
#         return render_template("attendance_exists.html")

#     # Mark attendance
#     cursor.execute("""
#         INSERT INTO attendance (student_id, session_id, status)
#         VALUES (?, ?, ?)
#     """, (student_id, session_id, "Present"))

#     conn.commit()
#     conn.close()

#     return render_template("attendance_success.html")


# @app.route("/attendance_percentage")
# def attendance_percentage():
#     student_id = session["user_id"]

#     conn = get_db()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT COUNT(DISTINCT session_id)
#         FROM attendance
#         WHERE student_id = ?
#     """, (student_id,))
#     attended = cursor.fetchone()[0]

#     cursor.execute("SELECT COUNT(*) FROM sessions")
#     total = cursor.fetchone()[0]

#     conn.close()

#     percentage = 0
#     if total > 0:
#         percentage = min((attended / total) * 100, 100)

#     # return render_template(
#     #     "attendance_percentage.html",
#     #     attended=attended,
#     #     total=total,
#     #     percentage=round(percentage, 2)
#     # )
#     return render_template("attendance_percentage.html",
#                            attended=attended,
#                            total=total,
#                            percentage=percentage)

# @app.route("/view_attendance")
# def view_attendance():
#     if session.get("role") != "faculty":
#         return redirect("/")

#     conn = get_db()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT users.name, attendance.date, attendance.status
#         FROM attendance
#         JOIN users ON users.id = attendance.student_id
#         ORDER BY attendance.date DESC
#     """)

#     records = cursor.fetchall()
#     conn.close()

#     return render_template("view_attendance.html", records=records)



# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         name = request.form["name"]
#         email = request.form["email"]
#         password = request.form["password"]
#         role = request.form["role"]

#         conn = get_db()
#         cursor = conn.cursor()

#         try:
#             cursor.execute(
#                 "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
#                 (name, email, password, role)
#             )
#             conn.commit()

#         except sqlite3.IntegrityError:
#             conn.close()
#             return """
#             <h3 style="color:red;">⚠ Email already registered</h3>
#             <a href="/register">Try another email</a>
#             """

#         finally:
#             conn.close()

#         return redirect("/")

#     return render_template("register.html")



# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/")

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=False)


from flask import Flask, render_template, request, redirect, session
import sqlite3
from utils.qr_generator import generate_qr
from datetime import date, datetime
import json
import re

app = Flask(__name__)
app.secret_key = "smart_attendance_secret"


# =========================
# DATABASE CONNECTION
# =========================
def get_db():
    """Establish and return a connection to the SQLite database."""
    return sqlite3.connect("database/attendance.db")

def init_db():
    """Ensure database has the required columns for GPS tracking."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Add latitude column
        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN latitude REAL")
            conn.commit()
        except:
            pass
            
        # Add longitude column
        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN longitude REAL")
            conn.commit()
        except:
            pass

        # Add address column
        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN address TEXT")
            conn.commit()
        except:
            pass
            
        # Add accuracy column
        try:
            cursor.execute("ALTER TABLE attendance ADD COLUMN accuracy REAL")
            conn.commit()
        except:
            pass
        
        # Add latitude column to sessions
        try:
            cursor.execute("ALTER TABLE sessions ADD COLUMN latitude REAL")
            conn.commit()
        except:
            pass
            
        # Add longitude column to sessions
        try:
            cursor.execute("ALTER TABLE sessions ADD COLUMN longitude REAL")
            conn.commit()
        except:
            pass
            
        conn.close()
    except Exception as e:
        print(f"Database init error: {e}")

def insert_master_users():
    """Guarantee that there is always at least one valid faculty and student account."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Faculty
        cursor.execute("SELECT id FROM users WHERE email='admin@test.com'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (name, email, password, role) VALUES ('Master Faculty', 'admin@test.com', 'Admin@123!', 'faculty')")
        else:
            cursor.execute("UPDATE users SET password='Admin@123!' WHERE email='admin@test.com'")
            
        # Student
        cursor.execute("SELECT id FROM users WHERE email='student@test.com'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (name, email, password, role) VALUES ('Master Student', 'student@test.com', 'Student@123!', 'student')")
        else:
            cursor.execute("UPDATE users SET password='Student@123!' WHERE email='student@test.com'")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Master users error: {e}")

init_db()
insert_master_users()


# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    """
    Handle user authentication.
    POST: Verify credentials and initialize a session for student or faculty.
    GET: Render the login form.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["role"] = user[1]

            if user[1] == "student":
                return redirect("/student")
            else:
                return redirect("/faculty")

        return "<h3 style='color:red;'>Invalid Credentials</h3>"

    return render_template("login.html")


# =========================
# STUDENT DASHBOARD
# =========================
@app.route("/student")
def student_dashboard():
    """Render the student dashboard if the user is logged in as a student."""
    if session.get("role") != "student":
        return redirect("/")
    return render_template("student_dashboard.html")


# =========================
# FACULTY DASHBOARD
# =========================
@app.route("/faculty")
def faculty_dashboard():
    """Render the faculty dashboard if the user is logged in as faculty."""
    if session.get("role") != "faculty":
        return redirect("/")
    return render_template("faculty_dashboard.html")


# =========================
# GENERATE QR (FACULTY)
# =========================
@app.route("/generate_qr")
def generate_qr_route():
    """
    Create a new attendance session for the faculty and generate a QR code for it.
    Only accessible by faculty users.
    """
    if session.get("role") != "faculty":
        return redirect("/")

    print("➡️ Generate QR route hit")

    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sessions (faculty_id, subject, session_date, created_at, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        "Regular Class",
        date.today().isoformat(),
        datetime.now().isoformat(),
        lat, lon
    ))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print("🆔 Session ID:", session_id)

    generate_qr(session_id)
    print("✅ QR generated")

    return render_template("faculty_dashboard.html", qr=True)


# =========================
# SCAN QR (STUDENT)
# =========================
@app.route("/scan_qr")
def scan_qr():
    """Render the QR scanning page for students."""
    if session.get("role") != "student":
        return redirect("/")
    return render_template("scan_qr.html")


# =========================
# MARK ATTENDANCE (STUDENT)
# =========================
@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    """
    Process QR code data to mark attendance for a student.
    Ensures that a student cannot mark attendance twice for the same session.
    """
    if session.get("role") != "student":
        return redirect("/")

    try:
        qr_data = request.form["qrdata"]
        data = json.loads(qr_data)
        session_id = data["session_id"]
    except:
        return "<h3>❌ Invalid QR Code</h3>"

    # Capture incoming location details
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    accuracy = request.form.get("accuracy")
    address = request.form.get("address", "Unknown Location")

    student_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    # Prevent duplicate attendance for same session
    cursor.execute("""
        SELECT id FROM attendance
        WHERE student_id = ? AND session_id = ?
    """, (student_id, session_id))

    if cursor.fetchone():
        conn.close()
        return render_template("attendance_exists.html")

    # Mark attendance with location metadata to prevent proxy status
    cursor.execute("""
        INSERT INTO attendance (student_id, session_id, status, latitude, longitude, address, accuracy)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (student_id, session_id, "Present", latitude, longitude, address, accuracy))

    conn.commit()
    conn.close()

    return render_template("attendance_success.html")


# =========================
# ATTENDANCE PERCENTAGE (STUDENT)
# =========================
@app.route("/attendance_percentage")
def attendance_percentage():
    """
    Calculate and display the student's overall attendance percentage.
    Compares the sessions attended by the student against total sessions created.
    """
    if session.get("role") != "student":
        return redirect("/")

    student_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    # Classes attended by student
    cursor.execute("""
        SELECT COUNT(DISTINCT session_id)
        FROM attendance
        WHERE student_id = ?
    """, (student_id,))
    attended = cursor.fetchone()[0]

    # Total classes conducted (sessions)
    cursor.execute("""
        SELECT COUNT(*)
        FROM sessions
    """)
    total = cursor.fetchone()[0]

    conn.close()

    percentage = 0
    if total > 0:
        percentage = round((attended / total) * 100, 2)

    return render_template(
        "attendance_percentage.html",
        attended=attended,
        total=total,
        percentage=percentage
    )



# =========================
# VIEW ATTENDANCE (FACULTY)
# =========================
@app.route("/view_attendance")
def view_attendance():
    """
    Fetch and display all attendance records for the sessions created by the current faculty member.
    """
    if session.get("role") != "faculty":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.name, s.session_date, a.status, a.latitude, a.longitude, a.address, a.accuracy
        FROM attendance a
        JOIN users u ON u.id = a.student_id
        JOIN sessions s ON s.id = a.session_id
        WHERE s.faculty_id = ?
        ORDER BY s.session_date DESC
    """, (session["user_id"],))

    records = cursor.fetchall()
    conn.close()

    return render_template("view_attendance.html", records=records)



# =========================
# ATTENDANCE ANALYTICS (FACULTY)
# =========================
@app.route("/faculty_analytics")
def faculty_analytics():
    """
    Calculate and display attendance percentages for all students 
    for sessions created by the current faculty member.
    """
    if session.get("role") != "faculty":
        return redirect("/")

    faculty_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()

    # 1. Get total sessions created by this faculty
    cursor.execute("SELECT COUNT(*) FROM sessions WHERE faculty_id = ?", (faculty_id,))
    total_sessions = cursor.fetchone()[0]

    # 2. Get attendance data for all students
    # We want to see how many times each student attended sessions created by THIS faculty
    cursor.execute("""
        SELECT u.name, u.email, 
               (SELECT COUNT(*) FROM attendance a 
                JOIN sessions s ON a.session_id = s.id 
                WHERE a.student_id = u.id AND s.faculty_id = ?) as attended_count
        FROM users u
        WHERE u.role = 'student'
    """, (faculty_id,))
    
    student_data = cursor.fetchall()
    conn.close()

    analytics = []
    for name, email, attended in student_data:
        percentage = 0
        if total_sessions > 0:
            percentage = round((attended / total_sessions) * 100, 2)
        
        analytics.append({
            "name": name,
            "email": email,
            "attended": attended,
            "total": total_sessions,
            "percentage": percentage
        })

    return render_template("faculty_analytics.html", analytics=analytics)


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration for both students and faculty.
    Ensures email uniqueness in the database.
    """
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        # Validate password complexity
        if not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9]).{8,}$", password):
            return """
            <h3 style="color:red;">⚠ Password must contain at least 8 characters, including uppercase, lowercase, numbers, and symbols.</h3>
            <a href="/register">Back to Registration</a>
            """

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (name, email, password, role))
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return """
            <h3 style="color:red;">⚠ Email already registered</h3>
            <a href="/register">Try another email</a>
            """

        conn.close()
        return redirect("/")

    return render_template("register.html")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    """Clear the active user session and redirect to the login page."""
    session.clear()
    return redirect("/")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    # Run on port 5001 to avoid MacOS AirPlay port 5000 conflicts
    app.run(host="127.0.0.1", port=5001, debug=True)
