from typing import Optional, List
from .invoice import Invoice

class SalesInvoice(Invoice):
    def __init__(self, id: Optional[str] = None, customer_id: Optional[str] = None, 
                 employee_id: Optional[str] = None, total_amount: float = 0.0, 
                 created_date: Optional[str] = None, status: str = "",
                 items: List[dict] = None):
        super().__init__(id, customer_id, employee_id, total_amount, created_date, "sale", status)
        self.items = items or []
    
    def calculate_total(self):
        self.total_amount = sum(item.get('price', 0) * item.get('quantity', 0) for item in self.items)
        return self.total_amount