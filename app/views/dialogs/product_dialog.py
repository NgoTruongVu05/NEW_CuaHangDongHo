from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton,
                             QDoubleSpinBox, QSpinBox, QMessageBox, QComboBox,
                             QCheckBox, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel,
                             QTextEdit)
from PyQt6.QtCore import Qt
from app.models.mechanical_watch import MechanicalWatch
from app.models.electronic_watch import ElectronicWatch

class ProductDialog(QDialog):
    def __init__(self, db, watch_controller, brand_controller, product_id=None):
        super().__init__()
        self.db = db
        self.watch_controller = watch_controller
        self.brand_controller = brand_controller
        self.product_id = product_id
        self.product_type = "mechanical"
        self.init_ui()
        if product_id:
            self.load_product_data()

    def _format_input(self, line_edit):
        text = line_edit.text()
        if text:
            try:
                num = float(text.replace('.', ''))
                formatted = f"{num:,.0f}".replace(',', '.')
                if formatted != text:
                    line_edit.setText(formatted)
                    line_edit.setCursorPosition(len(formatted))
            except ValueError:
                pass
    
    def init_ui(self):
        self.setWindowTitle('Thêm/Sửa sản phẩm' if not self.product_id else 'Sửa sản phẩm')
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Basic info
        basic_group = QGroupBox('Thông tin cơ bản')
        basic_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        basic_layout.addRow('Tên sản phẩm:', self.name_input)
        
        self.brand_combo = QComboBox()
        self.load_brands()
        basic_layout.addRow('Thương hiệu:', self.brand_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Đồng hồ cơ', 'Đồng hồ điện tử'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        basic_layout.addRow('Loại đồng hồ:', self.type_combo)
        
        price_layout = QHBoxLayout()
        self.price_input = QLineEdit()
        self.price_input.setMaxLength(20)
        self.price_input.textChanged.connect(lambda: self._format_input(self.price_input))
        price_label = QLabel('VND')
        price_layout.addWidget(self.price_input)
        price_layout.addWidget(price_label)
        price_layout.addStretch()
        basic_layout.addRow('Giá:', price_layout)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMaximum(100)
        basic_layout.addRow('Số lượng:', self.quantity_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        basic_layout.addRow('Mô tả:', self.description_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Mechanical watch specific
        self.mech_group = QGroupBox('Thông số đồng hồ cơ')
        mech_layout = QFormLayout()
        
        self.movement_combo = QComboBox()
        self.movement_combo.addItems(['Automatic', 'Manual'])
        mech_layout.addRow('Loại máy:', self.movement_combo)
        
        power_reserve_layout = QHBoxLayout()
        self.power_reserve_input = QSpinBox()
        self.power_reserve_input.setMinimum(30)
        self.power_reserve_input.setMaximum(999)
        power_reserve_label = QLabel('giờ')
        power_reserve_layout.addWidget(self.power_reserve_input)
        power_reserve_layout.addWidget(power_reserve_label)
        power_reserve_layout.addStretch()
        mech_layout.addRow('Dự trữ năng lượng:', power_reserve_layout)
        
        self.water_resistant_check = QCheckBox('Chống nước')
        mech_layout.addRow(self.water_resistant_check)
        
        self.mech_group.setLayout(mech_layout)
        layout.addWidget(self.mech_group)
        
        # Electronic watch specific
        self.elec_group = QGroupBox('Thông số đồng hồ điện tử')
        elec_layout = QFormLayout()
        
        battery_life_layout = QHBoxLayout()
        self.battery_life_input = QSpinBox()
        self.battery_life_input.setMaximum(99)
        battery_life_label = QLabel('năm')
        battery_life_layout.addWidget(self.battery_life_input)
        battery_life_layout.addWidget(battery_life_label)
        battery_life_layout.addStretch()
        elec_layout.addRow('Thời lượng pin:', battery_life_layout)
        
        self.features_layout = QVBoxLayout()
        self.heart_rate_check = QCheckBox('Theo dõi nhịp tim')
        self.gps_check = QCheckBox('GPS')
        self.steps_check = QCheckBox('Đếm bước chân')
        self.sleep_check = QCheckBox('Theo dõi giấc ngủ')
        
        self.features_layout.addWidget(self.heart_rate_check)
        self.features_layout.addWidget(self.gps_check)
        self.features_layout.addWidget(self.steps_check)
        self.features_layout.addWidget(self.sleep_check)
        
        features_group = QGroupBox('Tính năng')
        features_group.setLayout(self.features_layout)
        elec_layout.addRow(features_group)
        
        self.connectivity_combo = QComboBox()
        self.connectivity_combo.addItems(['Không', 'Bluetooth', 'WiFi', 'Cả hai'])
        elec_layout.addRow('Kết nối:', self.connectivity_combo)
        
        self.elec_group.setLayout(elec_layout)
        layout.addWidget(self.elec_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Lưu')
        save_btn.clicked.connect(self.save_product)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('Hủy')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        self.on_type_changed('Đồng hồ cơ')
    
    def on_type_changed(self, product_type):
        if product_type == 'Đồng hồ cơ':
            self.product_type = "mechanical"
            self.mech_group.show()
            self.elec_group.hide()
        else:
            self.product_type = "electronic"
            self.mech_group.hide()
            self.elec_group.show()
    
    def load_brands(self):
        brands = self.brand_controller.get_all_brands()
        self.brand_combo.clear()
        for brand in brands:
            self.brand_combo.addItem(brand.name)
    
    def load_product_data(self):
        product = self.watch_controller.get_watch_by_id(self.product_id)
        if not product:
            return

        # Basic info
        self.name_input.setText(product.name)
        
        brand = self.brand_controller.get_brand_by_id(product.brand_id)
        if brand:
            self.brand_combo.setCurrentText(brand.name)
            
        try:
            self.price_input.setText(f"{product.price:,.0f}".replace(',', '.'))
        except:
            self.price_input.setText("0")
            
        self.quantity_input.setValue(product.quantity)
        self.description_input.setPlainText(product.description or '')
        
        # Set product type and specific properties
        if isinstance(product, MechanicalWatch):
            self.type_combo.setCurrentText('Đồng hồ cơ')
            self.movement_combo.setCurrentText(product.movement_type or 'Automatic')
            self.power_reserve_input.setValue(product.power_reserve or 0)
            self.water_resistant_check.setChecked(product.water_resistant or False)
        else:
            self.type_combo.setCurrentText('Đồng hồ điện tử')
            self.battery_life_input.setValue(product.battery_life or 0)
            
            # Features
            features = product.features or []
            self.heart_rate_check.setChecked('heart_rate' in features)
            self.gps_check.setChecked('gps' in features)
            self.steps_check.setChecked('steps' in features)
            self.sleep_check.setChecked('sleep' in features)
            
            self.connectivity_combo.setCurrentText(product.connectivity or 'Không')
    
    def save_product(self):
        name = self.name_input.text().strip()
        brand_name = self.brand_combo.currentText()
        
        if not name or not brand_name:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ thông tin cơ bản!')
            return
        
        try:
            price_text = self.price_input.text().replace('.', '')
            price = float(price_text)
        except ValueError:
            QMessageBox.warning(self, 'Lỗi', 'Giá phải là số hợp lệ!')
            return
            
        quantity = self.quantity_input.value()
        description = self.description_input.toPlainText().strip()
        
        if self.product_type == "mechanical":
            movement_type = self.movement_combo.currentText().lower()
            power_reserve = self.power_reserve_input.value()
            water_resistant = self.water_resistant_check.isChecked()
            
            if self.product_id:
                success, message = self.watch_controller.update_mechanical_watch(
                    self.product_id, name, brand_name, price, quantity, description,
                    movement_type, power_reserve, water_resistant
                )
            else:
                success, message = self.watch_controller.create_mechanical_watch(
                    name, brand_name, price, quantity, description,
                    movement_type, power_reserve, water_resistant
                )
        else:
            battery_life = self.battery_life_input.value()
            connectivity = self.connectivity_combo.currentText()
            
            features = []
            if self.heart_rate_check.isChecked(): features.append('heart_rate')
            if self.gps_check.isChecked(): features.append('gps')
            if self.steps_check.isChecked(): features.append('steps')
            if self.sleep_check.isChecked(): features.append('sleep')
            
            if self.product_id:
                success, message = self.watch_controller.update_electronic_watch(
                    self.product_id, name, brand_name, price, quantity, description,
                    battery_life, features, connectivity
                )
            else:
                success, message = self.watch_controller.create_electronic_watch(
                    name, brand_name, price, quantity, description,
                    battery_life, features, connectivity
                )
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, 'Lỗi', message)