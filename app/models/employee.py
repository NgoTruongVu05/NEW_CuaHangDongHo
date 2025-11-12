from typing import Optional
from .person import Person

class Employee(Person):
    def __init__(self, id: Optional[str] = None, name: str = "", phone: str = "", 
                 email: str = "", ma_dinh_danh: str = "", password: str = "",
                 role: int = 0, base_salary: float = 0.0):
        super().__init__(id, name, phone, email)
        self.ma_dinh_danh = ma_dinh_danh
        self.password = password
        self.role = role  # 0: nhân viên, 1: quản lý
        self.base_salary = base_salary
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'ma_dinh_danh': self.ma_dinh_danh,
            'password': self.password,
            'role': self.role,
            'base_salary': self.base_salary
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        employee = cls(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            ma_dinh_danh=data.get('ma_dinh_danh', ''),
            password=data.get('password', ''),
            role=data.get('role', 0),
            base_salary=data.get('base_salary', 0.0)
        )
        return employee
    
    def get_role_text(self):
        return "Quản lý" if self.role == 1 else "Nhân viên"