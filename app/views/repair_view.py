from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QLineEdit, QTableWidgetItem, QTextEdit,
    QGroupBox, QMessageBox, QCheckBox, QHeaderView, QDateEdit
)
from PyQt6.QtCore import QDate, Qt
from app.controllers.repair_controller import RepairController
from app.controllers.customer_controller import CustomerController
from app.controllers.watch_controller import WatchController

class CreateRepairTab(QWidget):
    def __init__(self, db, controllers, user_id):
        super().__init__()
        self.db = db
        self.repair_controller: RepairController = controllers['repair']
        self.customer_controller: CustomerController = controllers['customer']
        self.watch_controller: WatchController = controllers['watch']
        self.user_id = user_id
        self.selected_customer = None
        self.selected_product = None
        self.all_customers = []
        self.filtered_customers = []
        self.all_products = []
        self.filtered_products = []
        self.current_customer_page = 1
        self.current_product_page = 1
        self.items_per_page = 10
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Left side
        left_layout = QVBoxLayout()

        # Product selection (Đồng hồ)
        product_group = QGroupBox('Chọn đồng hồ')
        product_layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Tìm kiếm đồng hồ...")
        self.product_search.textChanged.connect(self.search_products)
        search_layout.addWidget(self.product_search)
        product_layout.addLayout(search_layout)

        # Product table
        self.product_table = QTableWidget()
        self.product_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(['Chọn', 'Tên đồng hồ', 'Giá', 'Tồn kho', 'ID'])
        self.product_table.setColumnHidden(4, True)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.verticalHeader().setDefaultSectionSize(36)

        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.product_table.setColumnWidth(0, 50)

        product_layout.addWidget(self.product_table)

        # Pagination for products
        pagination_layout = QHBoxLayout()
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_product_btn = QPushButton("◀ Trước")
        self.next_product_btn = QPushButton("Sau ▶")
        self.product_page_label = QLabel("Trang 1/1")
        self.prev_product_btn.clicked.connect(self.prev_product_page)
        self.next_product_btn.clicked.connect(self.next_product_page)
        pagination_layout.addWidget(self.prev_product_btn)
        pagination_layout.addWidget(self.product_page_label)
        pagination_layout.addWidget(self.next_product_btn)
        product_layout.addLayout(pagination_layout)

        product_group.setLayout(product_layout)
        left_layout.addWidget(product_group)

        # Customer info
        customer_group = QGroupBox('Thông tin khách hàng')
        customer_layout = QVBoxLayout()

        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Tìm khách hàng theo SĐT...")
        self.customer_search.textChanged.connect(self.search_customers)
        customer_layout.addWidget(self.customer_search)

        self.customer_table = QTableWidget()
        self.customer_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.customer_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(['Chọn', 'Tên', 'Số điện thoại', 'Địa chỉ'])
        self.customer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.customer_table.setAlternatingRowColors(True)

        header = self.customer_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.customer_table.setColumnWidth(0, 50)

        customer_layout.addWidget(self.customer_table)

        # Customer Pagination
        cust_pag_layout = QHBoxLayout()
        cust_pag_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_cust_btn = QPushButton("◀ Trước")
        self.next_cust_btn = QPushButton("Sau ▶")
        self.cust_page_label = QLabel("Trang 1/1")
        self.prev_cust_btn.clicked.connect(self.prev_customer_page)
        self.next_cust_btn.clicked.connect(self.next_customer_page)
        cust_pag_layout.addWidget(self.prev_cust_btn)
        cust_pag_layout.addWidget(self.cust_page_label)
        cust_pag_layout.addWidget(self.next_cust_btn)
        customer_layout.addLayout(cust_pag_layout)

        customer_group.setLayout(customer_layout)
        left_layout.addWidget(customer_group)

        # Right side
        right_layout = QVBoxLayout()

        self.customer_label = QLabel("Khách hàng: (chưa chọn)")
        self.customer_label.setStyleSheet("font-weight: bold; color: white; margin-bottom: 4px;")
        right_layout.addWidget(self.customer_label)

        # Đồng hồ đã chọn
        self.product_label = QLabel("Đồng hồ: (chưa chọn)")
        self.product_label.setStyleSheet("font-weight: bold; color: #1976D2; margin-bottom: 8px;")
        right_layout.addWidget(self.product_label)

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
        self.load_products()
        self.load_customers()
        self.reset_form()

    def load_products(self):
        self.all_products = self.watch_controller.get_available_watches()
        self.filtered_products = self.all_products[:]
        self.current_product_page = 1
        self.display_product_page()

    def load_customers(self):
        self.all_customers = self.customer_controller.get_all_customers()
        self.filtered_customers = self.all_customers[:]
        self.current_customer_page = 1
        self.display_customer_page()

    def search_products(self):
        text = self.product_search.text().strip().lower()
        if text:
            self.filtered_products = [
                p for p in self.all_products if text in p.name.lower()
            ]
        else:
            self.filtered_products = self.all_products[:]
        self.current_product_page = 1
        self.display_product_page()

    def display_product_page(self):
        self.product_table.setRowCount(0)
        start = (self.current_product_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_items = self.filtered_products[start:end]

        self.product_table.setRowCount(len(page_items))
        for row, product in enumerate(page_items):
            checkbox = QCheckBox()
            checkbox.setStyleSheet("margin-left:10px;")
            checkbox.stateChanged.connect(lambda state, p=product, r=row: self.select_single_product(p, r))
            self.product_table.setCellWidget(row, 0, checkbox)

            self.product_table.setItem(row, 1, QTableWidgetItem(product.name))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{product.price:,.0f} VND"))
            self.product_table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))
            self.product_table.setItem(row, 4, QTableWidgetItem(str(product.id)))

        total_pages = max(1, (len(self.filtered_products) + self.items_per_page - 1) // self.items_per_page)
        self.product_page_label.setText(f"Trang {self.current_product_page}/{total_pages}")
        self.prev_product_btn.setEnabled(self.current_product_page > 1)
        self.next_product_btn.setEnabled(self.current_product_page < total_pages)

    def select_single_product(self, product, row):
        """Chỉ cho phép chọn 1 đồng hồ duy nhất"""
        for r in range(self.product_table.rowCount()):
            checkbox = self.product_table.cellWidget(r, 0)
            if checkbox and r != row:
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)

        checkbox = self.product_table.cellWidget(row, 0)
        if checkbox and checkbox.isChecked():
            self.selected_product = {'id': product.id, 'name': product.name}
            self.product_label.setText(f"Đồng hồ: {product.name}")
        else:
            self.selected_product = None
            self.product_label.setText("Đồng hồ: (chưa chọn)")

    def next_product_page(self):
        total_pages = (len(self.filtered_products) + self.items_per_page - 1) // self.items_per_page
        if self.current_product_page < total_pages:
            self.current_product_page += 1
            self.display_product_page()

    def prev_product_page(self):
        if self.current_product_page > 1:
            self.current_product_page -= 1
            self.display_product_page()

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
            checkbox.stateChanged.connect(lambda state, c=customer, r=row: self.select_single_customer(c, r))
            self.customer_table.setCellWidget(row, 0, checkbox)
            self.customer_table.setItem(row, 1, QTableWidgetItem(customer.name))
            self.customer_table.setItem(row, 2, QTableWidgetItem(customer.phone or ''))
            self.customer_table.setItem(row, 3, QTableWidgetItem(customer.address or ''))
        
        total_pages = max(1, (len(self.filtered_customers) + self.items_per_page - 1) // self.items_per_page)
        self.cust_page_label.setText(f"Trang {self.current_customer_page}/{total_pages}")
        
        self.prev_cust_btn.setEnabled(self.current_customer_page > 1)
        self.next_cust_btn.setEnabled(self.current_customer_page < total_pages)

    def select_single_customer(self, customer, row):
        """Đảm bảo chỉ chọn 1 khách hàng duy nhất"""
        for r in range(self.customer_table.rowCount()):
            checkbox = self.customer_table.cellWidget(r, 0)
            if checkbox and r != row:
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)

        checkbox = self.customer_table.cellWidget(row, 0)
        if checkbox and checkbox.isChecked():
            self.selected_customer = {'name': customer.name, 'phone': customer.phone}
            self.customer_label.setText(f"Khách hàng: {customer.name}")
        else:
            self.selected_customer = None
            self.customer_label.setText("Khách hàng: (chưa chọn)")

    def next_customer_page(self):
        total_pages = (len(self.filtered_customers) + self.items_per_page - 1) // self.items_per_page
        if self.current_customer_page < total_pages:
            self.current_customer_page += 1
            self.display_customer_page()

    def prev_customer_page(self):
        if self.current_customer_page > 1:
            self.current_customer_page -= 1
            self.display_customer_page()

    def create_repair_order(self):
        if not self.selected_customer:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn khách hàng!')
            return
        
        if not self.selected_product:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn đồng hồ!')
            return
        
        if not self.issue_desc_input.toPlainText().strip():
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập mô tả lỗi!')
            return

        issue_desc = self.issue_desc_input.toPlainText()
        estimated_date = self.estimated_completion_input.date()
        today = QDate.currentDate()
        
        # Chặn ngày dự kiến hoàn thành trước ngày hôm nay
        if estimated_date < today:
            QMessageBox.warning(self, 'Lỗi', 'Ngày dự kiến hoàn thành không được trước ngày hôm nay!')
            return
        
        estimated = estimated_date.toString('yyyy-MM-dd')
        product_id = str(self.selected_product['id'])

        success, message = self.repair_controller.create_repair_order(
            self.selected_customer['phone'], self.user_id, issue_desc, estimated, product_id
        )
        
        if success:
            QMessageBox.information(self, 'Thành công', message)
            self.load_data()
        else:
            QMessageBox.warning(self, 'Lỗi', message)

    def reset_form(self):
        self.selected_customer = None
        self.selected_product = None
        self.customer_label.setText("Khách hàng: (chưa chọn)")
        self.product_label.setText("Đồng hồ: (chưa chọn)")
        self.issue_desc_input.clear()
        self.estimated_completion_input.setDate(QDate.currentDate().addDays(7))
        self.customer_search.clear()
        self.product_search.clear()