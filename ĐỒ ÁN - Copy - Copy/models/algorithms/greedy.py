"""
Greedy Best-First Search CHÍNH XÁC cho TSP.

THUẬT TOÁN GREEDY BEST-FIRST SEARCH ĐÚNG:
- Greedy Best-First Search là thuật toán tìm kiếm informed search
- Chỉ sử dụng heuristic h(n) để chọn node tiếp theo
- KHÔNG quan tâm đến chi phí thực tế g(n) đã đi
- Luôn expand node có h(n) nhỏ nhất (tham lam - greedy)
- KHÔNG đảm bảo tối ưu (có thể tìm được lời giải tệ)
- Nhanh nhưng có thể bị kẹt vào local minimum

So với A* và UCS:
- UCS: chọn theo g(n) only → tối ưu nhưng chậm
- A*: chọn theo f(n) = g(n) + h(n) → tối ưu (nếu h admissible) và nhanh
- Greedy: chọn theo h(n) only → không tối ưu nhưng rất nhanh
"""
import time
import heapq


class GreedyBestFirstSearchTSP:
    """Greedy Best-First Search CHÍNH XÁC cho TSP.

    Triển khai đúng theo lý thuyết:
    - State space search với priority queue
    - Mỗi state = (heuristic h(n), thành phố hiện tại, visited set, đường đi)
    - Luôn expand state có h(n) nhỏ nhất
    - CHỈ dùng heuristic, KHÔNG dùng chi phí thực tế g(n)
    - KHÔNG đảm bảo tối ưu
    
    Heuristic h(n) cho TSP:
    - Ước lượng chi phí còn lại để hoàn thành tour
    - Có thể dùng: khoảng cách đến start, MST của thành phố chưa thăm, etc.
    - Ở đây dùng: tổng khoảng cách nhỏ nhất từ các thành phố chưa thăm về start
    """

    def __init__(self, distance_matrix, city_names, coordinates):
        self.distance_matrix = distance_matrix
        self.city_names = city_names
        self.coordinates = coordinates
        self.n_cities = len(city_names)
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0

    def heuristic(self, current_city, visited_set, start_city):
        """
        Heuristic h(n) cho Greedy Best-First Search
        
        Ước lượng chi phí còn lại để hoàn thành tour:
        1. Tổng khoảng cách nhỏ nhất từ mỗi thành phố chưa thăm đến các thành phố khác
        2. Khoảng cách từ thành phố hiện tại về start
        
        Lưu ý: Greedy không yêu cầu heuristic admissible như A*
        Có thể dùng heuristic "lạc quan" (optimistic) hoặc "bi quan" (pessimistic)
        """
        unvisited = [city for city in range(self.n_cities) if city not in visited_set]
        
        if not unvisited:
            # Tất cả đã thăm, chỉ cần quay về start
            return self.distance_matrix[current_city][start_city]
        
        # Heuristic: tổng khoảng cách nhỏ nhất từ current đến unvisited + về start
        # Cách 1: khoảng cách min từ current đến bất kỳ unvisited + về start
        min_to_unvisited = min(self.distance_matrix[current_city][city] for city in unvisited)
        min_from_unvisited_to_start = min(self.distance_matrix[city][start_city] for city in unvisited)
        
        # Ước lượng đơn giản: min edge + return to start
        return min_to_unvisited + min_from_unvisited_to_start

    def solve(self, start_city=0, step_callback=None):
        """
        Greedy Best-First Search ĐÚNG cho TSP
        
        Algorithm:
        1. Khởi tạo frontier với initial state
        2. Lặp:
           a. Lấy state có h(n) nhỏ nhất từ frontier
           b. Nếu đã thăm tất cả thành phố → goal state → return
           c. Expand state: tạo các successor states
           d. Tính h(n) cho mỗi successor (KHÔNG dùng g(n))
           e. Thêm các successor vào frontier
        3. Khi tìm được goal, thêm quay về start và return
        
        Lưu ý: Greedy chỉ quan tâm h(n), không quan tâm chi phí thực tế g(n)
        """
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0
        
        # Initial state: (h_cost, current_city, visited_frozenset, path, g_cost)
        # g_cost chỉ để tracking, KHÔNG dùng trong việc chọn state
        initial_h = self.heuristic(start_city, frozenset([start_city]), start_city)
        initial_state = (start_city, frozenset([start_city]), [start_city], 0)
        
        # Priority queue: (h_cost, counter, state_tuple)
        # Sắp xếp theo h(n) only (greedy)
        frontier = []
        counter = 0
        heapq.heappush(frontier, (initial_h, counter, initial_state))
        
        # Explored states để tránh lặp
        # Key: (current_city, visited_frozenset)
        explored = set()
        
        # Bước khởi đầu
        self.steps.append({
            'step': 0,
            'current': self.city_names[start_city],
            'current_idx': start_city,
            'next': None,
            'next_idx': None,
            'distance': 0,
            'heuristic': initial_h,
            'total_distance': 0,
            'visited': [start_city],
            'candidates': [],
            'frontier_size': 1
        })
        if step_callback:
            step_callback(self.steps[-1])
        
        step_num = 0
        best_solution = None
        
        # Greedy Best-First Search Main Loop
        while frontier:
            self.operations += 1
            # Lấy state có h(n) nhỏ nhất (GREEDY - chỉ nhìn vào heuristic)
            h_cost, _, state = heapq.heappop(frontier)
            current_city, visited_set, path, g_cost = state[0], state[1], state[2], state[3]
            
            # Kiểm tra xem state này đã explored chưa
            state_key = (current_city, visited_set)
            if state_key in explored:
                continue  # Đã explore state này rồi
            
            explored.add(state_key)
            self.nodes_explored += 1
            
            # Goal test: đã thăm tất cả thành phố?
            if len(visited_set) == self.n_cities:
                # Tìm được solution! Thêm quay về start
                return_cost = self.distance_matrix[current_city][start_city]
                total_cost = g_cost + return_cost
                final_path = list(path) + [start_city]
                
                best_solution = (final_path, total_cost)
                
                # Log bước cuối
                step_num += 1
                self.steps.append({
                    'step': step_num,
                    'current': self.city_names[current_city],
                    'current_idx': current_city,
                    'next': self.city_names[start_city],
                    'next_idx': start_city,
                    'distance': return_cost,
                    'heuristic': 0,
                    'total_distance': total_cost,
                    'visited': final_path,
                    'candidates': [],
                    'frontier_size': len(frontier)
                })
                if step_callback:
                    step_callback(self.steps[-1])
                
                break  # Tìm được goal → return
            
            # Expand state: tạo successors
            candidates = []
            successors = []
            
            for next_city in range(self.n_cities):
                if next_city not in visited_set:
                    self.operations += 1
                    # Tính chi phí edge (chỉ để tracking, không dùng trong selection)
                    edge_cost = self.distance_matrix[current_city][next_city]
                    new_g_cost = g_cost + edge_cost
                    
                    # Tạo successor state
                    new_visited = visited_set | frozenset([next_city])
                    new_path = list(path) + [next_city]
                    
                    # Tính heuristic h(n) cho successor - ĐÂY LÀ TIÊU CHÍ DUY NHẤT
                    h_cost_successor = self.heuristic(next_city, new_visited, start_city)
                    
                    successor_state = (next_city, new_visited, new_path, new_g_cost)
                    
                    # Kiểm tra xem có nên thêm successor vào frontier không
                    successor_key = (next_city, new_visited)
                    if successor_key not in explored:
                        counter += 1
                        # Priority theo h(n) only (GREEDY)
                        heapq.heappush(frontier, (h_cost_successor, counter, successor_state))
                        successors.append((h_cost_successor, successor_state))
                    
                    candidates.append({
                        'city': self.city_names[next_city],
                        'city_idx': next_city,
                        'distance': edge_cost,
                        'heuristic': h_cost_successor
                    })
            
            # Log step
            if candidates:
                step_num += 1
                # Tìm next_city được chọn (successor có h nhỏ nhất)
                if successors:
                    next_h, next_state = min(successors, key=lambda x: x[0])
                    next_city_idx = next_state[0]
                    next_distance = self.distance_matrix[current_city][next_city_idx]
                else:
                    next_city_idx = candidates[0]['city_idx']
                    next_distance = candidates[0]['distance']
                
                self.steps.append({
                    'step': step_num,
                    'current': self.city_names[current_city],
                    'current_idx': current_city,
                    'next': self.city_names[next_city_idx],
                    'next_idx': next_city_idx,
                    'distance': next_distance,
                    'heuristic': h_cost,
                    'total_distance': g_cost,
                    'visited': list(path),
                    'candidates': candidates,
                    'frontier_size': len(frontier)
                })
                if step_callback:
                    step_callback(self.steps[-1])
                    time.sleep(0.3)
        
        if best_solution:
            return best_solution
        
        # Fallback: nếu không tìm được
        return None, float('inf')
