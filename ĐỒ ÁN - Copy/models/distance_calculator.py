"""
Module tính toán khoảng cách sử dụng OSRM API với caching
"""
import requests
import numpy as np
import time
from geopy.distance import geodesic
from .cache import DistanceCache


class OSRMDistanceCalculator:
    """
    Tính khoảng cách MIỄN PHÍ bằng OSRM với cache để tránh gọi lại
    """
    
    def __init__(self, use_cache=True):
        self.base_url = "http://router.project-osrm.org/route/v1/driving"
        self.use_cache = use_cache
        self.cache = DistanceCache() if use_cache else None
        self.cache_hits = 0
        self.api_calls = 0
    
    def get_distance(self, coord1, coord2):
        """
        Lấy khoảng cách giữa 2 điểm
        
        Args:
            coord1: (lat, lng)
            coord2: (lat, lng)
            
        Returns:
            float: Khoảng cách tính bằng km, hoặc None nếu lỗi
        """
        url = f"{self.base_url}/{coord1[1]},{coord1[0]};{coord2[1]},{coord2[0]}"
        
        try:
            response = requests.get(url, params={'overview': 'false'}, timeout=10)
            data = response.json()
            
            if data['code'] == 'Ok':
                distance_meters = data['routes'][0]['distance']
                return distance_meters / 1000  # Chuyển sang km
            else:
                print(f"⚠️ OSRM error: {data.get('message', 'Unknown')}")
                return None
        except Exception as e:
            print(f"✗ Lỗi khi gọi OSRM: {e}")
            return None
    
    def get_distance_matrix(self, coordinates_dict):
        """
        Tạo ma trận khoảng cách cho tất cả các điểm với caching
        
        Args:
            coordinates_dict: {city_name: (lat, lng), ...}
        
        Returns:
            numpy.ndarray: Ma trận khoảng cách
        """
        city_names = list(coordinates_dict.keys())
        n = len(city_names)
        distance_matrix = np.zeros((n, n))
        
        total_requests = n * (n - 1)
        self.cache_hits = 0
        self.api_calls = 0
        
        print(f"\n🔍 Đang tính toán ma trận khoảng cách (OSRM API với Cache)...")
        print(f"   Tổng số cặp: {total_requests}")
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    city1 = city_names[i]
                    city2 = city_names[j]
                    coord1 = coordinates_dict[city1]
                    coord2 = coordinates_dict[city2]
                    
                    # Kiểm tra cache trước
                    if self.use_cache and self.cache.has(city1, city2):
                        distance = self.cache.get(city1, city2)
                        self.cache_hits += 1
                        distance_matrix[i][j] = distance
                        print(f"  💾 {city1} → {city2}: {distance:.2f} km (cached)")
                    else:
                        # Gọi API
                        distance = self.get_distance(coord1, coord2)
                        self.api_calls += 1
                        
                        if distance:
                            distance_matrix[i][j] = distance
                            # Lưu vào cache
                            if self.use_cache:
                                self.cache.set(city1, city2, distance)
                            print(f"  ✓ {city1} → {city2}: {distance:.2f} km")
                        else:
                            # Fallback: dùng khoảng cách đường chim bay × 1.3
                            distance = geodesic(coord1, coord2).kilometers * 1.3
                            distance_matrix[i][j] = distance
                            if self.use_cache:
                                self.cache.set(city1, city2, distance)
                            print(f"  ≈ {city1} → {city2}: {distance:.2f} km (ước lượng)")
                        
                        # Delay chỉ khi gọi API
                        time.sleep(0.1)
        
        print(f"✓ Hoàn thành! Cache hits: {self.cache_hits}/{total_requests} ({self.cache_hits/total_requests*100:.1f}%)")
        print(f"  API calls: {self.api_calls}, Cached: {self.cache_hits}\n")
        return distance_matrix
