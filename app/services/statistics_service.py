from typing import List, Tuple, Dict
from app.utils.database import Database

class StatisticsService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_revenue_statistics(self, month: str, year: int) -> Dict:
        cursor = self.db.conn.cursor()
        
        # Sales revenue
        if month == 'Tất cả':
            cursor.execute('''
                SELECT IFNULL(SUM(total_amount), 0), COUNT(*) 
                FROM invoices 
                WHERE strftime("%Y", created_date) = ?
            ''', (str(year),))
        else:
            cursor.execute('''
                SELECT IFNULL(SUM(total_amount), 0), COUNT(*) 
                FROM invoices 
                WHERE strftime("%Y", created_date) = ? AND strftime("%m", created_date) = ?
            ''', (str(year), month.zfill(2)))
        
        sales_result = cursor.fetchone()
        sales_revenue = sales_result[0] if sales_result else 0
        sales_count = sales_result[1] if sales_result else 0
        
        # Repair revenue
        if month == 'Tất cả':
            cursor.execute('''
                SELECT IFNULL(SUM(actual_cost), 0), COUNT(*), 
                       SUM(CASE WHEN status = "Hoàn thành" THEN 1 ELSE 0 END)
                FROM repair_orders 
                WHERE strftime("%Y", created_date) = ?
            ''', (str(year),))
        else:
            cursor.execute('''
                SELECT IFNULL(SUM(actual_cost), 0), COUNT(*),
                       SUM(CASE WHEN status = "Hoàn thành" THEN 1 ELSE 0 END)
                FROM repair_orders 
                WHERE strftime("%Y", created_date) = ? AND strftime("%m", created_date) = ?
            ''', (str(year), month.zfill(2)))
        
        repair_result = cursor.fetchone()
        repair_revenue = repair_result[0] if repair_result else 0
        repair_count = repair_result[1] if repair_result else 0
        completed_repairs = repair_result[2] if repair_result else 0
        
        return {
            'sales_revenue': sales_revenue,
            'sales_count': sales_count,
            'repair_revenue': repair_revenue,
            'repair_count': repair_count,
            'completed_repairs': completed_repairs
        }
    
    def get_customer_statistics(self, month: str, year: int) -> Dict:
        cursor = self.db.conn.cursor()
        
        # Total customers
        cursor.execute('SELECT COUNT(*) FROM customers')
        total_customers = cursor.fetchone()[0] or 0
        
        # Repeat customers
        cursor.execute('''
            SELECT COUNT(*) FROM (
                SELECT customer_id FROM invoices 
                WHERE customer_id IS NOT NULL
                GROUP BY customer_id HAVING COUNT(*) > 1
            )
        ''')
        repeat_customers = cursor.fetchone()[0] or 0
        
        # New customers
        if month == 'Tất cả':
            cursor.execute('''
                SELECT COUNT(*) FROM (
                    SELECT customer_id, MIN(created_date) as first_date 
                    FROM invoices
                    WHERE customer_id IS NOT NULL
                    GROUP BY customer_id
                    HAVING strftime('%Y', first_date) = ?
                )
            ''', (str(year),))
        else:
            cursor.execute('''
                SELECT COUNT(*) FROM (
                    SELECT customer_id, MIN(created_date) as first_date 
                    FROM invoices
                    WHERE customer_id IS NOT NULL
                    GROUP BY customer_id
                    HAVING strftime('%Y', first_date) = ? AND strftime('%m', first_date) = ?
                )
            ''', (str(year), month.zfill(2)))
        
        new_customers = cursor.fetchone()[0] or 0
        
        return {
            'total_customers': total_customers,
            'repeat_customers': repeat_customers,
            'new_customers': new_customers
        }
    
    def get_top_products(self, month: str, year: int, limit: int = 5) -> List[Tuple]:
        cursor = self.db.conn.cursor()
        
        if month == 'Tất cả':
            cursor.execute('''
                SELECT p.name, SUM(id.quantity) as sold_qty
                FROM invoice_details id
                JOIN products p ON p.id = id.product_id
                JOIN invoices inv ON inv.id = id.invoice_id
                WHERE strftime('%Y', inv.created_date) = ?
                GROUP BY p.name 
                ORDER BY sold_qty DESC 
                LIMIT ?
            ''', (str(year), limit))
        else:
            cursor.execute('''
                SELECT p.name, SUM(id.quantity) as sold_qty
                FROM invoice_details id
                JOIN products p ON p.id = id.product_id
                JOIN invoices inv ON inv.id = id.invoice_id
                WHERE strftime('%Y', inv.created_date) = ? AND strftime('%m', inv.created_date) = ?
                GROUP BY p.name 
                ORDER BY sold_qty DESC 
                LIMIT ?
            ''', (str(year), month.zfill(2), limit))
        
        return cursor.fetchall()
    
    def get_monthly_revenue(self, year: int) -> List[Tuple]:
        cursor = self.db.conn.cursor()
        
        cursor.execute('''
            SELECT strftime('%m', created_date) as month, 
                   COALESCE(SUM(total_amount), 0) as revenue
            FROM invoices 
            WHERE strftime('%Y', created_date) = ?
            GROUP BY month
            ORDER BY month
        ''', (str(year),))
        
        return cursor.fetchall()

    def get_monthly_revenue_breakdown(self, year: int) -> List[Tuple[str, float, float]]:
        """
        Return list of (month, sales_revenue, repair_revenue)
        """
        cursor = self.db.conn.cursor()

        cursor.execute('''
            SELECT strftime('%m', created_date) AS month, COALESCE(SUM(total_amount), 0)
            FROM invoices
            WHERE strftime('%Y', created_date) = ?
            GROUP BY month
        ''', (str(year),))
        sales_map = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute('''
            SELECT strftime('%m', created_date) AS month, COALESCE(SUM(actual_cost), 0)
            FROM repair_orders
            WHERE strftime('%Y', created_date) = ?
            GROUP BY month
        ''', (str(year),))
        repair_map = {row[0]: row[1] for row in cursor.fetchall()}

        breakdown = []
        for month in range(1, 13):
            mm = f'{month:02d}'
            breakdown.append((mm, sales_map.get(mm, 0), repair_map.get(mm, 0)))

        return breakdown

    def get_daily_revenue_breakdown(self, month: str, year: int) -> List[Tuple[str, float, float]]:
        """
        Return list of (day, sales_revenue, repair_revenue) for a given month/year
        """
        mm = month.zfill(2)
        cursor = self.db.conn.cursor()

        cursor.execute('''
            SELECT strftime('%d', created_date) AS day, COALESCE(SUM(total_amount), 0)
            FROM invoices
            WHERE strftime('%Y', created_date) = ? AND strftime('%m', created_date) = ?
            GROUP BY day
            ORDER BY day
        ''', (str(year), mm))
        sales_rows = cursor.fetchall()
        sales_map = {row[0]: row[1] for row in sales_rows}

        cursor.execute('''
            SELECT strftime('%d', created_date) AS day, COALESCE(SUM(actual_cost), 0)
            FROM repair_orders
            WHERE strftime('%Y', created_date) = ? AND strftime('%m', created_date) = ?
            GROUP BY day
            ORDER BY day
        ''', (str(year), mm))
        repair_rows = cursor.fetchall()
        repair_map = {row[0]: row[1] for row in repair_rows}

        all_days = sorted(set(sales_map.keys()) | set(repair_map.keys()), key=lambda d: int(d))
        breakdown = [(day, sales_map.get(day, 0), repair_map.get(day, 0)) for day in all_days]
        return breakdown

    def get_monthly_customer_trends(self, year: int) -> List[Tuple[str, int, int]]:
        """
        Return list of (month, new_customers, repeat_customers)
        """
        cursor = self.db.conn.cursor()

        # New customers: customers whose first purchase was in this month
        months = [f'{i:02d}' for i in range(1, 13)]
        new_map = {}
        for m in months:
            cursor.execute('''
                SELECT COUNT(*) FROM (
                    SELECT customer_id, MIN(created_date) as first_date FROM invoices
                    WHERE customer_id IS NOT NULL
                    GROUP BY customer_id
                    HAVING strftime('%Y', first_date)=? AND strftime('%m', first_date)=?
                )
            ''', (str(year), m))
            result = cursor.fetchone()
            new_map[m] = result[0] if result else 0

        # Repeat customers: customers who have more than 1 invoice total and made a purchase in this month
        repeat_map = {}
        for m in months:
            cursor.execute('''
                SELECT COUNT(DISTINCT customer_id) FROM invoices 
                WHERE strftime("%m", created_date)=? AND strftime("%Y", created_date)=? 
                AND customer_id IN (
                    SELECT customer_id FROM invoices GROUP BY customer_id HAVING COUNT(*)>1
                )
            ''', (m, str(year)))
            result = cursor.fetchone()
            repeat_map[m] = result[0] if result else 0

        trends = []
        for month in range(1, 13):
            mm = f'{month:02d}'
            trends.append((mm, new_map.get(mm, 0), repeat_map.get(mm, 0)))

        return trends

    def get_daily_customer_trends(self, month: str, year: int) -> List[Tuple[str, int, int]]:
        """
        Return list of (day, new_customers, repeat_customers) for given month/year
        Includes all days in the month, even if there's no data
        """
        import calendar
        mm = month.zfill(2)
        cursor = self.db.conn.cursor()

        # Get number of days in the month
        month_int = int(month)
        num_days = calendar.monthrange(year, month_int)[1]
        all_days = [f'{d:02d}' for d in range(1, num_days + 1)]

        # Query daily new customers: customers whose first purchase was on this day
        cursor.execute('''
            SELECT strftime('%d', first_date) as d, COUNT(*) FROM (
                SELECT customer_id, MIN(created_date) as first_date FROM invoices
                WHERE customer_id IS NOT NULL
                GROUP BY customer_id
                HAVING strftime('%Y', first_date)=? AND strftime('%m', first_date)=?
            ) GROUP BY d ORDER BY d
        ''', (str(year), mm))
        new_rows = cursor.fetchall()
        new_map = {row[0]: row[1] for row in new_rows}

        # Query daily repeat customers: customers who have >1 invoice total and made a purchase on this day
        cursor.execute('''
            SELECT strftime('%d', created_date) as d, COUNT(DISTINCT customer_id) FROM invoices
            WHERE strftime('%Y', created_date)=? AND strftime('%m', created_date)=?
            AND customer_id IN (
                SELECT customer_id FROM invoices GROUP BY customer_id HAVING COUNT(*)>1
            )
            GROUP BY d ORDER BY d
        ''', (str(year), mm))
        rep_rows = cursor.fetchall()
        rep_map = {row[0]: row[1] for row in rep_rows}

        # Create trends for all days in the month
        trends = [(day, new_map.get(day, 0), rep_map.get(day, 0)) for day in all_days]

        return trends