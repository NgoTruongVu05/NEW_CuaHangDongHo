from typing import List, Optional, Tuple
from app.models.brand import Brand
from app.services.brand_service import BrandService

class BrandController:
    def __init__(self, brand_service: BrandService):
        self.brand_service = brand_service
    
    def get_all_brands(self) -> List[Brand]:
        return self.brand_service.get_all_brands()
    
    def get_brand_by_id(self, brand_id: str) -> Optional[Brand]:
        return self.brand_service.get_brand_by_id(brand_id)
    
    def get_brand_by_name(self, name: str) -> Optional[Brand]:
        return self.brand_service.get_brand_by_name(name)
    
    def create_brand(self, name: str, country: str = "") -> Tuple[bool, str]:
        if not name.strip():
            return False, "Tên thương hiệu không được để trống"
        
        # Check if brand already exists
        existing_brand = self.get_brand_by_name(name)
        if existing_brand:
            return False, "Thương hiệu đã tồn tại"
        
        brand = Brand(name=name, country=country)
        success = self.brand_service.create_brand(brand)
        
        if success:
            return True, "Thêm thương hiệu thành công"
        else:
            return False, "Lỗi khi thêm thương hiệu"
    
    def update_brand(self, brand_id: str, name: str, country: str = "") -> Tuple[bool, str]:
        if not name.strip():
            return False, "Tên thương hiệu không được để trống"
        
        brand = Brand(id=brand_id, name=name, country=country)
        success = self.brand_service.update_brand(brand)
        
        if success:
            return True, "Cập nhật thương hiệu thành công"
        else:
            return False, "Lỗi khi cập nhật thương hiệu"
    
    def delete_brand(self, brand_id: str) -> Tuple[bool, str]:
        # Check if brand is used by any products
        if self.brand_service.is_brand_used(brand_id):
            return False, "Không thể xóa thương hiệu đang được sử dụng bởi sản phẩm"
        
        success = self.brand_service.delete_brand(brand_id)
        if success:
            return True, "Xóa thương hiệu thành công"
        else:
            return False, "Lỗi khi xóa thương hiệu"