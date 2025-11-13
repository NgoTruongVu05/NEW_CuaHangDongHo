from typing import List, Optional, Union
from app.models.watch import Watch
from app.models.mechanical_watch import MechanicalWatch
from app.models.electronic_watch import ElectronicWatch
from app.utils.database import Database
from app.utils.error_handler import handle_database_error, safe_execute

class WatchService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_watches(self) -> List[Union[MechanicalWatch, ElectronicWatch]]:
        try:
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
                try:
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
                except (IndexError, ValueError, TypeError) as e:
                    # Skip invalid records but continue processing
                    from app.utils.error_handler import logger
                    logger.warning(f"Skipping invalid product record: {e}")
                    continue
            return watches
        except Exception as e:
            handle_database_error(e, "lấy danh sách sản phẩm")
            return []
    
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
                features_str = ','.join(watch.features) if watch.features else ''
                cursor.execute('''
                    INSERT INTO products (name, brand_id, product_type, price, quantity, description,
                    battery_life, features, connectivity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (watch.name, watch.brand_id, watch.product_type, watch.price, watch.quantity,
                      watch.description, watch.battery_life, features_str, watch.connectivity))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            handle_database_error(e, "tạo sản phẩm")
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
                features_str = ','.join(watch.features) if watch.features else ''
                cursor.execute('''
                    UPDATE products SET name=?, brand_id=?, product_type=?, price=?, quantity=?, description=?,
                    movement_type=NULL, power_reserve=NULL, water_resistant=NULL, battery_life=?, features=?, connectivity=?
                    WHERE id=?
                ''', (watch.name, watch.brand_id, watch.product_type, watch.price, watch.quantity,
                      watch.description, watch.battery_life, features_str, watch.connectivity, watch.id))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            handle_database_error(e, "cập nhật sản phẩm")
            return False
    
    def delete_watch(self, watch_id: str) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (watch_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            handle_database_error(e, "xóa sản phẩm")
            return False
    
    def update_watch_quantity(self, watch_id: str, new_quantity: int) -> bool:
        try:
            if new_quantity < 0:
                raise ValueError("Số lượng không thể âm")
            cursor = self.db.conn.cursor()
            cursor.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, watch_id))
            self.db.conn.commit()
            return True
        except ValueError as e:
            from app.utils.error_handler import handle_validation_error
            handle_validation_error(e, "số lượng")
            return False
        except Exception as e:
            handle_database_error(e, "cập nhật số lượng sản phẩm")
            return False
    
    def get_available_watches(self) -> List[Union[MechanicalWatch, ElectronicWatch]]:
        """Get watches with quantity > 0"""
        all_watches = self.get_all_watches()
        return [watch for watch in all_watches if watch.quantity > 0]
    
    def get_watches_with_filters(self, filters: dict, order_by: str = 'p.quantity', order_dir: str = 'ASC', 
                                  page_size: int = 50, offset: int = 0) -> tuple:
        """
        Get watches with filters, ordering, and pagination.
        Returns: (watches_list, total_count)
        """
        try:
            cursor = self.db.conn.cursor()
            
            # Build WHERE clause for filters
            where_clauses = []
            params = []
            
            # Search filter (name or brand)
            search_text = filters.get('search', '').strip()
            if search_text:
                where_clauses.append('(LOWER(p.name) LIKE ? OR LOWER(b.name) LIKE ?)')
                search_param = f'%{search_text.lower()}%'
                params.extend([search_param, search_param])
            
            # Brand filter
            selected_brand = filters.get('brand', 'Tất cả')
            if selected_brand != 'Tất cả':
                where_clauses.append('LOWER(b.name) = ?')
                params.append(selected_brand.lower())
            
            # Type filter
            selected_type = filters.get('type', 'Tất cả')
            if selected_type != 'Tất cả':
                if selected_type == 'Đồng hồ cơ':
                    where_clauses.append("LOWER(p.product_type) IN ('mechanical', 'm', 'coil')")
                elif selected_type == 'Đồng hồ điện tử':
                    where_clauses.append("LOWER(p.product_type) IN ('digital', 'smart', 'electronic')")
            
            # Price range filters
            price_min = filters.get('price_min')
            if price_min is not None:
                where_clauses.append('p.price >= ?')
                params.append(price_min)
            
            price_max = filters.get('price_max')
            if price_max is not None:
                where_clauses.append('p.price <= ?')
                params.append(price_max)
            
            # Advanced filters
            power_reserve_min = filters.get('power_reserve_min')
            if power_reserve_min is not None:
                where_clauses.append('p.power_reserve >= ?')
                params.append(power_reserve_min)
            
            battery_life_min = filters.get('battery_life_min')
            if battery_life_min is not None:
                where_clauses.append('p.battery_life >= ?')
                params.append(battery_life_min)
            
            selected_connectivity = filters.get('connectivity', 'Tất cả')
            if selected_connectivity != 'Tất cả':
                where_clauses.append('LOWER(p.connectivity) LIKE ?')
                params.append(f'%{selected_connectivity.lower()}%')
            
            where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
            
            # Get total count for pagination with filters
            count_query = f'SELECT COUNT(*) FROM products p LEFT JOIN brands b ON p.brand_id = b.id WHERE {where_sql}'
            cursor.execute(count_query, params)
            result = cursor.fetchone()
            total_count = result[0] if result else 0
            
            # Fetch paginated products with filters
            query = f'''
                SELECT p.id, p.name, p.brand_id, b.name AS brand, p.product_type, p.price, p.quantity,
                       p.description, p.movement_type, p.power_reserve, p.water_resistant,
                       p.battery_life, p.features, p.connectivity
                FROM products p
                LEFT JOIN brands b ON p.brand_id = b.id
                WHERE {where_sql}
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            '''
            cursor.execute(query, params + [page_size, offset])
            products_data = cursor.fetchall()
            
            # Convert to watch objects
            watches = []
            for data in products_data:
                try:
                    if data[4] and data[4].lower() in ('mechanical', 'm', 'coil'):
                        watch = MechanicalWatch(
                            id=str(data[0]),
                            name=data[1] or '',
                            brand_id=str(data[2]) if data[2] else '',
                            price=data[5] or 0,
                            quantity=data[6] or 0,
                            description=data[7] or '',
                            movement_type=data[8] or '',
                            power_reserve=data[9],
                            water_resistant=bool(data[10]) if data[10] is not None else False
                        )
                    else:
                        features = data[12].split(',') if data[12] else []
                        watch = ElectronicWatch(
                            id=str(data[0]),
                            name=data[1] or '',
                            brand_id=str(data[2]) if data[2] else '',
                            price=data[5] or 0,
                            quantity=data[6] or 0,
                            description=data[7] or '',
                            battery_life=data[11],
                            features=features,
                            connectivity=data[13] or ''
                        )
                    # Store brand name in a custom attribute for easy access
                    watch.brand_name = data[3] or ''
                    watches.append(watch)
                except (IndexError, ValueError, TypeError) as e:
                    from app.utils.error_handler import logger
                    logger.warning(f"Skipping invalid product record: {e}")
                    continue
            
            return watches, total_count
        except Exception as e:
            handle_database_error(e, "lấy danh sách sản phẩm với bộ lọc")
            return [], 0