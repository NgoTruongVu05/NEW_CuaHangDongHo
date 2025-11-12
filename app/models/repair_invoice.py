from typing import Optional
from .invoice import Invoice

class RepairInvoice(Invoice):
    def __init__(self, id: Optional[str] = None, customer_id: Optional[str] = None, 
                 employee_id: Optional[str] = None, total_amount: float = 0.0, 
                 created_date: Optional[str] = None, status: str = "",
                 issue_description: str = "", estimated_completion: Optional[str] = None,
                 actual_cost: float = 0.0):
        super().__init__(id, customer_id, employee_id, total_amount, created_date, "repair", status)
        self.issue_description = issue_description
        self.estimated_completion = estimated_completion
        self.actual_cost = actual_cost
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'issue_description': self.issue_description,
            'estimated_completion': self.estimated_completion,
            'actual_cost': self.actual_cost
        })
        return data