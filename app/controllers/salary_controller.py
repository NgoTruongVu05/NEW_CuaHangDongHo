from typing import List, Dict
from app.services.salary_service import SalaryService

class SalaryController:
    def __init__(self, salary_service: SalaryService):
        self.salary_service = salary_service
    
    def calculate_all_salaries(self, month: int, year: int) -> List[Dict]:
        return self.salary_service.get_all_salaries(month, year)
    
    def calculate_employee_salary(self, employee_id: str, month: int, year: int) -> Dict:
        return self.salary_service.calculate_salary(employee_id, month, year)