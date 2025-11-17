import time
import heapq

class AStarTSP:
    """    
    Sử dụng f(n) = g(n) + h(n) với:
    - g(n): khoảng cách đã đi từ start đến thành phố hiện tại
    - h(n): khoảng cách ước lượng từ thành phố đến đích
    Chọn thành phố có f(n) nhỏ nhất.
    """

    def __init__(self, distance_matrix, city_names, coordinates):
        self.distance_matrix = distance_matrix
        self.city_names = city_names
        self.coordinates = coordinates
        self.n_cities = len(city_names)
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0  # Đếm số phép tính/so sánh

    def heuristic(self, city, goal_city):
        """Heuristic h(n): khoảng cách đến đích"""
        return self.distance_matrix[city][goal_city]

    def solve(self, start_city=0, step_callback=None):
        """A* Search thuần túy với f(n) = g(n) + h(n)"""
        goal_city = start_city
        visited = [False] * self.n_cities
        visited[start_city] = True
        route = [start_city]
        total_distance = 0  # g(n) tích lũy
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

        # A* Search: chọn theo f(n) = g(n) + h(n)
        for step in range(self.n_cities - 1):
            priority_queue = []
            candidates = []
            
            # Thêm tất cả thành phố chưa thăm vào priority queue
            for city in range(self.n_cities):
                if not visited[city]:
                    self.nodes_explored += 1
                    self.operations += 2  # 2 matrix lookups
                    # g(n): chi phí tích lũy từ start = total_distance + distance[current][city]
                    distance_to_city = self.distance_matrix[current_city][city]
                    g_cost = total_distance + distance_to_city
                    # h(n): heuristic từ city đến goal (remaining estimated cost)
                    h_cost = self.heuristic(city, goal_city)
                    self.operations += 2  # 1 addition for g_cost, 1 for f
                    # f(n) = g(n) + h(n) - cân bằng giữa chi phí thực tế và ước lượng
                    f = g_cost + h_cost
                    
                    self.operations += 1  # heap push operation
                    # Priority queue: sắp xếp theo f(n)
                    heapq.heappush(priority_queue, (f, city))
                    
                    candidates.append({
                        'city': self.city_names[city],
                        'city_idx': city,
                        'distance': distance_to_city,
                        'g': g_cost,
                        'heuristic': h_cost,
                        'f': f
                    })
            
            if not priority_queue:
                break
            
            self.operations += 1  # heap pop operation
            # Chọn thành phố có f(n) nhỏ nhất
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
                'g': d,
                'heuristic': self.heuristic(next_city, goal_city),
                'f': d + self.heuristic(next_city, goal_city),
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
