from typing import List, Optional, Tuple
from app.models.customer import Customer
from app.services.customer_service import CustomerService
from app.utils.validators import Validators

class CustomerController:
    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service
    
    def get_all_customers(self) -> List[Customer]:
        return self.customer_service.get_all_customers()
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        return self.customer_service.get_customer_by_id(customer_id)
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        return self.customer_service.get_customer_by_phone(phone)
    
    def create_customer(self, name: str, phone: str, email: str = "", address: str = "") -> Tuple[bool, str]:
        # Validate input
        if not name.strip():
            return False, "Tên khách hàng không được để trống"
        
        if not phone.strip():
            return False, "Số điện thoại không được để trống"
        
        if not Validators.is_valid_phone(phone):
            return False, "Số điện thoại không hợp lệ"
        
        if email and not Validators.is_valid_email(email):
            return False, "Email không hợp lệ"
        
        if self.customer_service.is_phone_exists(phone):
            return False, "Số điện thoại đã tồn tại"
        
        if email and self.customer_service.is_email_exists(email):
            return False, "Email đã tồn tại"
        
        customer = Customer(name=name, phone=phone, email=email, address=address)
        success = self.customer_service.create_customer(customer)
        
        if success:
            return True, "Thêm khách hàng thành công"
        else:
            return False, "Lỗi khi thêm khách hàng"
    
    def update_customer(self, customer_id: str, name: str, phone: str, email: str = "", address: str = "") -> Tuple[bool, str]:
        if not name.strip():
            return False, "Tên khách hàng không được để trống"
        
        if not phone.strip():
            return False, "Số điện thoại không được để trống"
        
        if not Validators.is_valid_phone(phone):
            return False, "Số điện thoại không hợp lệ"
        
        if email and not Validators.is_valid_email(email):
            return False, "Email không hợp lệ"
        
        if self.customer_service.is_phone_exists(phone, customer_id):
            return False, "Số điện thoại đã tồn tại"
        
        if email and self.customer_service.is_email_exists(email, customer_id):
            return False, "Email đã tồn tại"
        
        customer = Customer(id=customer_id, name=name, phone=phone, email=email, address=address)
        success = self.customer_service.update_customer(customer)
        
        if success:
            return True, "Cập nhật khách hàng thành công"
        else:
            return False, "Lỗi khi cập nhật khách hàng"
    
    def delete_customer(self, customer_id: str) -> Tuple[bool, str]:
        # Kiểm tra xem khách hàng có tồn tại trong hóa đơn không
        if self.customer_service.is_customer_has_invoices(customer_id):
            return False, "Không thể xóa khách hàng đã có giao dịch"
        
        success = self.customer_service.delete_customer(customer_id)
        if success:
            return True, "Xóa khách hàng thành công"
        else:
            return False, "Lỗi khi xóa khách hàng"
    
    def search_customers(self, search_type: str, search_text: str) -> List[Customer]:
        all_customers = self.get_all_customers()
        
        if not search_text:
            return all_customers
        
        search_text = search_text.lower()
        if search_type == 'Tất cả':
            return [c for c in all_customers 
                   if search_text in c.name.lower() or search_text in (c.phone or '')]
        elif search_type == 'Tên':
            return [c for c in all_customers if search_text in c.name.lower()]
        elif search_type == 'Số điện thoại':
            return [c for c in all_customers if search_text in (c.phone or '')]
        
        return all_customers