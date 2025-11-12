from typing import List, Optional
from app.models.repair_invoice import RepairInvoice
from app.utils.database import Database

class RepairService:
    def __init__(self, db: Database):
        self.db = db
    
    def create_repair_order(self, repair: RepairInvoice) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO repair_orders 
                (customer_id, employee_id, issue_description, actual_cost, 
                 created_date, estimated_completion, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (repair.customer_id, repair.employee_id, repair.issue_description,
                  repair.actual_cost, repair.created_date, repair.estimated_completion, 
                  repair.status))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating repair order: {e}")
            return False
    
    def update_repair_order(self, repair: RepairInvoice) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE repair_orders
                SET actual_cost = ?, estimated_completion = ?, status = ?
                WHERE id = ?
            ''', (repair.actual_cost, repair.estimated_completion, repair.status, repair.id))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating repair order: {e}")
            return False
    
    def get_repair_by_id(self, repair_id: str) -> Optional[RepairInvoice]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT r.id, r.customer_id, r.employee_id, r.issue_description,
                   r.actual_cost, r.created_date, r.estimated_completion, r.status,
                   c.name as customer_name, e.full_name as employee_name
            FROM repair_orders r
            LEFT JOIN customers c ON r.customer_id = c.id
            LEFT JOIN employees e ON r.employee_id = e.id
            WHERE r.id = ?
        ''', (repair_id,))
        
        data = cursor.fetchone()
        if data:
            return RepairInvoice(
                id=str(data[0]),
                customer_id=str(data[1]),
                employee_id=data[2],
                issue_description=data[3],
                actual_cost=data[4],
                created_date=data[5],
                estimated_completion=data[6],
                status=data[7]
            )
        return None
    
    def get_all_repairs(self) -> List[RepairInvoice]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT r.id, r.customer_id, r.employee_id, r.issue_description,
                   r.actual_cost, r.created_date, r.estimated_completion, r.status,
                   c.name as customer_name, e.full_name as employee_name
            FROM repair_orders r
            LEFT JOIN customers c ON r.customer_id = c.id
            LEFT JOIN employees e ON r.employee_id = e.id
            ORDER BY r.id DESC
        ''')
        
        repairs = []
        for data in cursor.fetchall():
            repair = RepairInvoice(
                id=str(data[0]),
                customer_id=str(data[1]),
                employee_id=data[2],
                issue_description=data[3],
                actual_cost=data[4],
                created_date=data[5],
                estimated_completion=data[6],
                status=data[7]
            )
            repairs.append(repair)
        return repairs