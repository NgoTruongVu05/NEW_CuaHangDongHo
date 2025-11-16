from typing import List, Optional, Tuple
from app.models.employee import Employee
from app.services.employee_service import EmployeeService
from app.utils.validators import Validators

class EmployeeController:
    def __init__(self, employee_service: EmployeeService):
        self.employee_service = employee_service
    
    def get_all_employees(self) -> List[Employee]:
        return self.employee_service.get_all_employees()
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        return self.employee_service.get_employee_by_id(employee_id)
    
    def verify_login(self, user_id: str, password: str) -> Optional[Employee]:
        return self.employee_service.verify_login(user_id, password)
    
    def create_employee(self, ma_dinh_danh: str, password: str, name: str, 
                       role: int, base_salary: float, phone: str = "", email: str = "") -> Tuple[bool, str]:
        # Validate input
        if not ma_dinh_danh.strip() or len(ma_dinh_danh) != 12 or not ma_dinh_danh.isdigit():
            return False, "Mã định danh phải có đúng 12 chữ số"
        
        if not password.strip():
            return False, "Mật khẩu không được để trống"
        
        if not name.strip():
            return False, "Họ tên không được để trống"
        
        # Bắt buộc số điện thoại
        if not phone.strip():
            return False, "Số điện thoại không được để trống"
        
        # Bắt buộc email
        if not email.strip():
            return False, "Email không được để trống"
        
        if not Validators.is_valid_phone(phone):
            return False, "Số điện thoại không hợp lệ"
        
        if not Validators.is_valid_email(email):
            return False, "Email không hợp lệ"
        
        if self.employee_service.is_ma_dinh_danh_exists(ma_dinh_danh):
            return False, "Mã định danh đã tồn tại"
        
        # Kiểm tra số điện thoại trùng
        if self.employee_service.is_phone_exists(phone):
            return False, "Số điện thoại đã tồn tại"
        
        # Kiểm tra email trùng
        if self.employee_service.is_email_exists(email):
            return False, "Email đã tồn tại"
        
        # Generate employee ID - CHỈ DÙNG 6 SỐ CUỐI
        employee_id = ma_dinh_danh[-6:]
        
        if self.employee_service.is_id_exists(employee_id):
            return False, "ID nhân viên đã tồn tại"
        
        hashed_password = self.employee_service.db.hash_password(password)
        employee = Employee(
            id=employee_id,
            ma_dinh_danh=ma_dinh_danh,
            password=hashed_password,
            name=name,
            role=role,
            phone=phone,
            email=email,
            base_salary=base_salary
        )
        
        success = self.employee_service.create_employee(employee)
        if success:
            return True, "Thêm nhân viên thành công"
        else:
            return False, "Lỗi khi thêm nhân viên"
    
    def update_employee(self, employee_id: str, name: str, role: int, 
                   base_salary: float, phone: str = "", email: str = "", 
                   password: str = "") -> Tuple[bool, str]:
        if not name.strip():
            return False, "Họ tên không được để trống"
        
        # Bắt buộc số điện thoại
        if not phone.strip():
            return False, "Số điện thoại không được để trống"
        
        # Bắt buộc email
        if not email.strip():
            return False, "Email không được để trống"
        
        if not Validators.is_valid_phone(phone):
            return False, "Số điện thoại không hợp lệ"
        
        if not Validators.is_valid_email(email):
            return False, "Email không hợp lệ"
        
        # Kiểm tra số điện thoại trùng (trừ chính nhân viên đang sửa)
        if self.employee_service.is_phone_exists(phone, employee_id):
            return False, "Số điện thoại đã tồn tại"
        
        # Kiểm tra email trùng (trừ chính nhân viên đang sửa)
        if self.employee_service.is_email_exists(email, employee_id):
            return False, "Email đã tồn tại"
        
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            return False, "Không tìm thấy nhân viên"
        
        # KHÔNG cho phép thay đổi vai trò của quản lý khác
        if employee.role == 1 and role == 0:
            return False, "Không thể thay đổi vai trò của quản lý"
        
        # Update fields
        employee.name = name
        employee.role = role
        employee.phone = phone
        employee.email = email
        employee.base_salary = base_salary
        
        if password:
            employee.password = self.employee_service.db.hash_password(password)
        
        success = self.employee_service.update_employee(employee)
        if success:
            return True, "Cập nhật nhân viên thành công"
        else:
            return False, "Lỗi khi cập nhật nhân viên"
    
    def delete_employee(self, employee_id: str, current_user_id: str = None) -> Tuple[bool, str]:
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            return False, "Không tìm thấy nhân viên"
        
        # Không cho phép xóa chính mình
        if employee_id == current_user_id:
            return False, "Không thể xóa tài khoản của chính mình"
        
        if employee.role == 1:
            return False, "Không thể xóa tài khoản quản lý"
        
        # Kiểm tra xem nhân viên có tồn tại trong hóa đơn không
        if self.employee_service.is_employee_has_invoices(employee_id):
            return False, "Không thể xóa nhân viên đã có giao dịch"
        
        success = self.employee_service.delete_employee(employee_id)
        if success:
            return True, "Xóa nhân viên thành công"
        else:
            return False, "Lỗi khi xóa nhân viên"
    
    def search_employees(self, search_type: str, search_text: str) -> List[Employee]:
        all_employees = self.get_all_employees()
        
        if not search_text:
            return all_employees
        
        search_text = search_text.lower()
        if search_type == 'Tất cả':
            return [e for e in all_employees 
                   if search_text in e.id.lower() or 
                   search_text in e.ma_dinh_danh.lower() or 
                   search_text in e.name.lower() or
                   search_text in (e.phone or '').lower() or
                   search_text in (e.email or '').lower()]
        elif search_type == 'ID':
            return [e for e in all_employees if search_text in e.id.lower()]
        elif search_type == 'Mã ĐD':
            return [e for e in all_employees if search_text in e.ma_dinh_danh.lower()]
        elif search_type == 'Họ tên':
            return [e for e in all_employees if search_text in e.name.lower()]
        elif search_type == 'Số điện thoại':
            return [e for e in all_employees if search_text in (e.phone or '').lower()]
        elif search_type == 'Email':
            return [e for e in all_employees if search_text in (e.email or '').lower()]
        elif search_type == 'Vai trò':
            role_text = "quản lý" if search_text in ['quản lý', '1'] else "nhân viên"
            return [e for e in all_employees if e.get_role_text().lower() == role_text]
        
        return all_employees