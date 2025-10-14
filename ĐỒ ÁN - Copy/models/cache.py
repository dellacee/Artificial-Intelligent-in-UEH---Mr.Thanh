"""
Cache cho kết quả OSRM API - tránh gọi lại nhiều lần
"""
import json
import os
import hashlib
from pathlib import Path


class DistanceCache:
    """Cache khoảng cách giữa các thành phố"""
    
    def __init__(self, cache_file='distance_cache.json'):
        self.cache_file = Path(__file__).parent.parent / cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache từ file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache vào file"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def _make_key(self, city1, city2):
        """Tạo key duy nhất cho cặp thành phố"""
        # Sử dụng tên thành phố để tạo key (không phụ thuộc vào tọa độ)
        return f"{city1}__to__{city2}"
    
    def get(self, city1, city2):
        """Lấy khoảng cách từ cache"""
        key = self._make_key(city1, city2)
        return self.cache.get(key)
    
    def set(self, city1, city2, distance):
        """Lưu khoảng cách vào cache"""
        key = self._make_key(city1, city2)
        self.cache[key] = distance
        self._save_cache()
    
    def has(self, city1, city2):
        """Kiểm tra xem đã có trong cache chưa"""
        key = self._make_key(city1, city2)
        return key in self.cache
    
    def clear(self):
        """Xóa toàn bộ cache"""
        self.cache = {}
        self._save_cache()
    
    def get_stats(self):
        """Thống kê cache"""
        return {
            'total_entries': len(self.cache),
            'cache_file': str(self.cache_file)
        }
