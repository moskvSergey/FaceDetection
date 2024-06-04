from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    people = db.relationship('Person', backref='group', lazy=True)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    lessons = db.relationship('Lesson', backref='teacher', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    attended = db.Column(db.Boolean, nullable=False)
    person = db.relationship('Person', backref='attendances')

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now)
    attendances = db.relationship('Attendance', backref='lesson', lazy=True)


@app.route('/add_group', methods=['POST'])
def add_group():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    new_group = Group(name=name)
    db.session.add(new_group)
    db.session.commit()

    return jsonify({'message': 'Group added successfully'}), 201


@app.route('/add_person', methods=['POST'])
def add_person():
    data = request.get_json()
    name = data.get('name')
    group_id = data.get('group_id')

    if not name or not group_id:
        return jsonify({'error': 'Name and group_id are required'}), 400

    new_person = Person(name=name, group_id=group_id)
    db.session.add(new_person)
    db.session.commit()

    return jsonify({'message': 'Person added successfully'}), 201


@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    new_teacher = Teacher(name=name)
    db.session.add(new_teacher)
    db.session.commit()

    return jsonify({'message': 'Teacher added successfully'}), 201


@app.route('/add_lesson', methods=['POST'])
def add_lesson():
    data = request.get_json()
    group_id = data.get('group_id')
    teacher_id = data.get('teacher_id')

    if not group_id or not teacher_id:
        return jsonify({'error': 'Group ID and Teacher ID are required'}), 400

    new_lesson = Lesson(group_id=group_id, teacher_id=teacher_id)
    db.session.add(new_lesson)
    db.session.commit()

    # Automatically create attendance records for each person in the group
    group = Group.query.get(group_id)
    for person in group.people:
        new_attendance = Attendance(lesson_id=new_lesson.id, person_id=person.id, attended=False)
        db.session.add(new_attendance)

    db.session.commit()

    return jsonify({'message': 'Lesson and attendance records added successfully'}), 201


@app.route('/update_attendance', methods=['POST'])
def update_attendance():
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    person_id = data.get('person_id')
    attended = data.get('attended')

    if lesson_id is None or person_id is None or attended is None:
        return jsonify({'error': 'Lesson ID, Person ID, and attendance status are required'}), 400

    attendance_record = Attendance.query.filter_by(lesson_id=lesson_id, person_id=person_id).first()
    if attendance_record:
        attendance_record.attended = attended
        db.session.commit()
        return jsonify({'message': 'Attendance updated successfully'}), 200
    else:
        return jsonify({'error': 'Attendance record not found'}), 404


@app.route('/get_people', methods=['GET'])
def get_people():
    people = Person.query.all()
    people_list = [{'id': person.id, 'name': person.name, 'group_id': person.group_id} for person in people]
    return jsonify(people_list), 200


@app.route('/get_teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.all()
    teachers_list = [{'id': teacher.id, 'name': teacher.name} for teacher in teachers]
    return jsonify(teachers_list), 200


@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    attendance_records = Attendance.query.all()
    attendance_list = [
        {'id': record.id, 'lesson_id': record.lesson_id, 'person_id': record.person_id, 'attended': record.attended} for
        record in attendance_records]
    return jsonify(attendance_list), 200