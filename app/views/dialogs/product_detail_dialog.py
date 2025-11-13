from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from app.models.mechanical_watch import MechanicalWatch
from app.models.electronic_watch import ElectronicWatch


class ProductDetailDialog(QDialog):
    def __init__(self, db, watch_controller, brand_controller, product_id):
        super().__init__()
        self.db = db
        self.watch_controller = watch_controller
        self.brand_controller = brand_controller
        self.product_id = product_id

        self.setWindowTitle("Chi tiết sản phẩm")
        self.setMinimumSize(480, 560)

        self._init_ui()
        self._load_product_details()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # Basic information group
        self.basic_group = QGroupBox("Thông tin cơ bản")
        basic_layout = QFormLayout()

        self.id_value = QLabel("-")
        self.name_value = QLabel("-")
        self.brand_value = QLabel("-")
        self.type_value = QLabel("-")
        self.price_value = QLabel("-")
        self.quantity_value = QLabel("-")

        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMinimumHeight(100)

        for label in (
            self.id_value,
            self.name_value,
            self.brand_value,
            self.type_value,
            self.price_value,
            self.quantity_value,
        ):
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        basic_layout.addRow("Mã sản phẩm:", self.id_value)
        basic_layout.addRow("Tên sản phẩm:", self.name_value)
        basic_layout.addRow("Thương hiệu:", self.brand_value)
        basic_layout.addRow("Loại:", self.type_value)
        basic_layout.addRow("Giá:", self.price_value)
        basic_layout.addRow("Số lượng tồn:", self.quantity_value)
        basic_layout.addRow("Mô tả:", self.description_text)

        self.basic_group.setLayout(basic_layout)
        main_layout.addWidget(self.basic_group)

        # Mechanical information group
        self.mech_group = QGroupBox("Thông số đồng hồ cơ")
        mech_layout = QFormLayout()
        self.movement_value = QLabel("-")
        self.power_reserve_value = QLabel("-")
        self.water_resistant_value = QLabel("-")

        mech_layout.addRow("Loại máy:", self.movement_value)
        mech_layout.addRow("Dự trữ năng lượng:", self.power_reserve_value)
        mech_layout.addRow("Chống nước:", self.water_resistant_value)
        self.mech_group.setLayout(mech_layout)
        main_layout.addWidget(self.mech_group)

        # Electronic information group
        self.elec_group = QGroupBox("Thông số đồng hồ điện tử")
        elec_layout = QFormLayout()
        self.battery_life_value = QLabel("-")
        self.features_value = QLabel("-")
        self.connectivity_value = QLabel("-")

        self.features_value.setWordWrap(True)

        elec_layout.addRow("Thời lượng pin:", self.battery_life_value)
        elec_layout.addRow("Tính năng:", self.features_value)
        elec_layout.addRow("Kết nối:", self.connectivity_value)
        self.elec_group.setLayout(elec_layout)
        main_layout.addWidget(self.elec_group)

        # Dialog buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)

        main_layout.addStretch()

    def _load_product_details(self):
        product = self.watch_controller.get_watch_by_id(self.product_id)
        if not product:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy sản phẩm.")
            self.reject()
            return

        brand_name = "Unknown"
        if product.brand_id:
            brand = self.brand_controller.get_brand_by_id(product.brand_id)
            if brand:
                brand_name = brand.name

        self.id_value.setText(product.id or "-")
        self.name_value.setText(product.name or "-")
        self.brand_value.setText(brand_name)
        self.price_value.setText(self._format_currency(product.price))
        self.quantity_value.setText(self._format_quantity(product.quantity))
        self.description_text.setPlainText(product.description or "Không có mô tả")

        if isinstance(product, MechanicalWatch):
            self._show_mechanical_info(product)
        elif isinstance(product, ElectronicWatch):
            self._show_electronic_info(product)
        else:
            # Unknown product type, hide both groups
            self.mech_group.hide()
            self.elec_group.hide()
            self.type_value.setText("Không xác định")

    def _show_mechanical_info(self, product: MechanicalWatch):
        self.type_value.setText("Đồng hồ cơ")
        self.mech_group.show()
        self.elec_group.hide()

        movement = product.movement_type or "-"
        if movement and movement != "-":
            movement = movement.capitalize()

        self.movement_value.setText(movement)
        self.power_reserve_value.setText(self._format_hours(product.power_reserve))
        self.water_resistant_value.setText("Có" if product.water_resistant else "Không")

    def _show_electronic_info(self, product: ElectronicWatch):
        self.type_value.setText("Đồng hồ điện tử")
        self.mech_group.hide()
        self.elec_group.show()

        self.battery_life_value.setText(self._format_years(product.battery_life))
        self.features_value.setText(self._format_features(product.features))
        self.connectivity_value.setText(product.connectivity or "Không")

    @staticmethod
    def _format_currency(value) -> str:
        try:
            if value is None or value == "":
                return "Không xác định"
            numeric = float(value)
            return f"{numeric:,.0f} VND"
        except (TypeError, ValueError):
            return "Không xác định"

    @staticmethod
    def _format_hours(hours) -> str:
        try:
            if hours is None or hours == "":
                return "Không xác định"
            numeric = int(float(hours))
            return f"{numeric} giờ"
        except (TypeError, ValueError):
            return "Không xác định"

    @staticmethod
    def _format_years(years) -> str:
        try:
            if years is None or years == "":
                return "Không xác định"
            numeric = int(float(years))
            return f"{numeric} năm"
        except (TypeError, ValueError):
            return "Không xác định"

    @staticmethod
    def _format_features(features) -> str:
        if not features:
            return "Không có"

        if isinstance(features, str):
            text = features.strip()
            if text.startswith("[") and text.endswith("]"):
                try:
                    import json

                    parsed = json.loads(text)
                    if isinstance(parsed, list):
                        features = parsed
                except json.JSONDecodeError:
                    pass
            if isinstance(features, str):
                import re

                parts = [item.strip() for item in re.split(r"[;,]", text) if item.strip()]
                features = parts

        feature_labels = {
            "heart_rate": "Theo dõi nhịp tim",
            "gps": "GPS",
            "steps": "Đếm bước chân",
            "sleep": "Theo dõi giấc ngủ",
            "step_counter": "Đếm bước chân",
            "sleep_tracking": "Theo dõi giấc ngủ",
            "water_resistant": "Chống nước",
            "waterproof": "Chống nước",
            "music_control": "Điều khiển nhạc",
            "notifications": "Thông báo",
            "nfc": "NFC",
            "bluetooth": "Bluetooth",
            "wifi": "WiFi",
            "none": "Không",
        }

        readable = [feature_labels.get(f, f) for f in features]
        return ", ".join(readable)

    @staticmethod
    def _format_quantity(quantity) -> str:
        try:
            if quantity is None or quantity == "":
                return "Không xác định"
            numeric = int(float(quantity))
            return str(numeric)
        except (TypeError, ValueError):
            return "Không xác định"

