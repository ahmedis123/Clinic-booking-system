from flask import Flask, render_template, request, jsonify
import csv
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# مسار ملف CSV
CSV_FILE = 'appointments.csv'

# إنشاء ملف CSV إذا لم يكن موجودًا
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'الاسم', 'رقم الهاتف', 'النوع', 'العمر', 'التاريخ', 'الوقت', 'الحالة'])

# بيانات تسجيل دخول الإدارة
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# تحقق من صحة رقم الهاتف
def validate_phone(phone):
    return phone.isdigit() and len(phone) == 10

# تحقق من صحة العمر
def validate_age(age):
    return age.isdigit() and 0 < int(age) < 120

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

# API لحجز موعد
@app.route('/api/book', methods=['POST'])
def book_appointment():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    gender = data.get('gender')
    age = data.get('age')
    date = data.get('date')
    time = data.get('time')

    if not all([name, phone, gender, age, date, time]):
        return jsonify({'error': 'جميع الحقول مطلوبة!'}), 400

    if not validate_phone(phone):
        return jsonify({'error': 'رقم الهاتف غير صحيح!'}), 400

    if not validate_age(age):
        return jsonify({'error': 'العمر غير صحيح!'}), 400

    appointment_id = str(uuid.uuid4())

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([appointment_id, name, phone, gender, age, date, time, 'معلق'])

    return jsonify({'message': 'تم حجز الموعد بنجاح!', 'id': appointment_id}), 201

# API لاسترجاع جميع المواعيد
@app.route('/api/admin/appointments', methods=['GET'])
def get_all_appointments():
    appointments = []

    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            appointments.append({
                'id': row[0],
                'name': row[1],
                'phone': row[2],
                'gender': row[3],
                'age': row[4],
                'date': row[5],
                'time': row[6],
                'status': row[7]
            })

    return jsonify(appointments), 200

# API لتأكيد أو إلغاء الموعد
@app.route('/api/admin/appointments/<appointment_id>', methods=['PUT'])
def update_appointment_status(appointment_id):
    data = request.json
    new_status = data.get('status')  # 'مؤكد' أو 'ملغى'

    appointments = []

    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            if row[0] == appointment_id:
                row[7] = new_status
            appointments.append(row)

    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(appointments)

    return jsonify({'message': 'تم تحديث حالة الموعد بنجاح!'}), 200

# API لحساب زمن المقابلة
@app.route('/api/waiting-time', methods=['GET'])
def get_waiting_time():
    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        appointments = list(reader)

    num_appointments = len(appointments)
    waiting_time_minutes = num_appointments * 15

    return jsonify({'waiting_time_minutes': waiting_time_minutes}), 200

# تقديم ملفات HTML
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patient')
def patient():
    return render_template('patient/index.html')

@app.route('/admin')
def admin():
    return render_template('admin/admin.html')

# تشغيل الخادم
if __name__ == '__main__':
    app.run(debug=True, port=0000)
