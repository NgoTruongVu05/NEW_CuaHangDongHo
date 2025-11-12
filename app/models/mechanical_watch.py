from typing import Optional
from .watch import Watch

class MechanicalWatch(Watch):
    def __init__(self, id: Optional[str] = None, name: str = "", brand_id: Optional[str] = None,
                 price: float = 0.0, quantity: int = 0, description: str = "",
                 movement_type: str = "", power_reserve: int = 0, water_resistant: bool = False):
        super().__init__(id, name, brand_id, price, quantity, description)
        self.movement_type = movement_type
        self.power_reserve = power_reserve
        self.water_resistant = water_resistant
        self.product_type = "mechanical"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'product_type': self.product_type,
            'movement_type': self.movement_type,
            'power_reserve': self.power_reserve,
            'water_resistant': self.water_resistant
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        watch = cls(
            id=data.get('id'),
            name=data.get('name', ''),
            brand_id=data.get('brand_id'),
            price=data.get('price', 0.0),
            quantity=data.get('quantity', 0),
            description=data.get('description', ''),
            movement_type=data.get('movement_type', ''),
            power_reserve=data.get('power_reserve', 0),
            water_resistant=bool(data.get('water_resistant', False))
        )
        return watch