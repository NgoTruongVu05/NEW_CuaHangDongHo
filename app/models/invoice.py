from typing import Optional, List
from datetime import datetime

class Invoice:
    def __init__(self, id: Optional[str] = None, customer_id: Optional[str] = None, 
                 employee_id: Optional[str] = None, total_amount: float = 0.0, 
                 created_date: Optional[str] = None, invoice_type: str = "sale", 
                 status: str = ""):
        self.id = id
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.total_amount = total_amount
        self.created_date = created_date or datetime.now().strftime('%Y-%m-%d')
        self.invoice_type = invoice_type
        self.status = status
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'employee_id': self.employee_id,
            'total_amount': self.total_amount,
            'created_date': self.created_date,
            'invoice_type': self.invoice_type,
            'status': self.status
        }

class InvoiceDetail:
    def __init__(self, id: Optional[str] = None, invoice_id: Optional[str] = None, 
                 product_id: Optional[str] = None, quantity: int = 0, price: float = 0.0):
        self.id = id
        self.invoice_id = invoice_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }