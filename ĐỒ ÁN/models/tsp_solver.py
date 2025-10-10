"""
Module giải bài toán TSP bằng Greedy Best-First Search
"""
import time


class GreedyBestFirstSearchTSP:
    """
    Giải bài toán TSP bằng Greedy Best-First Search THỰC SỰ
    
    Greedy Best-First Search sử dụng:
    - Heuristic function: khoảng cách từ thành phố đang xét đến điểm đích (start_city)
    - Chọn thành phố có heuristic nhỏ nhất (gần đích nhất)
    - Khác với Nearest Neighbor (chọn gần nhất từ current)
    """
    
    def __init__(self, distance_matrix, city_names, coordinates):
        """
        Khởi tạo solver
        
        Args:
            distance_matrix: Ma trận khoảng cách
            city_names: Danh sách tên thành phố
            coordinates: Dictionary tọa độ thành phố
        """
        self.distance_matrix = distance_matrix
        self.city_names = city_names
        self.coordinates = coordinates
        self.n_cities = len(city_names)
        self.steps = []  # Lưu các bước để animation
        
    def heuristic(self, city, goal_city):
        """
        Heuristic function: khoảng cách từ city đến goal_city
        
        Args:
            city: Index của thành phố cần đánh giá
            goal_city: Index của thành phố đích
            
        Returns:
            float: h(n) = khoảng cách từ n đến đích
        """
        return self.distance_matrix[city][goal_city]
    
    def solve(self, start_city=0, step_callback=None):
        """
        Giải TSP bằng Greedy Best-First Search
        
        Best-First Search:
        - Đích cuối cùng: quay về start_city
        - Mỗi bước: chọn thành phố chưa thăm có h(n) nhỏ nhất (gần đích nhất)
        - h(n) = khoảng cách từ thành phố đó về start_city
        
        Args:
            start_city: Index của thành phố xuất phát
            step_callback: Hàm callback được gọi mỗi bước
            
        Returns:
            tuple: (route, total_distance)
        """
        current_city = start_city
        goal_city = start_city  # Đích cuối cùng là quay về điểm xuất phát
        visited = [False] * self.n_cities
        visited[current_city] = True
        route = [current_city]
        total_distance = 0
        
        self._print_header(start_city, goal_city)
        
        # Lưu bước đầu tiên
        self.steps.append({
            'step': 0,
            'current': self.city_names[current_city],
            'current_idx': current_city,
            'next': None,
            'next_idx': None,
            'distance': 0,
            'total_distance': 0,
            'visited': route.copy(),
            'candidates': []
        })
        
        if step_callback:
            step_callback(self.steps[-1])
        
        # Tìm kiếm từng bước
        for step in range(self.n_cities - 1):
            best_heuristic = float('inf')
            next_city = None
            candidates = []
            
            print(f"\n{'='*70}")
            print(f"Bước {step + 1}:")
            print(f"  📍 Đang ở: {self.city_names[current_city]}")
            print(f"  🔍 Đánh giá các thành phố chưa thăm:")
            print(f"     (g = chi phí thực tế, h = heuristic về đích)")
            
            # Đánh giá tất cả thành phố chưa thăm
            for city in range(self.n_cities):
                if not visited[city]:
                    g_cost = self.distance_matrix[current_city][city]
                    h_cost = self.heuristic(city, goal_city)
                    
                    print(f"     • {self.city_names[city]}:")
                    print(f"       - g(n) = {g_cost:.2f} km (từ {self.city_names[current_city]})")
                    print(f"       - h(n) = {h_cost:.2f} km (về {self.city_names[goal_city]})")
                    print(f"       - Ưu tiên: h(n) = {h_cost:.2f} km")
                    
                    candidates.append({
                        'city': self.city_names[city],
                        'city_idx': city,
                        'distance': g_cost,
                        'heuristic': h_cost
                    })
                    
                    # Greedy Best-First: chọn h(n) nhỏ nhất (gần đích nhất)
                    if h_cost < best_heuristic:
                        best_heuristic = h_cost
                        next_city = city
            
            # Di chuyển đến thành phố được chọn
            if next_city is not None:
                actual_distance = self.distance_matrix[current_city][next_city]
                
                print(f"\n  ✅ CHỌN: {self.city_names[next_city]}")
                print(f"     Lý do: h(n) = {best_heuristic:.2f} km (nhỏ nhất - gần đích nhất)")
                print(f"     Chi phí thực tế: g(n) = {actual_distance:.2f} km")
                
                visited[next_city] = True
                route.append(next_city)
                total_distance += actual_distance
                
                # Lưu bước
                step_info = {
                    'step': step + 1,
                    'current': self.city_names[current_city],
                    'current_idx': current_city,
                    'next': self.city_names[next_city],
                    'next_idx': next_city,
                    'distance': actual_distance,
                    'heuristic': best_heuristic,
                    'total_distance': total_distance,
                    'visited': route.copy(),
                    'candidates': candidates
                }
                self.steps.append(step_info)
                
                if step_callback:
                    step_callback(step_info)
                    time.sleep(0.5)  # Delay để thấy animation
                
                current_city = next_city
        
        # Quay về điểm xuất phát
        return_distance = self.distance_matrix[current_city][start_city]
        route.append(start_city)
        total_distance += return_distance
        
        print(f"\n{'='*70}")
        print(f"Bước cuối:")
        print(f"  🏁 Quay về: {self.city_names[start_city]} ({return_distance:.2f} km)")
        
        self.steps.append({
            'step': len(route) - 1,
            'current': self.city_names[current_city],
            'current_idx': current_city,
            'next': self.city_names[start_city],
            'next_idx': start_city,
            'distance': return_distance,
            'total_distance': total_distance,
            'visited': route.copy(),
            'candidates': []
        })
        
        if step_callback:
            step_callback(self.steps[-1])
        
        print("="*70)
        
        return route, total_distance
    
    def _print_header(self, start_city, goal_city):
        """In header cho quá trình tìm kiếm"""
        print("\n" + "="*70)
        print("GREEDY BEST-FIRST SEARCH - QUÁ TRÌNH TÌM KIẾM")
        print("="*70)
        print(f"🎯 Điểm xuất phát & đích: {self.city_names[start_city]}")
        print(f"📊 Heuristic: h(n) = khoảng cách từ n về {self.city_names[goal_city]}")
    
    def print_solution(self, route, total_distance):
        """
        In kết quả cuối cùng
        
        Args:
            route: Danh sách thành phố theo thứ tự
            total_distance: Tổng khoảng cách
        """
        print("\n" + "="*70)
        print("KẾT QUẢ CUỐI CÙNG")
        print("="*70)
        print(f"\nTuyến đường tối ưu:")
        for i, city_idx in enumerate(route):
            if i < len(route) - 1:
                print(f"  {i+1}. {self.city_names[city_idx]}")
            else:
                print(f"  {i+1}. {self.city_names[city_idx]} (quay về)")
        
        print(f"\n📍 Tổng khoảng cách: {total_distance:.2f} km")
        print("="*70)
