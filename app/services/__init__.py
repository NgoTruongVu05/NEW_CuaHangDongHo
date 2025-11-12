# Services package
from .customer_service import CustomerService
from .employee_service import EmployeeService
from .watch_service import WatchService
from .brand_service import BrandService
from .sales_service import SalesService
from .repair_service import RepairService
from .invoice_service import InvoiceService
from .salary_service import SalaryService
from .statistics_service import StatisticsService

__all__ = [
    'CustomerService', 'EmployeeService', 'WatchService', 'BrandService',
    'SalesService', 'RepairService', 'InvoiceService', 'SalaryService',
    'StatisticsService'
]