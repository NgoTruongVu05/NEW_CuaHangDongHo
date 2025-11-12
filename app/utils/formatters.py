from datetime import datetime

class Formatters:
    @staticmethod
    def format_currency(amount: float) -> str:
        return f"{amount:,.0f} VND"
    
    @staticmethod
    def format_date(date_str: str) -> str:
        if not date_str:
            return ''
        for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d'):
            try:
                return datetime.strptime(date_str, fmt).strftime('%d/%m/%Y')
            except:
                continue
        return date_str
    
    @staticmethod
    def format_phone(phone: str) -> str:
        if not phone:
            return ''
        # Simple phone formatting
        if phone.startswith('+84'):
            return f"+84 {phone[3:6]} {phone[6:9]} {phone[9:]}"
        elif phone.startswith('84'):
            return f"+84 {phone[2:5]} {phone[5:8]} {phone[8:]}"
        elif phone.startswith('0'):
            return f"0{phone[1:4]} {phone[4:7]} {phone[7:]}"
        return phone
    
    @staticmethod
    def parse_currency(currency_str: str) -> float:
        try:
            return float(currency_str.replace(' VND', '').replace(',', '').replace('.', ''))
        except:
            return 0.0