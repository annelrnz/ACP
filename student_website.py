from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('attendify.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            name TEXT,
            course TEXT,
            block TEXT,
            gsuite TEXT,
            first_scan_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            course_code TEXT,
            class_time TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# HTML templates as strings
INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Attendify - Student Portal</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 500px; 
            margin: 0 auto; 
            padding: 20px; 
            background: #ffffff;
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .attendify-title { 
            font-size: 36px; 
            font-weight: bold; 
            color: #2E86AB; 
            margin: 0; 
        }
        .subtitle { 
            font-size: 14px; 
            color: #666666; 
            margin: 5px 0 0 0; 
        }
        .form-container { 
            background: #f8f9fa; 
            padding: 30px; 
            border-radius: 10px; 
            border: 1px solid #ddd;
        }
        input, select { 
            width: 100%; 
            padding: 12px; 
            margin: 8px 0; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            box-sizing: border-box;
        }
        button { 
            background: #2E86AB; 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
            width: 100%; 
            margin-top: 10px;
        }
        button:hover { background: #1a5a7a; }
        .hidden { display: none; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="attendify-title">Attendify</h1>
        <p class="subtitle">MAKE YOUR PRESENCE</p>
    </div>

    <div class="form-container">
        <h3>Enter Your Student ID</h3>
        <input type="text" id="studentId" placeholder="Enter your Student ID" required>
        <button onclick="checkStudent()">Continue</button>
        
        <div id="registrationForm" class="hidden">
            <h3>First Time Registration</h3>
            <form id="regForm" onsubmit="submitRegistration(event)">
                <input type="hidden" name="student_id" id="formStudentId">
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="text" name="course" placeholder="Course" required>
                <input type="text" name="block" placeholder="Block" required>
                <input type="email" name="gsuite" placeholder="GSuite Email" required>
                <select name="Select class" required>
                     <option value="">Select Class</option>
                    <option value=" Advanced Computer Programming">Advanced Computer Programming</option>
                    <option value=" Object Oriented Programming">Object Oriented Programming</option>
                    <option value="Discrete Mathematics">Discrete Mathematics</option>
                    <option value="Computer Networking">Computer Networking</option>
                    <option value="PathFit-3">PathFit-3</option>
                    <option value="Asean Literature">Asean Literature</option>
                </select>
                <select name="class_time" required>
                    <option value="">Select Class Time</option>
                    <option value="8:00-9:00 AM">8:00-9:00 AM</option>
                    <option value="9:00-10:00 AM">9:00-10:00 AM</option>
                    <option value="10:00-11:00 AM">10:00-11:00 AM</option>
                    <option value="11:00-12:00 PM">11:00-12:00 PM</option>
                    <option value="12:00-1:00 PM">12:00-1:00 PM</option>
                    <option value="1:00-2:00 PM">1:00-2:00 PM</option>
                    <option value="2:00-3:00 PM">2:00-3:00 PM</option>
                    <option value="3:00-4:00 PM">3:00-4:00 PM</option>
                    <option value="4:00-5:00 PM">4:00-5:00 PM</option>
                    <option value="5:00-6:00 PM">5:00-6:00 PM</option>
                    <option value="6:00-7:00 PM">6:00-7:00 PM</option>
                </select>
                <button type="submit">Submit Attendance</button>
            </form>
        </div>

        <div id="attendanceForm" class="hidden">
            <h3>Record Attendance</h3>
            <p>Welcome back, <span id="studentName"></span>!</p>
            <select name="Select class" required>
                     <option value="">Select Class</option>
                    <option value=" Advanced Computer Programming">Advanced Computer Programming</option>
                    <option value=" Object Oriented Programming">Object Oriented Programming</option>
                    <option value="Discrete Mathematics">Discrete Mathematics</option>
                    <option value="Computer Networking">Computer Networking</option>
                    <option value="PathFit-3">PathFit-3</option>
                    <option value="Asean Literature">Asean Literature</option>
                </select>
            <select id="classTime">
                <option value="">Select Class Time</option>
                <option value="8:00-9:00 AM">8:00-9:00 AM</option>
                <option value="9:00-10:00 AM">9:00-10:00 AM</option>
                <option value="10:00-11:00 AM">10:00-11:00 AM</option>
                <option value="1:00-2:00 PM">1:00-2:00 PM</option>
                <option value="2:00-3:00 PM">2:00-3:00 PM</option>
            </select>
            <button onclick="recordAttendance()">Record Attendance</button>
        </div>

        <div id="message" class="hidden"></div>
    </div>

    <script>
        async function checkStudent() {
            const studentId = document.getElementById('studentId').value;
            if (!studentId) return showMessage('Please enter your Student ID', 'error');
            
            try {
                const response = await fetch('/check_student', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ student_id: studentId })
                });
                
                const data = await response.json();
                
                if (data.registered) {
                    // Existing student
                    document.getElementById('studentName').textContent = data.name;
                    document.getElementById('attendanceForm').classList.remove('hidden');
                    document.getElementById('registrationForm').classList.add('hidden');
                } else {
                    // New student
                    document.getElementById('formStudentId').value = studentId;
                    document.getElementById('registrationForm').classList.remove('hidden');
                    document.getElementById('attendanceForm').classList.add('hidden');
                }
                hideMessage();
                
            } catch (error) {
                showMessage('Error checking student: ' + error, 'error');
            }
        }
        
        async function submitRegistration(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        showSuccess();
                    } else {
                        showMessage(result.message || 'Registration failed', 'error');
                    }
                } else {
                    showMessage('Registration failed', 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error, 'error');
            }
        }
        
        async function recordAttendance() {
            const studentId = document.getElementById('studentId').value;
            const classTime = document.getElementById('classTime').value;
            
            if (!classTime) return showMessage('Please select class time', 'error');
            
            try {
                const response = await fetch('/record_attendance', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        student_id: studentId, 
                        class_time: classTime 
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showSuccess();
                } else {
                    showMessage('Error recording attendance', 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error, 'error');
            }
        }
        
        function showSuccess() {
            document.body.innerHTML = `
                <div class="header">
                    <h1 class="attendify-title">Attendify</h1>
                    <p class="subtitle">MAKE YOUR PRESENCE</p>
                </div>
                <div class="form-container">
                    <div style="text-align: center;">
                        <div style="font-size: 80px; color: #28a745;">✅</div>
                        <h2>ATTENDANCE SUCCESSFULLY RECORDED!</h2>
                        <p>Your presence has been logged in the system.</p>
                        <p>Thank you!</p>
                        <button onclick="location.reload()">Record Another Attendance</button>
                    </div>
                </div>
            `;
        }
        
        function showMessage(message, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = message;
            messageDiv.className = type;
            messageDiv.classList.remove('hidden');
        }
        
        function hideMessage() {
            document.getElementById('message').classList.add('hidden');
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def home():
    return INDEX_HTML

@app.route('/check_student', methods=['POST'])
def check_student():
    student_id = request.json.get('student_id')
    
    conn = sqlite3.connect('attendify.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    
    if student:
        return jsonify({'registered': True, 'name': student[2]})
    else:
        return jsonify({'registered': False})

@app.route('/register', methods=['POST'])
def register():
    student_id = request.form['student_id']
    name = request.form['name']
    course = request.form['course']
    block = request.form['block']
    gsuite = request.form['gsuite']
    class_time = request.form['class_time']
    
    conn = sqlite3.connect('attendify.db')
    cursor = conn.cursor()
    
    try:
        # Save student
        cursor.execute('''
            INSERT INTO students (student_id, name, course, block, gsuite)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, name, course, block, gsuite))
        
        # Record attendance
        cursor.execute('''
            INSERT INTO attendance_records (student_id, course_code, class_time)
            VALUES (?, ?, ?)
        ''', (student_id, course, class_time))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Attendance recorded successfully!'})
        
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Student ID already exists!'})
    
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/record_attendance', methods=['POST'])
def record_attendance():
    data = request.json
    student_id = data.get('student_id')
    class_time = data.get('class_time')
    
    conn = sqlite3.connect('attendify.db')
    cursor = conn.cursor()
    
    try:
        # Get student course
        cursor.execute("SELECT course FROM students WHERE student_id = ?", (student_id,))
        student = cursor.fetchone()
        
        if student:
            course = student[0]
            # Record attendance
            cursor.execute('''
                INSERT INTO attendance_records (student_id, course_code, class_time)
                VALUES (?, ?, ?)
            ''', (student_id, course, class_time))
            
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        
        conn.close()
        return jsonify({'success': False, 'message': 'Student not found'})
    
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    init_db()
    print("🚀 Attendify Student Website running on http://localhost:5000")
    print("📱 Students can scan QR code to access this website")
    app.run(debug=True, host='0.0.0.0', port=5000)