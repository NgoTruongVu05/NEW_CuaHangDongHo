from abc import ABC
from typing import Optional

class Watch(ABC):
    def __init__(self, id: Optional[str] = None, name: str = "", brand_id: Optional[str] = None,
                 price: float = 0.0, quantity: int = 0, description: str = ""):
        self.id = id
        self.name = name
        self.brand_id = brand_id
        self.price = price
        self.quantity = quantity
        self.description = description
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand_id': self.brand_id,
            'price': self.price,
            'quantity': self.quantity,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            brand_id=data.get('brand_id'),
            price=data.get('price', 0.0),
            quantity=data.get('quantity', 0),
            description=data.get('description', '')
        )