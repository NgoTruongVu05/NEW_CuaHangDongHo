from typing import List, Optional
from app.models.brand import Brand
from app.utils.database import Database
from app.utils.error_handler import handle_database_error

class BrandService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_brands(self) -> List[Brand]:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM brands ORDER BY name')
            brands_data = cursor.fetchall()
            
            brands = []
            for data in brands_data:
                try:
                    brand = Brand(
                        id=str(data[0]),
                        name=data[1],
                        country=data[2] if len(data) > 2 else ""
                    )
                    brands.append(brand)
                except (IndexError, ValueError, TypeError) as e:
                    from app.utils.error_handler import logger
                    logger.warning(f"Skipping invalid brand record: {e}")
                    continue
            return brands
        except Exception as e:
            handle_database_error(e, "lấy danh sách thương hiệu")
            return []
    
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
                         (brand.name, brand.country or ""))
            self.db.conn.commit()
            return True
        except Exception as e:
            handle_database_error(e, "tạo thương hiệu")
            return False
    
    def update_brand(self, brand: Brand) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('UPDATE brands SET name=?, country=? WHERE id=?', 
                         (brand.name, brand.country or "", brand.id))
            self.db.conn.commit()
            return True
        except Exception as e:
            handle_database_error(e, "cập nhật thương hiệu")
            return False
    
    def delete_brand(self, brand_id: str) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM brands WHERE id = ?', (brand_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            handle_database_error(e, "xóa thương hiệu")
            return False
    
    def is_brand_used(self, brand_id: str) -> bool:
        """Check if brand is used by any products"""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products WHERE brand_id = ?', (brand_id,))
        count = cursor.fetchone()[0]
        return count > 0