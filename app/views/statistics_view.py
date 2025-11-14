from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QGridLayout, QComboBox, QSpinBox,
                             QPushButton, QFrame, QToolTip)
from PyQt6.QtCore import QDate
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as mtick
import numpy as np
from app.controllers.statistics_controller import StatisticsController

class StatisticsTab(QWidget):
    def __init__(self, db, controllers, user_role):
        super().__init__()
        self.db = db
        self.statistics_controller: StatisticsController = controllers['statistics']
        self.user_role = user_role
        self.current_mode = "revenue"
        self.init_ui()
        self.switch_statistics(self.current_mode)
        self.load_statistics()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12,12,12,12)
        layout.setSpacing(12)

        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        filter_layout.addWidget(QLabel('Tháng:'))
        self.month_filter = QComboBox()
        self.month_filter.addItems(['Tất cả'] + [str(i) for i in range(1,13)])
        current_month = str(QDate.currentDate().month())
        self.month_filter.setCurrentText(current_month)
        self.month_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.month_filter)

        filter_layout.addWidget(QLabel('Năm:'))
        self.year_filter = QSpinBox()
        self.year_filter.setRange(2000, 2030)
        self.year_filter.setValue(QDate.currentDate().year())
        self.year_filter.valueChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.year_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        self.revenue_btn = QPushButton('Doanh thu')
        self.revenue_btn.setFixedHeight(36)
        self.revenue_btn.clicked.connect(lambda: self.switch_statistics("revenue"))
        self.customer_btn = QPushButton('Khách hàng')
        self.customer_btn.setFixedHeight(36)
        self.customer_btn.clicked.connect(lambda: self.switch_statistics("customer"))
        self.top_types_btn = QPushButton('Sản phẩm bán chạy')
        self.top_types_btn.setFixedHeight(36)
        self.top_types_btn.clicked.connect(lambda: self.switch_statistics("top_types"))

        QToolTip.setFont(self.font())
        self.revenue_btn.setToolTip('Xem doanh thu bán hàng và sửa chữa theo thời gian')
        self.customer_btn.setToolTip('Theo dõi khách hàng mới và khách hàng thân thiết')
        self.top_types_btn.setToolTip('Thống kê top sản phẩm bán chạy trong giai đoạn chọn')

        for b in (self.revenue_btn, self.customer_btn, self.top_types_btn):
            button_layout.addWidget(b)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Summary grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        # Sales revenue
        self.sales_group = QGroupBox('Doanh thu - Bán hàng')
        sl = QVBoxLayout()
        self.total_revenue_label = QLabel('Tổng doanh thu bán hàng: 0 VND')
        self.total_revenue_label.setStyleSheet("color: white;")
        self.total_sales_label = QLabel('Tổng số hóa đơn bán hàng: 0')
        self.total_sales_label.setStyleSheet("color: white;")
        self.avg_sale_label = QLabel('Giá trị trung bình mỗi hóa đơn: 0 VND')
        self.avg_sale_label.setStyleSheet("color: white;")
        for w in (self.total_revenue_label, self.total_sales_label, self.avg_sale_label):
            sl.addWidget(w)
        self.sales_group.setLayout(sl)
        grid_layout.addWidget(self.sales_group, 0, 0)

        # Repair revenue
        self.repair_group = QGroupBox('Doanh thu - Sửa chữa')
        rl = QVBoxLayout()
        self.total_repair_revenue_label = QLabel('Tổng doanh thu sửa chữa: 0 VND')
        self.total_repair_revenue_label.setStyleSheet("color: white;")
        self.total_repairs_label = QLabel('Tổng số đơn sửa chữa: 0')
        self.total_repairs_label.setStyleSheet("color: white;")
        self.completed_repairs_label = QLabel('Đơn đã hoàn thành: 0')
        self.completed_repairs_label.setStyleSheet("color: white;")
        for w in (self.total_repair_revenue_label, self.total_repairs_label, self.completed_repairs_label):
            rl.addWidget(w)
        self.repair_group.setLayout(rl)
        grid_layout.addWidget(self.repair_group, 0, 1)

        # Customer
        self.customer_group = QGroupBox('Thống kê khách hàng')
        cl = QVBoxLayout()
        self.total_customers_label = QLabel('Tổng số khách hàng: 0')
        self.total_customers_label.setStyleSheet("color: white;")
        self.repeat_customers_label = QLabel('Khách hàng thân thiết: 0')
        self.repeat_customers_label.setStyleSheet("color: white;")
        self.new_customers_month_label = QLabel('Khách hàng mới (tháng): 0')
        self.new_customers_month_label.setStyleSheet("color: white;")
        cl.addWidget(self.total_customers_label)
        cl.addWidget(self.repeat_customers_label)
        cl.addWidget(self.new_customers_month_label)
        self.customer_group.setLayout(cl)
        grid_layout.addWidget(self.customer_group, 1, 0, 1, 2)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addLayout(grid_layout)
        layout.addWidget(sep)

        # Chart area
        self.chart_group = QGroupBox('Biểu đồ thống kê')
        chart_layout = QVBoxLayout()
        self.figure = Figure(dpi=100)
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        self.chart_group.setLayout(chart_layout)

        layout.addWidget(self.chart_group)
        self.setLayout(layout)

        # Connect resize event for responsive chart
        self.resizeEvent = self.on_resize

        # Styles
        self.active_style = '''
            QPushButton {
                background-color: #2C3E50; 
                color: white; 
                border: 2px solid #F39C12; 
                border-radius: 12px; 
                padding: 8px 14px; 
                font-weight: 600;
            }
        '''
        self.inactive_style = '''
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: 1px solid #777777;
                border-radius: 12px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        '''

    def on_filter_changed(self, *_):
        self.load_statistics()

    def load_statistics(self):
        month = self.month_filter.currentText()
        year = self.year_filter.value()
        
        # Load revenue statistics
        revenue_stats = self.statistics_controller.get_revenue_statistics(month, year)
        self.total_revenue_label.setText(f'Tổng doanh thu bán hàng: {revenue_stats["sales_revenue"]:,.0f} VND')
        self.total_sales_label.setText(f'Tổng số hóa đơn bán hàng: {revenue_stats["sales_count"]}')
        avg_sale = revenue_stats["sales_revenue"] / revenue_stats["sales_count"] if revenue_stats["sales_count"] > 0 else 0
        self.avg_sale_label.setText(f'Giá trị trung bình mỗi hóa đơn: {avg_sale:,.0f} VND')
        
        self.total_repair_revenue_label.setText(f'Tổng doanh thu sửa chữa: {revenue_stats["repair_revenue"]:,.0f} VND')
        self.total_repairs_label.setText(f'Tổng số đơn sửa chữa: {revenue_stats["repair_count"]}')
        self.completed_repairs_label.setText(f'Đơn đã hoàn thành: {revenue_stats["completed_repairs"]}')
        
        # Load customer statistics
        customer_stats = self.statistics_controller.get_customer_statistics(month, year)
        self.total_customers_label.setText(f'Tổng số khách hàng: {customer_stats["total_customers"]}')
        self.repeat_customers_label.setText(f'Khách hàng thân thiết: {customer_stats["repeat_customers"]}')
        self.new_customers_month_label.setText(f'Khách hàng mới (tháng): {customer_stats["new_customers"]}')

        # Update chart
        self.update_chart()

    def switch_statistics(self, mode):
        self.current_mode = mode
        if mode == "revenue":
            self.sales_group.show()
            self.repair_group.show()
            self.customer_group.hide()
        elif mode == "customer":
            self.sales_group.hide()
            self.repair_group.hide()
            self.customer_group.show()
        elif mode == "top_types":
            self.sales_group.hide()
            self.repair_group.hide()
            self.customer_group.hide()
        self.update_button_styles()
        self.update_chart()

    def update_button_styles(self):
        for name, btn in (("revenue", self.revenue_btn), ("customer", self.customer_btn), ("top_types", self.top_types_btn)):
            btn.setStyleSheet(self.active_style if self.current_mode == name else self.inactive_style)

    def update_chart(self):
        month = self.month_filter.currentText()
        year = self.year_filter.value()

        self.figure.clear()
        self.figure.patch.set_facecolor('#353535')
        
        if self.current_mode == "revenue":
            if month == 'Tất cả':
                breakdown = self.statistics_controller.get_monthly_revenue_breakdown(year)
                labels = [f'T{int(item[0])}' for item in breakdown]
                sales_data = [item[1] for item in breakdown]
                repair_data = [item[2] for item in breakdown]
                x_label = 'Tháng'
                title = f'Doanh thu bán hàng & sửa chữa năm {year}'
                rotation = 0
            else:
                breakdown = self.statistics_controller.get_daily_revenue_breakdown(month, year)
                labels = [str(int(item[0])) for item in breakdown]
                sales_data = [item[1] for item in breakdown]
                repair_data = [item[2] for item in breakdown]
                x_label = 'Ngày'
                title = f'Doanh thu bán hàng & sửa chữa tháng {month}/{year}'
                rotation = 45

            if breakdown:
                x = np.arange(len(labels))
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#353535')
                ax.plot(x, sales_data, marker='o', label='Doanh thu bán hàng', color='#3498DB', linewidth=2)
                ax.plot(x, repair_data, marker='s', label='Doanh thu sửa chữa', color='#E74C3C', linewidth=2)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, color='white', rotation=rotation)
                ax.set_ylabel('Doanh thu (VND)', color='white')
                ax.set_xlabel(x_label, color='white')
                ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
                ax.tick_params(axis='y', colors='white', labelcolor='white')
                ax.grid(True, alpha=0.3, color='white')
                ax.set_title(title, color='white', fontsize=12, fontweight='bold')
                legend = ax.legend(frameon=True)
                legend.get_frame().set_facecolor('#2C3E50')
                legend.get_frame().set_edgecolor('white')
                for text in legend.get_texts():
                    text.set_color('white')
            else:
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#353535')
                ax.text(0.5, 0.5, 'Không có dữ liệu doanh thu trong khoảng thời gian này',
                        ha='center', va='center', color='white')
        
        elif self.current_mode == "customer":
            if month == 'Tất cả':
                trends = self.statistics_controller.get_monthly_customer_trends(year)
                labels = [f'T{int(item[0])}' for item in trends]
                new_data = [item[1] for item in trends]
                repeat_data = [item[2] for item in trends]
                x_label = 'Tháng'
                title = f'Khách hàng mới & thân thiết năm {year}'
                rotation = 0
            else:
                trends = self.statistics_controller.get_daily_customer_trends(month, year)
                labels = [str(int(item[0])) for item in trends]
                new_data = [item[1] for item in trends]
                repeat_data = [item[2] for item in trends]
                x_label = 'Ngày'
                title = f'Khách hàng tháng {month}/{year}'
                rotation = 45

            if trends:
                x = np.arange(len(labels))
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#353535')
                ax.plot(x, new_data, marker='o', label='Khách hàng mới', color='#3498DB', linewidth=2)
                ax.plot(x, repeat_data, marker='s', label='Khách hàng thân thiết', color='#E74C3C', linewidth=2)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, color='white', rotation=rotation)
                ax.set_ylabel('Số lượng khách hàng', color='white')
                ax.set_xlabel(x_label, color='white')
                ax.tick_params(axis='y', colors='white', labelcolor='white')
                ax.grid(True, alpha=0.3, color='white')
                ax.set_title(title, color='white', fontsize=12, fontweight='bold')
                legend = ax.legend(frameon=True)
                legend.get_frame().set_facecolor('#2C3E50')
                legend.get_frame().set_edgecolor('white')
                for text in legend.get_texts():
                    text.set_color('white')
            else:
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#353535')
                ax.text(0.5, 0.5, 'Không có dữ liệu khách hàng trong khoảng thời gian này',
                        ha='center', va='center', color='white')
        
        elif self.current_mode == "top_types":
            top_products = self.statistics_controller.get_top_products(month, year, 5)
            if month == 'Tất cả':
                title = f'Top sản phẩm bán chạy năm {year}'
            else:
                title = f'Top sản phẩm bán chạy tháng {month}/{year}'
            if top_products:
                products = [p[0] for p in top_products]
                quantities = [p[1] for p in top_products]

                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#353535')
                y_pos = np.arange(len(products))
                colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6']

                bars = ax.barh(y_pos, quantities, color=colors[:len(products)])
                ax.set_yticks(y_pos)
                ax.set_yticklabels(products, color='white')
                ax.invert_yaxis()
                ax.set_xlabel('Số lượng bán', color='white')
                ax.tick_params(axis='x', colors='white')
                ax.set_title(title, color='white', fontsize=12, fontweight='bold')

                for bar in bars:
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2.,
                           f'{int(width)}',
                           ha='left', va='center', color='white')
            else:
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#353535')
                ax.text(0.5, 0.5, 'Không có dữ liệu sản phẩm bán chạy',
                       ha='center', va='center', color='white')
        
        # Set fixed subplot position to prevent height changes
        ax.set_position([0.1, 0.1, 0.85, 0.8])
        self.canvas.draw()

    def on_resize(self, event):
        # Update figure size based on current canvas size
        width = self.canvas.width() / self.figure.dpi
        height = self.canvas.height() / self.figure.dpi
        self.figure.set_size_inches(width, height)
        self.update_chart()
        super().resizeEvent(event)
