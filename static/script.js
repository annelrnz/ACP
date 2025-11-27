// static/script.js
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
            document.getElementById('studentName').textContent = data.name;
            document.getElementById('attendanceForm').classList.remove('hidden');
            document.getElementById('registrationForm').classList.add('hidden');
        } else {
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
        
        const result = await response.json();
        if (result.success) {
            showSuccess();
        } else {
            showMessage(result.message || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error, 'error');
    }
}

async function recordAttendance() {
    const studentId = document.getElementById('studentId').value;
    const courseCode = document.getElementById('courseCode').value;
    const classTime = document.getElementById('classTime').value;
    
    if (!courseCode || !classTime) {
        return showMessage('Please select both class and time', 'error');
    }
    
    try {
        const response = await fetch('/record_attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                student_id: studentId, 
                course_code: courseCode,
                class_time: classTime 
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess();
        } else {
            showMessage(data.message || 'Error recording attendance', 'error');
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