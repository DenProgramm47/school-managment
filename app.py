from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import traceback

app = Flask(__name__)
CORS(app)

# Параметры подключения к PostgreSQL
DB_CONFIG = {
    'database': 'school_db',
    'user': 'postgres',
    'password': '2580', 
    'host': 'localhost',
    'port': '5432',
    'client_encoding': 'UTF8'
}

def get_db_connection():
    """Получение подключения к базе данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None

def safe_string(value):
    """Безопасное преобразование в строку"""
    if value is None:
        return None
    
    try:
        if isinstance(value, bytes):
            for encoding in ['utf-8', 'cp1251', 'koi8-r', 'latin1']:
                try:
                    return value.decode(encoding, errors='replace')
                except:
                    continue
            return value.decode('utf-8', errors='ignore')
        elif isinstance(value, str):
            return value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        else:
            return str(value)
    except Exception as e:
        print(f"⚠️  Ошибка обработки строки: {e}")
        return str(value) if value else None

def serialize_value(value):
    """Сериализация значений для JSON"""
    if value is None:
        return None
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, (int, float, bool)):
        return value
    else:
        return safe_string(value)

@app.route('/api/students', methods=['GET'])
def get_students():
    """Получение списка всех учеников с фильтрацией"""
    conn = None
    cursor = None
    
    try:
        # Получаем параметры фильтрации
        fio_filter = request.args.get('fio', '').strip()
        course_filter = request.args.get('course', '').strip()
        site_filter = request.args.get('site', '').strip()
        liter_filter = request.args.get('liter', '').strip()
        
        print(f"🔍 Запрос данных...")
        print(f"  Фильтры: fio={fio_filter}, course={course_filter}, site={site_filter}, liter={liter_filter}")
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Не удалось подключиться к базе данных'
            }), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Формируем запрос
        query = "SELECT * FROM students WHERE 1=1"
        params = []
        
        if fio_filter:
            query += " AND fio ILIKE %s"
            params.append(f"%{fio_filter}%")
            print(f"  ✅ Фильтр по ФИО: %{fio_filter}%")
        
        if course_filter:
            query += " AND course = %s"
            params.append(course_filter)
            print(f"  ✅ Фильтр по классу: {course_filter}")
        
        if site_filter:
            query += " AND site ILIKE %s"
            params.append(f"%{site_filter}%")
            print(f"  ✅ Фильтр по корпусу: %{site_filter}%")
        
        if liter_filter:
            query += " AND liter = %s"
            params.append(liter_filter)
            print(f"  ✅ Фильтр по литере: {liter_filter}")
        
        # Сортировка по порядку импорта (id - автоинкремент)
        query += " ORDER BY id"
        
        print(f"📊 Выполняю запрос...")
        cursor.execute(query, params)
        students = cursor.fetchall()
        
        print(f"✅ Получено записей: {len(students)}")
        
        # Обрабатываем каждую запись
        students_list = []
        for idx, student in enumerate(students):
            try:
                student_dict = {}
                for key, value in student.items():
                    student_dict[key] = serialize_value(value)
                students_list.append(student_dict)
            except Exception as row_error:
                print(f"⚠️  Ошибка обработки строки {idx}: {row_error}")
                continue
        
        print(f"✅ Обработано записей: {len(students_list)}")
        
        return jsonify({
            'success': True,
            'count': len(students_list),
            'data': students_list
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Критическая ошибка: {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({'status': 'ok', 'message': 'Database connected'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/', methods=['GET'])
def index():
    """Главная страница"""
    return jsonify({
        'message': 'School Management API',
        'endpoints': {
            'students': '/api/students',
            'health': '/api/health'
        }
    }), 200

if __name__ == '__main__':
    print("🚀 Запуск сервера...")
    print("📍 URL: http://localhost:5000")
    print("📍 API: http://localhost:5000/api/students")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)