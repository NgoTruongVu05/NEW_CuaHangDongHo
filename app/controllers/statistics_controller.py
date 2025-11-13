from typing import Dict, List, Tuple
from app.services.statistics_service import StatisticsService

class StatisticsController:
    def __init__(self, statistics_service: StatisticsService):
        self.statistics_service = statistics_service
    
    def get_revenue_statistics(self, month: str, year: int) -> Dict:
        return self.statistics_service.get_revenue_statistics(month, year)
    
    def get_customer_statistics(self, month: str, year: int) -> Dict:
        return self.statistics_service.get_customer_statistics(month, year)
    
    def get_top_products(self, month: str, year: int, limit: int = 5) -> List[Tuple]:
        return self.statistics_service.get_top_products(month, year, limit)
    
    def get_monthly_revenue(self, year: int) -> List[Tuple]:
        return self.statistics_service.get_monthly_revenue(year)

    def get_monthly_revenue_breakdown(self, year: int) -> List[Tuple[str, float, float]]:
        return self.statistics_service.get_monthly_revenue_breakdown(year)

    def get_daily_revenue_breakdown(self, month: str, year: int) -> List[Tuple[str, float, float]]:
        return self.statistics_service.get_daily_revenue_breakdown(month, year)

    def get_monthly_customer_trends(self, year: int) -> List[Tuple[str, int, int]]:
        return self.statistics_service.get_monthly_customer_trends(year)

    def get_daily_customer_trends(self, month: str, year: int) -> List[Tuple[str, int, int]]:
        return self.statistics_service.get_daily_customer_trends(month, year)