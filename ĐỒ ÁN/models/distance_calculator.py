"""
Module tính toán khoảng cách sử dụng OSRM API
"""
import requests
import numpy as np
import time
from geopy.distance import geodesic


class OSRMDistanceCalculator:
    """
    Tính khoảng cách MIỄN PHÍ bằng OSRM
    """
    
    def __init__(self):
        self.base_url = "http://router.project-osrm.org/route/v1/driving"
    
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
        Tạo ma trận khoảng cách cho tất cả các điểm
        
        Args:
            coordinates_dict: {city_name: (lat, lng), ...}
        
        Returns:
            numpy.ndarray: Ma trận khoảng cách
        """
        city_names = list(coordinates_dict.keys())
        n = len(city_names)
        distance_matrix = np.zeros((n, n))
        
        total_requests = n * (n - 1)
        completed = 0
        
        print(f"\n🔍 Đang tính toán ma trận khoảng cách (OSRM API)...")
        print(f"   Số lượng requests: {total_requests}")
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    coord1 = coordinates_dict[city_names[i]]
                    coord2 = coordinates_dict[city_names[j]]
                    
                    distance = self.get_distance(coord1, coord2)
                    
                    if distance:
                        distance_matrix[i][j] = distance
                        print(f"  ✓ {city_names[i]} → {city_names[j]}: {distance:.2f} km")
                    else:
                        # Fallback: dùng khoảng cách đường chim bay × 1.3
                        distance = geodesic(coord1, coord2).kilometers * 1.3
                        distance_matrix[i][j] = distance
                        print(f"  ≈ {city_names[i]} → {city_names[j]}: {distance:.2f} km (ước lượng)")
                    
                    completed += 1
                    
                    # Delay để tránh spam server
                    time.sleep(0.1)
        
        print("✓ Hoàn thành tính toán ma trận khoảng cách\n")
        return distance_matrix
