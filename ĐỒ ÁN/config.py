"""
Configuration file - Cấu hình ứng dụng
"""

# Dữ liệu thành phố mặc định
DEFAULT_CITIES = {
    "Hà Nội": (21.0285, 105.8542),
    "Hải Phòng": (20.8449, 106.6881),
    "Đà Nẵng": (16.0544, 108.2022),
    "Nha Trang": (12.2388, 109.1967),
    "TP. Hồ Chí Minh": (10.8231, 106.6297)
}

# Cấu hình server
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
DEBUG_MODE = False

# Cấu hình OSRM
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"
OSRM_TIMEOUT = 10  # seconds
OSRM_DELAY = 0.1  # delay giữa các request (seconds)

# Cấu hình thuật toán
ANIMATION_DELAY = 0.5  # seconds giữa các bước animation
GEODESIC_MULTIPLIER = 1.3  # nhân tố ước lượng khi OSRM fail
