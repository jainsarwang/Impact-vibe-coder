from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# In-memory data storage (for simplicity)
students = []
courses = []
enrollments = []

# Student API endpoints
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    student = {'id': len(students) + 1, 'name': data['name'], 'email': data['email']}
    students.append(student)
    return jsonify(student), 201

@app.route('/students', methods=['GET'])
def list_students():
    return jsonify(students)

# Course API endpoints
@app.route('/courses', methods=['POST'])
def add_course():
    data = request.get_json()
    course = {'id': len(courses) + 1, 'name': data['name'], 'description': data['description']}
    courses.append(course)
    return jsonify(course), 201

@app.route('/courses', methods=['GET'])
def list_courses():
    return jsonify(courses)

# Enrollment API endpoints
@app.route('/enrollments', methods=['POST'])
def enroll_student():
    data = request.get_json()
    enrollment = {'student_id': data['student_id'], 'course_id': data['course_id']}
    enrollments.append(enrollment)
    return jsonify(enrollment), 201

@app.route('/enrollments', methods=['GET'])
def list_enrollments():
    return jsonify(enrollments)

if __name__ == '__main__':
    app.run(debug=True)
