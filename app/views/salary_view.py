from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QSpinBox, QLabel, QGroupBox)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QFont
from app.controllers.salary_controller import SalaryController

class SalaryManagementTab(QWidget):
    def __init__(self, db, controllers, user_role):
        super().__init__()
        self.db = db
        self.salary_controller: SalaryController = controllers['salary']
        self.user_role = user_role
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Filter section
        filter_group = QGroupBox('Lọc dữ liệu')
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel('Tháng:'))
        self.month_filter = QSpinBox()
        self.month_filter.setRange(1, 12)
        self.month_filter.setValue(QDate.currentDate().month())
        self.month_filter.valueChanged.connect(self.load_data)
        filter_layout.addWidget(self.month_filter)
        
        filter_layout.addWidget(QLabel('Năm:'))
        self.year_filter = QSpinBox()
        self.year_filter.setRange(2020, 2030)
        self.year_filter.setValue(QDate.currentDate().year())
        self.year_filter.valueChanged.connect(self.load_data)
        filter_layout.addWidget(self.year_filter)
        
        filter_layout.addStretch()
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'ID NV', 'Họ tên', 'Vai trò', 'Lương cơ bản', 'Doanh số', 'Hoa hồng 0.5%', 'Tổng lương'
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)
    
    def load_data(self):
        month = self.month_filter.value()
        year = self.year_filter.value()
        
        salaries = self.salary_controller.calculate_all_salaries(month, year)
        self.display_salaries(salaries)
    
    def display_salaries(self, salaries):
        self.table.setRowCount(len(salaries))
        
        for row, salary_info in enumerate(salaries):
            self.table.setItem(row, 0, QTableWidgetItem(salary_info['employee_id']))
            self.table.setItem(row, 1, QTableWidgetItem(salary_info['employee_name']))
            
            # Get role from employee service (this would need to be injected)
            role_item = QTableWidgetItem("Nhân viên")  # Default
            self.table.setItem(row, 2, role_item)
            
            self.table.setItem(row, 3, QTableWidgetItem(f"{salary_info['base_salary']:,.0f} VND"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{salary_info['total_sales']:,.0f} VND"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{salary_info['commission']:,.0f} VND"))
            
            # Total salary - với style đặc biệt
            total_salary_item = QTableWidgetItem(f"{salary_info['total_salary']:,.0f} VND")
            total_salary_item.setForeground(QColor('#27AE60'))
            font = QFont()
            font.setBold(True)
            total_salary_item.setFont(font)
            self.table.setItem(row, 6, total_salary_item)
            
            # Đặt style cho các ô không được chọn/chỉnh sửa
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEditable)
        
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)