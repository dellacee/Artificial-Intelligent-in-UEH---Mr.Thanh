"""
Configuration file - Cấu hình ứng dụng
"""

# Dữ liệu thành phố mặc định - 10 thành phố Đông Nam Á
# Với caching, API calls chỉ chạy lần đầu, các lần sau load từ cache (<0.1s)
# 10 cities = 90 cặp = đủ để thấy sự khác biệt thời gian rõ ràng
DEFAULT_CITIES = {
    "Hà Nội": (21.0285, 105.8542),           # Vietnam - Bắc
    "Bangkok": (13.7563, 100.5018),          # Thailand - Trung tâm
    "TP.HCM": (10.8231, 106.6297),           # Vietnam - Nam Đông
    "Singapore": (1.3521, 103.8198),         # Singapore - Nam
    "Kuala Lumpur": (3.1390, 101.6869),      # Malaysia - Trung Nam
    "Manila": (14.5995, 120.9842),           # Philippines - Đông
    "Phnom Penh": (11.5564, 104.9282),       # Cambodia - Tây Nam
    "Yangon": (16.8661, 96.1951),            # Myanmar - Tây
    "Vientiane": (17.9757, 102.6331),        # Laos - Tây Bắc
    "Jakarta": (-6.2088, 106.8456)           # Indonesia - Nam xa
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
