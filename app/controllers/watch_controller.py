from typing import List, Optional, Tuple, Union
from app.models.watch import Watch
from app.models.mechanical_watch import MechanicalWatch
from app.models.electronic_watch import ElectronicWatch
from app.services.watch_service import WatchService
from app.services.brand_service import BrandService

class WatchController:
    def __init__(self, watch_service: WatchService, brand_service: BrandService):
        self.watch_service = watch_service
        self.brand_service = brand_service
    
    def get_all_watches(self) -> List[Union[MechanicalWatch, ElectronicWatch]]:
        return self.watch_service.get_all_watches()
    
    def get_watch_by_id(self, watch_id: str) -> Optional[Union[MechanicalWatch, ElectronicWatch]]:
        return self.watch_service.get_watch_by_id(watch_id)
    
    def get_available_watches(self) -> List[Union[MechanicalWatch, ElectronicWatch]]:
        return self.watch_service.get_available_watches()
    
    def create_mechanical_watch(self, name: str, brand_name: str, price: float, 
                              quantity: int, description: str = "", movement_type: str = "",
                              power_reserve: int = 0, water_resistant: bool = False) -> Tuple[bool, str]:
        # Validate input
        if not name.strip():
            return False, "Tên sản phẩm không được để trống"
        
        if not brand_name.strip():
            return False, "Thương hiệu không được để trống"
        
        if price <= 0:
            return False, "Giá phải lớn hơn 0"
        
        if quantity < 0:
            return False, "Số lượng không được âm"
        
        # Get or create brand
        brand = self.brand_service.get_brand_by_name(brand_name)
        if not brand:
            return False, "Thương hiệu không tồn tại"
        
        watch = MechanicalWatch(
            name=name,
            brand_id=brand.id,
            price=price,
            quantity=quantity,
            description=description,
            movement_type=movement_type,
            power_reserve=power_reserve,
            water_resistant=water_resistant
        )
        
        success = self.watch_service.create_watch(watch)
        if success:
            return True, "Thêm đồng hồ cơ thành công"
        else:
            return False, "Lỗi khi thêm đồng hồ cơ"
    
    def create_electronic_watch(self, name: str, brand_name: str, price: float,
                              quantity: int, description: str = "", battery_life: int = 0,
                              features: List[str] = None, connectivity: str = "") -> Tuple[bool, str]:
        # Validate input
        if not name.strip():
            return False, "Tên sản phẩm không được để trống"
        
        if not brand_name.strip():
            return False, "Thương hiệu không được để trống"
        
        if price <= 0:
            return False, "Giá phải lớn hơn 0"
        
        if quantity < 0:
            return False, "Số lượng không được âm"
        
        # Get or create brand
        brand = self.brand_service.get_brand_by_name(brand_name)
        if not brand:
            return False, "Thương hiệu không tồn tại"
        
        watch = ElectronicWatch(
            name=name,
            brand_id=brand.id,
            price=price,
            quantity=quantity,
            description=description,
            battery_life=battery_life,
            features=features or [],
            connectivity=connectivity
        )
        
        success = self.watch_service.create_watch(watch)
        if success:
            return True, "Thêm đồng hồ điện tử thành công"
        else:
            return False, "Lỗi khi thêm đồng hồ điện tử"
    
    def update_mechanical_watch(self, watch_id: str, name: str, brand_name: str, price: float,
                              quantity: int, description: str = "", movement_type: str = "",
                              power_reserve: int = 0, water_resistant: bool = False) -> Tuple[bool, str]:
        # Validate input
        if not name.strip():
            return False, "Tên sản phẩm không được để trống"
        
        if not brand_name.strip():
            return False, "Thương hiệu không được để trống"
        
        if price <= 0:
            return False, "Giá phải lớn hơn 0"
        
        if quantity < 0:
            return False, "Số lượng không được âm"
        
        # Get brand
        brand = self.brand_service.get_brand_by_name(brand_name)
        if not brand:
            return False, "Thương hiệu không tồn tại"
        
        watch = MechanicalWatch(
            id=watch_id,
            name=name,
            brand_id=brand.id,
            price=price,
            quantity=quantity,
            description=description,
            movement_type=movement_type,
            power_reserve=power_reserve,
            water_resistant=water_resistant
        )
        
        success = self.watch_service.update_watch(watch)
        if success:
            return True, "Cập nhật đồng hồ cơ thành công"
        else:
            return False, "Lỗi khi cập nhật đồng hồ cơ"
    
    def update_electronic_watch(self, watch_id: str, name: str, brand_name: str, price: float,
                              quantity: int, description: str = "", battery_life: int = 0,
                              features: List[str] = None, connectivity: str = "") -> Tuple[bool, str]:
        # Validate input
        if not name.strip():
            return False, "Tên sản phẩm không được để trống"
        
        if not brand_name.strip():
            return False, "Thương hiệu không được để trống"
        
        if price <= 0:
            return False, "Giá phải lớn hơn 0"
        
        if quantity < 0:
            return False, "Số lượng không được âm"
        
        # Get brand
        brand = self.brand_service.get_brand_by_name(brand_name)
        if not brand:
            return False, "Thương hiệu không tồn tại"
        
        watch = ElectronicWatch(
            id=watch_id,
            name=name,
            brand_id=brand.id,
            price=price,
            quantity=quantity,
            description=description,
            battery_life=battery_life,
            features=features or [],
            connectivity=connectivity
        )
        
        success = self.watch_service.update_watch(watch)
        if success:
            return True, "Cập nhật đồng hồ điện tử thành công"
        else:
            return False, "Lỗi khi cập nhật đồng hồ điện tử"
    
    def delete_watch(self, watch_id: str) -> Tuple[bool, str]:
        # Check if watch has been sold
        # This would require additional service method to check sales history
        success = self.watch_service.delete_watch(watch_id)
        if success:
            return True, "Xóa sản phẩm thành công"
        else:
            return False, "Lỗi khi xóa sản phẩm"
    
    def search_watches(self, search_text: str) -> List[Union[MechanicalWatch, ElectronicWatch]]:
        all_watches = self.get_all_watches()
        
        if not search_text:
            return all_watches
        
        search_text = search_text.lower()
        return [w for w in all_watches if search_text in w.name.lower()]
    
    def filter_watches(self, brand_filter: str, type_filter: str, 
                      price_min: float = None, price_max: float = None) -> List[Union[MechanicalWatch, ElectronicWatch]]:
        all_watches = self.get_all_watches()
        filtered_watches = all_watches
        
        # Filter by brand
        if brand_filter != 'Tất cả':
            filtered_watches = [w for w in filtered_watches 
                              if self._get_brand_name(w.brand_id) == brand_filter]
        
        # Filter by type
        if type_filter != 'Tất cả':
            if type_filter == 'Đồng hồ cơ':
                filtered_watches = [w for w in filtered_watches if isinstance(w, MechanicalWatch)]
            elif type_filter == 'Đồng hồ điện tử':
                filtered_watches = [w for w in filtered_watches if isinstance(w, ElectronicWatch)]
        
        # Filter by price
        if price_min is not None:
            filtered_watches = [w for w in filtered_watches if w.price >= price_min]
        
        if price_max is not None:
            filtered_watches = [w for w in filtered_watches if w.price <= price_max]
        
        return filtered_watches
    
    def _get_brand_name(self, brand_id: str) -> str:
        brand = self.brand_service.get_brand_by_id(brand_id)
        return brand.name if brand else "Unknown"