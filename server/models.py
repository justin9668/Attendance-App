from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Instructor(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    classrooms = db.relationship('Classroom', backref='instructor', lazy=True)

class Student(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    classrooms = db.relationship('Classroom', secondary='student_classrooms', backref=db.backref('students', lazy=True))

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True)
    name = db.Column(db.String(100))
    instructor_id = db.Column(db.String(36), db.ForeignKey('instructor.id'))
    sessions = db.relationship('Session', backref='classroom', lazy=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))
    attendances = db.relationship('Attendance', backref='session', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    student_id = db.Column(db.String(36), db.ForeignKey('student.id'))
    attended = db.Column(db.Boolean, default=False)

student_classrooms = db.Table('student_classrooms',
    db.Column('student_id', db.String(36), db.ForeignKey('student.id'), primary_key=True),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classroom.id'), primary_key=True)
)