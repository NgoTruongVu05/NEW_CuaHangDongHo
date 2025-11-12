from abc import ABC
from typing import Optional

class Person(ABC):
    def __init__(self, id: Optional[str] = None, name: str = "", phone: str = "", email: str = ""):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )