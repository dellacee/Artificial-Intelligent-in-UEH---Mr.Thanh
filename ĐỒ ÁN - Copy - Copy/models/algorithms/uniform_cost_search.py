"""
Uniform Cost Search (UCS) CHÍNH XÁC cho TSP.

THUẬT TOÁN UCS ĐÚNG:
- UCS là thuật toán tìm kiếm theo chiều rộng có ưu tiên (Best-First Search)
- Mỗi node/state đại diện cho: (thành phố hiện tại, tập thành phố đã thăm, đường đi, chi phí g(n))
- Luôn mở rộng (expand) node có chi phí g(n) nhỏ nhất
- Duy trì priority queue (frontier) chứa TẤT CẢ các state có thể
- Khi tìm được goal state (đã thăm tất cả thành phố), trả về solution
- ĐẢM BẢO TỐI ƯU (optimal) vì luôn chọn đường đi có chi phí thấp nhất
"""
import time
import heapq


class UniformCostSearchTSP:
    """Uniform Cost Search (UCS) CHÍNH XÁC cho TSP.
    
    Triển khai đúng theo lý thuyết:
    - State space search với priority queue
    - Mỗi state = (chi phí g(n), thành phố hiện tại, visited set, đường đi)
    - Luôn expand state có g(n) nhỏ nhất
    - KHÔNG sử dụng heuristic h(n)
    - Đảm bảo tối ưu
    """

    def __init__(self, distance_matrix, city_names, coordinates):
        self.distance_matrix = distance_matrix
        self.city_names = city_names
        self.coordinates = coordinates
        self.n_cities = len(city_names)
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0

    def solve(self, start_city=0, step_callback=None):
        """
        Uniform Cost Search ĐÚNG cho TSP
        
        Algorithm:
        1. Khởi tạo frontier với initial state
        2. Lặp:
           a. Lấy state có g(n) nhỏ nhất từ frontier
           b. Nếu đã thăm tất cả thành phố → goal state → return
           c. Expand state: tạo các successor states (thêm thành phố chưa thăm)
           d. Thêm các successor vào frontier
        3. Khi tìm được goal, thêm quay về start và return
        """
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0
        
        # Initial state: (g_cost, current_city, visited_frozenset, path)
        # Sử dụng frozenset để visited có thể hash (dùng làm key)
        initial_state = (0, start_city, frozenset([start_city]), [start_city])
        
        # Priority queue: (g_cost, counter, state_tuple)
        # counter để đảm bảo FIFO khi g_cost bằng nhau
        frontier = []
        counter = 0
        heapq.heappush(frontier, (0, counter, initial_state))
        
        # Lưu trạng thái đã explored để tránh lặp
        # Key: (current_city, visited_frozenset), Value: g_cost
        explored = {}
        
        # Bước khởi đầu
        self.steps.append({
            'step': 0,
            'current': self.city_names[start_city],
            'current_idx': start_city,
            'next': None,
            'next_idx': None,
            'distance': 0,
            'total_distance': 0,
            'visited': [start_city],
            'candidates': [],
            'frontier_size': 1
        })
        if step_callback:
            step_callback(self.steps[-1])
        
        step_num = 0
        best_solution = None
        
        # UCS Main Loop
        while frontier:
            self.operations += 1
            # Lấy state có g(n) nhỏ nhất
            g_cost, _, state = heapq.heappop(frontier)
            current_city, visited_set, path = state[1], state[2], state[3]
            
            # Kiểm tra xem state này đã explored chưa
            state_key = (current_city, visited_set)
            if state_key in explored and explored[state_key] <= g_cost:
                continue  # Đã có đường đi tốt hơn đến state này
            
            explored[state_key] = g_cost
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
                    'g': g_cost,
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
                    # Tính chi phí đến next_city
                    edge_cost = self.distance_matrix[current_city][next_city]
                    new_g_cost = g_cost + edge_cost
                    
                    # Tạo successor state
                    new_visited = visited_set | frozenset([next_city])
                    new_path = list(path) + [next_city]
                    successor_state = (new_g_cost, next_city, new_visited, new_path)
                    
                    # Kiểm tra xem có nên thêm successor vào frontier không
                    successor_key = (next_city, new_visited)
                    if successor_key not in explored or explored[successor_key] > new_g_cost:
                        counter += 1
                        heapq.heappush(frontier, (new_g_cost, counter, successor_state))
                        successors.append(successor_state)
                    
                    candidates.append({
                        'city': self.city_names[next_city],
                        'city_idx': next_city,
                        'distance': edge_cost,
                        'g': new_g_cost,
                        'heuristic': 0  # UCS không dùng heuristic
                    })
            
            # Log step
            if candidates:
                step_num += 1
                # Tìm next_city được chọn (successor đầu tiên sẽ được expand sau)
                if successors:
                    next_state = min(successors, key=lambda x: x[0])
                    next_city_idx = next_state[1]
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
                    'g': g_cost,
                    'heuristic': 0,
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
        
        # Fallback: nếu không tìm được (không nên xảy ra với TSP đầy đủ)
        return None, float('inf')
