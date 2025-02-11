from flask import Flask, render_template, request, jsonify
import csv
import os
import uuid
from flask_cors import CORS

app = Flask(__name__, template_folder='../frontend')  # قم بتعيين template_folder إلى المجلد الرئيسي (frontend)
CORS(app)

# مسار ملف CSV
CSV_FILE = 'students.csv'

# إنشاء ملف CSV إذا لم يكن موجودًا
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'الاسم', 'الوشاح', 'الهاشتاق', 'المقاس', 'النوع', 'الحالة'])

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

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([student_id, name, scarf, hashtag, size, gender, 'تم التسجيل'])

    return jsonify({'message': 'تم تسجيل الطالب بنجاح!', 'id': student_id}), 201

# API لاسترجاع جميع الطلاب
@app.route('/api/admin/students', methods=['GET'])
def get_all_students():
    students = []

    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # تخطي الصف الأول (العناوين)
        for row in reader:
            students.append({
                'id': row[0],
                'name': row[1],
                'scarf': row[2],
                'hashtag': row[3],
                'size': row[4],
                'gender': row[5],
                'status': row[6]
            })

    return jsonify(students), 200

# API لتحديث حالة الطالب
@app.route('/api/admin/students/<student_id>', methods=['PUT'])
def update_student_status(student_id):
    data = request.json
    new_status = data.get('status')  # 'تم التسجيل' أو 'غير مؤكد'

    students = []

    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # قراءة العناوين
        for row in reader:
            if row[0] == student_id:  # تحديث حالة الطالب
                row[6] = new_status
            students.append(row)

    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # كتابة العناوين
        writer.writerows(students)  # كتابة البيانات المحدثة

    return jsonify({'message': 'تم تحديث حالة الطالب بنجاح!'}), 200

# API لحساب عدد الطلاب المسجلين
@app.route('/api/students-count', methods=['GET'])
def get_students_count():
    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # تخطي الصف الأول (العناوين)
        students = list(reader)

    num_students = len(students)

    return jsonify({'students_count': num_students}), 200

# واجهة الطالب
@app.route('/')
def index():
    return render_template('student/index.html')  # ملف index.html في frontend/student/

@app.route('/student')
def student():
    return render_template('student/index.html')  # ملف index.html في frontend/student/

# واجهة الإدارة
@app.route('/admin')
def admin():
    return render_template('admin/admin.html')  # ملف admin.html في frontend/admin/

# تشغيل الخادم
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))  # استخدام PORT من متغير البيئة أو 3000 كافتراضي
    app.run(debug=True, host='0.0.0.0', port=port)
