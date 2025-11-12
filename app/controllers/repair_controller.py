from typing import List, Optional, Tuple
from app.models.repair_invoice import RepairInvoice
from app.services.repair_service import RepairService
from app.services.customer_service import CustomerService

class RepairController:
    def __init__(self, repair_service: RepairService, customer_service: CustomerService):
        self.repair_service = repair_service
        self.customer_service = customer_service
    
    def create_repair_order(self, customer_phone: str, employee_id: str, 
                           issue_description: str, estimated_completion: str) -> Tuple[bool, str]:
        if not issue_description.strip():
            return False, "Mô tả lỗi không được để trống"
        
        # Get customer
        customer = self.customer_service.get_customer_by_phone(customer_phone)
        if not customer:
            return False, "Không tìm thấy khách hàng"
        
        repair = RepairInvoice(
            customer_id=customer.id,
            employee_id=employee_id,
            issue_description=issue_description,
            estimated_completion=estimated_completion,
            status="Chờ xử lý",
            actual_cost=0.0
        )
        
        success = self.repair_service.create_repair_order(repair)
        if success:
            return True, "Đơn sửa chữa đã được tạo thành công!"
        else:
            return False, "Lỗi khi tạo đơn sửa chữa"
    
    def update_repair_order(self, repair_id: str, actual_cost: float, 
                           estimated_completion: str, status: str) -> Tuple[bool, str]:
        repair = self.repair_service.get_repair_by_id(repair_id)
        if not repair:
            return False, "Không tìm thấy đơn sửa chữa"
        
        repair.actual_cost = actual_cost
        repair.estimated_completion = estimated_completion
        repair.status = status
        
        success = self.repair_service.update_repair_order(repair)
        if success:
            return True, "Cập nhật đơn sửa chữa thành công"
        else:
            return False, "Lỗi khi cập nhật đơn sửa chữa"
    
    def get_all_repairs(self) -> List[RepairInvoice]:
        return self.repair_service.get_all_repairs()
    
    def get_repair_by_id(self, repair_id: str) -> Optional[RepairInvoice]:
        return self.repair_service.get_repair_by_id(repair_id)