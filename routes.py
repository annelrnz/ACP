from datetime import datetime
from flask import render_template, request, jsonify
from models import Student, Attendance, AttendanceHistory 

def setup_routes(app):
    
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/check_student', methods=['POST'])
    def check_student():
        """Check if student is registered"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'registered': False, 'message': 'Invalid JSON data'})
            
            student_id = data.get('student_id')
            
            if not student_id:
                return jsonify({'registered': False, 'message': 'Student ID is required'})
            
            student = Student.get_student_by_id(student_id)
            if student:
                return jsonify({
                    'registered': True,
                    'name': student[2] if len(student) > 2 else 'Unknown',
                    'student_id': student[1] if len(student) > 1 else student_id,
                    'course': student[3] if len(student) > 3 else 'Unknown',
                    'section': student[4] if len(student) > 4 else 'Unknown'
                })
            else:
                return jsonify({'registered': False, 'message': 'Student not found'})
        except Exception as e:
            return jsonify({'registered': False, 'message': f'Error: {str(e)}'})
    
    @app.route('/register', methods=['POST'])
    def register_student():
        """Register a new student"""
        try:
            student_data = {
                'student_id': request.form.get('student_id'),
                'name': request.form.get('name'),
                'course': request.form.get('course'),
                'section': request.form.get('section'),
                'block': request.form.get('block', ''),
                'gsuite': request.form.get('gsuite', '')
            }
            
            # Validate required fields
            required_fields = ['student_id', 'name', 'course', 'section']
            for field in required_fields:
                if not student_data[field]:
                    return jsonify({'success': False, 'message': f'Missing required field: {field}'})
            
            success, message = Student.create(student_data)
            return jsonify({'success': success, 'message': message})
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Registration error: {str(e)}'})
    
    @app.route('/record_attendance', methods=['POST'])
    def record_attendance():
        """Record attendance for a student - JSON API endpoint"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Invalid JSON data'})
            
            student_id = data.get('student_id')
            course_code = data.get('course_code')
            class_time = data.get('class_time')
            
            if not all([student_id, course_code, class_time]):
                return jsonify({'success': False, 'message': 'Missing required fields'})
            
            # Get student to determine section
            student = Student.get_student_by_id(student_id)
            if not student:
                return jsonify({'success': False, 'message': 'Student not found'})
            
            section = student[4] if len(student) > 4 else 'Unknown'
            
            # Mark attendance
            success, message = Attendance.mark_attendance(student_id, course_code, section, class_time)
            return jsonify({'success': success, 'message': message})
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error recording attendance: {str(e)}'})
    
    @app.route('/attendance')
    def attendance_page():
        course_code = request.args.get('course', 'Unknown Course')
        section = request.args.get('section', 'Unknown Section')
        class_time = request.args.get('time', 'Unknown Time')
        
        return f"""
        <html>
            <head>
                <title>Attendance - {course_code}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .container {{ max-width: 500px; margin: 0 auto; text-align: center; }}
                    .info {{ background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                    input, button {{ padding: 10px; margin: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎯 Attendify</h1>
                    <div class="info">
                        <h2>{course_code}</h2>
                        <p>Section: {section}</p>
                        <p>Time: {class_time}</p>
                    </div>
                    <h3>Student Attendance Portal</h3>
                    <p>Please log in to mark your attendance</p>
                    <input type="text" id="student_id" placeholder="Enter Student ID">
                    <button onclick="markAttendance()">Mark Attendance</button>
                    <div id="result" style="margin-top: 20px;"></div>
                </div>
                
                <script>
                    function markAttendance() {{
                        const studentId = document.getElementById('student_id').value;
                        if (!studentId) {{
                            alert('Please enter your Student ID');
                            return;
                        }}
                        
                        // First check if student exists
                        fetch('/check_student', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ student_id: studentId }})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.registered) {{
                                // Student exists, record attendance
                                fetch('/record_attendance', {{
                                    method: 'POST',
                                    headers: {{ 'Content-Type': 'application/json' }},
                                    body: JSON.stringify({{
                                        student_id: studentId,
                                        course_code: '{course_code}',
                                        class_time: '{class_time}'
                                    }})
                                }})
                                .then(response => response.json())
                                .then(attendanceData => {{
                                    if (attendanceData.success) {{
                                        document.getElementById('result').innerHTML = 
                                            `<div style="color: green; font-size: 18px;">
                                                ✅ Attendance recorded successfully!<br>
                                                Student: ${{data.name}}<br>
                                                Section: ${{data.section}}<br>
                                                Time: {datetime.now().strftime('%H:%M:%S')}
                                            </div>`;
                                    }} else {{
                                        document.getElementById('result').innerHTML = 
                                            `<div style="color: red;">❌ ${{attendanceData.message}}</div>`;
                                    }}
                                }})
                                .catch(error => {{
                                    document.getElementById('result').innerHTML = 
                                        `<div style="color: red;">❌ Error: ${{error}}</div>`;
                                }});
                            }} else {{
                                document.getElementById('result').innerHTML = 
                                    `<div style="color: red;">❌ Student not found. Please contact your professor.</div>`;
                            }}
                        }})
                        .catch(error => {{
                            document.getElementById('result').innerHTML = 
                                `<div style="color: red;">❌ Error: ${{error}}</div>`;
                        }});
                    }}
                </script>
            </body>
        </html>
        """
    
    @app.route('/mark_attendance', methods=['POST'])
    def mark_attendance():
        """HTML form endpoint for attendance marking"""
        student_id = request.form.get('student_id')
        course_code = request.form.get('course_code')
        section = request.form.get('section')
        class_time = request.form.get('class_time')
   
        student = Student.get_student_by_id(student_id)
        if not student:
            return "Error: Student ID not found. Please make sure you're registered in the professor system.", 400
    
        # Check if student belongs to this section
        student_section = student[4] if len(student) > 4 else ""  
        if student_section != section:
            return f"Error: You are registered in section {student_section}, but this QR code is for section {section}", 400
    
        success, message = Attendance.mark_attendance(student_id, course_code, section, class_time)
        
        if success:
            student_name = student[2] if len(student) > 2 else "Unknown"
            
            # Get the exact timestamp from attendance_history
            history = AttendanceHistory.get_student_attendance_history(student_id, course_code)
            exact_timestamp = ""
            if history and len(history) > 0:
                # Get the most recent attendance
                latest = history[0]
                exact_date = latest['date']
                exact_time = latest['time']
                exact_timestamp = f"{exact_date} {exact_time}"
            else:
                exact_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return f"""
            <html>
                <head>
                    <title>Attendance Confirmed</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; margin: 50px; }}
                        .success {{ color: green; font-size: 24px; }}
                        .info {{ background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 400px; }}
                    </style>
                </head>
                <body>
                    <h1>✅ Attendance Marked Successfully!</h1>
                    <div class="info">
                        <p><strong>Student:</strong> {student_name}</p>
                        <p><strong>Student ID:</strong> {student_id}</p>
                        <p><strong>Course:</strong> {course_code}</p>
                        <p><strong>Section:</strong> {section}</p>
                        <p><strong>Time:</strong> {class_time}</p>
                        <p><strong>Timestamp:</strong> {exact_timestamp}</p>
                    </div>
                    <p>Attendance has been recorded in your history.</p>
                    <p>You can close this window now.</p>
                </body>
            </html>
            """
        else:
            return f"Error: {message}", 400
    
    @app.route('/student_history')
    def student_history_page():
        """Page for students to view their own attendance history"""
        pass
    
    @app.route('/get_student_history', methods=['GET'])
    def get_student_history():
        """Get attendance history for a student"""
        pass
    
    @app.route('/section_history')
    def section_history_page():
        """Page for professors to view section attendance history"""
        pass
    
    @app.route('/get_section_history', methods=['GET'])
    def get_section_history():
        """Get attendance history for a section"""
        pass
    
    @app.route('/export_section_history', methods=['GET'])
    def export_section_history():
        """Export section history to CSV"""
        pass