from typing import List, Optional
from app.models.employee import Employee
from app.utils.database import Database

class EmployeeService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_employees(self) -> List[Employee]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM employees ORDER BY id')
        employees_data = cursor.fetchall()
        
        employees = []
        for data in employees_data:
            employee = Employee(
                id=data[0],
                ma_dinh_danh=data[1],
                password=data[2],
                name=data[3],
                role=data[4],
                phone=data[5],
                email=data[6],
                base_salary=data[7]
            )
            employees.append(employee)
        return employees
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        data = cursor.fetchone()
        
        if data:
            return Employee(
                id=data[0],
                ma_dinh_danh=data[1],
                password=data[2],
                name=data[3],
                role=data[4],
                phone=data[5],
                email=data[6],
                base_salary=data[7]
            )
        return None
    
    def create_employee(self, employee: Employee) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO employees (id, ma_dinh_danh, password, full_name, vaitro, phone, email, base_salary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (employee.id, employee.ma_dinh_danh, employee.password, employee.name, 
                  employee.role, employee.phone, employee.email, employee.base_salary))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating employee: {e}")
            return False
    
    def update_employee(self, employee: Employee) -> bool:
        try:
            cursor = self.db.conn.cursor()
            if employee.password:
                cursor.execute('''
                    UPDATE employees SET password=?, full_name=?, vaitro=?, phone=?, email=?, base_salary=?
                    WHERE id=?
                ''', (employee.password, employee.name, employee.role, employee.phone, 
                      employee.email, employee.base_salary, employee.id))
            else:
                cursor.execute('''
                    UPDATE employees SET full_name=?, vaitro=?, phone=?, email=?, base_salary=?
                    WHERE id=?
                ''', (employee.name, employee.role, employee.phone, employee.email, 
                      employee.base_salary, employee.id))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating employee: {e}")
            return False
    
    def delete_employee(self, employee_id: str) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return False
    
    def is_ma_dinh_danh_exists(self, ma_dinh_danh: str) -> bool:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id FROM employees WHERE ma_dinh_danh = ?', (ma_dinh_danh,))
        return cursor.fetchone() is not None
    
    def is_id_exists(self, employee_id: str) -> bool:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id FROM employees WHERE id = ?', (employee_id,))
        return cursor.fetchone() is not None
    
    def is_phone_exists(self, phone: str, exclude_employee_id: Optional[str] = None) -> bool:
        cursor = self.db.conn.cursor()
        if exclude_employee_id:
            cursor.execute('SELECT id FROM employees WHERE phone = ? AND id != ?', 
                         (phone, exclude_employee_id))
        else:
            cursor.execute('SELECT id FROM employees WHERE phone = ?', (phone,))
        return cursor.fetchone() is not None
    
    def is_email_exists(self, email: str, exclude_employee_id: Optional[str] = None) -> bool:
        cursor = self.db.conn.cursor()
        if exclude_employee_id:
            cursor.execute('SELECT id FROM employees WHERE email = ? AND id != ?', 
                         (email, exclude_employee_id))
        else:
            cursor.execute('SELECT id FROM employees WHERE email = ?', (email,))
        return cursor.fetchone() is not None
    
    def verify_login(self, user_id: str, password: str) -> Optional[Employee]:
        cursor = self.db.conn.cursor()
        hashed_password = self.db.hash_password(password)
        cursor.execute('SELECT * FROM employees WHERE id = ? AND password = ?', 
                      (user_id, hashed_password))
        data = cursor.fetchone()
        
        if data:
            return Employee(
                id=data[0],
                ma_dinh_danh=data[1],
                password=data[2],
                name=data[3],
                role=data[4],
                phone=data[5],
                email=data[6],
                base_salary=data[7]
            )
        return None
    
    def is_employee_has_invoices(self, employee_id: str) -> bool:
        """Kiểm tra xem nhân viên có tồn tại trong hóa đơn không"""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM invoices WHERE employee_id = ?', (employee_id,))
        count = cursor.fetchone()[0]
        return count > 0