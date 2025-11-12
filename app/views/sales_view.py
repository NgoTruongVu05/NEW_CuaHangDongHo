from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QLineEdit, QTableWidgetItem, QSpinBox,
    QGroupBox, QMessageBox, QCheckBox, QHeaderView
)
from PyQt6.QtCore import QDate, Qt
from app.controllers.sales_controller import SalesController
from app.controllers.customer_controller import CustomerController
from app.controllers.watch_controller import WatchController

class CreateInvoiceTab(QWidget):
    def __init__(self, db, controllers, user_id):
        super().__init__()
        self.db = db
        self.sales_controller: SalesController = controllers['sales']
        self.customer_controller: CustomerController = controllers['customer']
        self.watch_controller: WatchController = controllers['watch']
        self.user_id = user_id
        self.cart = []
        self.selected_customer = None
        self.all_products = []
        self.filtered_products = []
        self.all_customers = []
        self.filtered_customers = []
        self.current_page = 1
        self.customer_current_page = 1
        self.items_per_page = 10
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Left side
        left_layout = QVBoxLayout()

        # Product selection
        product_group = QGroupBox('Chọn sản phẩm')
        product_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Tìm kiếm sản phẩm...")
        self.product_search.textChanged.connect(self.search_products)
        search_layout.addWidget(self.product_search)
        product_layout.addLayout(search_layout)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(['Chọn', 'Tên', 'Giá', 'Tồn kho', 'Số lượng', 'ID'])
        self.product_table.setColumnHidden(5, True)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setAlternatingRowColors(True)

        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.product_table.setColumnWidth(0, 50)

        product_layout.addWidget(self.product_table)

        add_to_cart_btn = QPushButton('Thêm vào giỏ')
        add_to_cart_btn.setStyleSheet("""
            QPushButton {
                background-color: #388E3C;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
        """)
        add_to_cart_btn.clicked.connect(self.add_selected_products_to_cart)
        product_layout.addWidget(add_to_cart_btn)

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

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(['Sản phẩm', 'Đơn giá', 'Số lượng', 'Thành tiền', 'Hành động'])

        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        right_layout.addWidget(self.cart_table)

        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel('Tổng cộng:'))
        self.total_label = QLabel('0 VND')
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()

        create_invoice_btn = QPushButton('Tạo hóa đơn')
        create_invoice_btn.setStyleSheet("""
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
        create_invoice_btn.clicked.connect(self.create_invoice)
        total_layout.addWidget(create_invoice_btn)
        right_layout.addLayout(total_layout)

        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 1)
        self.setLayout(layout)

    def load_data(self):
        self.reset_form()
        self.load_products()
        self.load_customers()

    def load_products(self):
        self.all_products = self.watch_controller.get_available_watches()
        self.filtered_products = self.all_products[:]
        self.display_products()

    def load_customers(self):
        self.all_customers = self.customer_controller.get_all_customers()
        self.filtered_customers = self.all_customers[:]
        self.display_customers()

    def search_products(self):
        search_text = self.product_search.text().strip().lower()
        if search_text:
            self.filtered_products = [
                p for p in self.all_products
                if search_text in p.name.lower()
            ]
        else:
            self.filtered_products = self.all_products[:]
        self.display_products()

    def search_customers(self):
        search_text = self.customer_search.text().strip()
        if search_text:
            self.filtered_customers = [
                c for c in self.all_customers
                if search_text in (c.phone or '')
            ]
        else:
            self.filtered_customers = self.all_customers[:]
        self.display_customers()

    def display_products(self):
        self.product_table.setRowCount(len(self.filtered_products))
        
        for row, product in enumerate(self.filtered_products):
            checkbox = QCheckBox()
            checkbox.setStyleSheet("margin-left:10px;")
            self.product_table.setCellWidget(row, 0, checkbox)

            self.product_table.setItem(row, 1, QTableWidgetItem(product.name))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{product.price:,.0f} VND"))
            self.product_table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))

            spin = QSpinBox()
            spin.setRange(1, product.quantity)
            spin.setValue(1)
            self.product_table.setCellWidget(row, 4, spin)

            self.product_table.setItem(row, 5, QTableWidgetItem(str(product.id)))

    def display_customers(self):
        self.customer_table.setRowCount(len(self.filtered_customers))
        
        for row, customer in enumerate(self.filtered_customers):
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

    def add_selected_products_to_cart(self):
        selected_products = []
        
        for row in range(self.product_table.rowCount()):
            checkbox = self.product_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                product_id = int(self.product_table.item(row, 5).text())
                name = self.product_table.item(row, 1).text()
                price = float(self.product_table.item(row, 2).text().replace(' VND', '').replace(',', ''))
                spin = self.product_table.cellWidget(row, 4)
                quantity = spin.value()

                selected_products.append({
                    'id': product_id,
                    'name': name,
                    'price': price,
                    'quantity': quantity
                })

        if not selected_products:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất một sản phẩm!")
            return

        # Thêm vào giỏ hàng
        for product in selected_products:
            existing = next((item for item in self.cart if item['id'] == product['id']), None)
            if existing:
                existing['quantity'] += product['quantity']
            else:
                self.cart.append(product)

        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart))
        total = 0

        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:,.0f} VND"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            
            total_item = item['price'] * item['quantity']
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{total_item:,.0f} VND"))
            total += total_item

            remove_btn = QPushButton("Xóa")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 11px;
                    margin: 0 3px;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
            """)
            remove_btn.clicked.connect(lambda _, r=row: self.remove_item_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_btn)

        self.total_label.setText(f"{total:,.0f} VND")

    def remove_item_from_cart(self, row):
        if 0 <= row < len(self.cart):
            item_name = self.cart[row]['name']
            reply = QMessageBox.question(
                self, "Xác nhận",
                f"Bạn có chắc muốn xóa sản phẩm '{item_name}' khỏi giỏ hàng?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self.cart[row]
                self.update_cart_display()

    def create_invoice(self):
        if not self.cart:
            QMessageBox.warning(self, 'Lỗi', 'Giỏ hàng trống!')
            return

        if not self.selected_customer:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng chọn khách hàng!')
            return
        
        # Chuyển đổi cart items sang định dạng phù hợp
        items = [
            {
                'product_id': item['id'],
                'quantity': item['quantity'],
                'price': item['price']
            }
            for item in self.cart
        ]
        
        success, message, invoice_id = self.sales_controller.create_sales_invoice(
            self.selected_customer['phone'], self.user_id, items
        )
        
        if success:
            QMessageBox.information(self, 'Thành công', message)
            self.load_data()
        else:
            QMessageBox.warning(self, 'Lỗi', message)

    def reset_form(self):
        self.cart.clear()
        self.selected_customer = None
        self.product_search.clear()
        self.customer_search.clear()
        self.update_cart_display()
        self.customer_label.setText("Khách hàng: (chưa chọn)")