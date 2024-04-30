import hashlib
import os
import random
from datetime import datetime, timedelta
from io import BytesIO
from math import radians, cos, sin, asin, sqrt

import requests
from flask import Flask, abort, request, jsonify, send_file, redirect, url_for, session
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

from models import db, Instructor, Student, Course, Session, Attendance

load_dotenv()

# App configuration
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL'),
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY'),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
CORS(app, origins='*', supports_credentials=True)

db.init_app(app)
with app.app_context():
    db.drop_all() # clear database (temporary for testing)
    db.create_all()

# OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration',
)

def create_or_update_user(user_info, role):
    user_id = user_info.get('id')
    name = user_info.get('name')

    if role == 'instructor':
        user = Instructor.query.get(user_id)
        if not user:
            user = Instructor(id=user_id, name=name)
            db.session.add(user)
        else:
            user.name = name  # update name if necessary
    elif role == 'student':
        user = Student.query.get(user_id)
        if not user:
            user = Student(id=user_id, name=name)
            db.session.add(user)
        else:
            user.name = name  # update name if necessary
    db.session.commit()

    return user

def get_location():
    GOOGLE_GEOLOCATION_URL = "https://www.googleapis.com/geolocation/v1/geolocate"
    response = requests.post(
        f"{GOOGLE_GEOLOCATION_URL}?key={app.config['GOOGLE_API_KEY']}",
        json={"considerIp": "true"}
    )
    if response.status_code == 200:
        data = response.json().get('location', {})
        return {'lat': data.get('lat'), 'lng': data.get('lng')}
    else:
        print(f"Error fetching geolocation: {response.text}")
        return None
    
def compare_location(lat1, lon1, lat2, lon2, max_distance=100):  # max_distance in meters
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula to calculate the distance between two points on the Earth
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Radius of Earth in meters
    distance = c * r

    return distance <= max_distance

@app.route('/')
def home():
    return "Here"

# testing: get all instructors in the database
@app.route('/api/instructors', methods=['GET'])
def get_instructors():
    instructors = Instructor.query.all()
    instructor_names = [instructor.name for instructor in instructors]
    return jsonify(instructor_names)

# testing: get all students in the database
@app.route('/api/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    student_names = [student.name for student in students]
    return jsonify(student_names)

# testing: get all courses in the database
@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    if courses:
        courses_data = [{'id': course.id, 'name': course.name, 'code': course.code, 'instructor_id': course.instructor_id} for course in courses]
        return jsonify(courses_data), 200
    return jsonify(message='No courses found'), 404

# testing: get all sessions in the database
@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = Session.query.all()
    if sessions:
        sessions_data = [{'id': session.id, 'code': session.code, 'start_time': session.start_time, 'end_time': session.end_time, 'course_id': session.course_id, 'is_active': session.is_active} for session in sessions]
        return jsonify(sessions_data), 200
    return jsonify(message='No sessions found'), 404

# testing: get all attendance records in the database
@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    attendances = Attendance.query.all()
    if attendances:
        attendance_data = [{'id': attendance.id, 'session_id': attendance.session_id, 'student_id': attendance.student_id, 'attended': attendance.attended} for attendance in attendances]
        return jsonify(attendance_data), 200
    return jsonify(message='No attendance records found'), 404

@app.route('/auth/login', methods=['GET'])
def login():
    role = request.args.get('role')
    session['user_role'] = role

    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    session['state'] = state    

    redirect_uri = url_for('authorize', _external=True)

    return google.authorize_redirect(redirect_uri, state=state)

@app.route('/authorize', methods=['GET'])
def authorize():
    if 'state' not in session or 'state' not in request.args:
        abort(400, description="Missing state parameter.")
    if session['state'] != request.args['state']:
        abort(400, description="Invalid state parameter.")

    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()

    # retrieve the role from the session
    role = session.get('user_role', 'student')  # default to 'student' if not set

    # function to handle user creation or update
    user = create_or_update_user(user_info, role)
        
    # store user information in session
    session['user'] = {
        'id': user.id,
        'name': user.name,
        'role': role,
        'email': user_info.get('email')
    }

    return redirect('http://localhost:5173' + '/dashboard')

@app.route('/auth/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify(message="Logged out"), 200

@app.route('/auth/check_auth', methods=['GET'])
def check_auth():
    if 'user' in session:
        return jsonify({'isAuthenticated': True}), 200
    else:
        return jsonify({'isAuthenticated': False}), 401

@app.route('/api/user_info', methods=['GET'])
def get_user_info():
    if 'user' not in session:
        return jsonify(message='User not authenticated'), 401
    
    user_id = session['user']['id']
    role = session['user']['role']
    name = session['user']['name']

    response_data = {
        'id': user_id,
        'name': name,
        'role': role
    }

    if role == 'instructor':
        instructor = Instructor.query.get(user_id)
        courses = [{'id': course.id, 'name': course.name} for course in instructor.courses]
        response_data['courses'] = courses if courses else []
    elif role == 'student':
        student = Student.query.get(user_id)
        courses = [{'id': course.id, 'name': course.name} for course in student.courses]
        response_data['courses'] = courses if courses else []

    return jsonify(response_data)

# instructor endpoint
@app.route('/api/create_course', methods=['POST'])
def create_course():
    instructor_id = session['user']['id']
    course_name = request.json.get('course_name')
    course_code = str(random.randint(1000, 9999))

    if not course_name:
        return jsonify(message="Course name required"), 400
    
    new_course = Course(code=course_code, name=course_name, instructor_id=instructor_id)
    db.session.add(new_course)
    db.session.commit()

    return jsonify(message='Course created', id=new_course.id, code=new_course.code, name=new_course.name), 200

@app.route('/api/course_details/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify(message="Course not found"), 404

    instructor = Instructor.query.get(course.instructor_id)
    instructor_details = {
        "id": instructor.id,
        "name": instructor.name
    }

    students = []
    for student in course.students:
        total_attendance, total_sessions, attendance_ratio = calculate_student_attendance(student.id, course.id)

        students.append({
            "id": student.id,
            "name": student.name,
            "attendance": {
                "attended_sessions": total_attendance,
                "total_sessions": total_sessions,
                "attendance_ratio": attendance_ratio
            }
        })

    course_details = {
        "id": course.id,
        "name": course.name,
        "code": course.code,
        "instructor": instructor_details,
        "students": students
    }

    return jsonify(course_details), 200

# instructor endpoint
@app.route('/api/remove_student', methods=['DELETE'])
def remove_student():
    student_id = request.json.get('student_id')
    course_id = request.json.get('course_id')

    student = Student.query.get(student_id)
    course = Course.query.filter_by(id=course_id).first()

    if not student or not course:
        return jsonify(message='Invalid student or course'), 400

    course.students.remove(student)
    db.session.commit()

    return jsonify(message='Student removed'), 200

# instructor endpoint
@app.route('/api/delete_course', methods=['DELETE'])
def delete_course():
    instructor_id = session['user']['id']
    course_id = request.json.get('course_id')
    course = Course.query.filter_by(id=course_id, instructor_id=instructor_id).first()
    
    if not course:
        return jsonify(message='Course not found'), 404
    
    db.session.delete(course)
    db.session.commit()
    
    return jsonify(message='Course deleted'), 200

# student endpoint
@app.route('/api/join_course', methods=['POST'])
def join_course():
    student_id = session['user']['id']
    course_code = request.json.get('course_code')

    course = Course.query.filter_by(code=course_code).first()
    student = Student.query.get(student_id)
    
    if not course:
        return jsonify(message='Course not found'), 404
    
    if student in course.students:
        return jsonify(message='Student already joined'), 409
    
    course.students.append(student)
    db.session.commit()

    return jsonify(message='Course joined'), 200

# student endpoint
@app.route('/api/leave_course', methods=['DELETE'])
def leave_course():
    student_id = session['user']['id']
    course_id = request.json.get('course_id')

    course = Course.query.filter_by(id=course_id).first()
    student = Student.query.get(student_id)

    course.students.remove(student)
    db.session.commit()

    return jsonify(message='Course removed'), 200

# instructor endpoint
@app.route('/api/session_status/<int:course_id>', methods=['GET'])
def session_status(course_id):
    session = Session.query.filter_by(course_id=course_id, is_active=True).first()
    if session:
        return jsonify(code=session.code, start_time=str(session.start_time), end_time=str(session.end_time), is_active=session.is_active), 200
    return jsonify(is_active=False), 200

# instructor endpoint
@app.route('/api/start_session', methods=['POST'])
def start_session():
    course_id = request.json.get('course_id')
    start_time = datetime.now()
    duration = request.json.get('duration', 1)  # default duration is 1 hour for simplicity
    end_time = start_time + timedelta(hours=duration)
    session_code = random.randint(1000, 9999)

    #geolocation implementation
    instructor_location = get_location() # implemented line 50ish

    new_session = Session(code=session_code, start_time=start_time, end_time=end_time, course_id=course_id, is_active=True, 
                          instructor_latitude=instructor_location['lat'], instructor_longitude=instructor_location['lng']) #notice change for geoloc
    db.session.add(new_session)
    db.session.commit()
        
    return jsonify(message='Session Started', code=new_session.code, start_time=str(start_time), end_time=str(end_time)), 200

# instructor endpoint
@app.route('/api/end_session', methods=['POST'])
def end_session():
    session_code = request.json.get('session_code')
    session = Session.query.filter_by(code=session_code).first()
    if session:
        session.is_active = False
        session.end_time = datetime.now()
        db.session.commit()
        return jsonify(message='Session Stopped'), 200
    return jsonify(message='Session not found'), 404

# instructor endpoint
@app.route('/api/qr_code/<session_code>', methods=["GET"])
def generate_qr_code(session_code):
    size = '200x200'
    api_url = f'https://api.qrserver.com/v1/create-qr-code/?data={session_code}&size={size}'
    response = requests.get(api_url)

    if response.status_code == 200:
        img = BytesIO(response.content)
        img.seek(0)
        return send_file(img, mimetype='image/png', as_attachment=False, download_name=f'qr_{session_code}.png'), 200

    return jsonify(message='Failed to generate QR code, try again'), 500

# student endpoint
@app.route('/api/submit_attendence', methods=['POST'])
def submit_attendence():
    student_id = request.json.get('user_id')
    course_id = request.json.get('course_id')
    session_code = request.json.get('session_code')
    
    student_location = get_location()
    #debugging
    print("Student Location: Latitude = {}, Longitude = {}".format(student_location['lat'], student_location['lng']))

    session = Session.query.filter_by(code=session_code, course_id=course_id).first()

    if session:
        #debugging instructor loc
        print("Instructor Location: Latitude = {}, Longitude = {}".format(session.instructor_latitude, session.instructor_longitude))
        
        if session.is_active == False:
            return jsonify(message='Attendance has closed'), 403
        
        if datetime.now() > session.end_time:
            return jsonify(message='Attendance has ended'), 403

        attendance_status = Attendance.query.filter_by(session_id=session.id, student_id=student_id).first()
        if attendance_status:
            return jsonify(message='Attendance already recorded'), 409
        
        if compare_location(session.instructor_latitude, session.instructor_longitude, student_location['lat'], student_location['lng']):
            attendance = Attendance(session_id=session.id, student_id=student_id, attended=True)
            db.session.add(attendance)
            db.session.commit()
            return jsonify(message='Attendance recorded'), 200
    
    return jsonify(message='Incorrect code or Wrong, try again'), 404

@app.route('/api/student_attendance', methods=['GET'])
def get_student_attendance():
    student_id = request.args.get('user_id')
    course_id = request.args.get('course_id')

    total_attendance, total_sessions, attendance_ratio = calculate_student_attendance(student_id, course_id)

    return jsonify( total_attendance=total_attendance, total_sessions=total_sessions, attendance_ratio=attendance_ratio), 200

def calculate_student_attendance(student_id, course_id):
    sessions = Session.query.filter_by(course_id=course_id).all()
    total_attendance = 0

    for session in sessions:
        attendance = Attendance.query.filter_by(session_id=session.id, student_id=student_id).first()
        if attendance and attendance.attended:
            total_attendance += 1
    
    attendance_ratio = total_attendance / len(sessions) if sessions else 0

    return total_attendance, len(sessions), attendance_ratio

if __name__ == '__main__': 
    app.run(debug=True, host='localhost', port=3000)