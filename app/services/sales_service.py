from typing import List, Optional, Dict
from app.models.sales_invoice import SalesInvoice
from app.utils.database import Database

class SalesService:
    def __init__(self, db: Database):
        self.db = db
    
    def create_sales_invoice(self, invoice: SalesInvoice) -> bool:
        try:
            cursor = self.db.conn.cursor()
            
            # Insert invoice
            cursor.execute('''
                INSERT INTO invoices (id, customer_id, employee_id, total_amount, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (invoice.id, invoice.customer_id, invoice.employee_id, 
                  invoice.total_amount, invoice.created_date))
            
            # Insert invoice details and update product quantities
            for item in invoice.items:
                cursor.execute('''
                    INSERT INTO invoice_details (invoice_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (invoice.id, item['product_id'], item['quantity'], item['price']))
                
                # Update product quantity
                cursor.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', 
                             (item['quantity'], item['product_id']))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating sales invoice: {e}")
            return False
    
    def generate_invoice_id(self) -> str:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id FROM invoices WHERE id LIKE "HD%" ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        
        if result is None:
            return 'HD001'
        
        last_id = result[0]
        num = int(last_id[2:]) + 1
        return f'HD{num:03d}'
    
    def get_sales_by_employee(self, employee_id: str, month: int, year: int) -> float:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM invoices 
            WHERE employee_id = ? 
            AND strftime('%m', created_date) = ? 
            AND strftime('%Y', created_date) = ?
        ''', (employee_id, f"{month:02d}", str(year)))
        
        result = cursor.fetchone()
        return result[0] if result else 0.0