from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QComboBox, QLineEdit, QLabel)
from PyQt6.QtCore import Qt
from app.controllers.employee_controller import EmployeeController

class EmployeeManagementTab(QWidget):
    def __init__(self, db, controllers, user_role, user_id):
        super().__init__()
        self.db = db
        self.employee_controller: EmployeeController = controllers['employee']
        self.user_role = user_role
        self.user_id = user_id
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_btn = QPushButton('Thêm nhân viên')
        add_btn.clicked.connect(self.add_employee)
        controls_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Search area
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel('Tìm kiếm theo:'))
        
        self.search_type = QComboBox()
        self.search_type.addItems(['Tất cả', 'ID', 'Mã ĐD', 'Họ tên', 'Vai trò'])
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        search_layout.addWidget(self.search_type)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
        self.search_input.textChanged.connect(self.search_employees)
        search_layout.addWidget(self.search_input)
        
        # Dropdown cho tìm kiếm theo vai trò
        self.role_search_combo = QComboBox()
        self.role_search_combo.addItems(['Quản lý', 'Nhân viên'])
        self.role_search_combo.currentTextChanged.connect(self.search_employees)
        self.role_search_combo.setVisible(False)
        search_layout.addWidget(self.role_search_combo)
        
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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Mã ĐD', 'Họ tên', 'Vai trò', 'Lương cơ bản', 'Điện thoại', 'Email', 'Hành động'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def on_search_type_changed(self, search_type):
        if search_type == 'Vai trò':
            self.search_input.setVisible(False)
            self.role_search_combo.setVisible(True)
            self.search_employees()
        else:
            self.search_input.setVisible(True)
            self.role_search_combo.setVisible(False)
            
            if search_type == 'Tất cả':
                self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
            elif search_type == 'ID':
                self.search_input.setPlaceholderText('Nhập ID nhân viên...')
            elif search_type == 'Mã ĐD':
                self.search_input.setPlaceholderText('Nhập mã định danh...')
            elif search_type == 'Họ tên':
                self.search_input.setPlaceholderText('Nhập họ tên nhân viên...')
            elif search_type == 'Số điện thoại':
                self.search_input.setPlaceholderText('Nhập số điện thoại...')
            elif search_type == 'Email':
                self.search_input.setPlaceholderText('Nhập email...')
            
            self.search_employees()
    
    def search_employees(self):
        search_type = self.search_type.currentText()
        search_text = self.search_input.text().strip()
        
        if search_type == 'Vai trò':
            search_text = self.role_search_combo.currentText()
        
        employees = self.employee_controller.search_employees(search_type, search_text)
        self.display_employees(employees)
    
    def clear_search(self):
        self.search_type.setCurrentText('Tất cả')
        self.search_input.clear()
        self.role_search_combo.setCurrentText('Quản lý')
        self.load_data()
    
    def load_data(self):
        employees = self.employee_controller.get_all_employees()
        self.display_employees(employees)
    
    def display_employees(self, employees):
        self.table.setRowCount(0)
        self.table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            self.table.setItem(row, 0, QTableWidgetItem(employee.id))
            self.table.setItem(row, 1, QTableWidgetItem(employee.ma_dinh_danh))
            self.table.setItem(row, 2, QTableWidgetItem(employee.name))
            self.table.setItem(row, 3, QTableWidgetItem(employee.get_role_text()))
            self.table.setItem(row, 4, QTableWidgetItem(f"{employee.base_salary:,.0f} VND"))
            self.table.setItem(row, 5, QTableWidgetItem(employee.phone or ''))
            self.table.setItem(row, 6, QTableWidgetItem(employee.email or ''))
            
            # Nút hành động
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)

            # Xác định có được phép sửa không
            can_edit = True
            # Không được sửa quản lý khác (trừ khi là chính mình)
            if employee.role == 1 and employee.id != self.user_id:
                can_edit = False
            
            if can_edit:
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
                edit_btn.clicked.connect(lambda checked, eid=employee.id: self.edit_employee(eid))
                action_layout.addWidget(edit_btn)

            # Chỉ cho phép xóa nhân viên (không phải quản lý) và chỉ khi có quyền sửa
            if employee.role == 0 and can_edit:  # Nhân viên và có quyền sửa
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
                delete_btn.clicked.connect(lambda checked, eid=employee.id: self.delete_employee(eid))
                action_layout.addWidget(delete_btn)
            
            # Nếu không có quyền sửa, hiển thị thông báo
            if not can_edit:
                no_permission_label = QLabel('Không thể chỉnh sửa')
                no_permission_label.setStyleSheet('color: #95A5A6; font-style: italic;')
                action_layout.addWidget(no_permission_label)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 7, action_widget)
        
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
    def add_employee(self):
        from .dialogs.employee_dialog import EmployeeDialog
        dialog = EmployeeDialog(self.db, self.employee_controller)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm nhân viên mới!')
    
    def edit_employee(self, employee_id):
        from .dialogs.employee_dialog import EmployeeDialog
        dialog = EmployeeDialog(self.db, self.employee_controller, employee_id, self.user_id, self.user_role)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật nhân viên!')
    
    def delete_employee(self, employee_id):
        employee = self.employee_controller.get_employee_by_id(employee_id)
        if not employee:
            return
        
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   f'Bạn có chắc muốn xóa nhân viên "{employee.name}"?')
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.employee_controller.delete_employee(employee_id)
            if success:
                self.load_data()
                QMessageBox.information(self, 'Thành công', message)
            else:
                QMessageBox.warning(self, 'Lỗi', message)