from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QTableWidget, QTableWidgetItem, QMessageBox,
                            QHeaderView, QDialog, QFormLayout, QLineEdit,
                            QFileDialog, QProgressDialog)
from PyQt6.QtCore import Qt
import csv
from app.controllers.brand_controller import BrandController

class BrandManagementTab(QWidget):
    def __init__(self, db, controllers, user_role):
        super().__init__()
        self.db = db
        self.brand_controller: BrandController = controllers['brand']
        self.user_role = user_role
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        if self.user_role == 1:
            add_btn = QPushButton('Thêm thương hiệu')
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
            add_btn.clicked.connect(self.add_brand)
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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Tên thương hiệu', 'Quốc gia', 'Hành động'])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def load_data(self):
        brands = self.brand_controller.get_all_brands()
        self.display_brands(brands)
    
    def display_brands(self, brands):
        self.table.setRowCount(len(brands))
        for row, brand in enumerate(brands):
            self.table.setItem(row, 0, QTableWidgetItem(str(brand.id)))
            self.table.setItem(row, 1, QTableWidgetItem(brand.name))
            self.table.setItem(row, 2, QTableWidgetItem(brand.country or ''))
            
            # Nút hành động
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
                edit_btn.clicked.connect(lambda checked, bid=brand.id: self.edit_brand(bid))
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
                delete_btn.clicked.connect(lambda checked, bid=brand.id: self.delete_brand(bid))
                action_layout.addWidget(delete_btn)
            
            action_layout.addStretch()
            self.table.setCellWidget(row, 3, action_widget)
        
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
    def add_brand(self):
        dialog = BrandDialog(self.db, self.brand_controller)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã thêm thương hiệu mới!')
    
    def edit_brand(self, brand_id):
        dialog = BrandDialog(self.db, self.brand_controller, brand_id)
        if dialog.exec():
            self.load_data()
            QMessageBox.information(self, 'Thành công', 'Đã cập nhật thương hiệu!')
    
    def delete_brand(self, brand_id):
        brand = self.brand_controller.get_brand_by_id(brand_id)
        if not brand:
            return
        
        success, message = self.brand_controller.delete_brand(brand_id)
        if success:
            self.load_data()
            QMessageBox.information(self, 'Thành công', message)
        else:
            QMessageBox.warning(self, 'Lỗi', message)

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file CSV", "", "CSV files (*.csv);;All files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            if not rows:
                QMessageBox.warning(self, 'Lỗi', 'File CSV trống hoặc không có dữ liệu.')
                return

            # Kiểm tra xem đây có phải là file sản phẩm không
            product_indicators = ['brand', 'product_type', 'price', 'quantity']
            has_product_indicators = any(indicator in reader.fieldnames for indicator in product_indicators)
            
            if has_product_indicators:
                QMessageBox.warning(
                    self, 
                    'Lỗi định dạng file', 
                    'File CSV này là file sản phẩm, không phải file thương hiệu.\n'
                    'Vui lòng sử dụng chức năng "Nhập CSV" trong phần Quản lý sản phẩm.'
                )
                return

            # Validate headers
            required_headers = ['name']
            if not all(header in reader.fieldnames for header in required_headers):
                QMessageBox.warning(self, 'Lỗi', f'File CSV thiếu các cột bắt buộc: {", ".join(required_headers)}')
                return

            progress = QProgressDialog("Đang nhập dữ liệu...", "Hủy", 0, len(rows), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            imported_count = 0
            skipped_count = 0

            for i, row in enumerate(rows):
                if progress.wasCanceled():
                    break

                progress.setValue(i + 1)

                try:
                    name = row.get('name', '').strip()
                    country = row.get('country', '').strip()

                    if not name:
                        skipped_count += 1
                        continue

                    # Kiểm tra brand đã tồn tại chưa
                    existing_brand = self.brand_controller.get_brand_by_name(name)
                    if existing_brand:
                        skipped_count += 1
                        continue

                    success, message = self.brand_controller.create_brand(name, country)
                    if success:
                        imported_count += 1
                    else:
                        skipped_count += 1

                except Exception as e:
                    skipped_count += 1
                    continue

            progress.setValue(len(rows))

            success_msg = f'Đã nhập thành công {imported_count} thương hiệu.'
            if skipped_count > 0:
                success_msg += f'\nĐã bỏ qua {skipped_count} thương hiệu (đã tồn tại hoặc lỗi).'
            
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

class BrandDialog(QDialog):
    def __init__(self, db, brand_controller, brand_id=None):
        super().__init__()
        self.db = db
        self.brand_controller = brand_controller
        self.brand_id = brand_id
        self.init_ui()
        if brand_id:
            self.load_brand_data()
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa thương hiệu')
        self.setFixedSize(400, 200)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        layout.addRow('Tên thương hiệu:', self.name_input)
        
        self.country_input = QLineEdit()
        layout.addRow('Quốc gia:', self.country_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_brand)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Hủy')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def load_brand_data(self):
        brand = self.brand_controller.get_brand_by_id(self.brand_id)
        if brand:
            self.name_input.setText(brand.name)
            self.country_input.setText(brand.country or '')
    
    def save_brand(self):
        name = self.name_input.text().strip()
        country = self.country_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập tên thương hiệu!')
            return
        
        if self.brand_id:
            success, message = self.brand_controller.update_brand(self.brand_id, name, country)
        else:
            success, message = self.brand_controller.create_brand(name, country)
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, 'Lỗi', message)