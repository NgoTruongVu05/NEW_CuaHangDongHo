from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                             QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout,
                             QSpacerItem, QSizePolicy)

class CustomerDialog(QDialog):
    def __init__(self, db, customer_controller, customer_id=None):
        super().__init__()
        self.db = db
        self.customer_controller = customer_controller
        self.customer_id = customer_id
        self.init_ui()
        if customer_id:
            self.load_customer_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa khách hàng' if not self.customer_id else 'Sửa khách hàng')
        self.setFixedSize(400, 250)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow('Tên khách hàng:', self.name_input)
        
        self.phone_input = QLineEdit()
        form_layout.addRow('Điện thoại:*', self.phone_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow('Email:', self.email_input)
        
        self.address_input = QLineEdit()
        form_layout.addRow('Địa chỉ:', self.address_input)

        self.save_btn = QPushButton('Lưu')
        self.save_btn.clicked.connect(self.save_customer)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        main_layout.addLayout(btn_row)
        
        self.setLayout(main_layout)
    
    def load_customer_data(self):
        customer = self.customer_controller.get_customer_by_id(self.customer_id)
        if customer:
            self.name_input.setText(customer.name)
            self.phone_input.setText(customer.phone or '')
            self.email_input.setText(customer.email or '')
            self.address_input.setText(customer.address or '')
    
    def save_customer(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()
        
        if self.customer_id:
            # Update existing customer
            success, message = self.customer_controller.update_customer(
                self.customer_id, name, phone, email, address
            )
        else:
            # Create new customer
            success, message = self.customer_controller.create_customer(
                name, phone, email, address
            )
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, 'Lỗi', message)