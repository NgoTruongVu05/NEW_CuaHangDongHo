from typing import Optional

class Salary:
    def __init__(self, id: Optional[str] = None, employee_id: Optional[str] = None, 
                 month: int = 0, year: int = 0, base_salary: float = 0.0, 
                 bonus: float = 0.0, deductions: float = 0.0, total_salary: float = 0.0, 
                 status: str = "pending"):
        self.id = id
        self.employee_id = employee_id
        self.month = month
        self.year = year
        self.base_salary = base_salary
        self.bonus = bonus
        self.deductions = deductions
        self.total_salary = total_salary
        self.status = status
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'month': self.month,
            'year': self.year,
            'base_salary': self.base_salary,
            'bonus': self.bonus,
            'deductions': self.deductions,
            'total_salary': self.total_salary,
            'status': self.status
        }
    
    def calculate_total(self):
        self.total_salary = self.base_salary + self.bonus - self.deductions
        return self.total_salary