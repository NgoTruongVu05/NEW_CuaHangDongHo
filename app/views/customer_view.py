from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QLineEdit, QLabel, QComboBox)
from PyQt6.QtCore import Qt
from app.controllers.customer_controller import CustomerController

class CustomerManagementTab(QWidget):
    def __init__(self, db, controllers, user_role):
        super().__init__()
        self.db = db
        self.customer_controller: CustomerController = controllers['customer']
        self.user_role = user_role
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()

        add_btn = QPushButton('Thêm khách hàng')
        add_btn.clicked.connect(self.add_customer)
        controls_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Search area
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel('Tìm kiếm:'))
        
        self.search_type = QComboBox()
        self.search_type.addItems(['Tất cả', 'Tên', 'Số điện thoại'])
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        search_layout.addWidget(self.search_type)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
        self.search_input.textChanged.connect(self.search_customers)
        search_layout.addWidget(self.search_input)
        
        # Clear search button
        clear_search_btn = QPushButton('Xóa tìm kiếm')
        clear_search_btn.clicked.connect(self.clear_search)
        clear_search_btn.setStyleSheet('''
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        ''')
        search_layout.addWidget(clear_search_btn)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Tên', 'Điện thoại', 'Email', 'Địa chỉ', 'Hành động'])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def on_search_type_changed(self, search_type):
        if search_type == 'Tất cả':
            self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
        elif search_type == 'Tên':
            self.search_input.setPlaceholderText('Nhập tên khách hàng...')
        elif search_type == 'Số điện thoại':
            self.search_input.setPlaceholderText('Nhập số điện thoại...')
        
        self.search_customers()
    
    def search_customers(self):
        search_text = self.search_input.text().strip()
        search_type = self.search_type.currentText()
        
        customers = self.customer_controller.search_customers(search_type, search_text)
        self.display_customers(customers)
    
    def clear_search(self):
        self.search_type.setCurrentText('Tất cả')
        self.search_input.clear()
        self.load_data()
    
    def load_data(self):
        customers = self.customer_controller.get_all_customers()
        self.display_customers(customers)
    
    def display_customers(self, customers):
        self.table.setRowCount(0)
        self.table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            # ID, Tên, Điện thoại, Email, Địa chỉ
            self.table.setItem(row, 0, QTableWidgetItem(str(customer.id)))
            self.table.setItem(row, 1, QTableWidgetItem(customer.name))
            self.table.setItem(row, 2, QTableWidgetItem(customer.phone or ''))
            self.table.setItem(row, 3, QTableWidgetItem(customer.email or ''))
            self.table.setItem(row, 4, QTableWidgetItem(customer.address or ''))
            
            # Nút hành động
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)

            edit_btn = QPushButton('Sửa')
            edit_btn.setStyleSheet('''
                QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 11px;
                    margin-right: 2px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
            ''')
            edit_btn.clicked.connect(lambda checked, cid=customer.id: self.edit_customer(cid))
            action_layout.addWidget(edit_btn)
            
            if self.user_role == 1:  # Chỉ admin được xóa
                delete_btn = QPushButton('Xóa')
                delete_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        border: none;
                        margin: 0 3px;
                        border-radius: 3px;
                        padding: 3px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                ''')
                delete_btn.clicked.connect(lambda checked, cid=customer.id: self.delete_customer(cid))
                action_layout.addWidget(delete_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 5, action_widget)

        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
    def add_customer(self):
        from .dialogs.customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.db, self.customer_controller)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm khách hàng mới!')
    
    def edit_customer(self, customer_id):
        from .dialogs.customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.db, self.customer_controller, customer_id)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật khách hàng!')
    
    def delete_customer(self, customer_id):
        customer = self.customer_controller.get_customer_by_id(customer_id)
        if not customer:
            return
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa khách hàng "{customer.name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.customer_controller.delete_customer(customer_id)
            if success:
                self.load_data()
                QMessageBox.information(self, 'Thành công', message)
            else:
                QMessageBox.warning(self, 'Lỗi', message)