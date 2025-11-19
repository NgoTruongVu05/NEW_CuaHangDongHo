from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QGridLayout, QComboBox, QSpinBox,
                             QPushButton, QFrame, QToolTip)
from PyQt6.QtCore import QDate, Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as mtick
import numpy as np
from app.controllers.statistics_controller import StatisticsController

class StatisticsTab(QWidget):
    """Tab widget for displaying business statistics including revenue, customers, and top products."""
    
    # Define constants
    ACTIVE_BTN_STYLE = '''
        QPushButton {
            background-color: #2C3E50; 
            color: white; 
            border: 2px solid #F39C12; 
            border-radius: 12px; 
            padding: 8px 14px; 
            font-weight: 600;
        }
    '''
    INACTIVE_BTN_STYLE = '''
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
    CHART_BG_COLOR = '#353535'
    LEGEND_BG_COLOR = '#2C3E50'
    
    def __init__(self, db, controllers, user_role):
        super().__init__()
        self.db = db
        self.statistics_controller: StatisticsController = controllers['statistics']
        self.user_role = user_role
        self.current_mode = "revenue"
        
        # Initialize UI components as None
        self.month_filter = None
        self.year_filter = None
        self.revenue_btn = None
        self.customer_btn = None
        self.top_types_btn = None
        
        # Summary labels
        self.total_revenue_label = None
        self.total_sales_label = None
        self.avg_sale_label = None
        self.total_repair_revenue_label = None
        self.total_repairs_label = None
        self.completed_repairs_label = None
        self.total_customers_label = None
        self.repeat_customers_label = None
        self.new_customers_month_label = None
        
        # Groups
        self.sales_group = None
        self.repair_group = None
        self.customer_group = None
        self.chart_group = None
        
        # Chart components
        self.figure = None
        self.canvas = None
        
        self.init_ui()
        self.switch_statistics(self.current_mode)
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Create filter section
        self._create_filter_section(layout)
        
        # Create mode buttons
        self._create_mode_buttons(layout)
        
        # Create summary grid
        self._create_summary_grid(layout)
        
        # Add separator
        layout.addWidget(self._create_separator())
        
        # Create chart area
        self._create_chart_area(layout)
        
        self.setLayout(layout)

    def _create_filter_section(self, parent_layout):
        """Create the filter section with month and year selectors."""
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        
        # Month filter
        filter_layout.addWidget(QLabel('Tháng:'))
        self.month_filter = QComboBox()
        self.month_filter.addItems(['Tất cả'] + [str(i) for i in range(1, 13)])
        self.month_filter.setCurrentText(str(QDate.currentDate().month()))
        self.month_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.month_filter)

        # Year filter
        filter_layout.addWidget(QLabel('Năm:'))
        self.year_filter = QSpinBox()
        self.year_filter.setRange(2000, 2030)
        self.year_filter.setValue(QDate.currentDate().year())
        self.year_filter.valueChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.year_filter)

        filter_layout.addStretch()
        parent_layout.addLayout(filter_layout)

    def _create_mode_buttons(self, parent_layout):
        """Create mode selection buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Define button configurations
        buttons_config = [
            ('revenue', 'Doanh thu', 'Xem doanh thu bán hàng và sửa chữa theo thời gian'),
            ('customer', 'Khách hàng', 'Theo dõi khách hàng mới và khách hàng thân thiết'),
            ('top_types', 'Sản phẩm bán chạy', 'Thống kê top sản phẩm bán chạy trong giai đoạn chọn')
        ]
        
        QToolTip.setFont(self.font())
        
        for mode, text, tooltip in buttons_config:
            btn = QPushButton(text)
            btn.setFixedHeight(36)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, m=mode: self.switch_statistics(m))
            button_layout.addWidget(btn)
            
            # Store reference to button
            if mode == 'revenue':
                self.revenue_btn = btn
            elif mode == 'customer':
                self.customer_btn = btn
            elif mode == 'top_types':
                self.top_types_btn = btn
        
        button_layout.addStretch()
        parent_layout.addLayout(button_layout)

    def _create_summary_grid(self, parent_layout):
        """Create the summary statistics grid."""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        # Sales revenue group
        self.sales_group = self._create_group_box(
            'Doanh thu - Bán hàng',
            [
                ('total_revenue_label', 'Tổng doanh thu bán hàng: 0 VND'),
                ('total_sales_label', 'Tổng số hóa đơn bán hàng: 0'),
                ('avg_sale_label', 'Giá trị trung bình mỗi hóa đơn: 0 VND')
            ]
        )
        grid_layout.addWidget(self.sales_group, 0, 0)

        # Repair revenue group
        self.repair_group = self._create_group_box(
            'Doanh thu - Sửa chữa',
            [
                ('total_repair_revenue_label', 'Tổng doanh thu sửa chữa: 0 VND'),
                ('total_repairs_label', 'Tổng số đơn sửa chữa: 0'),
                ('completed_repairs_label', 'Đơn đã hoàn thành: 0')
            ]
        )
        grid_layout.addWidget(self.repair_group, 0, 1)

        # Customer group
        self.customer_group = self._create_group_box(
            'Thống kê khách hàng',
            [
                ('total_customers_label', 'Tổng số khách hàng: 0'),
                ('repeat_customers_label', 'Khách hàng thân thiết: 0'),
                ('new_customers_month_label', 'Khách hàng mới (tháng): 0')
            ]
        )
        grid_layout.addWidget(self.customer_group, 1, 0, 1, 2)

        parent_layout.addLayout(grid_layout)

    def _create_group_box(self, title, label_configs):
        """
        Create a group box with labels.
        
        Args:
            title: Title of the group box
            label_configs: List of tuples (attribute_name, initial_text)
        """
        group = QGroupBox(title)
        layout = QVBoxLayout()
        
        for attr_name, text in label_configs:
            label = QLabel(text)
            label.setStyleSheet("color: white;")
            layout.addWidget(label)
            setattr(self, attr_name, label)
        
        group.setLayout(layout)
        return group

    def _create_separator(self):
        """Create a horizontal separator line."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        return sep

    def _create_chart_area(self, parent_layout):
        """Create the chart display area."""
        self.chart_group = QGroupBox('Biểu đồ thống kê')
        chart_layout = QVBoxLayout()
        
        self.figure = Figure(dpi=100, tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(400, 300)
        chart_layout.addWidget(self.canvas)
        
        self.chart_group.setLayout(chart_layout)
        parent_layout.addWidget(self.chart_group)

    def on_filter_changed(self, *_):
        """Handle filter changes."""
        self.load_data()

    def load_data(self):
        """Load and display all statistics based on current filters."""
        month = self.month_filter.currentText()
        year = self.year_filter.value()
        
        self._load_revenue_statistics(month, year)
        self._load_customer_statistics(month, year)
        self.update_chart()

    def _load_revenue_statistics(self, month, year):
        """Load and update revenue statistics."""
        revenue_stats = self.statistics_controller.get_revenue_statistics(month, year)
        
        # Update sales labels
        self.total_revenue_label.setText(
            f'Tổng doanh thu bán hàng: {revenue_stats["sales_revenue"]:,.0f} VND'
        )
        self.total_sales_label.setText(
            f'Tổng số hóa đơn bán hàng: {revenue_stats["sales_count"]}'
        )
        
        avg_sale = (revenue_stats["sales_revenue"] / revenue_stats["sales_count"] 
                   if revenue_stats["sales_count"] > 0 else 0)
        self.avg_sale_label.setText(
            f'Giá trị trung bình mỗi hóa đơn: {avg_sale:,.0f} VND'
        )
        
        # Update repair labels
        self.total_repair_revenue_label.setText(
            f'Tổng doanh thu sửa chữa: {revenue_stats["repair_revenue"]:,.0f} VND'
        )
        self.total_repairs_label.setText(
            f'Tổng số đơn sửa chữa: {revenue_stats["repair_count"]}'
        )
        self.completed_repairs_label.setText(
            f'Đơn đã hoàn thành: {revenue_stats["completed_repairs"]}'
        )

    def _load_customer_statistics(self, month, year):
        """Load and update customer statistics."""
        customer_stats = self.statistics_controller.get_customer_statistics(month, year)
        
        self.total_customers_label.setText(
            f'Tổng số khách hàng: {customer_stats["total_customers"]}'
        )
        self.repeat_customers_label.setText(
            f'Khách hàng thân thiết: {customer_stats["repeat_customers"]}'
        )
        self.new_customers_month_label.setText(
            f'Khách hàng mới (tháng): {customer_stats["new_customers"]}'
        )

    def switch_statistics(self, mode):
        """Switch between different statistics modes."""
        self.current_mode = mode
        
        # Update visibility of groups
        visibility_map = {
            "revenue": (True, True, False),
            "customer": (False, False, True),
            "top_types": (False, False, False)
        }
        
        if mode in visibility_map:
            sales_vis, repair_vis, customer_vis = visibility_map[mode]
            self.sales_group.setVisible(sales_vis)
            self.repair_group.setVisible(repair_vis)
            self.customer_group.setVisible(customer_vis)
        
        self.update_button_styles()
        self.update_chart()

    def update_button_styles(self):
        """Update button styles based on current mode."""
        button_map = {
            "revenue": self.revenue_btn,
            "customer": self.customer_btn,
            "top_types": self.top_types_btn
        }
        
        for mode, btn in button_map.items():
            style = self.ACTIVE_BTN_STYLE if self.current_mode == mode else self.INACTIVE_BTN_STYLE
            btn.setStyleSheet(style)

    def update_chart(self):
        """Update the chart based on current mode and filters."""
        month = self.month_filter.currentText()
        year = self.year_filter.value()

        self.figure.clear()
        self.figure.patch.set_facecolor(self.CHART_BG_COLOR)
        
        chart_methods = {
            "revenue": self._draw_revenue_chart,
            "customer": self._draw_customer_chart,
            "top_types": self._draw_top_products_chart
        }
        
        if self.current_mode in chart_methods:
            ax = chart_methods[self.current_mode](month, year)
            if ax:
                # Let tight_layout handle positioning automatically
                pass
        
        self.canvas.draw_idle()

    def _draw_revenue_chart(self, month, year):
        """Draw the revenue chart."""
        if month == 'Tất cả':
            breakdown = self.statistics_controller.get_monthly_revenue_breakdown(year)
            labels = [f'T{int(item[0])}' for item in breakdown]
            x_label = 'Tháng'
            title = f'Doanh thu bán hàng & sửa chữa năm {year}'
            rotation = 0
        else:
            breakdown = self.statistics_controller.get_daily_revenue_breakdown(month, year)
            labels = [str(int(item[0])) for item in breakdown]
            x_label = 'Ngày'
            title = f'Doanh thu bán hàng & sửa chữa tháng {month}/{year}'
            rotation = 45

        if not breakdown:
            return self._draw_no_data_message('Không có dữ liệu doanh thu trong khoảng thời gian này')
        
        sales_data = [item[1] for item in breakdown]
        repair_data = [item[2] for item in breakdown]
        
        return self._draw_line_chart(
            labels, [sales_data, repair_data],
            ['Doanh thu bán hàng', 'Doanh thu sửa chữa'],
            ['#3498DB', '#E74C3C'],
            ['o', 's'],
            x_label, 'Doanh thu (VND)', title, rotation
        )

    def _draw_customer_chart(self, month, year):
        """Draw the customer trends chart."""
        if month == 'Tất cả':
            trends = self.statistics_controller.get_monthly_customer_trends(year)
            labels = [f'T{int(item[0])}' for item in trends]
            x_label = 'Tháng'
            title = f'Khách hàng mới & thân thiết năm {year}'
            rotation = 0
        else:
            trends = self.statistics_controller.get_daily_customer_trends(month, year)
            labels = [str(int(item[0])) for item in trends]
            x_label = 'Ngày'
            title = f'Khách hàng tháng {month}/{year}'
            rotation = 45

        if not trends:
            return self._draw_no_data_message('Không có dữ liệu khách hàng trong khoảng thời gian này')
        
        new_data = [item[1] for item in trends]
        repeat_data = [item[2] for item in trends]
        
        return self._draw_line_chart(
            labels, [new_data, repeat_data],
            ['Khách hàng mới', 'Khách hàng thân thiết'],
            ['#3498DB', '#E74C3C'],
            ['o', 's'],
            x_label, 'Số lượng khách hàng', title, rotation
        )

    def _draw_top_products_chart(self, month, year):
        """Draw the top products bar chart."""
        top_products = self.statistics_controller.get_top_products(month, year, 5)
        
        title = (f'Top sản phẩm bán chạy năm {year}' if month == 'Tất cả'
                else f'Top sản phẩm bán chạy tháng {month}/{year}')
        
        if not top_products:
            return self._draw_no_data_message('Không có dữ liệu sản phẩm bán chạy')
        
        products = [p[0] for p in top_products]
        quantities = [p[1] for p in top_products]
        colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6']

        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.CHART_BG_COLOR)
        
        y_pos = np.arange(len(products))
        bars = ax.barh(y_pos, quantities, color=colors[:len(products)])
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(products, color='white')
        ax.invert_yaxis()
        ax.set_xlabel('Số lượng bán', color='white')
        ax.tick_params(axis='x', colors='white')
        ax.set_title(title, color='white', fontsize=12, fontweight='bold')

        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)}', ha='left', va='center', color='white')
        
        return ax

    def _draw_line_chart(self, labels, data_series, legend_labels, colors, markers, 
                        x_label, y_label, title, rotation):
        """
        Draw a line chart with multiple series.
        
        Args:
            labels: X-axis labels
            data_series: List of data series to plot
            legend_labels: Labels for legend
            colors: Colors for each series
            markers: Marker styles for each series
            x_label: X-axis label
            y_label: Y-axis label
            title: Chart title
            rotation: Label rotation angle
        """
        x = np.arange(len(labels))
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.CHART_BG_COLOR)
        
        # Plot each series
        for data, label, color, marker in zip(data_series, legend_labels, colors, markers):
            ax.plot(x, data, marker=marker, label=label, color=color, linewidth=2)
        
        # Configure axes
        ax.set_xticks(x)
        ax.set_xticklabels(labels, color='white', rotation=rotation)
        ax.set_ylabel(y_label, color='white')
        ax.set_xlabel(x_label, color='white')
        ax.tick_params(axis='y', colors='white', labelcolor='white')
        ax.grid(True, alpha=0.3, color='white')
        ax.set_title(title, color='white', fontsize=12, fontweight='bold')
        
        # Format y-axis for currency if needed
        if 'VND' in y_label:
            ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
        
        # Configure legend
        legend = ax.legend(frameon=True)
        legend.get_frame().set_facecolor(self.LEGEND_BG_COLOR)
        legend.get_frame().set_edgecolor('white')
        for text in legend.get_texts():
            text.set_color('white')
        
        return ax

    def _draw_no_data_message(self, message):
        """Draw a message when no data is available."""
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.CHART_BG_COLOR)
        ax.text(0.5, 0.5, message, ha='center', va='center', color='white')
        return ax
    
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Use timer to debounce resize events
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.draw_idle()