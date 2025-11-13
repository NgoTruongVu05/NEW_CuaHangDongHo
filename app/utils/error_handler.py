"""
Error handling utilities for the application
"""
import logging
import traceback
from typing import Optional, Tuple
import sqlite3

# Setup logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/error.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class FileError(Exception):
    """Custom exception for file operation errors"""
    pass


def handle_database_error(e: Exception, operation: str) -> Tuple[bool, str]:
    """
    Handle database-related errors
    
    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    error_msg = f"Lỗi khi {operation}"
    
    if isinstance(e, sqlite3.IntegrityError):
        if "UNIQUE constraint" in str(e):
            error_msg = f"Lỗi: Dữ liệu đã tồn tại trong hệ thống"
        elif "FOREIGN KEY constraint" in str(e):
            error_msg = f"Lỗi: Không thể thực hiện thao tác do ràng buộc dữ liệu"
        elif "NOT NULL constraint" in str(e):
            error_msg = f"Lỗi: Thiếu thông tin bắt buộc"
        else:
            error_msg = f"Lỗi: Vi phạm ràng buộc dữ liệu"
    elif isinstance(e, sqlite3.OperationalError):
        error_msg = f"Lỗi: Không thể kết nối hoặc thao tác với cơ sở dữ liệu"
    elif isinstance(e, sqlite3.DatabaseError):
        error_msg = f"Lỗi: Lỗi cơ sở dữ liệu"
    else:
        error_msg = f"Lỗi không xác định khi {operation}"
    
    # Log the full error
    logger.error(f"Database error in {operation}: {str(e)}\n{traceback.format_exc()}")
    
    return False, error_msg


def handle_file_error(e: Exception, operation: str, file_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Handle file operation errors
    
    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        file_path: Path to the file (optional)
        
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    error_msg = f"Lỗi khi {operation}"
    
    if isinstance(e, FileNotFoundError):
        error_msg = f"Không tìm thấy file: {file_path or 'file không xác định'}"
    elif isinstance(e, PermissionError):
        error_msg = f"Không có quyền truy cập file: {file_path or 'file không xác định'}"
    elif isinstance(e, UnicodeDecodeError):
        error_msg = f"Lỗi đọc file: File không đúng định dạng hoặc mã hóa"
    elif isinstance(e, IOError):
        error_msg = f"Lỗi đọc/ghi file: {str(e)}"
    else:
        error_msg = f"Lỗi không xác định khi {operation}"
    
    # Log the full error
    logger.error(f"File error in {operation}: {str(e)}\n{traceback.format_exc()}")
    
    return False, error_msg


def handle_validation_error(e: Exception, field: Optional[str] = None) -> Tuple[bool, str]:
    """
    Handle validation errors
    
    Args:
        e: The exception that occurred
        field: Name of the field that failed validation (optional)
        
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    if isinstance(e, ValueError):
        error_msg = f"Giá trị không hợp lệ" + (f" cho trường {field}" if field else "")
    elif isinstance(e, TypeError):
        error_msg = f"Kiểu dữ liệu không đúng" + (f" cho trường {field}" if field else "")
    else:
        error_msg = f"Lỗi xác thực dữ liệu" + (f" cho trường {field}" if field else "")
    
    logger.warning(f"Validation error: {str(e)}")
    
    return False, error_msg


def handle_generic_error(e: Exception, operation: str) -> Tuple[bool, str]:
    """
    Handle generic errors
    
    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    error_msg = f"Lỗi không xác định khi {operation}: {str(e)}"
    
    # Log the full error
    logger.error(f"Error in {operation}: {str(e)}\n{traceback.format_exc()}")
    
    return False, error_msg


def safe_execute(func, operation: str, error_type: str = "generic", *args, **kwargs):
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        operation: Description of the operation
        error_type: Type of error handling ('database', 'file', 'validation', 'generic')
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Tuple of (success: bool, result or error_message)
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except sqlite3.Error as e:
        return handle_database_error(e, operation)
    except (FileNotFoundError, PermissionError, IOError, UnicodeDecodeError) as e:
        return handle_file_error(e, operation)
    except (ValueError, TypeError) as e:
        return handle_validation_error(e)
    except Exception as e:
        if error_type == "database":
            return handle_database_error(e, operation)
        elif error_type == "file":
            return handle_file_error(e, operation)
        elif error_type == "validation":
            return handle_validation_error(e)
        else:
            return handle_generic_error(e, operation)

