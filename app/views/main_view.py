from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTabWidget, QLabel, QMessageBox)
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self, user_info, db, controllers):
        super().__init__()
        self.user_info = user_info
        self.db = db
        self.controllers = controllers
        self.user_role = user_info[4]  # vaitro ở index 4
        self.init_ui()
    
    def init_ui(self):
        # Hiển thị thông tin người dùng
        user_id = self.user_info[0]  # id ở index 0
        role_text = "Quản lý" if self.user_role == 1 else "Nhân viên"
        self.setWindowTitle(f'Hệ thống quản lý cửa hàng đồng hồ - {user_id} ({role_text})')
        self.setGeometry(100, 100, 1200, 700)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header với thông tin user và nút đăng xuất
        header_layout = QHBoxLayout()
        
        user_info_text = f'{user_id} ({role_text})'
        self.user_info_label = QLabel(user_info_text)
        self.user_info_label.setStyleSheet('font-weight: bold; color: #2E86AB;')
        header_layout.addWidget(self.user_info_label)
        
        header_layout.addStretch()
        
        self.logout_btn = QPushButton('Đăng xuất')
        self.logout_btn.clicked.connect(self.logout)
        self.logout_btn.setStyleSheet('''
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        ''')
        header_layout.addWidget(self.logout_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Khởi tạo các tab
        self.init_tabs()
        
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def init_tabs(self):
        """Khởi tạo các tab dựa trên vai trò người dùng"""
        from .sales_view import CreateInvoiceTab
        from .repair_view import CreateRepairTab
        from .customer_view import CustomerManagementTab
        from .invoice_view import InvoiceManagementTab
        from .statistics_view import StatisticsTab
        from .watch_view import ProductManagementTab
        from .brand_view import BrandManagementTab
        from .employee_view import EmployeeManagementTab
        from .salary_view import SalaryManagementTab
        
        # Tab bán hàng và sửa chữa (luôn hiển thị)
        self.create_invoice_tab = CreateInvoiceTab(self.db, self.controllers, self.user_info[0])
        self.create_repair_tab = CreateRepairTab(self.db, self.controllers, self.user_info[0])
        self.tabs.addTab(self.create_invoice_tab, "Bán hàng")
        self.tabs.addTab(self.create_repair_tab, "Sửa chữa")
        
        # Các tab quản lý cơ bản
        self.customer_tab = CustomerManagementTab(self.db, self.controllers, self.user_role)
        self.invoice_tab = InvoiceManagementTab(self.db, self.controllers, self.user_role)
        self.statistics_tab = StatisticsTab(self.db, self.controllers, self.user_role)
        
        self.tabs.addTab(self.customer_tab, "Quản lý khách hàng")
        self.tabs.addTab(self.invoice_tab, "Quản lý hóa đơn")
        self.tabs.addTab(self.statistics_tab, "Thống kê")
        
        # Chỉ thêm tab quản lý cho admin
        if self.user_role == 1:
            self.product_tab = ProductManagementTab(self.db, self.controllers, self.user_role)
            self.brand_tab = BrandManagementTab(self.db, self.controllers, self.user_role)
            self.employee_tab = EmployeeManagementTab(self.db, self.controllers, self.user_role, self.user_info[0])
            self.salary_tab = SalaryManagementTab(self.db, self.controllers, self.user_role)
            
            self.tabs.addTab(self.product_tab, "Quản lý sản phẩm")
            self.tabs.addTab(self.brand_tab, "Quản lý thương hiệu")
            self.tabs.addTab(self.employee_tab, "Quản lý nhân viên")
            self.tabs.addTab(self.salary_tab, "Quản lý lương")
    
    def on_tab_changed(self, index):
        """Handle tab changed event - reload data when tab is selected"""
        current_tab = self.tabs.widget(index)
        
        # Gọi phương thức load_data nếu tab có phương thức này
        if hasattr(current_tab, 'load_data'):
            QTimer.singleShot(100, current_tab.load_data)
    
    def logout(self):
        reply = QMessageBox.question(self, 'Xác nhận', 
                                   'Bạn có chắc muốn đăng xuất?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()