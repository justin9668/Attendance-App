import hashlib
import os
import random
from datetime import datetime, timedelta
from io import BytesIO

import requests
from flask import Flask, abort, request, jsonify, send_file, redirect, url_for, session
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

from models import db, Instructor, Student, Classroom, Session, Attendance

load_dotenv()

# App configuration
app = Flask(__name__)
CORS(app, origins='*', supports_credentials=True)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)

with app.app_context():
    db.drop_all() # temp
    db.create_all()

# Update session cookie configurations
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

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

@app.route('/')
def home():
    return "Here"

@app.route('/auth/login', methods=['GET'])
def login():
    role = request.args.get('role')
    session['user_role'] = role

    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    session['state'] = state    
    print(f"State set in session: {session.get('state')}") # debugging

    redirect_uri = url_for('authorize', _external=True)
    if 'state' not in session: # debugging
        raise Exception("State not set in session.") # debugging
    return google.authorize_redirect(redirect_uri, state=state)

@app.route('/authorize', methods=['GET'])
def authorize():
    # debugging
    print(f"State in session: {session.get('state')}")
    print(f"State in request: {request.args.get('state')}")
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
    return jsonify(message="Successfully logged out"), 200

@app.route('/auth/check_auth', methods=['GET'])
def check_auth():
    if 'user' in session:
        user_role = session['user']['role']
        return jsonify({'isAuthenticated': True, 'role': user_role}), 200
    else:
        return jsonify({'isAuthenticated': False, 'role': None}), 401

# this route fetches from the session cookie
# expand this route to include other user information
@app.route('/api/user_info', methods=['GET'])
def user_info():
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

    # fetch classes based on the user's role
    if role == 'instructor':
        instructor = Instructor.query.get(user_id)
        if instructor:
            classes = [{'id': classroom.id, 'name': classroom.name} for classroom in instructor.classrooms]
            response_data['classes'] = classes if classes else []
        else:
            return jsonify(message='Instructor not found'), 404
    elif role == 'student':
        student = Student.query.get(user_id)
        if student:
            classes = [{'id': classroom.id, 'name': classroom.name} for classroom in student.classrooms]
            response_data['classes'] = classes if classes else []
        else:
            return jsonify(message='Student not found'), 404

    return jsonify(response_data)

# for testing purposes
@app.route('/api/instructors', methods=['GET'])
def get_instructors():
    instructors = Instructor.query.all()
    instructor_names = [instructor.name for instructor in instructors]
    return jsonify(instructor_names)

# for testing purposes
@app.route('/api/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    student_names = [student.name for student in students]
    return jsonify(student_names)

# for testing purposes
@app.route('/api/classrooms', methods=['GET'])
def get_classrooms():
    classrooms = Classroom.query.all()

    if classrooms:
        classroom_data = [{'id': classroom.id, 'name': classroom.name, 'instructor_id': classroom.instructor_id} for classroom in classrooms]
        return jsonify(classroom_data), 200
    else:
        return jsonify(message='No classrooms found'), 404

# for testing purposes
# merged to /api/user_info
@app.route('/api/instructor_classes', methods=['GET'])
def instructor_classes():
    instructor_id = session['user']['id']
    instructor = Instructor.query.get(instructor_id)
    classes = [{'id': classroom.id, 'name': classroom.name} for classroom in instructor.classrooms]

    if not classes:
        return jsonify(message='No classes found.'), 404
    
    return jsonify(classes=classes)

# for testing purposes
# merged to /api/user_info
@app.route('/api/student_classes', methods=['GET'])
def student_classes():
    student_id = session['user']['id']
    student = Student.query.get(student_id)
    classes = [{'id': classroom.id, 'name': classroom.name} for classroom in student.classrooms]

    if not classes:
        return jsonify(message='No classes found.'), 404
    
    return jsonify(classes=classes)

# instructor endpoint
@app.route('/api/create_classroom', methods=['POST'])
def create_classroom():
    instructor_id = session['user']['id']
    classroom_name = request.json.get('classroom_name')
    classroom_code = str(random.randint(1000, 9999))

    if not classroom_name:
        return jsonify(message="Classroom name is required."), 400
    
    new_classroom = Classroom(code=classroom_code, name=classroom_name, instructor_id=instructor_id)
    db.session.add(new_classroom)
    db.session.commit()

    return jsonify(id=new_classroom.id, code=new_classroom.code, name=new_classroom.name)

# instructor endpoint
# implement frontend
@app.route('/api/delete_classroom', methods=['POST'])
def delete_classroom():
    instructor_id = session['user']['id']
    classroom_id = request.json.get('classroom_id')
    classroom = Classroom.query.filter_by(id=classroom_id, instructor_id=instructor_id).first()
    
    if not classroom:
        return jsonify(message='Classroom not found'), 404
    
    db.session.delete(classroom)
    db.session.commit()
    
    return jsonify(message='Classroom deleted successfully'), 200

# student endpoint
# implement frontend
@app.route('/api/join_classroom', methods=['POST'])
def join_classroom():
    student_id = session['user']['id']
    classroom_code = request.json.get('classroom_code')

    classroom = Classroom.query.filter_by(code=classroom_code).first()
    student = Student.query.get(student_id)
    
    if not classroom:
        return jsonify(message='Classroom not found'), 404
    
    if student in classroom.students:
        return jsonify(message='Student already joined'), 409
    
    classroom.students.append(student)
    db.session.commit()

    return jsonify(message='Joined successfully'), 200

# student endpoint
# implement frontend
@app.route('/api/leave_classroom', methods=['POST'])
def leave_classroom():
    student_id = session['user']['id']
    classroom_id = request.json.get('classroom_id') # prolly wont work

    classroom = Classroom.query.filter_by(id=classroom_id).first()
    student = Student.query.get(student_id)

    classroom.students.remove(student)
    db.session.commit()

    return jsonify(message='Successfully left the classroom'), 200

# instructor endpoint
# implement frontend
@app.route('/api/create_session', methods=['POST'])
def create_session():
    classroom_id = request.json.get('classroom_id') # prolly wont work
    start_time = datetime.now()
    duration = request.json.get('duration', 1)  # default duration is 1 hour for simplicity
    end_time = start_time + timedelta(hours=duration)

    session_code = random.randint(1000, 9999)
    new_session = Session(code=session_code, start_time=start_time, end_time=end_time, classroom_id=classroom_id)
        
    db.session.add(new_session)
    db.session.commit()
        
    return jsonify(id=new_session.id, code=new_session.code, start_time=str(start_time), end_time=str(end_time))

# instructor endpoint
# implement frontend
@app.route('/api/qrcode/<session_code>', methods=["GET"])
def qrcode(session_code):
    size = '200x200'
    api_url = f'https://api.qrserver.com/v1/create-qr-code/?data={session_code}&size={size}'
    response = requests.get(api_url)

    if response.status_code == 200:
        img = BytesIO(response.content)
        img.seek(0)
        return send_file(img, mimetype='image/png', as_attachment=False, download_name=f'qr_{session_code}.png'), 200

    return jsonify(message='Failed to generate QR code, try again'), 500

# student endpoint
# implement frontend
@app.route('/api/verify_attendence', methods=['POST'])
def verify_attendence():
    student_id = session['user']['id']
    session_code = request.json.get('session_code')

    session = Session.query.filter_by(code=session_code).first()
    student = Student.query.get(student_id)

    if session:
        attendance = Attendance(session_id=session.id, student_id=student.id, attended=True)
        db.session.add(attendance)
        db.session.commit()
        return jsonify(message='Your attendence was recorded'), 200
    
    return jsonify(message='Incorrect code, try again'), 404

if __name__ == '__main__': 
    app.run(debug=True, host='localhost', port=3000)