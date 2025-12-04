// Global State
let currentPage = 'homepage';
let currentRole = null;
let registeredStudents = {};
let loggedInUser = null;
let lastActivityTime = null;
let inactivityTimer = null;
let videoStream = null;
let loginVideoStream = null;

const INACTIVITY_TIMEOUT = 3 * 60 * 1000; // 3 minutes
const INACTIVITY_WARNING_TIME = 2.5 * 60 * 1000; // 2.5 minutes

// Mock Data
const mockStudents = [
    { name: "John Smith", srCode: "21-00001", department: "CS", section: "A", subjects: ["Math 101", "Physics 101"], attendance: "ON TIME" },
    { name: "Maria Garcia", srCode: "21-00002", department: "CS", section: "A", subjects: ["Math 101", "Physics 101"], attendance: "ON TIME" },
    { name: "Ahmed Hassan", srCode: "21-00003", department: "CS", section: "B", subjects: ["Data Structures", "Database"], attendance: "LATE" },
    { name: "Sarah Lee", srCode: "21-00004", department: "EN", section: "A", subjects: ["Engineering Design", "Materials"], attendance: "ON TIME" },
    { name: "Carlos Lopez", srCode: "21-00005", department: "BUS", section: "C", subjects: ["Business Law", "Economics"], attendance: "ON TIME" },
    { name: "Emily Chen", srCode: "21-00006", department: "CS", section: "B", subjects: ["Data Structures", "Database"], attendance: "ON TIME" },
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000);
    loadRegisteredStudents();
});

// Clock Update
function updateClock() {
    const now = new Date();
    
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    
    const timeDisplay = document.getElementById('timeDisplay');
    if (timeDisplay) {
        timeDisplay.textContent = `${hours}:${minutes}:${seconds}`;
    }
    
    const dateDisplay = document.getElementById('dateDisplay');
    if (dateDisplay) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateDisplay.textContent = now.toLocaleDateString('en-US', options);
    }
}

// Navigation
function selectRole(role) {
    currentRole = role;
    if (role === 'student') {
        navigateTo('studentMenu');
    } else if (role === 'teacher') {
        navigateTo('teacherView');
    }
}

function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page).classList.add('active');
    currentPage = page;
    
    // Clear errors
    document.querySelectorAll('.error-message').forEach(err => err.classList.remove('show'));
}

function goBack() {
    stopVideoStreams();
    if (currentRole === 'student') {
        navigateTo('studentMenu');
    } else if (currentRole === 'teacher') {
        navigateTo('teacherView');
    } else {
        navigateTo('homepage');
        currentRole = null;
    }
}

// SR Code Validation
function validateSrCode(srCode) {
    const pattern = /^\d{2}-\d{5}$/;
    return pattern.test(srCode);
}

// Student Registration
function registerStudent() {
    const srCode = document.getElementById('srCodeInput').value.trim();
    const name = document.getElementById('studentNameInput').value.trim();
    const department = document.getElementById('departmentSelect').value;
    const section = document.getElementById('sectionSelect').value;
    const errorDiv = document.getElementById('registerError');
    
    errorDiv.classList.remove('show');
    
    if (!validateSrCode(srCode)) {
        showError(errorDiv, 'Invalid SR Code. Format: XX-XXXXX (e.g., 21-12345)');
        return;
    }
    
    if (!name) {
        showError(errorDiv, 'Please enter your full name');
        return;
    }
    
    if (!department) {
        showError(errorDiv, 'Please select a department');
        return;
    }
    
    if (!section) {
        showError(errorDiv, 'Please select a section');
        return;
    }
    
    if (registeredStudents[srCode]) {
        showError(errorDiv, 'SR Code already registered');
        return;
    }
    
    // Store registered student
    registeredStudents[srCode] = {
        name,
        srCode,
        department,
        section,
        registeredAt: new Date().toLocaleString()
    };
    
    saveRegisteredStudents();
    
    // Show success and clear form
    alert(`✓ Registration successful!\nWelcome, ${name}!`);
    document.getElementById('srCodeInput').value = '';
    document.getElementById('studentNameInput').value = '';
    document.getElementById('departmentSelect').value = '';
    document.getElementById('sectionSelect').value = '';
    
    navigateTo('studentMenu');
}

// Face Scan
function startFaceScan() {
    const department = document.getElementById('scanDepartmentSelect').value;
    const section = document.getElementById('scanSectionSelect').value;
    const errorDiv = document.getElementById('scanError');
    
    errorDiv.classList.remove('show');
    
    if (!department) {
        showError(errorDiv, 'Please select a department');
        return;
    }
    
    if (!section) {
        showError(errorDiv, 'Please select a section');
        return;
    }
    
    const video = document.getElementById('videoFeed');
    
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoStream = stream;
            video.srcObject = stream;
        })
        .catch(err => {
            showError(errorDiv, 'Cannot access camera: ' + err.message);
        });
}

function captureFace() {
    const department = document.getElementById('scanDepartmentSelect').value;
    const section = document.getElementById('scanSectionSelect').value;
    const errorDiv = document.getElementById('scanError');
    
    errorDiv.classList.remove('show');
    
    if (!department || !section) {
        showError(errorDiv, 'Please select department and section');
        return;
    }
    
    // Simulate face detection and matching
    const matchedStudent = mockStudents.find(s => s.department === department && s.section === section);
    
    if (matchedStudent) {
        stopVideoStreams();
        showSuccessNotification(matchedStudent);
        navigateTo('studentMenu');
    } else {
        showError(errorDiv, 'No matching student found in this section');
    }
}

function showSuccessNotification(student) {
    const notification = document.getElementById('successNotification');
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    const isLate = now.getHours() > 9 || (now.getHours() === 9 && now.getMinutes() > 0);
    
    document.getElementById('notifName').textContent = student.name;
    document.getElementById('notifSrCode').textContent = student.srCode;
    document.getElementById('notifTime').textContent = timeStr;
    
    const statusElement = document.getElementById('notifStatus');
    if (isLate) {
        statusElement.textContent = 'LATE';
        statusElement.className = 'status late';
    } else {
        statusElement.textContent = 'ON TIME';
        statusElement.className = 'status on-time';
    }
    
    document.getElementById('notifSubjects').textContent = student.subjects.join(', ');
    
    notification.classList.add('show');
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        closeNotification();
    }, 5000);
}

function closeNotification() {
    document.getElementById('successNotification').classList.remove('show');
}

// Profile Dashboard
function startProfileLogin() {
    const srCode = document.getElementById('loginSrCode').value.trim();
    const errorDiv = document.getElementById('loginError');
    
    errorDiv.classList.remove('show');
    
    if (!validateSrCode(srCode)) {
        showError(errorDiv, 'Invalid SR Code. Format: XX-XXXXX');
        return;
    }
    
    const video = document.getElementById('loginVideoFeed');
    
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            loginVideoStream = stream;
            video.srcObject = stream;
        })
        .catch(err => {
            showError(errorDiv, 'Cannot access camera: ' + err.message);
        });
}

function loginWithFace() {
    const srCode = document.getElementById('loginSrCode').value.trim();
    const errorDiv = document.getElementById('loginError');
    
    errorDiv.classList.remove('show');
    
    if (!validateSrCode(srCode)) {
        showError(errorDiv, 'Invalid SR Code');
        return;
    }
    
    // Find student in registered or mock data
    const student = registeredStudents[srCode] || mockStudents.find(s => s.srCode === srCode);
    
    if (!student) {
        showError(errorDiv, 'Student not found. Please register first.');
        return;
    }
    
    // Successful login
    loggedInUser = student;
    lastActivityTime = Date.now();
    stopVideoStreams();
    showProfileDashboard();
    startInactivityTimer();
}

function showProfileDashboard() {
    document.getElementById('profileNotLoggedIn').style.display = 'none';
    document.getElementById('profileLoggedIn').style.display = 'block';
    
    document.getElementById('profileName').textContent = loggedInUser.name;
    document.getElementById('profileSrCode').textContent = `SR Code: ${loggedInUser.srCode}`;
    document.getElementById('profileDepartment').textContent = `Department: ${loggedInUser.department}`;
    document.getElementById('profileSection').textContent = `Section: ${loggedInUser.section}`;
    
    // Load attendance
    loadAttendance();
}

function loadAttendance() {
    const attendanceList = document.getElementById('attendanceList');
    const student = mockStudents.find(s => s.srCode === loggedInUser.srCode);
    
    if (student) {
        const today = new Date().toLocaleDateString();
        const html = `
            <div class="attendance-item ${student.attendance === 'LATE' ? 'late' : 'present'}">
                <strong>Date:</strong> ${today}<br>
                <strong>Status:</strong> ${student.attendance}<br>
                <strong>Subjects:</strong> ${student.subjects.join(', ')}
            </div>
        `;
        attendanceList.innerHTML = html;
    }
}

function startInactivityTimer() {
    // Warning at 2.5 minutes
    setTimeout(() => {
        if (loggedInUser) {
            updateInactivityWarning(30);
        }
    }, INACTIVITY_WARNING_TIME);
    
    // Auto logout at 3 minutes
    inactivityTimer = setTimeout(() => {
        if (loggedInUser) {
            logoutProfile();
        }
    }, INACTIVITY_TIMEOUT);
}

function updateInactivityWarning(secondsRemaining) {
    const warning = document.getElementById('inactivityWarning');
    if (warning && loggedInUser) {
        warning.textContent = `⚠️ Session will expire in ${secondsRemaining} seconds due to inactivity`;
    }
}

function resetInactivityTimer() {
    if (inactivityTimer) {
        clearTimeout(inactivityTimer);
    }
    if (loggedInUser) {
        lastActivityTime = Date.now();
        startInactivityTimer();
    }
}

// Activity listeners for profile page
document.addEventListener('mousemove', resetInactivityTimer);
document.addEventListener('keypress', resetInactivityTimer);
document.addEventListener('click', resetInactivityTimer);

function logoutProfile() {
    if (inactivityTimer) {
        clearTimeout(inactivityTimer);
    }
    loggedInUser = null;
    stopVideoStreams();
    
    document.getElementById('profileNotLoggedIn').style.display = 'block';
    document.getElementById('profileLoggedIn').style.display = 'none';
    document.getElementById('loginSrCode').value = '';
    document.getElementById('loginError').classList.remove('show');
    
    alert('Session expired. You have been logged out.');
}

// Teacher View
function loadStudentsBySection() {
    const section = document.getElementById('teacherSectionSelect').value;
    const grid = document.getElementById('studentsGrid');
    
    if (!section) {
        grid.innerHTML = '';
        return;
    }
    
    const studentsInSection = mockStudents.filter(s => s.section === section);
    
    grid.innerHTML = studentsInSection.map(student => `
        <div class="student-card" onclick="showStudentAttendance('${student.srCode}', '${student.name}')">
            <div class="student-card-avatar">👤</div>
            <div class="student-card-name">${student.name}</div>
            <div class="student-card-code">${student.srCode}</div>
        </div>
    `).join('');
}

function showStudentAttendance(srCode, name) {
    const student = mockStudents.find(s => s.srCode === srCode);
    
    if (student) {
        const html = `
            <p><strong>Student:</strong> ${name}</p>
            <p><strong>SR Code:</strong> ${srCode}</p>
            <p><strong>Department:</strong> ${student.department}</p>
            <p><strong>Section:</strong> ${student.section}</p>
            <hr>
            <h4>Today's Attendance</h4>
            <div class="attendance-item ${student.attendance === 'LATE' ? 'late' : 'present'}">
                <strong>Status:</strong> ${student.attendance}<br>
                <strong>Subjects:</strong> ${student.subjects.join(', ')}<br>
                <strong>Time:</strong> ${new Date().toLocaleTimeString()}
            </div>
        `;
        document.getElementById('modalAttendanceList').innerHTML = html;
        document.getElementById('attendanceModal').classList.add('show');
    }
}

function closeModal() {
    document.getElementById('attendanceModal').classList.remove('show');
}

// Utility Functions
function showError(element, message) {
    element.textContent = message;
    element.classList.add('show');
}

function stopVideoStreams() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    if (loginVideoStream) {
        loginVideoStream.getTracks().forEach(track => track.stop());
        loginVideoStream = null;
    }
}

// Local Storage
function saveRegisteredStudents() {
    localStorage.setItem('registeredStudents', JSON.stringify(registeredStudents));
}

function loadRegisteredStudents() {
    const saved = localStorage.getItem('registeredStudents');
    if (saved) {
        registeredStudents = JSON.parse(saved);
    }
}

// Close modal on outside click
window.addEventListener('click', (event) => {
    const modal = document.getElementById('attendanceModal');
    if (event.target === modal) {
        closeModal();
    }
});
