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