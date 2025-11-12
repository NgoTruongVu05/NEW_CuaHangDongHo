import sqlite3
import hashlib
import os
from typing import Optional, List, Tuple

class Database:
    def __init__(self, db_path: str = 'data/database/watch_management.db'):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()

        # Bảng thương hiệu (brands)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                country TEXT
            )
        ''')
        
        # Bảng sản phẩm (liên kết brand_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand_id INTEGER NOT NULL,
                product_type TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                description TEXT,
                movement_type TEXT,
                power_reserve INTEGER,
                water_resistant BOOLEAN,
                battery_life INTEGER,
                features TEXT,
                connectivity TEXT,
                FOREIGN KEY (brand_id) REFERENCES brands (id)
            )
        ''')

        # Bảng nhân viên
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                ma_dinh_danh TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                vaitro INTEGER NOT NULL DEFAULT 0,
                phone TEXT,
                email TEXT,
                base_salary REAL DEFAULT 0
            )
        ''')
        
        # Bảng khách hàng
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        ''')
        
        # Bảng hóa đơn
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                customer_id INTEGER,
                employee_id TEXT,
                total_amount REAL NOT NULL,
                created_date TEXT NOT NULL,
                status TEXT DEFAULT '',
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Bảng chi tiết hóa đơn
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Bảng đơn sửa chữa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repair_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                employee_id TEXT,
                issue_description TEXT NOT NULL,
                actual_cost REAL DEFAULT 0,
                created_date TEXT NOT NULL,
                estimated_completion TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Thêm admin mặc định - QL + 6 SỐ CUỐI
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (id, ma_dinh_danh, password, full_name, vaitro, base_salary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('ql123456', '777777123456', self.hash_password('admin123'), 'Quản trị viên', 1, 15000000))
        
        # Thêm nhân viên mặc định - NV + 6 SỐ CUỐI
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (id, ma_dinh_danh, password, full_name, vaitro, base_salary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('nv654321', '888888654321', self.hash_password('123456'), 'Nhân Viên Mẫu', 0, 8000000))
        
        # Thêm một số thương hiệu mẫu
        sample_brands = [
            ('Rolex', 'Thụy Sĩ'),
            ('Omega', 'Thụy Sĩ'),
            ('Casio', 'Nhật Bản'),
            ('Seiko', 'Nhật Bản'),
            ('Tissot', 'Thụy Sĩ'),
            ('Citizen', 'Nhật Bản')
        ]
        
        cursor.executemany('INSERT OR IGNORE INTO brands (name, country) VALUES (?, ?)', sample_brands)
        
        self.conn.commit()
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, login_input: str, password: str) -> Optional[Tuple]:
        cursor = self.conn.cursor()
        hashed_password = self.hash_password(password)
        
        cursor.execute('SELECT * FROM employees WHERE id = ? AND password = ?', 
                      (login_input, hashed_password))
        user = cursor.fetchone()
        
        return user
    
    def generate_employee_id(self, ma_dinh_danh: str, role: int) -> str:
        """Tạo ID theo format: nv/ql + 6 số cuối mã định danh"""
        if len(ma_dinh_danh) != 12 or not ma_dinh_danh.isdigit():
            raise ValueError("Mã định danh phải có đúng 12 chữ số")
        
        six_digits = ma_dinh_danh[-6:]  # 6 số cuối
        prefix = 'ql' if role == 1 else 'nv'
        return f"{prefix}{six_digits}"
    
    def check_ma_dinh_danh_exists(self, ma_dinh_danh: str) -> bool:
        """Kiểm tra mã định danh đã tồn tại chưa"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM employees WHERE ma_dinh_danh = ?', (ma_dinh_danh,))
        return cursor.fetchone() is not None

    def generate_invoice_id(self) -> str:
        """Tạo ID hóa đơn theo format HD001, HD002,..."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM invoices WHERE id LIKE "HD%" ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        
        if result is None:
            return 'HD001'
        
        last_id = result[0]
        num = int(last_id[2:]) + 1  # Lấy phần số và tăng 1
        return f'HD{num:03d}'

    def close(self):
        """Đóng kết nối database"""
        if self.conn:
            self.conn.close()