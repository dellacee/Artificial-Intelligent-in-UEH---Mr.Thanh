"""
Configuration file - Cấu hình ứng dụng
"""

# Dữ liệu thành phố mặc định - 10 thành phố Đông Nam Á
# Với caching, API calls chỉ chạy lần đầu, các lần sau load từ cache (<0.1s)
# 10 cities = 90 cặp = đủ để thấy sự khác biệt thời gian rõ ràng
DEFAULT_CITIES = {
    "Hà Nội": (21.0285, 105.8542),          
    "Bangkok": (13.7563, 100.5018),          
    "TP.HCM": (10.8231, 106.6297),          
    "Singapore": (1.3521, 103.8198),        
    "Kuala Lumpur": (3.1390, 101.6869),     
    "Manila": (14.5995, 120.9842),           
    "Phnom Penh": (11.5564, 104.9282),    
    "Yangon": (16.8661, 96.1951),           
    "Vientiane": (17.9757, 102.6331),      
    "Jakarta": (-6.2088, 106.8456)         
}

# Tình huống 2: Các thành phố Việt Nam
SCENARIO_2_CITIES = {
    "Hà Nội": (21.0285, 105.8542),           # Thủ đô
    "Ninh Bình": (20.2506, 105.9745),        # Miền Bắc
    "Huế": (16.4637, 107.5909),              # Miền Trung
    "Nha Trang": (12.2388, 109.1967),        # Miền Trung Nam
    "TP.HCM": (10.8231, 106.6297),           # Miền Nam
    "Đồng Tháp": (10.4938, 105.6881)         # Đồng bằng sông Cửu Long
}

# Map tình huống
SCENARIOS = {
    1: DEFAULT_CITIES,
    2: SCENARIO_2_CITIES
}

# Cấu hình server
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
DEBUG_MODE = False

# API Base URL - Dùng cho frontend khi chạy trên port khác
API_BASE_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'  # http://localhost:5000

# Cấu hình OSRM
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"
OSRM_TIMEOUT = 10  # seconds
OSRM_DELAY = 0.1  # delay giữa các request (seconds)

# Cấu hình thuật toán
ANIMATION_DELAY = 0.5  # seconds giữa các bước animation
GEODESIC_MULTIPLIER = 1.3  # nhân tố ước lượng khi OSRM fail
