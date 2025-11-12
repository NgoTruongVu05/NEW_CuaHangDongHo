from typing import Optional

class Brand:
    def __init__(self, id: Optional[str] = None, name: str = "", country: str = ""):
        self.id = id
        self.name = name
        self.country = country
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            country=data.get('country', '')
        )