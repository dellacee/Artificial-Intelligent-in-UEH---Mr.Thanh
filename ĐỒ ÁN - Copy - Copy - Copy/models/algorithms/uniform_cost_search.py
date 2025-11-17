"""
Uniform Cost Search (UCS) thuần túy cho TSP.

Thuật toán UCS chỉ sử dụng g(n) (chi phí thực tế tích lũy) để chọn thành phố tiếp theo.
Không sử dụng heuristic h(n). Đảm bảo tìm được đường đi tối ưu.
"""
import time
import heapq


class UniformCostSearchTSP:
    """Uniform Cost Search (UCS) for TSP.
    
    UCS thuần túy: chọn thành phố có chi phí tích lũy g(n) nhỏ nhất.
    - g(n) = tổng khoảng cách từ start đến thành phố hiện tại + khoảng cách đến candidate
    - KHÔNG sử dụng heuristic h(n)
    - Đảm bảo tối ưu (optimal)
    """

    def __init__(self, distance_matrix, city_names, coordinates):
        self.distance_matrix = distance_matrix
        self.city_names = city_names
        self.coordinates = coordinates
        self.n_cities = len(city_names)
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0  # Đếm số phép tính/so sánh

    def solve(self, start_city=0, step_callback=None):
        """Uniform Cost Search thuần túy - chọn theo g(n) only"""
        goal_city = start_city
        visited = [False] * self.n_cities
        visited[start_city] = True
        route = [start_city]
        total_distance = 0  # g(n) tích lũy từ start
        current_city = start_city
        
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0
        
        # Bước khởi đầu
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

        # UCS: chọn thành phố có g(n) nhỏ nhất (chi phí tích lũy)
        for step in range(self.n_cities - 1):
            priority_queue = []
            candidates = []
            
            # Thêm tất cả thành phố chưa thăm vào priority queue
            for city in range(self.n_cities):
                if not visited[city]:
                    self.nodes_explored += 1
                    self.operations += 1  # 1 matrix lookup
                    # g(n): chi phí tích lũy = total_distance + distance[current][city]
                    distance_to_city = self.distance_matrix[current_city][city]
                    g_cost = total_distance + distance_to_city
                    
                    self.operations += 1  # 1 addition
                    self.operations += 1  # heap push operation
                    # Priority queue: sắp xếp theo g(n) - chi phí tích lũy
                    heapq.heappush(priority_queue, (g_cost, city))
                    
                    candidates.append({
                        'city': self.city_names[city],
                        'city_idx': city,
                        'distance': distance_to_city,
                        'g': g_cost,
                        'heuristic': 0  # UCS không dùng heuristic
                    })
            
            if not priority_queue:
                break
            
            self.operations += 1  # heap pop operation
            # Chọn thành phố có g(n) nhỏ nhất
            _, next_city = heapq.heappop(priority_queue)
            
            # Di chuyển đến thành phố được chọn
            d = self.distance_matrix[current_city][next_city]
            visited[next_city] = True
            route.append(next_city)
            total_distance += d
            
            step_info = {
                'step': step + 1,
                'current': self.city_names[current_city],
                'current_idx': current_city,
                'next': self.city_names[next_city],
                'next_idx': next_city,
                'distance': d,
                'g': total_distance,  # UCS: chi phí tích lũy
                'heuristic': 0,  # UCS không dùng heuristic
                'total_distance': total_distance,
                'visited': route.copy(),
                'candidates': candidates
            }
            self.steps.append(step_info)
            if step_callback:
                step_callback(step_info)
                time.sleep(0.3)
            
            current_city = next_city
        
        # Quay về điểm xuất phát
        return_dist = self.distance_matrix[current_city][start_city]
        route.append(start_city)
        total_distance += return_dist
        
        self.steps.append({
            'step': len(route) - 1,
            'current': self.city_names[current_city],
            'current_idx': current_city,
            'next': self.city_names[start_city],
            'next_idx': start_city,
            'distance': return_dist,
            'total_distance': total_distance,
            'visited': route.copy(),
            'candidates': []
        })
        if step_callback:
            step_callback(self.steps[-1])
        
        return route, total_distance
