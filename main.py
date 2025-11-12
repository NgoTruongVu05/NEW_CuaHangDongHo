import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon

# Thêm đường dẫn để import từ app
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.database import Database
from app.views.main_view import MainWindow
from app.views.login_dialog import LoginDialog

# Import controllers và services
from app.services.customer_service import CustomerService
from app.services.employee_service import EmployeeService
from app.services.watch_service import WatchService
from app.services.brand_service import BrandService
from app.services.sales_service import SalesService
from app.services.repair_service import RepairService
from app.services.invoice_service import InvoiceService
from app.services.salary_service import SalaryService
from app.services.statistics_service import StatisticsService

from app.controllers.customer_controller import CustomerController
from app.controllers.employee_controller import EmployeeController
from app.controllers.watch_controller import WatchController
from app.controllers.brand_controller import BrandController
from app.controllers.sales_controller import SalesController
from app.controllers.repair_controller import RepairController
from app.controllers.invoice_controller import InvoiceController
from app.controllers.salary_controller import SalaryController
from app.controllers.statistics_controller import StatisticsController

def set_app_style(app):
    # Set application-wide font
    app.setFont(QFont('Segoe UI', 10))
    
    # Set modern style
    app.setStyle('Fusion')
    
    # Set color palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    app.setPalette(palette)
    
    # Set stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #353535;
        }
        QPushButton {
            background-color: #2a82da;
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #3891e8;
        }
        QPushButton:pressed {
            background-color: #1e5b99;
        }
        QTableWidget {
            gridline-color: #5c5c5c;
            background-color: #252525;
            border: 1px solid #5c5c5c;
            border-radius: 4px;
            padding: 2px;
        }
        QTableWidget::item {
            padding: 6px;
        }
        QHeaderView::section {
            background-color: #353535;
            padding: 6px;
            border: 1px solid #5c5c5c;
            font-weight: bold;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            padding: 6px;
            background-color: #252525;
            border: 1px solid #5c5c5c;
            border-radius: 4px;
            color: white;
        }
        QLabel {
            color: white;
        }
        QTabWidget::pane {
            border: 1px solid #5c5c5c;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #353535;
            color: white;
            padding: 8px 16px;
            border: 1px solid #5c5c5c;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #2a82da;
        }
        QTabBar::tab:hover {
            background-color: #3891e8;
        }
    """)

def initialize_controllers(db):
    """Khởi tạo tất cả services và controllers"""
    # Khởi tạo services
    customer_service = CustomerService(db)
    employee_service = EmployeeService(db)
    watch_service = WatchService(db)
    brand_service = BrandService(db)
    sales_service = SalesService(db)
    repair_service = RepairService(db)
    invoice_service = InvoiceService(db)
    salary_service = SalaryService(db)
    statistics_service = StatisticsService(db)
    
    # Khởi tạo controllers
    customer_controller = CustomerController(customer_service)
    employee_controller = EmployeeController(employee_service)
    watch_controller = WatchController(watch_service, brand_service)
    brand_controller = BrandController(brand_service)
    sales_controller = SalesController(sales_service, customer_service, watch_service)
    repair_controller = RepairController(repair_service, customer_service)
    invoice_controller = InvoiceController(invoice_service)
    salary_controller = SalaryController(salary_service)
    statistics_controller = StatisticsController(statistics_service)
    
    controllers = {
        'customer': customer_controller,
        'employee': employee_controller,
        'watch': watch_controller,
        'brand': brand_controller,
        'sales': sales_controller,
        'repair': repair_controller,
        'invoice': invoice_controller,
        'salary': salary_controller,
        'statistics': statistics_controller
    }
    
    return controllers

def main():
    app = QApplication(sys.argv)

    # Set application icon
    if os.path.exists('images/icon.png'):
        app.setWindowIcon(QIcon('images/icon.png'))

    # Set application style
    set_app_style(app)
    
    # Khởi tạo database
    db = Database()
    
    # Khởi tạo controllers
    controllers = initialize_controllers(db)
    
    # Vòng lặp chính cho đăng nhập
    while True:
        # Hiển thị dialog đăng nhập
        login_dialog = LoginDialog(db)
        if login_dialog.exec():
            user_info = login_dialog.user_info
            
            # Hiển thị main window sau khi đăng nhập thành công
            main_window = MainWindow(user_info, db, controllers)
            main_window.show()
            
            # Chạy ứng dụng và chờ đợi
            app.exec()
            
            # Khi main_window đóng (đăng xuất), quay lại vòng lặp đăng nhập
            continue
        else:
            # Thoát ứng dụng nếu không đăng nhập
            break
    
    # Đóng kết nối database khi thoát ứng dụng
    db.close()
    sys.exit(0)

if __name__ == '__main__':
    main()