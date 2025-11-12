from typing import List, Tuple, Optional
from app.services.invoice_service import InvoiceService

class InvoiceController:
    def __init__(self, invoice_service: InvoiceService):
        self.invoice_service = invoice_service
    
    def get_all_invoices(self) -> List[Tuple]:
        return self.invoice_service.get_all_invoices()
    
    def get_invoice_details(self, invoice_id: str) -> List:
        return self.invoice_service.get_invoice_details(invoice_id)
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Tuple]:
        return self.invoice_service.get_invoice_by_id(invoice_id)
    
    def search_invoices(self, search_type: str, search_text: str, 
                       from_date: str, to_date: str) -> List[Tuple]:
        all_invoices = self.get_all_invoices()
        
        if not search_text:
            return all_invoices
        
        search_text = search_text.lower()
        filtered_invoices = []
        
        for invoice in all_invoices:
            invoice_id, customer_name, employee_name, total_amount, created_date = invoice
            
            # Filter by date range
            if created_date < from_date or created_date > to_date:
                continue
            
            if search_type == 'Tất cả':
                if (search_text in invoice_id.lower() or 
                    search_text in (customer_name or '').lower() or 
                    search_text in (employee_name or '').lower()):
                    filtered_invoices.append(invoice)
            elif search_type == 'ID hóa đơn':
                if search_text in invoice_id.lower():
                    filtered_invoices.append(invoice)
            elif search_type == 'Tên khách hàng':
                if search_text in (customer_name or '').lower():
                    filtered_invoices.append(invoice)
            elif search_type == 'Tên nhân viên':
                if search_text in (employee_name or '').lower():
                    filtered_invoices.append(invoice)
        
        return filtered_invoices