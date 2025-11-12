from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox,
                             QHeaderView, QHBoxLayout, QLabel, QDialog,
                             QLineEdit, QDateEdit, QComboBox, QTextEdit)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from app.controllers.invoice_controller import InvoiceController
from app.controllers.repair_controller import RepairController

def _format_date(val: str) -> str:
    if not val:
        return ''
    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d'):
        try:
            return datetime.strptime(val, fmt).strftime('%d/%m/%Y')
        except Exception:
            continue
    return val

class InvoiceManagementTab(QWidget):
    def __init__(self, db, controllers, user_role):
        super().__init__()
        self.db = db
        self.invoice_controller: InvoiceController = controllers['invoice']
        self.repair_controller: RepairController = controllers['repair']
        self.user_role = user_role
        self.current_mode = "invoices"
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        self.invoice_btn = QPushButton('Hóa đơn bán hàng')
        self.invoice_btn.setFixedHeight(35)
        self.invoice_btn.clicked.connect(lambda: self.switch_mode("invoices"))
        
        self.repair_btn = QPushButton('Hóa đơn sửa chữa')
        self.repair_btn.setFixedHeight(35)
        self.repair_btn.clicked.connect(lambda: self.switch_mode("repairs"))
        
        controls_layout.addWidget(self.invoice_btn)
        controls_layout.addWidget(self.repair_btn)
        controls_layout.addStretch()
        
        refresh_btn = QPushButton('Làm mới')
        refresh_btn.setFixedHeight(35)
        refresh_btn.setStyleSheet('''
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        ''')
        refresh_btn.clicked.connect(self.load_data)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Search layout for invoices
        self.invoice_search_layout = QHBoxLayout()
        self.invoice_search_layout.addWidget(QLabel('Loại tìm kiếm:'))
        
        self.search_type = QComboBox()
        self.search_type.addItems(['Tất cả', 'ID hóa đơn', 'Tên khách hàng', 'Tên nhân viên'])
        self.search_type.currentTextChanged.connect(self.on_search_type_changed)
        self.invoice_search_layout.addWidget(self.search_type)
        
        self.invoice_search_layout.addWidget(QLabel('Từ khóa:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')
        self.search_input.textChanged.connect(self.search_data)
        self.invoice_search_layout.addWidget(self.search_input)
        
        self.invoice_search_layout.addWidget(QLabel('Từ ngày:'))
        self.invoice_from_date = QDateEdit()
        self.invoice_from_date.setDate(QDate.currentDate().addMonths(-1))
        self.invoice_from_date.setCalendarPopup(True)
        self.invoice_from_date.setDisplayFormat('dd/MM/yyyy')
        self.invoice_from_date.dateChanged.connect(self.load_data)
        self.invoice_search_layout.addWidget(self.invoice_from_date)
        
        self.invoice_search_layout.addWidget(QLabel('Đến ngày:'))
        self.invoice_to_date = QDateEdit()
        self.invoice_to_date.setDate(QDate.currentDate())
        self.invoice_to_date.setCalendarPopup(True)
        self.invoice_to_date.setDisplayFormat('dd/MM/yyyy')
        self.invoice_to_date.dateChanged.connect(self.load_data)
        self.invoice_search_layout.addWidget(self.invoice_to_date)

        self.invoice_search_layout.addStretch()
        
        clear_invoice_btn = QPushButton('Xóa tìm kiếm')
        clear_invoice_btn.clicked.connect(self.clear_search)
        clear_invoice_btn.setStyleSheet('''
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
        self.invoice_search_layout.addWidget(clear_invoice_btn)
        
        # Search layout for repairs
        self.repair_search_layout = QHBoxLayout()
        self.repair_search_layout.addWidget(QLabel('Tìm theo tên khách hàng:'))
        self.repair_search_input = QLineEdit()
        self.repair_search_input.setPlaceholderText('Nhập tên khách hàng cần tìm...')
        self.repair_search_input.textChanged.connect(self.load_data)
        self.repair_search_layout.addWidget(self.repair_search_input)
        
        self.repair_search_layout.addWidget(QLabel('Từ ngày:'))
        self.repair_date_from = QDateEdit()
        self.repair_date_from.setDate(QDate.currentDate().addMonths(-1))
        self.repair_date_from.setCalendarPopup(True)
        self.repair_date_from.setDisplayFormat('dd/MM/yyyy')
        self.repair_date_from.dateChanged.connect(self.load_data)
        self.repair_search_layout.addWidget(self.repair_date_from)
        
        self.repair_search_layout.addWidget(QLabel('Đến ngày:'))
        self.repair_date_to = QDateEdit()
        self.repair_date_to.setDate(QDate.currentDate())
        self.repair_date_to.setCalendarPopup(True)
        self.repair_date_to.setDisplayFormat('dd/MM/yyyy')
        self.repair_date_to.dateChanged.connect(self.load_data)
        self.repair_search_layout.addWidget(self.repair_date_to)
        
        clear_repair_btn = QPushButton('Xóa tìm kiếm')
        clear_repair_btn.clicked.connect(self.clear_search)
        clear_repair_btn.setStyleSheet('''
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
        self.repair_search_layout.addWidget(clear_repair_btn)
        
        layout.addLayout(self.invoice_search_layout)
        layout.addLayout(self.repair_search_layout)
        
        # Main table
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        self.update_search_controls()
        self.update_button_styles()

    def on_search_type_changed(self, search_type):
        if search_type == 'ID hóa đơn':
            self.search_input.setPlaceholderText('Nhập ID hóa đơn...')
        elif search_type == 'Tên khách hàng':
            self.search_input.setPlaceholderText('Nhập tên khách hàng...')
        elif search_type == 'Tên nhân viên':
            self.search_input.setPlaceholderText('Nhập tên nhân viên...')
        else:
            self.search_input.setPlaceholderText('Nhập từ khóa tìm kiếm...')

    def search_data(self):
        if self.current_mode == "invoices":
            self.load_invoices_data()
        else:
            self.load_repairs_data()

    def clear_search(self):
        if self.current_mode == "invoices":
            self.search_type.setCurrentText('Tất cả')
            self.search_input.clear()
            self.invoice_from_date.setDate(QDate.currentDate().addMonths(-1))
            self.invoice_to_date.setDate(QDate.currentDate())
        else:
            self.repair_search_input.clear()
            self.repair_date_from.setDate(QDate.currentDate().addMonths(-1))
            self.repair_date_to.setDate(QDate.currentDate())
        self.load_data()
    
    def switch_mode(self, mode):
        self.current_mode = mode
        self.update_search_controls()
        self.load_data()
        self.update_button_styles()
        
    def update_search_controls(self):
        if self.current_mode == "invoices":
            for i in range(self.invoice_search_layout.count()):
                widget = self.invoice_search_layout.itemAt(i).widget()
                if widget:
                    widget.show()
            for i in range(self.repair_search_layout.count()):
                widget = self.repair_search_layout.itemAt(i).widget()
                if widget:
                    widget.hide()
        else:
            for i in range(self.invoice_search_layout.count()):
                widget = self.invoice_search_layout.itemAt(i).widget()
                if widget:
                    widget.hide()
            for i in range(self.repair_search_layout.count()):
                widget = self.repair_search_layout.itemAt(i).widget()
                if widget:
                    widget.show()

    def update_button_styles(self):
        active_style = '''
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: 3px solid #F39C12;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
        '''
        
        inactive_style = '''
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: 2px solid #145A32;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
                border: 2px solid #F39C12;
            }
        '''
        
        if self.current_mode == "invoices":
            self.invoice_btn.setStyleSheet(active_style)
            self.repair_btn.setStyleSheet(inactive_style)
        else:
            self.invoice_btn.setStyleSheet(inactive_style)
            self.repair_btn.setStyleSheet(active_style)
    
    def load_data(self):
        self.table.clearContents()
        if self.current_mode == "invoices":
            self.load_invoices_data()
        else:
            self.load_repairs_data()
    
    def load_invoices_data(self):
        from_date = self.invoice_from_date.date().toString('yyyy-MM-dd')
        to_date = self.invoice_to_date.date().toString('yyyy-MM-dd')
        search_type = self.search_type.currentText()
        search_text = self.search_input.text().strip()
        
        if search_text:
            invoices = self.invoice_controller.search_invoices(search_type, search_text, from_date, to_date)
        else:
            invoices = self.invoice_controller.get_all_invoices()
            # Filter by date
            invoices = [inv for inv in invoices if from_date <= inv[4] <= to_date]
        
        self.setup_invoices_table()
        self.table.setRowCount(len(invoices))
        
        for row, invoice in enumerate(invoices):
            invoice_id, customer_name, employee_name, total_amount, created_date = invoice
            
            self.table.setItem(row, 0, QTableWidgetItem(invoice_id))
            self.table.setItem(row, 1, QTableWidgetItem(customer_name or 'Khách lẻ'))
            self.table.setItem(row, 2, QTableWidgetItem(employee_name or ''))
            self.table.setItem(row, 3, QTableWidgetItem(f"{total_amount:,.0f} VND"))
            self.table.setItem(row, 4, QTableWidgetItem(_format_date(created_date)))

            detail_btn = QPushButton('Xem chi tiết')
            detail_btn.setStyleSheet('''
                QPushButton {
                    background-color: #1E88E5;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 3px 6px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
            ''')
            detail_btn.clicked.connect(lambda checked, inv_id=invoice_id: self.show_invoice_details(inv_id))
            self.table.setCellWidget(row, 5, detail_btn)
            self.table.setRowHeight(row, 36)
    
    def load_repairs_data(self):
        from_date = self.repair_date_from.date().toString('yyyy-MM-dd')
        to_date = self.repair_date_to.date().toString('yyyy-MM-dd')
        search_text = self.repair_search_input.text().strip().lower()
        
        repairs = self.repair_controller.get_all_repairs()
        # Filter by date and search text
        filtered_repairs = []
        for repair in repairs:
            if from_date <= repair.created_date <= to_date:
                if not search_text:
                    filtered_repairs.append(repair)
                else:
                    # Tìm theo tên khách hàng (cần lấy thông tin khách hàng)
                    customer = self.repair_controller.customer_service.get_customer_by_id(repair.customer_id)
                    if customer and search_text in customer.name.lower():
                        filtered_repairs.append(repair)
        
        self.setup_repairs_table()
        self.table.setRowCount(len(filtered_repairs))
        
        for row, repair in enumerate(filtered_repairs):
            customer = self.repair_controller.customer_service.get_customer_by_id(repair.customer_id)
            employee = self.repair_controller.repair_service.db.get_employee_by_id(repair.employee_id)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(repair.id)))
            self.table.setItem(row, 1, QTableWidgetItem(customer.name if customer else 'Khách lẻ'))
            self.table.setItem(row, 2, QTableWidgetItem(employee[3] if employee else ''))  # employee name
            self.table.setItem(row, 3, QTableWidgetItem(f"{repair.actual_cost:,.0f} VND"))
            self.table.setItem(row, 4, QTableWidgetItem(_format_date(repair.created_date)))
            self.table.setItem(row, 5, QTableWidgetItem(_format_date(repair.estimated_completion)))
            self.table.setItem(row, 6, QTableWidgetItem(repair.status))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(8, 4, 8, 4)

            view_btn = QPushButton('Xem chi tiết')
            view_btn.setFixedHeight(30)
            view_btn.setStyleSheet('''
                QPushButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            ''')
            view_btn.clicked.connect(lambda checked, rid=repair.id: self.view_repair_details(rid))

            if self.user_role == 1:
                edit_btn = QPushButton('Sửa')
                edit_btn.setFixedHeight(30)
                edit_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #3498DB;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2980B9;
                    }
                ''')
                edit_btn.clicked.connect(lambda checked, rid=repair.id: self.edit_repair(rid))
                action_layout.addWidget(edit_btn)

            action_layout.addStretch()
            action_layout.addWidget(view_btn)
            if self.user_role == 1:
                action_layout.addSpacing(10)
                action_layout.addWidget(edit_btn)
            action_layout.addStretch()

            self.table.setCellWidget(row, 7, action_widget)
            self.table.setRowHeight(row, 46)
    
    def setup_invoices_table(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Khách hàng', 'Nhân viên', 'Tổng tiền', 'Ngày tạo', 'Chi tiết'
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
    
    def setup_repairs_table(self):
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Khách hàng', 'Nhân viên', 'Chi phí', 'Ngày tạo', 'Dự kiến hoàn thành', 'Trạng thái', 'Hành động'
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(7, 180)

    def show_invoice_details(self, invoice_id):
        invoice_data = self.invoice_controller.get_invoice_by_id(invoice_id)
        if not invoice_data:
            QMessageBox.warning(self, 'Lỗi', f'Không tìm thấy hóa đơn #{invoice_id}')
            return

        details = self.invoice_controller.get_invoice_details(invoice_id)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f'Chi tiết hóa đơn #{invoice_id}')
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f'HÓA ĐƠN #{invoice_id}')
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        layout.addWidget(header_label)
        
        # Invoice info
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f'Ngày tạo: {_format_date(invoice_data[4])}'))
        info_layout.addWidget(QLabel(f'Nhân viên: {invoice_data[8]}'))
        info_layout.addWidget(QLabel(f'Khách hàng: {invoice_data[5]}'))
        if invoice_data[6]:  # phone
            info_layout.addWidget(QLabel(f'SĐT: {invoice_data[6]}'))
        if invoice_data[7]:  # address
            info_layout.addWidget(QLabel(f'Địa chỉ: {invoice_data[7]}'))
        
        layout.addLayout(info_layout)
        
        # Products table
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Sản phẩm', 'Số lượng', 'Đơn giá', 'Thành tiền'])
        
        table.setRowCount(len(details))
        total = 0
        for row, detail in enumerate(details):
            product_name = getattr(detail, 'product_name', f"Sản phẩm {detail.product_id}")
            table.setItem(row, 0, QTableWidgetItem(product_name))
            table.setItem(row, 1, QTableWidgetItem(str(detail.quantity)))
            table.setItem(row, 2, QTableWidgetItem(f"{detail.price:,.0f} VND"))
            line_total = detail.quantity * detail.price
            table.setItem(row, 3, QTableWidgetItem(f"{line_total:,.0f} VND"))
            total += line_total
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(QLabel('CHI TIẾT SẢN PHẨM'))
        layout.addWidget(table)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_label = QLabel(f'Tổng cộng: {total:,.0f} VND')
        total_label.setStyleSheet("font-weight: bold; color: #27AE60; font-size: 14px;")
        total_layout.addWidget(total_label)
        layout.addLayout(total_layout)
        
        # Close button
        close_btn = QPushButton('Đóng')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def view_repair_details(self, repair_id):
        repair = self.repair_controller.get_repair_by_id(repair_id)
        if not repair:
            QMessageBox.warning(self, 'Lỗi', f'Không tìm thấy đơn sửa chữa #{repair_id}')
            return

        customer = self.repair_controller.customer_service.get_customer_by_id(repair.customer_id)
        employee = self.repair_controller.repair_service.db.get_employee_by_id(repair.employee_id)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f'Chi tiết đơn sửa chữa #{repair_id}')
        dialog.setMinimumWidth(560)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        title_label = QLabel(f'ĐƠN SỬA CHỮA #{repair_id}')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        layout.addWidget(title_label)
        
        # Repair info
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f'Ngày tạo: {_format_date(repair.created_date)}'))
        info_layout.addWidget(QLabel(f'Nhân viên: {employee[3] if employee else ""}'))
        info_layout.addWidget(QLabel(f'Khách hàng: {customer.name if customer else ""}'))
        info_layout.addWidget(QLabel(f'Trạng thái: {repair.status}'))
        info_layout.addWidget(QLabel(f'Dự kiến hoàn thành: {_format_date(repair.estimated_completion)}'))
        info_layout.addWidget(QLabel(f'Chi phí: {repair.actual_cost:,.0f} VND'))
        
        layout.addLayout(info_layout)
        
        # Issue description
        issue_group = QGroupBox("Mô tả lỗi")
        issue_layout = QVBoxLayout()
        issue_text = QTextEdit()
        issue_text.setPlainText(repair.issue_description)
        issue_text.setReadOnly(True)
        issue_layout.addWidget(issue_text)
        issue_group.setLayout(issue_layout)
        layout.addWidget(issue_group)
        
        # Close button
        close_btn = QPushButton('Đóng')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def edit_repair(self, repair_id):
        from .dialogs.edit_repair_dialog import EditRepairDialog
        dialog = EditRepairDialog(self.db, self.repair_controller, repair_id, self)
        if dialog.exec():
            self.load_data()