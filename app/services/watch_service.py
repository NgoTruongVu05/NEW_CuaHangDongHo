from typing import List, Optional, Union
from app.models.watch import Watch
from app.models.mechanical_watch import MechanicalWatch
from app.models.electronic_watch import ElectronicWatch
from app.utils.database import Database

class WatchService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_watches(self) -> List[Union[MechanicalWatch, ElectronicWatch]]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT p.*, b.name as brand_name 
            FROM products p 
            LEFT JOIN brands b ON p.brand_id = b.id 
            ORDER BY p.id
        ''')
        products_data = cursor.fetchall()
        
        watches = []
        for data in products_data:
            if data[3] == "mechanical":  # product_type
                watch = MechanicalWatch(
                    id=str(data[0]),
                    name=data[1],
                    brand_id=str(data[2]),
                    price=data[4],
                    quantity=data[5],
                    description=data[6],
                    movement_type=data[7],
                    power_reserve=data[8],
                    water_resistant=bool(data[9])
                )
            else:
                features = data[11].split(',') if data[11] else []
                watch = ElectronicWatch(
                    id=str(data[0]),
                    name=data[1],
                    brand_id=str(data[2]),
                    price=data[4],
                    quantity=data[5],
                    description=data[6],
                    battery_life=data[10],
                    features=features,
                    connectivity=data[12]
                )
            watches.append(watch)
        return watches
    
    def get_watch_by_id(self, watch_id: str) -> Optional[Union[MechanicalWatch, ElectronicWatch]]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT p.*, b.name as brand_name 
            FROM products p 
            LEFT JOIN brands b ON p.brand_id = b.id 
            WHERE p.id = ?
        ''', (watch_id,))
        data = cursor.fetchone()
        
        if not data:
            return None
            
        if data[3] == "mechanical":
            return MechanicalWatch(
                id=str(data[0]),
                name=data[1],
                brand_id=str(data[2]),
                price=data[4],
                quantity=data[5],
                description=data[6],
                movement_type=data[7],
                power_reserve=data[8],
                water_resistant=bool(data[9])
            )
        else:
            features = data[11].split(',') if data[11] else []
            return ElectronicWatch(
                id=str(data[0]),
                name=data[1],
                brand_id=str(data[2]),
                price=data[4],
                quantity=data[5],
                description=data[6],
                battery_life=data[10],
                features=features,
                connectivity=data[12]
            )
    
    def create_watch(self, watch: Union[MechanicalWatch, ElectronicWatch]) -> bool:
        try:
            cursor = self.db.conn.cursor()
            
            if isinstance(watch, MechanicalWatch):
                cursor.execute('''
                    INSERT INTO products (name, brand_id, product_type, price, quantity, description,
                    movement_type, power_reserve, water_resistant)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (watch.name, watch.brand_id, watch.product_type, watch.price, watch.quantity,
                      watch.description, watch.movement_type, watch.power_reserve, watch.water_resistant))
            else:
                features_str = ','.join(watch.features)
                cursor.execute('''
                    INSERT INTO products (name, brand_id, product_type, price, quantity, description,
                    battery_life, features, connectivity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (watch.name, watch.brand_id, watch.product_type, watch.price, watch.quantity,
                      watch.description, watch.battery_life, features_str, watch.connectivity))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating watch: {e}")
            return False
    
    def update_watch(self, watch: Union[MechanicalWatch, ElectronicWatch]) -> bool:
        try:
            cursor = self.db.conn.cursor()
            
            if isinstance(watch, MechanicalWatch):
                cursor.execute('''
                    UPDATE products SET name=?, brand_id=?, product_type=?, price=?, quantity=?, description=?,
                    movement_type=?, power_reserve=?, water_resistant=?, battery_life=NULL, features=NULL, connectivity=NULL
                    WHERE id=?
                ''', (watch.name, watch.brand_id, watch.product_type, watch.price, watch.quantity,
                      watch.description, watch.movement_type, watch.power_reserve, watch.water_resistant, watch.id))
            else:
                features_str = ','.join(watch.features)
                cursor.execute('''
                    UPDATE products SET name=?, brand_id=?, product_type=?, price=?, quantity=?, description=?,
                    movement_type=NULL, power_reserve=NULL, water_resistant=NULL, battery_life=?, features=?, connectivity=?
                    WHERE id=?
                ''', (watch.name, watch.brand_id, watch.product_type, watch.price, watch.quantity,
                      watch.description, watch.battery_life, features_str, watch.connectivity, watch.id))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating watch: {e}")
            return False
    
    def delete_watch(self, watch_id: str) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (watch_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting watch: {e}")
            return False
    
    def update_watch_quantity(self, watch_id: str, new_quantity: int) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, watch_id))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating watch quantity: {e}")
            return False
    
    def get_available_watches(self) -> List[Union[MechanicalWatch, ElectronicWatch]]:
        """Get watches with quantity > 0"""
        all_watches = self.get_all_watches()
        return [watch for watch in all_watches if watch.quantity > 0]