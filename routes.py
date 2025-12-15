from datetime import datetime  # FIXED: Use datetime instead of importing datetime module
from flask import render_template, request, jsonify
from models import Student, Attendance 

def setup_routes(app):
    
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/check_student', methods=['POST'])
    def check_student():
        """Check if student is registered"""
        data = request.get_json()
        student_id = data.get('student_id')
        
        student = Student.get_student_by_id(student_id)
        if student:
            return jsonify({
                'registered': True,
                'name': student[2],  # name is at index 2
                'student_id': student[1],
                'course': student[3],
                'section': student[4]
            })
        else:
            return jsonify({'registered': False})
    
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
        """Record attendance for a student"""
        try:
            data = request.get_json()
            student_id = data.get('student_id')
            course_code = data.get('course_code')
            class_time = data.get('class_time')
            
            if not all([student_id, course_code, class_time]):
                return jsonify({'success': False, 'message': 'Missing required fields'})
            
            # Get student to determine section
            student = Student.get_student_by_id(student_id)
            if not student:
                return jsonify({'success': False, 'message': 'Student not found'})
            
            section = student[4]  # section is at index 4
            
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
                    <form action="/mark_attendance" method="POST">
                        <input type="hidden" name="course_code" value="{course_code}">
                        <input type="hidden" name="section" value="{section}">
                        <input type="hidden" name="class_time" value="{class_time}">
                        <input type="text" name="student_id" placeholder="Enter Student ID" required>
                        <button type="submit">Mark Attendance</button>
                    </form>
                </div>
            </body>
        </html>
        """
    
    @app.route('/mark_attendance', methods=['POST'])
    def mark_attendance():
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
    
        # Mark attendance
        success, message = Attendance.mark_attendance(student_id, course_code, section, class_time)
        
        if success:
            student_name = student[2] if len(student) > 2 else "Unknown"  # name is at index 2
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
                        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <p>You can close this window now.</p>
                </body>
            </html>
            """
        else:
            return f"Error: {message}", 400