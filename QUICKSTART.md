# Quick Start Guide

## Prerequisites
- Python 3.13 installed
- Windows PowerShell

## Step 1: Open PowerShell
Navigate to your project directory and open PowerShell.

## Step 2: Install Dependencies (First Time Only)
Run this command to install all required packages:

```powershell
C:/Users/Sharlaine/AppData/Local/Programs/Python/Python313/python.exe -m pip install -r requirements.txt
```

**Expected output:** Successfully installed packages like Flask, opencv-python, face-recognition, etc.

## Step 3: Run the Application
Execute this command to start the Flask server:

```powershell
C:/Users/Sharlaine/AppData/Local/Programs/Python/Python313/python.exe app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

## Step 4: Access the Application
Open your web browser and go to:
```
http://localhost:5000
```

You should see the **Attendance System Welcome Page** with:
- Current time (updates every second)
- "I'm a Student" button
- "I'm a Teacher" button

## Step 5: Test the System

### As a Student:
1. Click **"I'm a Student"**
2. Click **"Register (SR Code)"**
3. Enter SR Code in format: `XX-XXXXX` (e.g., `21-12345`)
4. Enter name, department, section
5. Click **Register**
6. Click **"Scan Face"** or **"Profile Dashboard"**

### As a Teacher:
1. Click **"I'm a Teacher"**
2. You'll see the teacher view
3. Click on a student profile to see attendance records

## Step 6: Stop the Server
Press `Ctrl + C` in PowerShell to stop the application.

---

## Troubleshooting

### Issue: "Command not found"
- Make sure you're using the full Python path
- Check Python is installed: `C:/Users/Sharlaine/AppData/Local/Programs/Python/Python313/python.exe --version`

### Issue: "Port 5000 already in use"
Option 1 - Kill the process:
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

Option 2 - Change port in `app.py` last line:
```python
app.run(debug=True, port=5001)  # Use 5001 instead
```

### Issue: "ModuleNotFoundError"
Reinstall dependencies:
```powershell
C:/Users/Sharlaine/AppData/Local/Programs/Python/Python313/python.exe -m pip install --upgrade -r requirements.txt
```

### Issue: "Camera not working"
- Grant camera permissions to your browser
- Check: Settings → Privacy → Camera

---

## File Structure
- `app.py` - Main application
- `database.py` - Database models
- `face_recognition.py` - Face recognition engine
- `requirements.txt` - Dependencies
- `static/` - CSS, JS, images
- `templates/` - HTML pages
- `encodings/` - Face data (auto-created)
- `attendance_system.db` - Database (auto-created)

---

## Useful Commands

**Install specific package:**
```powershell
python -m pip install flask
```

**List installed packages:**
```powershell
python -m pip list
```

**Delete database (reset data):**
```powershell
Remove-Item attendance_system.db
```

**Test setup:**
```powershell
C:/Users/Sharlaine/AppData/Local/Programs/Python/Python313/python.exe test_setup.py
```

---

## Features Available

✓ Student registration with SR code validation
✓ Face recognition for attendance
✓ Teacher attendance tracking
✓ Student profile dashboard
✓ 3-minute auto sign-out on inactivity
✓ Receipt notifications
✓ Late/Present/Absent status tracking

---

**That's it! Your attendance system is now running! 🎉**
