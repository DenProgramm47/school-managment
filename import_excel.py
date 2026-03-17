import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

# Параметры подключения к PostgreSQL
DB_CONFIG = {
    'database': 'school_db',
    'user': 'postgres',
    'password': '2580',
    'host': 'localhost',
    'port': '5432'
}

def create_database_connection():
    """Создание подключения к базе данных"""
    return psycopg2.connect(**DB_CONFIG)

def create_table():
    """Создание таблицы students"""
    conn = create_database_connection()
    cursor = conn.cursor()
    
    # Удаляем таблицу если существует
    cursor.execute("DROP TABLE IF EXISTS students")
    
    # Создаем таблицу с auto-increment первичным ключом
    # id_student теперь обычное поле (может содержать дубликаты)
    create_table_query = '''
    CREATE TABLE students (
        id SERIAL PRIMARY KEY,
        id_student INTEGER,
        fio VARCHAR(255) NOT NULL,
        course INTEGER,
        liter VARCHAR(10),
        site VARCHAR(50),
        level VARCHAR(50),
        status VARCHAR(50),
        date_start DATE,
        date_end DATE
    );
    
    -- Добавляем индекс для быстрого поиска по id_student
    CREATE INDEX idx_id_student ON students(id_student);
    '''
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Таблица students создана успешно!")
    print("📌 id_student теперь может содержать дубликаты")

def parse_date(date_value):
    """Парсинг даты из различных форматов"""
    if pd.isna(date_value) or date_value == '':
        return None
    
    if isinstance(date_value, datetime):
        return date_value.date()
    
    if isinstance(date_value, str):
        formats = [
            '%d %B, %Y',
            '%d.%m.%Y',
            '%Y-%m-%d',
            '%d/%m/%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_value.strip(), fmt).date()
            except ValueError:
                continue
        
        try:
            cleaned = date_value.strip().replace('.', ' ').replace(',', ' ')
            return datetime.strptime(cleaned, '%d %B %Y').date()
        except:
            return None
    
    return None

def import_excel_to_postgresql(excel_file):
    """Импорт данных из Excel в PostgreSQL"""
    print(f"📖 Чтение файла {excel_file}...")
    
    df = pd.read_excel(excel_file)
    df = df.dropna(how='all')
    print(f"📊 Найдено записей: {len(df)}")
    
    conn = create_database_connection()
    cursor = conn.cursor()
    
    # Очистка таблицы
    cursor.execute("TRUNCATE TABLE students")
    conn.commit()
    
    # Собираем все данные
    records = []
    errors = []
    
    for index, row in df.iterrows():
        try:
            id_student = int(row['id_student']) if pd.notna(row.get('id_student')) else None
            fio = str(row.get('fio', '')).strip() if pd.notna(row.get('fio')) else ''
            course = int(row['course']) if pd.notna(row.get('course')) else None
            liter = str(row.get('liter', '')).strip() if pd.notna(row.get('liter')) else ''
            site = str(row.get('site', '')).strip() if pd.notna(row.get('site')) else ''
            level = str(row.get('level', '')).strip() if pd.notna(row.get('level')) else ''
            status = str(row.get('status', '')).strip() if pd.notna(row.get('status')) else ''
            
            date_start = parse_date(row.get('date_start'))
            date_end = parse_date(row.get('date_end'))
            
            records.append((
                id_student,
                fio,
                course,
                liter,
                site,
                level,
                status,
                date_start,
                date_end
            ))
            
        except Exception as e:
            errors.append((index, str(e)))
            print(f"❌ Ошибка при обработке строки {index}: {e}")
            continue
    
    # Вставка всех записей
    if records:
        insert_query = """
            INSERT INTO students 
            (id_student, fio, course, liter, site, level, status, date_start, date_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            execute_batch(cursor, insert_query, records, page_size=100)
            conn.commit()
            print(f"\n✅ Успешно загружено {len(records)} записей")
            print(f"📊 Включая все дубликаты id_student")
        except Exception as e:
            conn.rollback()
            print(f"❌ Ошибка при вставке данных: {e}")
    
    cursor.close()
    conn.close()
    
    if errors:
        print(f"\n⚠️  Ошибок при обработке: {len(errors)}")

if __name__ == "__main__":
    create_table()
    
    excel_file_path = 'students.xlsx'
    
    try:
        import_excel_to_postgresql(excel_file_path)
        print("\n🎉 Импорт завершен!")
    except FileNotFoundError:
        print(f"❌ Ошибка: Файл {excel_file_path} не найден!")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()