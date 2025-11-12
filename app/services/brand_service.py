from typing import List, Optional
from app.models.brand import Brand
from app.utils.database import Database

class BrandService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_brands(self) -> List[Brand]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM brands ORDER BY name')
        brands_data = cursor.fetchall()
        
        brands = []
        for data in brands_data:
            brand = Brand(
                id=str(data[0]),
                name=data[1],
                country=data[2]
            )
            brands.append(brand)
        return brands
    
    def get_brand_by_id(self, brand_id: str) -> Optional[Brand]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM brands WHERE id = ?', (brand_id,))
        data = cursor.fetchone()
        
        if data:
            return Brand(
                id=str(data[0]),
                name=data[1],
                country=data[2]
            )
        return None
    
    def get_brand_by_name(self, name: str) -> Optional[Brand]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM brands WHERE name = ?', (name,))
        data = cursor.fetchone()
        
        if data:
            return Brand(
                id=str(data[0]),
                name=data[1],
                country=data[2]
            )
        return None
    
    def create_brand(self, brand: Brand) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('INSERT INTO brands (name, country) VALUES (?, ?)', 
                         (brand.name, brand.country))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating brand: {e}")
            return False
    
    def update_brand(self, brand: Brand) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('UPDATE brands SET name=?, country=? WHERE id=?', 
                         (brand.name, brand.country, brand.id))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating brand: {e}")
            return False
    
    def delete_brand(self, brand_id: str) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM brands WHERE id = ?', (brand_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting brand: {e}")
            return False
    
    def is_brand_used(self, brand_id: str) -> bool:
        """Check if brand is used by any products"""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products WHERE brand_id = ?', (brand_id,))
        count = cursor.fetchone()[0]
        return count > 0