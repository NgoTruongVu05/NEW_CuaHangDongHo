from typing import Optional
from .person import Person

class Customer(Person):
    def __init__(self, id: Optional[str] = None, name: str = "", phone: str = "", 
                 email: str = "", address: str = ""):
        super().__init__(id, name, phone, email)
        self.address = address
    
    def to_dict(self):
        data = super().to_dict()
        data['address'] = self.address
        return data
    
    @classmethod
    def from_dict(cls, data):
        customer = cls(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', '')
        )
        return customer