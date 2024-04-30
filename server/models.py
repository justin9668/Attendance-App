from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Instructor(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    courses = db.relationship('Course', backref='instructor', lazy=True)

class Student(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    courses = db.relationship('Course', secondary='student_courses', backref=db.backref('students', lazy=True))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(4), unique=True)
    instructor_id = db.Column(db.String(36), db.ForeignKey('instructor.id'))
    sessions = db.relationship('Session', backref='course', lazy=True, cascade="all,delete")

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    is_active = db.Column(db.Boolean, default=False)
    attendances = db.relationship('Attendance', backref='session', lazy=True, cascade="all,delete")
    instructor_latitude = db.Column(db.Float)
    instructor_longitude = db.Column(db.Float)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    student_id = db.Column(db.String(36), db.ForeignKey('student.id'))
    attended = db.Column(db.Boolean, default=False)

student_courses = db.Table('student_courses',
    db.Column('student_id', db.String(36), db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)