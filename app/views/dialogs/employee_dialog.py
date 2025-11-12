from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                             QComboBox, QMessageBox, QDoubleSpinBox, QLabel,
                             QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy)

class EmployeeDialog(QDialog):
    def __init__(self, db, employee_controller, employee_id=None, user_id=None, user_role=None):
        super().__init__()
        self.db = db
        self.employee_controller = employee_controller
        self.employee_id = employee_id
        self.user_id = user_id
        self.user_role = user_role
        self.init_ui()
        if employee_id:
            self.load_employee_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa nhân viên' if not self.employee_id else 'Sửa nhân viên')
        self.setFixedSize(450, 400)
        
        form_layout = QFormLayout()
        
        # Mã định danh (chỉ nhập khi thêm mới)
        if not self.employee_id:
            self.ma_dinh_danh_input = QLineEdit()
            self.ma_dinh_danh_input.setPlaceholderText('Nhập 12 chữ số')
            self.ma_dinh_danh_input.textChanged.connect(self.on_ma_dinh_danh_changed)
            form_layout.addRow('Mã định danh (12 số):', self.ma_dinh_danh_input)
            
            self.id_label = QLabel('Chưa có ID')
            self.id_label.setStyleSheet('color: #2E86AB; font-weight: bold; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
            form_layout.addRow('ID:', self.id_label)
        else:
            employee = self.employee_controller.get_employee_by_id(self.employee_id)
            if employee:
                id_label = QLabel(employee.id)
                id_label.setStyleSheet('color: #666; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
                form_layout.addRow('ID:', id_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        if not self.employee_id:
            self.password_input.setPlaceholderText('Bắt buộc khi thêm mới')
        else:
            self.password_input.setPlaceholderText('Để trống nếu không đổi mật khẩu')
            
            # Không cho sửa mật khẩu của quản lý khác
            employee = self.employee_controller.get_employee_by_id(self.employee_id)
            if employee and employee.role == 1 and employee.id != self.user_id:
                self.password_input.setPlaceholderText('Không thể sửa mật khẩu của Quản lý khác')
                self.password_input.setDisabled(True)
        
        form_layout.addRow('Mật khẩu:', self.password_input)
        
        self.full_name_input = QLineEdit()
        form_layout.addRow('Họ tên:', self.full_name_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(['Nhân viên', 'Quản lý'])
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        
        # Không cho thay đổi vai trò của chính mình
        if self.employee_id and self.employee_id == self.user_id:
            self.role_combo.setEnabled(False)
            
        form_layout.addRow('Vai trò:', self.role_combo)
        
        self.base_salary_input = QDoubleSpinBox()
        self.base_salary_input.setMaximum(999999999)
        self.base_salary_input.setPrefix('VND ')
        self.base_salary_input.setValue(8000000)
        form_layout.addRow('Lương cơ bản:', self.base_salary_input)
        
        self.phone_input = QLineEdit()
        form_layout.addRow('Điện thoại:', self.phone_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow('Email:', self.email_input)
        
        self.save_btn = QPushButton('Lưu')
        self.save_btn.clicked.connect(self.save_employee)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        main_layout.addLayout(btn_row)

        self.setLayout(main_layout)
    
    def on_ma_dinh_danh_changed(self, text):
        if len(text) == 12 and text.isdigit():
            role = 1 if self.role_combo.currentText() == 'Quản lý' else 0
            employee_id = f"{'ql' if role == 1 else 'nv'}{text[-6:]}"
            
            # Kiểm tra ID đã tồn tại chưa
            existing = self.employee_controller.get_employee_by_id(employee_id)
            if existing:
                self.id_label.setText('ĐÃ CÓ - ' + employee_id)
                self.id_label.setStyleSheet('color: #FF0000; font-weight: bold; background-color: #ffe6e6; padding: 5px; border: 1px solid #ff0000;')
            else:
                self.id_label.setText(employee_id)
                self.id_label.setStyleSheet('color: #2E86AB; font-weight: bold; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
        else:
            self.id_label.setText('Chưa có ID')
            self.id_label.setStyleSheet('color: #2E86AB; font-weight: bold; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
    
    def on_role_changed(self, role_text):
        if not self.employee_id and hasattr(self, 'ma_dinh_danh_input'):
            ma_dinh_danh = self.ma_dinh_danh_input.text()
            if len(ma_dinh_danh) == 12 and ma_dinh_danh.isdigit():
                role = 1 if role_text == 'Quản lý' else 0
                employee_id = f"{'ql' if role == 1 else 'nv'}{ma_dinh_danh[-6:]}"
                
                existing = self.employee_controller.get_employee_by_id(employee_id)
                if existing:
                    self.id_label.setText('ĐÃ CÓ - ' + employee_id)
                    self.id_label.setStyleSheet('color: #FF0000; font-weight: bold; background-color: #ffe6e6; padding: 5px; border: 1px solid #ff0000;')
                else:
                    self.id_label.setText(employee_id)
                    self.id_label.setStyleSheet('color: #2E86AB; font-weight: bold; background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;')
    
    def load_employee_data(self):
        employee = self.employee_controller.get_employee_by_id(self.employee_id)
        if employee:
            self.full_name_input.setText(employee.name)
            self.role_combo.setCurrentText('Quản lý' if employee.role == 1 else 'Nhân viên')
            self.base_salary_input.setValue(employee.base_salary)
            self.phone_input.setText(employee.phone or '')
            self.email_input.setText(employee.email or '')
    
    def save_employee(self):
        password = self.password_input.text()
        full_name = self.full_name_input.text().strip()
        role = 1 if self.role_combo.currentText() == 'Quản lý' else 0
        base_salary = self.base_salary_input.value()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        
        if not self.employee_id:
            # Thêm mới
            ma_dinh_danh = self.ma_dinh_danh_input.text().strip()
            success, message = self.employee_controller.create_employee(
                ma_dinh_danh, password, full_name, role, base_salary, phone, email
            )
        else:
            # Sửa
            success, message = self.employee_controller.update_employee(
                self.employee_id, full_name, role, base_salary, phone, email, password
            )
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, 'Lỗi', message)