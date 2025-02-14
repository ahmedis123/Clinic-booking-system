from flask import Flask, render_template, request, jsonify
import os
import uuid
from flask_cors import CORS
import requests

app = Flask(__name__, template_folder='../frontend')  # قم بتعيين template_folder إلى المجلد الرئيسي (frontend)
CORS(app)

# مفتاح API لـ jsonbin.io
JSONBIN_API_KEY = '$2a$10$JElruOnxtw0rMry11o3DR.afE/vN5q1TNW.0o36grKXpZJdhbNrzu'
JSONBIN_BIN_ID = '67af5bcfad19ca34f803a957'  # معرف الـ Bin الخاص بك

# عنوان URL لـ jsonbin.io
JSONBIN_URL = f'https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}'

# بيانات تسجيل دخول الإدارة
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# تحقق من صحة الهاشتاق
def validate_hashtag(hashtag):
    return len(hashtag) > 0

# تحقق من صحة الوشاح
def validate_scarf(scarf):
    return len(scarf) > 0

# دالة لقراءة البيانات من jsonbin.io
def get_students():
    headers = {
        'X-Master-Key': JSONBIN_API_KEY
    }
    response = requests.get(JSONBIN_URL, headers=headers)
    if response.status_code == 200:
        return response.json().get('record', [])
    return []

# دالة لكتابة البيانات إلى jsonbin.io
def save_students(students):
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': JSONBIN_API_KEY
    }
    response = requests.put(JSONBIN_URL, json=students, headers=headers)
    return response.status_code == 200

# API لتسجيل دخول الإدارة
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
        return jsonify({'message': 'تم تسجيل الدخول بنجاح!'}), 200
    else:
        return jsonify({'error': 'اسم المستخدم أو كلمة المرور غير صحيحة!'}), 401

# API لتسجيل الطالب
@app.route('/api/register', methods=['POST'])
def register_student():
    data = request.json
    name = data.get('name')
    scarf = data.get('scarf')
    hashtag = data.get('hashtag')
    size = data.get('size')
    gender = data.get('gender')

    if not all([name, scarf, hashtag, size, gender]):
        return jsonify({'error': 'جميع الحقول مطلوبة!'}), 400

    if not validate_scarf(scarf):
        return jsonify({'error': 'الوشاح غير صحيح!'}), 400

    if not validate_hashtag(hashtag):
        return jsonify({'error': 'الهاشتاق غير صحيح!'}), 400

    student_id = str(uuid.uuid4())

    students = get_students()
    students.append({
        'id': student_id,
        'name': name,
        'scarf': scarf,
        'hashtag': hashtag,
        'size': size,
        'gender': gender,
        'status': 'تم التسجيل'
    })

    if save_students(students):
        return jsonify({'message': 'تم تسجيل الطالب بنجاح!', 'id': student_id}), 201
    else:
        return jsonify({'error': 'حدث خطأ أثناء حفظ البيانات!'}), 500

# API لاسترجاع جميع الطلاب
@app.route('/api/admin/students', methods=['GET'])
def get_all_students():
    students = get_students()
    return jsonify(students), 200

# API لتحديث حالة الطالب
@app.route('/api/admin/students/<student_id>', methods=['PUT'])
def update_student_status(student_id):
    data = request.json
    new_status = data.get('status')  # 'تم التسجيل' أو 'غير مؤكد'

    students = get_students()
    for student in students:
        if student['id'] == student_id:
            student['status'] = new_status
            break

    if save_students(students):
        return jsonify({'message': 'تم تحديث حالة الطالب بنجاح!'}), 200
    else:
        return jsonify({'error': 'حدث خطأ أثناء حفظ البيانات!'}), 500

# API لحساب عدد الطلاب المسجلين
@app.route('/api/students-count', methods=['GET'])
def get_students_count():
    students = get_students()
    num_students = len(students)
    return jsonify({'students_count': num_students}), 200

# واجهة الطالب
@app.route('/')
def index():
    return render_template('patient/index.html')  # ملف index.html في frontend/student/

@app.route('/student')
def student():
    return render_template('patient/index.html')  # ملف index.html في frontend/student/

# واجهة الإدارة
@app.route('/admin')
def admin():
    return render_template('admin/admin.html')  # ملف admin.html في frontend/admin/

# تشغيل الخادم
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))  # استخدام PORT من متغير البيئة أو 3000 كافتراضي
    app.run(debug=True, host='0.0.0.0', port=port)
