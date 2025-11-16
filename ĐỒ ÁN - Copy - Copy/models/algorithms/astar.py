import time
import heapq

class AStarTSP:
    """
    A* Search CHÍNH XÁC cho TSP.
    
    THUẬT TOÁN A* ĐÚNG:
    - A* là Best-First Search sử dụng hàm đánh giá f(n) = g(n) + h(n)
    - g(n): chi phí thực tế từ start đến node hiện tại
    - h(n): heuristic ước lượng chi phí từ node hiện tại đến goal
    - Mỗi node/state: (thành phố hiện tại, tập thành phố đã thăm, đường đi, g(n))
    - Luôn expand node có f(n) nhỏ nhất
    - Nếu h(n) admissible (không overestimate) → A* đảm bảo tối ưu
    - A* = UCS khi h(n) = 0
    
    Heuristic cho TSP:
    - MST (Minimum Spanning Tree) của các thành phố chưa thăm + chi phí về start
    - Đây là admissible heuristic vì MST <= actual tour cost
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
        Heuristic admissible cho TSP: MST của thành phố chưa thăm
        
        h(n) ước lượng chi phí còn lại để:
        1. Thăm tất cả thành phố chưa thăm
        2. Quay về start
        
        Sử dụng Prim's algorithm để tính MST
        """
        unvisited = [city for city in range(self.n_cities) if city not in visited_set]
        
        if not unvisited:
            # Tất cả đã thăm, chỉ cần quay về start
            return self.distance_matrix[current_city][start_city]
        
        # MST của unvisited cities + current + start
        all_nodes = [current_city] + unvisited + [start_city]
        
        if len(all_nodes) <= 2:
            # Chỉ có current và start
            return self.distance_matrix[current_city][start_city]
        
        # Prim's algorithm để tính MST
        mst_cost = 0
        in_mst = [False] * len(all_nodes)
        min_edge = [float('inf')] * len(all_nodes)
        min_edge[0] = 0  # Bắt đầu từ current_city
        
        for _ in range(len(all_nodes)):
            # Tìm node chưa trong MST có min_edge nhỏ nhất
            u = -1
            for i in range(len(all_nodes)):
                if not in_mst[i] and (u == -1 or min_edge[i] < min_edge[u]):
                    u = i
            
            if min_edge[u] == float('inf'):
                break
            
            in_mst[u] = True
            mst_cost += min_edge[u]
            
            # Update min_edge cho các node kề
            for v in range(len(all_nodes)):
                if not in_mst[v]:
                    node_u = all_nodes[u]
                    node_v = all_nodes[v]
                    edge_cost = self.distance_matrix[node_u][node_v]
                    if edge_cost < min_edge[v]:
                        min_edge[v] = edge_cost
        
        return mst_cost

    def solve(self, start_city=0, step_callback=None):
        """
        A* Search ĐÚNG cho TSP
        
        Algorithm:
        1. Khởi tạo frontier với initial state
        2. Lặp:
           a. Lấy state có f(n) = g(n) + h(n) nhỏ nhất từ frontier
           b. Nếu đã thăm tất cả thành phố → goal state → return
           c. Expand state: tạo các successor states
           d. Tính f(n) = g(n) + h(n) cho mỗi successor
           e. Thêm các successor vào frontier
        3. Khi tìm được goal, thêm quay về start và return
        """
        self.steps = []
        self.nodes_explored = 0
        self.operations = 0
        
        # Initial state: (f_cost, g_cost, current_city, visited_frozenset, path)
        initial_g = 0
        initial_h = self.heuristic(start_city, frozenset([start_city]), start_city)
        initial_f = initial_g + initial_h
        initial_state = (initial_g, start_city, frozenset([start_city]), [start_city])
        
        # Priority queue: (f_cost, counter, state_tuple)
        frontier = []
        counter = 0
        heapq.heappush(frontier, (initial_f, counter, initial_state))
        
        # Explored states: Key = (current_city, visited_frozenset), Value = g_cost
        explored = {}
        
        # Bước khởi đầu
        self.steps.append({
            'step': 0,
            'current': self.city_names[start_city],
            'current_idx': start_city,
            'next': None,
            'next_idx': None,
            'distance': 0,
            'g': 0,
            'heuristic': initial_h,
            'f': initial_f,
            'total_distance': 0,
            'visited': [start_city],
            'candidates': [],
            'frontier_size': 1
        })
        if step_callback:
            step_callback(self.steps[-1])
        
        step_num = 0
        best_solution = None
        
        # A* Main Loop
        while frontier:
            self.operations += 1
            # Lấy state có f(n) nhỏ nhất
            f_cost, _, state = heapq.heappop(frontier)
            g_cost, current_city, visited_set, path = state[0], state[1], state[2], state[3]
            
            # Kiểm tra xem state này đã explored chưa
            state_key = (current_city, visited_set)
            if state_key in explored and explored[state_key] <= g_cost:
                continue  # Đã có đường đi tốt hơn
            
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
                    'f': total_cost,
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
                    
                    # Tính heuristic h(n) cho successor
                    h_cost = self.heuristic(next_city, new_visited, start_city)
                    new_f_cost = new_g_cost + h_cost
                    
                    successor_state = (new_g_cost, next_city, new_visited, new_path)
                    
                    # Kiểm tra xem có nên thêm successor vào frontier không
                    successor_key = (next_city, new_visited)
                    if successor_key not in explored or explored[successor_key] > new_g_cost:
                        counter += 1
                        heapq.heappush(frontier, (new_f_cost, counter, successor_state))
                        successors.append((new_f_cost, successor_state))
                    
                    candidates.append({
                        'city': self.city_names[next_city],
                        'city_idx': next_city,
                        'distance': edge_cost,
                        'g': new_g_cost,
                        'heuristic': h_cost,
                        'f': new_f_cost
                    })
            
            # Log step
            if candidates:
                step_num += 1
                # Tìm next_city được chọn (successor có f nhỏ nhất)
                if successors:
                    next_f, next_state = min(successors, key=lambda x: x[0])
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
                    'heuristic': self.heuristic(current_city, visited_set, start_city),
                    'f': f_cost,
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
