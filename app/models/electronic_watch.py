from typing import Optional, List
from .watch import Watch

class ElectronicWatch(Watch):
    def __init__(self, id: Optional[str] = None, name: str = "", brand_id: Optional[str] = None,
                 price: float = 0.0, quantity: int = 0, description: str = "",
                 battery_life: int = 0, features: List[str] = None, connectivity: str = ""):
        super().__init__(id, name, brand_id, price, quantity, description)
        self.battery_life = battery_life
        self.features = features or []
        self.connectivity = connectivity
        self.product_type = "electronic"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'product_type': self.product_type,
            'battery_life': self.battery_life,
            'features': ','.join(self.features),
            'connectivity': self.connectivity
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        features_str = data.get('features', '')
        features = features_str.split(',') if features_str else []
        
        watch = cls(
            id=data.get('id'),
            name=data.get('name', ''),
            brand_id=data.get('brand_id'),
            price=data.get('price', 0.0),
            quantity=data.get('quantity', 0),
            description=data.get('description', ''),
            battery_life=data.get('battery_life', 0),
            features=features,
            connectivity=data.get('connectivity', '')
        )
        return watch