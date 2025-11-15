from typing import List, Optional, Tuple
from app.models.invoice import Invoice, InvoiceDetail
from app.utils.database import Database

class InvoiceService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_invoices(self) -> List[Tuple]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT i.id, c.name, e.full_name, i.total_amount, i.created_date
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN employees e ON i.employee_id = e.id
            ORDER BY i.id DESC
        ''')
        return cursor.fetchall()
    
    def get_invoice_details(self, invoice_id: str) -> List[InvoiceDetail]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id.*, p.name as product_name
            FROM invoice_details id
            JOIN products p ON id.product_id = p.id
            WHERE id.invoice_id = ?
        ''', (invoice_id,))

        details = []
        for data in cursor.fetchall():
            detail = InvoiceDetail(
                id=str(data[0]),
                invoice_id=data[1],
                product_id=str(data[2]),
                quantity=data[3],
                price=data[4],
                product_name=data[5]
            )
            details.append(detail)
        return details
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Tuple]:
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT i.id, i.customer_id, i.employee_id, i.total_amount, i.created_date,
                   c.name as customer_name, c.phone, c.address,
                   e.full_name as employee_name
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN employees e ON i.employee_id = e.id
            WHERE i.id = ?
        ''', (invoice_id,))
        return cursor.fetchone()