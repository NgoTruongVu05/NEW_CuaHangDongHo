from typing import List, Tuple, Dict
from app.models.sales_invoice import SalesInvoice
from app.services.sales_service import SalesService
from app.services.customer_service import CustomerService
from app.services.watch_service import WatchService

class SalesController:
    def __init__(self, sales_service: SalesService, customer_service: CustomerService, watch_service: WatchService):
        self.sales_service = sales_service
        self.customer_service = customer_service
        self.watch_service = watch_service
    
    def create_sales_invoice(self, customer_phone: str, employee_id: str, 
                           items: List[Dict]) -> Tuple[bool, str, str]:
        # Validate items
        if not items:
            return False, "Giỏ hàng trống", ""
        
        # Validate quantities
        for item in items:
            watch = self.watch_service.get_watch_by_id(item['product_id'])
            if not watch:
                return False, f"Sản phẩm {item['product_id']} không tồn tại", ""
            
            if watch.quantity < item['quantity']:
                return False, f"Sản phẩm {watch.name} chỉ còn {watch.quantity} trong kho", ""
        
        # Get or create customer
        customer = self.customer_service.get_customer_by_phone(customer_phone)
        customer_id = customer.id if customer else None
        
        # Generate invoice ID
        invoice_id = self.sales_service.generate_invoice_id()
        
        # Calculate total
        total_amount = sum(item['price'] * item['quantity'] for item in items)
        
        # Create invoice
        invoice = SalesInvoice(
            id=invoice_id,
            customer_id=customer_id,
            employee_id=employee_id,
            total_amount=total_amount,
            items=items
        )
        
        success = self.sales_service.create_sales_invoice(invoice)
        if success:
            return True, f"Hóa đơn #{invoice_id} đã được tạo thành công!", invoice_id
        else:
            return False, "Lỗi khi tạo hóa đơn", ""
    
    def get_sales_by_employee(self, employee_id: str, month: int, year: int) -> float:
        return self.sales_service.get_sales_by_employee(employee_id, month, year)