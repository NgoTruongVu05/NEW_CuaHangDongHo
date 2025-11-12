import re

class Validators:
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        phone = re.sub(r'[\s\-\(\)\.]', '', phone)
        patterns = [
            r'^0[3|5|7|8|9][0-9]{8}$',
            r'^0[3|5|7|8|9][0-9]{9}$',
            r'^\+84[3|5|7|8|9][0-9]{8}$',
            r'^\+84[3|5|7|8|9][0-9]{9}$',
            r'^84[3|5|7|8|9][0-9]{8}$',
            r'^84[3|5|7|8|9][0-9]{9}$'
        ]
        return any(re.match(pattern, phone) for pattern in patterns)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def is_valid_price(price: str) -> bool:
        try:
            price_value = float(price.replace('.', '').replace(',', ''))
            return price_value >= 0
        except:
            return False

    @staticmethod
    def is_valid_quantity(quantity: str) -> bool:
        try:
            quantity_value = int(quantity)
            return quantity_value >= 0
        except:
            return False