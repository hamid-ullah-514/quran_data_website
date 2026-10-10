import pymysql
import hashlib

# MySQL Server کی سیٹنگز (اگر آپ کا پاس ورڈ کچھ اور ہے تو یہاں اپ ڈیٹ کر لیں)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'autocommit': True,
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    conn = pymysql.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], password=DB_CONFIG['password'])
    conn.cursor().execute("CREATE DATABASE IF NOT EXISTS quran_app")
    conn.select_db('quran_app')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # یوزرز کا ٹیبل (کسٹم ٹوکن کے ساتھ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            custom_token VARCHAR(255) UNIQUE NOT NULL
        )
    ''')
    
    # پسندیدہ آیات کا ٹیبل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            surah_number INT,
            ayah_number INT,
            note TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # سرچ ہسٹری کا ٹیبل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            search_term VARCHAR(255) UNIQUE NOT NULL
        )
    ''')
    conn.close()

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()