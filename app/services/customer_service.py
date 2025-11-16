from typing import List, Optional
from app.models.customer import Customer
from app.utils.database import Database

class CustomerService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_customers(self) -> List[Customer]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers ORDER BY id')
        customers_data = cursor.fetchall()
        
        customers = []
        for data in customers_data:
            customer = Customer(
                id=str(data[0]),
                name=data[1],
                phone=data[2],
                email=data[3],
                address=data[4]
            )
            customers.append(customer)
        return customers
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        data = cursor.fetchone()
        
        if data:
            return Customer(
                id=str(data[0]),
                name=data[1],
                phone=data[2],
                email=data[3],
                address=data[4]
            )
        return None
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
        data = cursor.fetchone()
        
        if data:
            return Customer(
                id=str(data[0]),
                name=data[1],
                phone=data[2],
                email=data[3],
                address=data[4]
            )
        return None
    
    def create_customer(self, customer: Customer) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO customers (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            ''', (customer.name, customer.phone, customer.email, customer.address))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating customer: {e}")
            return False
    
    def update_customer(self, customer: Customer) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE customers SET name=?, phone=?, email=?, address=?
                WHERE id=?
            ''', (customer.name, customer.phone, customer.email, customer.address, customer.id))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating customer: {e}")
            return False
    
    def delete_customer(self, customer_id: str) -> bool:
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False
    
    def is_phone_exists(self, phone: str, exclude_customer_id: Optional[str] = None) -> bool:
        cursor = self.db.conn.cursor()
        if exclude_customer_id:
            cursor.execute('SELECT id FROM customers WHERE phone = ? AND id != ?', 
                         (phone, exclude_customer_id))
        else:
            cursor.execute('SELECT id FROM customers WHERE phone = ?', (phone,))
        return cursor.fetchone() is not None
    
    def is_email_exists(self, email: str, exclude_customer_id: Optional[str] = None) -> bool:
        if not email:
            return False
        cursor = self.db.conn.cursor()
        if exclude_customer_id:
            cursor.execute('SELECT id FROM customers WHERE email = ? AND id != ?', 
                         (email, exclude_customer_id))
        else:
            cursor.execute('SELECT id FROM customers WHERE email = ?', (email,))
        return cursor.fetchone() is not None
    
    def is_customer_has_invoices(self, customer_id: str) -> bool:
        """Kiểm tra xem khách hàng có tồn tại trong hóa đơn không"""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM invoices WHERE customer_id = ?', (customer_id,))
        count = cursor.fetchone()[0]
        return count > 0