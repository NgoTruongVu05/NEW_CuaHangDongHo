from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QLineEdit, QTableWidgetItem, QTextEdit,
    QGroupBox, QMessageBox, QCheckBox, QHeaderView, QDateEdit
)
from PyQt6.QtCore import QDate, Qt
from app.controllers.repair_controller import RepairController
from app.controllers.customer_controller import CustomerController

class CreateRepairTab(QWidget):
    def __init__(self, db, controllers, user_id):
        super().__init__()
        self.db = db
        self.repair_controller: RepairController = controllers['repair']
        self.customer_controller: CustomerController = controllers['customer']
        self.user_id = user_id
        self.selected_customer = None
        self.all_customers = []
        self.filtered_customers = []
        self.current_customer_page = 1
        self.items_per_page = 10
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Left side
        left_layout = QVBoxLayout()

        # Customer info
        customer_group = QGroupBox('Thông tin khách hàng')
        customer_layout = QVBoxLayout()

        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Tìm khách hàng theo SĐT...")
        self.customer_search.textChanged.connect(self.search_customers)
        customer_layout.addWidget(self.customer_search)

        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(['Chọn', 'Tên', 'Số điện thoại', 'Địa chỉ'])
        self.customer_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.customer_table.setAlternatingRowColors(True)

        header = self.customer_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.customer_table.setColumnWidth(0, 50)

        customer_layout.addWidget(self.customer_table)

        customer_group.setLayout(customer_layout)
        left_layout.addWidget(customer_group)

        # Right side
        right_layout = QVBoxLayout()

        self.customer_label = QLabel("Khách hàng: (chưa chọn)")
        self.customer_label.setStyleSheet("font-weight: bold; color: white; margin-bottom: 4px;")
        right_layout.addWidget(self.customer_label)

        # Repair details
        details_group = QGroupBox("Mô tả lỗi")
        details_layout = QVBoxLayout()

        # Issue description
        issue_layout = QHBoxLayout()
        self.issue_desc_input = QTextEdit()
        self.issue_desc_input.setPlaceholderText("Nhập mô tả chi tiết về lỗi của đồng hồ...")
        issue_layout.addWidget(self.issue_desc_input)
        details_layout.addLayout(issue_layout)

        # Estimated completion
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Dự kiến hoàn thành:"))
        self.estimated_completion_input = QDateEdit()
        self.estimated_completion_input.setDate(QDate.currentDate().addDays(7))
        self.estimated_completion_input.setCalendarPopup(True)
        self.estimated_completion_input.setDisplayFormat("dd/MM/yyyy")
        date_layout.addWidget(self.estimated_completion_input)
        details_layout.addLayout(date_layout)

        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)

        # Buttons
        total_layout = QHBoxLayout()
        total_layout.addStretch()

        create_btn = QPushButton('Tạo đơn sửa chữa')
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #388E3C;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
        """)
        create_btn.clicked.connect(self.create_repair_order)
        total_layout.addWidget(create_btn)

        right_layout.addLayout(total_layout)

        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 1)
        self.setLayout(layout)

    def load_data(self):
        self.load_customers()
        self.reset_form()

    def load_customers(self):
        self.all_customers = self.customer_controller.get_all_customers()
        self.filtered_customers = self.all_customers[:]
        self.current_customer_page = 1
        self.display_customer_page()

    def search_customers(self):
        text = self.customer_search.text().strip()
        if text:
            self.filtered_customers = [
                c for c in self.all_customers 
                if text in (c.phone or '')
            ]
        else:
            self.filtered_customers = self.all_customers[:]
        
        self.current_customer_page = 1
        self.display_customer_page()

    def display_customer_page(self):
        self.customer_table.setRowCount(0)
        start = (self.current_customer_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_items = self.filtered_customers[start:end]

        self.customer_table.setRowCount(len(page_items))
        for row, customer in enumerate(page_items):
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, r=row: self.select_single_customer(r))
            self.customer_table.setCellWidget(row, 0, checkbox)
            self.customer_table.setItem(row, 1, QTableWidgetItem(customer.name))
            self.customer_table.setItem(row, 2, QTableWidgetItem(customer.phone or ''))
            self.customer_table.setItem(row, 3, QTableWidgetItem(customer.address or ''))

    def select_single_customer(self, selected_row):
        for row in range(self.customer_table.rowCount()):
            checkbox = self.customer_table.cellWidget(row, 0)
            if row != selected_row:
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)

        checkbox = self.customer_table.cellWidget(selected_row, 0)
        if checkbox.isChecked():
            name = self.customer_table.item(selected_row, 1).text()
            phone = self.customer_table.item(selected_row, 2).text()
            self.selected_customer = {'name': name, 'phone': phone}
            self.customer_label.setText(f"Khách hàng: {name}")
        else:
            self.selected_customer = None
            self.customer_label.setText("Khách hàng: (chưa chọn)")

    def create_repair_order(self):
        if not self.selected_customer:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn khách hàng!')
            return
        
        if not self.issue_desc_input.toPlainText().strip():
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập mô tả lỗi!')
            return

        issue_desc = self.issue_desc_input.toPlainText()
        estimated = self.estimated_completion_input.date().toString('yyyy-MM-dd')

        success, message = self.repair_controller.create_repair_order(
            self.selected_customer['phone'], self.user_id, issue_desc, estimated
        )
        
        if success:
            QMessageBox.information(self, 'Thành công', message)
            self.load_data()
        else:
            QMessageBox.warning(self, 'Lỗi', message)

    def reset_form(self):
        self.selected_customer = None
        self.customer_label.setText("Khách hàng: (chưa chọn)")
        self.issue_desc_input.clear()
        self.estimated_completion_input.setDate(QDate.currentDate().addDays(7))
        self.customer_search.clear()