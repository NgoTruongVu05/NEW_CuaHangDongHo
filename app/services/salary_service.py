from typing import List, Optional, Dict
from app.models.salary import Salary
from app.utils.database import Database

class SalaryService:
    def __init__(self, db: Database):
        self.db = db
    
    def calculate_salary(self, employee_id: str, month: int, year: int) -> Dict:
        cursor = self.db.conn.cursor()
        
        # Get base salary
        cursor.execute('SELECT base_salary FROM employees WHERE id = ?', (employee_id,))
        result = cursor.fetchone()
        base_salary = result[0] if result and result[0] else 0
        
        # Calculate total sales
        cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM invoices 
            WHERE employee_id = ? 
            AND strftime('%m', created_date) = ? 
            AND strftime('%Y', created_date) = ?
        ''', (employee_id, f"{month:02d}", str(year)))
        
        result = cursor.fetchone()
        total_sales = result[0] if result else 0
        
        # Calculate commission (0.5%)
        commission = total_sales * 0.005
        total_salary = base_salary + commission
        
        return {
            'base_salary': base_salary,
            'total_sales': total_sales,
            'commission': commission,
            'total_salary': total_salary
        }
    
    def get_all_salaries(self, month: int, year: int) -> List[Dict]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, full_name, base_salary FROM employees')
        employees = cursor.fetchall()
        
        salaries = []
        for emp in employees:
            emp_id, emp_name, base_salary = emp
            salary_data = self.calculate_salary(emp_id, month, year)
            
            salary_info = {
                'employee_id': emp_id,
                'employee_name': emp_name,
                'base_salary': base_salary,
                'total_sales': salary_data['total_sales'],
                'commission': salary_data['commission'],
                'total_salary': salary_data['total_salary']
            }
            salaries.append(salary_info)
        
        return salaries