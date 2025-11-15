from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QLabel, QLineEdit, QComboBox,
                             QGraphicsDropShadowEffect, QFileDialog, QProgressDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIntValidator, QDoubleValidator
import csv
from app.controllers.watch_controller import WatchController
from app.controllers.brand_controller import BrandController

class ProductManagementTab(QWidget):
    def __init__(self, db, controllers, user_role):
        super().__init__()
        self.db = db
        self.watch_controller: WatchController = controllers['watch']
        self.brand_controller: BrandController = controllers['brand']
        self.user_role = user_role
        self.products = []
        self.page_size = 50
        self.current_page = 1
        self.total_pages = 1
        self.total_products = 0
        self.current_filters = {}
        self.order_by = 'p.quantity'
        self.order_dir = 'ASC'
        self.init_ui()
        self.load_data()

    def _parse_price_string(self, s):
        """
        Chuyển chuỗi giá (có thể có dấu phẩy/điểm/chuỗi 'VND') thành float.
        Nếu không parse được trả về 0.
        """
        if not s:
            return 0.0
        if isinstance(s, (int, float)):
            return float(s)
        s = str(s).strip()
        # loại bỏ chữ, dấu cách, giữ số
        import re
        s = re.sub(r'[^\d\-\.]', '', s)
        if not s:
            return 0.0
        try:
            return float(s)
        except Exception:
            try:
                # thay ',' bằng '' và thử lại (đề phòng 1,200,000)
                s2 = s.replace(',', '')
                return float(s2)
            except Exception:
                return 0.0

    def _parse_int_field(self, value, default=0):
        if value is None or value == "":
            return default
        try:
            if isinstance(value, str):
                value = value.strip()
            return int(float(value))
        except (TypeError, ValueError):
            return default

    def _parse_bool_field(self, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return bool(value)
        text = str(value).strip().lower()
        if text in {"1", "true", "yes", "y"}:
            return True
        if text in {"0", "false", "no", "n"}:
            return False
        return False

    def _parse_features_field(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        import re

        text = str(value).strip()
        if text.startswith("[") and text.endswith("]"):
            try:
                import json

                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass

        parts = [item.strip() for item in re.split(r"[;,]", text) if item.strip()]
        return parts

    def _format_input(self, line_edit):
        text = line_edit.text()
        if text:
            try:
                num = float(text.replace(',', ''))
                formatted = f"{num:,.0f}"
                if formatted != text:
                    line_edit.setText(formatted)
                    line_edit.setCursorPosition(len(formatted))
            except ValueError:
                pass

    def init_ui(self):
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel('Tìm kiếm:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Nhập tên sản phẩm hoặc thương hiệu...')
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Filters
        filter_layout = QHBoxLayout()
        brand_label = QLabel('Thương hiệu:')
        self.brand_filter = QComboBox()
        self.brand_filter.addItem('Tất cả')
        self.brand_filter.currentTextChanged.connect(self.filter_products)

        type_label = QLabel('Loại:')
        self.type_filter = QComboBox()
        self.type_filter.addItems(['Tất cả', 'Đồng hồ cơ', 'Đồng hồ điện tử'])
        self.type_filter.currentTextChanged.connect(self.filter_products)

        price_min_label = QLabel('Giá từ:')
        self.price_min_input = QLineEdit()
        self.price_min_input.setPlaceholderText('VNĐ')
        self.price_min_input.setMaxLength(20)
        self.price_min_input.textChanged.connect(lambda: self._format_input(self.price_min_input))
        self.price_min_input.textChanged.connect(self.filter_products)

        price_max_label = QLabel('đến:')
        self.price_max_input = QLineEdit()
        self.price_max_input.setPlaceholderText('VNĐ')
        self.price_max_input.setMaxLength(20)
        self.price_max_input.textChanged.connect(lambda: self._format_input(self.price_max_input))
        self.price_max_input.textChanged.connect(self.filter_products)

        filter_layout.addWidget(brand_label)
        filter_layout.addWidget(self.brand_filter)
        filter_layout.addWidget(type_label)
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(price_min_label)
        filter_layout.addWidget(self.price_min_input)
        filter_layout.addWidget(price_max_label)
        filter_layout.addWidget(self.price_max_input)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Advanced filters
        advanced_layout = QHBoxLayout()
        self.power_reserve_label = QLabel('Thời gian trữ cót (giờ):')
        self.power_reserve_input = QLineEdit()
        self.power_reserve_input.setPlaceholderText('(tối đa 3 số)')
        self.power_reserve_input.setMaxLength(3)
        self.power_reserve_input.setValidator(QDoubleValidator(0, 999, 1))
        self.power_reserve_input.textChanged.connect(self.filter_products)

        self.battery_life_label = QLabel('Thời lượng pin (năm):')
        self.battery_life_input = QLineEdit()
        self.battery_life_input.setPlaceholderText('(tối đa 2 số)')
        self.battery_life_input.setMaxLength(2)
        self.battery_life_input.setValidator(QIntValidator(0, 99))
        self.battery_life_input.textChanged.connect(self.filter_products)

        self.connectivity_label = QLabel('Kết nối:')
        self.connectivity_filter = QComboBox()
        self.connectivity_filter.addItems(['Tất cả', 'Bluetooth', 'Wi-Fi', 'GPS', 'NFC'])
        self.connectivity_filter.currentTextChanged.connect(self.filter_products)

        advanced_layout.addWidget(self.power_reserve_label)
        advanced_layout.addWidget(self.power_reserve_input)
        advanced_layout.addWidget(self.battery_life_label)
        advanced_layout.addWidget(self.battery_life_input)
        advanced_layout.addWidget(self.connectivity_label)
        advanced_layout.addWidget(self.connectivity_filter)
        advanced_layout.addStretch()
        layout.addLayout(advanced_layout)

        # Connect type filter to update advanced filters visibility
        self.type_filter.currentTextChanged.connect(self.update_advanced_filters_visibility)
        self.update_advanced_filters_visibility()  # Initial setup

        # Controls
        controls_layout = QHBoxLayout()

        if self.user_role == 1:
            add_btn = QPushButton('Thêm sản phẩm')
            add_btn.setStyleSheet('''
                QPushButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            ''')
            add_btn.clicked.connect(self.add_product)
            controls_layout.addWidget(add_btn)

            import_csv_btn = QPushButton('Nhập CSV')
            import_csv_btn.setStyleSheet('''
                QPushButton {
                    background-color: #9B59B6;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #8E44AD;
                }
            ''')
            import_csv_btn.clicked.connect(self.import_csv)
            controls_layout.addWidget(import_csv_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Table
        self.table = QTableWidget()
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['ID', 'Tên', 'Thương hiệu', 'Loại', 'Giá', 'Số lượng', 'Chi tiết sản phẩm', 'Hành động'])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        # Pagination
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()

        self.page_label = QLabel("Trang 1 / 1")
        pagination_layout.addWidget(self.page_label)

        self.prev_btn = QPushButton('Trước')
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton('Sau')
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_btn)

        pagination_layout.addStretch()
        layout.addLayout(pagination_layout)

        self.setLayout(layout)

    def _create_qty_widget(self, quantity: int):
        qty_widget = QWidget()
        layout = QHBoxLayout(qty_widget)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        qty_label = QLabel(str(quantity))
        qty_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        qty_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: 600;
                font-size: 13px;
                padding: 2px 0px;
            }
        """)
        layout.addWidget(qty_label)
        layout.addStretch()

        badge_label = QLabel()
        badge_label.setFixedHeight(20)
        badge_label.setFixedWidth(42)
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 60))
        badge_label.setGraphicsEffect(shadow)

        if quantity <= 2:
            badge_label.setText(f"⚠ {quantity}")
            badge_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF6B6B, stop:1 #E74C3C);
                    color: white;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 1px 4px;
                    border: 1px solid #C0392B;
                }
                QLabel:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF7979, stop:1 #FF6B6B);
                }
            """)
        elif quantity <= 5:
            badge_label.setText(f"⚠ {quantity}")
            badge_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FFA726, stop:1 #F39C12);
                    color: #2C3E50;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 1px 4px;
                    border: 1px solid #E67E22;
                }
                QLabel:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FFB74D, stop:1 #FFA726);
                }
            """)
        else:
            badge_label.hide()

        layout.addWidget(badge_label)

        if quantity <= 5:
            if quantity <= 2:
                tooltip_text = f"Cảnh báo: Chỉ còn {quantity} sản phẩm - Sắp hết hàng!"
            else:
                tooltip_text = f"Cảnh báo: Chỉ còn {quantity} sản phẩm - Số lượng thấp"
            qty_widget.setToolTip(tooltip_text)
            badge_label.setToolTip(tooltip_text)

        return qty_widget

    def load_data(self, filters=None):
        """
        Lấy dữ liệu sản phẩm kèm tên brand qua JOIN với pagination và filtering,
        rồi fill vào 8 cột của table.
        """
        if filters is None:
            filters = self.current_filters

        try:
            # Calculate offset for pagination
            offset = (self.current_page - 1) * self.page_size
            
            # Get watches with filters using server-side filtering
            self.products, self.total_products = self.watch_controller.get_watches_with_filters(
                filters, self.order_by, self.order_dir, self.page_size, offset
            )
            
            # Calculate total pages
            self.total_pages = max(1, (self.total_products + self.page_size - 1) // self.page_size)
            
            # Ensure current_page is within bounds
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            if self.current_page < 1:
                self.current_page = 1

            # Set table rows
            self.table.setRowCount(len(self.products))

            for row, product in enumerate(self.products):
                pid = product.id
                name = product.name or ''
                # Use brand_name from the join if available, otherwise get it
                if hasattr(product, 'brand_name'):
                    brand = product.brand_name or ''
                else:
                    brand = self._get_brand_name(product.brand_id)
                
                ptype = getattr(product, 'product_type', '')
                if ptype and ptype.lower() in ('mechanical', 'm', 'coil'):
                    type_text = "Đồng hồ cơ"
                elif ptype and ptype.lower() in ('digital', 'smart', 'electronic'):
                    type_text = "Đồng hồ điện tử"
                else:
                    type_text = ptype or ''
                
                price = product.price or 0
                quantity = product.quantity if product.quantity is not None else 0

                # Col 0: ID
                id_item = QTableWidgetItem(str(pid))
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, id_item)

                # Col 1: Tên
                name_item = QTableWidgetItem(name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, name_item)

                # Col 2: Thương hiệu
                brand_item = QTableWidgetItem(brand)
                brand_item.setFlags(brand_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 2, brand_item)

                # Col 3: Loại
                type_item = QTableWidgetItem(type_text)
                type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 3, type_item)

                # Col 4: Giá
                if price is None:
                    price_text = ''
                else:
                    try:
                        price_text = f"{price:,.0f} VND"
                    except:
                        price_text = str(price)
                price_item = QTableWidgetItem(price_text)
                price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 4, price_item)

                # Col 5: Số lượng
                qty_widget = self._create_qty_widget(quantity)
                self.table.setCellWidget(row, 5, qty_widget)

                # Col 6: Chi tiết sản phẩm
                detail_btn = QPushButton('Xem chi tiết')
                detail_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #2ECC71;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 3px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #27AE60;
                    }
                ''')
                detail_btn.clicked.connect(lambda checked, pid=pid: self.show_product_details(pid))
                self.table.setCellWidget(row, 6, detail_btn)

                # Col 7: Hành động
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)

                if self.user_role == 1:
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
                    edit_btn.clicked.connect(lambda checked, pid=pid: self.edit_product(pid))
                    action_layout.addWidget(edit_btn)

                    delete_btn = QPushButton('Xóa')
                    delete_btn.setStyleSheet('''
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
                    ''')
                    delete_btn.clicked.connect(lambda checked, pid=pid: self.delete_product(pid))
                    action_layout.addWidget(delete_btn)

                action_layout.addStretch()
                self.table.setCellWidget(row, 7, action_widget)
                
                # Set row height
                self.table.setRowHeight(row, 40)

            # Populate brand filter with all brands from database (always refresh) but preserve selection
            current_brand = self.brand_filter.currentText()
            self.brand_filter.blockSignals(True)
            self.brand_filter.clear()
            self.brand_filter.addItem('Tất cả')
            
            brands = self.brand_controller.get_all_brands()
            for brand in brands:
                if brand.name:
                    self.brand_filter.addItem(brand.name)
            
            # Restore selection if possible
            if current_brand and current_brand in [self.brand_filter.itemText(i) for i in range(self.brand_filter.count())]:
                self.brand_filter.setCurrentText(current_brand)
            self.brand_filter.blockSignals(False)

        except Exception as e:
            QMessageBox.critical(self, 'Lỗi tải dữ liệu', f'Không thể tải dữ liệu sản phẩm từ cơ sở dữ liệu.\nChi tiết lỗi: {str(e)}')
            self.products = []
            self.total_products = 0
            self.total_pages = 1
            self.current_page = 1

        # Update pagination
        self.page_label.setText(f"Trang {self.current_page} / {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def _get_brand_name(self, brand_id: str) -> str:
        brand = self.brand_controller.get_brand_by_id(brand_id)
        return brand.name if brand else "Unknown"

    def filter_products(self):
        """
        Collect filter values and reload data with filters applied.
        """
        search_text = self.search_input.text().strip()
        selected_brand = self.brand_filter.currentText()
        selected_type = self.type_filter.currentText()

        # Price filters (parse robust)
        price_min_text = self.price_min_input.text().strip()
        price_max_text = self.price_max_input.text().strip()
        price_min = None
        price_max = None
        if price_min_text:
            price_min = self._parse_price_string(price_min_text)
        if price_max_text:
            price_max = self._parse_price_string(price_max_text)

        # Advanced filters
        power_reserve_min_text = self.power_reserve_input.text().strip()
        try:
            power_reserve_min = float(power_reserve_min_text) if power_reserve_min_text else None
        except ValueError:
            power_reserve_min = None

        battery_life_min_text = self.battery_life_input.text().strip()
        try:
            battery_life_min = float(battery_life_min_text) if battery_life_min_text else None
        except ValueError:
            battery_life_min = None

        selected_connectivity = self.connectivity_filter.currentText()

        # Collect filters
        filters = {
            'search': search_text,
            'brand': selected_brand,
            'type': selected_type,
            'price_min': price_min,
            'price_max': price_max,
            'power_reserve_min': power_reserve_min,
            'battery_life_min': battery_life_min,
            'connectivity': selected_connectivity
        }

        # Update current filters and reset to first page, then load data
        self.current_filters = filters
        self.current_page = 1
        self.load_data()

    def update_advanced_filters_visibility(self):
        """
        Update visibility of advanced filters based on selected watch type.
        """
        selected_type = self.type_filter.currentText()

        if selected_type == 'Tất cả':
            # Show all filters
            self.power_reserve_label.show()
            self.power_reserve_input.show()
            self.battery_life_label.show()
            self.battery_life_input.show()
            self.connectivity_label.show()
            self.connectivity_filter.show()
        elif selected_type == 'Đồng hồ cơ':
            # Show only mechanical watch filters
            self.power_reserve_label.show()
            self.power_reserve_input.show()
            self.battery_life_label.hide()
            self.battery_life_input.hide()
            self.connectivity_label.hide()
            self.connectivity_filter.hide()
        elif selected_type == 'Đồng hồ điện tử':
            # Show only digital watch filters
            self.power_reserve_label.hide()
            self.power_reserve_input.hide()
            self.battery_life_label.show()
            self.battery_life_input.show()
            self.connectivity_label.show()
            self.connectivity_filter.show()

    def show_product_details(self, product_id):
        from .dialogs.product_detail_dialog import ProductDetailDialog
        dialog = ProductDetailDialog(self.db, self.watch_controller, self.brand_controller, product_id)
        dialog.exec()

    def add_product(self):
        from .dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db, self.watch_controller, self.brand_controller)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm sản phẩm mới!')

    def edit_product(self, product_id):
        from .dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.db, self.watch_controller, self.brand_controller, product_id)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật sản phẩm!')

    def delete_product(self, product_id):
        product = self.watch_controller.get_watch_by_id(product_id)
        if not product:
            return

        reply = QMessageBox.question(self, 'Xác nhận',
                                   f'Bạn có chắc muốn xóa sản phẩm "{product.name}"?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.watch_controller.delete_watch(product_id)
            if success:
                self.load_data()
                QMessageBox.information(self, 'Thành công', message)
            else:
                QMessageBox.warning(self, 'Lỗi', message)

    def _validate_csv_headers(self, reader):
        """Validate CSV headers and return validation result."""
        required_headers = ['name', 'brand', 'product_type', 'price', 'quantity']
        if not all(header in reader.fieldnames for header in required_headers):
            QMessageBox.warning(self, 'Lỗi', f'File CSV thiếu các cột bắt buộc: {", ".join(required_headers)}')
            return False
        return True

    def _check_if_brand_file(self, reader):
        """Check if the CSV file is actually a brand file."""
        product_required = ['brand', 'product_type', 'price', 'quantity']
        has_product_required = all(header in reader.fieldnames for header in product_required)

        if 'name' in reader.fieldnames and 'country' in reader.fieldnames and not has_product_required:
            if 'brand' not in reader.fieldnames and 'product_type' not in reader.fieldnames:
                QMessageBox.warning(
                    self,
                    'Lỗi định dạng file',
                    'File CSV này là file thương hiệu, không phải file sản phẩm.\n'
                    'Vui lòng sử dụng chức năng "Nhập CSV" trong phần Quản lý thương hiệu.'
                )
                return True
        return False

    def _process_csv_row(self, row, brand_cache):
        """Process a single CSV row and return the result."""
        try:
            name = row.get('name', '').strip()
            brand_name = row.get('brand', '').strip()
            product_type = row.get('product_type', '').strip()
            price = self._parse_price_string(row.get('price', 0))
            quantity = int(float(row.get('quantity', 0))) if row.get('quantity') else 0

            if not name or not brand_name or price <= 0 or quantity < 0:
                return False, "Dữ liệu không hợp lệ"

            # Check brand with caching
            if brand_name not in brand_cache:
                brand_cache[brand_name] = self.brand_controller.get_brand_by_name(brand_name)

            brand = brand_cache[brand_name]
            if not brand:
                return False, "Thương hiệu không tồn tại"

            # Create watch based on type
            if product_type.lower() in ['mechanical', 'cơ']:
                return self._create_mechanical_watch_from_row(row, name, brand_name, price, quantity)
            else:
                return self._create_electronic_watch_from_row(row, name, brand_name, price, quantity)

        except Exception as e:
            return False, f"Lỗi xử lý: {str(e)}"

    def _create_mechanical_watch_from_row(self, row, name, brand_name, price, quantity):
        """Create mechanical watch from CSV row data."""
        movement_type = (row.get('movement_type') or '').strip().lower()
        power_reserve = self._parse_int_field(row.get('power_reserve'))
        water_resistant = self._parse_bool_field(row.get('water_resistant'))

        success, message = self.watch_controller.create_mechanical_watch(
            name, brand_name, price, quantity, row.get('description', '').strip(),
            movement_type, power_reserve, water_resistant
        )
        return success, message

    def _create_electronic_watch_from_row(self, row, name, brand_name, price, quantity):
        """Create electronic watch from CSV row data."""
        battery_life = self._parse_int_field(row.get('battery_life'))
        features = self._parse_features_field(row.get('features'))
        connectivity = (row.get('connectivity') or '').strip()

        success, message = self.watch_controller.create_electronic_watch(
            name, brand_name, price, quantity, row.get('description', '').strip(),
            battery_life, features, connectivity
        )
        return success, message

    def import_csv(self):
        """Import products from CSV file with improved error handling and performance."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file CSV", "", "CSV files (*.csv);;All files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            if not rows:
                QMessageBox.warning(self, 'Lỗi', 'File CSV trống hoặc không có dữ liệu.')
                return

            # Validate file type and headers
            if self._check_if_brand_file(reader):
                return

            if not self._validate_csv_headers(reader):
                return

            # Setup progress dialog
            progress = QProgressDialog("Đang nhập dữ liệu...", "Hủy", 0, len(rows), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            imported_count = 0
            skipped_count = 0
            brand_cache = {}  # Cache for brand lookups

            # Process each row
            for i, row in enumerate(rows):
                if progress.wasCanceled():
                    break

                progress.setValue(i + 1)

                success, message = self._process_csv_row(row, brand_cache)
                if success:
                    imported_count += 1
                else:
                    skipped_count += 1

            progress.setValue(len(rows))

            # Show results
            success_msg = f'Đã nhập thành công {imported_count} sản phẩm mới.'
            if skipped_count > 0:
                success_msg += f'\nĐã bỏ qua {skipped_count} sản phẩm do lỗi.'

            QMessageBox.information(self, 'Thành công', success_msg)
            self.load_data()

        except FileNotFoundError:
            QMessageBox.critical(self, 'Lỗi', 'Không tìm thấy file CSV. Vui lòng kiểm tra đường dẫn file.')
        except PermissionError:
            QMessageBox.critical(self, 'Lỗi', 'Không có quyền truy cập file CSV. Vui lòng kiểm tra quyền truy cập.')
        except UnicodeDecodeError:
            QMessageBox.critical(self, 'Lỗi', 'Lỗi đọc file CSV: File không đúng định dạng hoặc mã hóa. Vui lòng kiểm tra file.')
        except Exception as e:
            from app.utils.error_handler import logger
            logger.error(f"Error importing CSV: {e}")
            QMessageBox.critical(self, 'Lỗi', f'Không thể đọc file CSV: {str(e)}')

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()