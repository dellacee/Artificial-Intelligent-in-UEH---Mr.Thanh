"""
Flask Application - TSP Solver với Greedy Best-First Search
"""
import webbrowser
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os

from models import OSRMDistanceCalculator, GreedyBestFirstSearchTSP, UniformCostSearchTSP, AStarTSP
from config import DEFAULT_CITIES, SCENARIOS, API_BASE_URL


app = Flask(__name__)
CORS(app)  # Enable CORS để frontend trên port khác có thể gọi API

# Config để templates tự động reload khi dev
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Global variables - Khởi tạo với DEFAULT_CITIES ngay từ đầu
current_cities = DEFAULT_CITIES.copy()
current_scenario = 1  # Scenario hiện tại
current_solution = None
solving_steps = []


@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html', api_base_url=API_BASE_URL)


@app.route('/style.css')
def serve_css():
    """Serve CSS file từ templates folder"""
    return send_from_directory('templates', 'style.css', mimetype='text/css')


@app.route('/app.js')
def serve_js():
    """Serve JS file từ templates folder"""
    return send_from_directory('templates', 'app.js', mimetype='application/javascript')


@app.route('/debug')
def debug_page():
    """Trang debug"""
    return render_template('test_debug.html', api_base_url=API_BASE_URL)


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Lấy danh sách thành phố"""
    cities_list = list(current_cities.items())
    print(f"\n🔍 [DEBUG] GET /api/cities - Returning {len(cities_list)} cities")
    return jsonify(cities_list)


@app.route('/api/cities', methods=['POST'])
def add_city():
    """Thêm thành phố mới"""
    data = request.json
    city_name = data.get('name')
    lat = data.get('lat')
    lng = data.get('lng')
    
    if not city_name or lat is None or lng is None:
        return jsonify({'error': 'Missing data'}), 400
    
    current_cities[city_name] = (float(lat), float(lng))
    return jsonify({'success': True, 'cities': list(current_cities.items())})


@app.route('/api/cities/<city_name>', methods=['DELETE'])
def delete_city(city_name):
    """Xóa thành phố"""
    if city_name in current_cities:
        del current_cities[city_name]
        return jsonify({'success': True, 'cities': list(current_cities.items())})
    return jsonify({'error': 'City not found'}), 404


@app.route('/api/scenario/<int:scenario_id>', methods=['POST'])
def switch_scenario(scenario_id):
    """Switch giữa các tình huống"""
    global current_cities, current_scenario, current_solution, solving_steps
    
    if scenario_id not in SCENARIOS:
        return jsonify({'error': f'Scenario {scenario_id} not found'}), 404
    
    current_scenario = scenario_id
    current_cities = SCENARIOS[scenario_id].copy()
    current_solution = None
    solving_steps = []
    
    print(f"\n🔄 Switched to Scenario {scenario_id}: {len(current_cities)} cities")
    
    return jsonify({
        'success': True,
        'scenario': scenario_id,
        'cities': list(current_cities.items())
    })


@app.route('/api/solve', methods=['POST'])
def solve_tsp():
    """Giải bài toán TSP với thuật toán được chọn"""
    global current_solution, solving_steps
    
    if len(current_cities) < 2:
        return jsonify({'error': 'Cần ít nhất 2 thành phố'}), 400
    
    # Lấy thuật toán được chọn
    data = request.json or {}
    algorithm = data.get('algorithm', 'greedy')  # mặc định: greedy
    
    solving_steps = []
    
    print(f"\n🚀 Bắt đầu giải bài toán TSP với thuật toán: {algorithm.upper()}...")
    
    # Tính ma trận khoảng cách
    calculator = OSRMDistanceCalculator()
    distance_matrix = calculator.get_distance_matrix(current_cities)
    
    # Chọn thuật toán
    city_names = list(current_cities.keys())
    
    if algorithm == 'best-first':
        solver = UniformCostSearchTSP(distance_matrix, city_names, current_cities)
    elif algorithm == 'astar':
        solver = AStarTSP(distance_matrix, city_names, current_cities)
    else:  # mặc định greedy
        solver = GreedyBestFirstSearchTSP(distance_matrix, city_names, current_cities)
    
    def step_callback(step_info):
        solving_steps.append(step_info)
    
    import time
    # Sử dụng perf_counter() cho độ chính xác cao hơn (nanosecond precision)
    start_time = time.perf_counter()
    route, total_distance = solver.solve(start_city=0, step_callback=step_callback)
    elapsed_time = time.perf_counter() - start_time
    
    # Format thời gian theo đơn vị phù hợp
    if elapsed_time < 0.001:
        time_display = f"{elapsed_time*1000000:.2f}µs"
    elif elapsed_time < 1:
        time_display = f"{elapsed_time*1000:.3f}ms"
    else:
        time_display = f"{elapsed_time:.4f}s"
    
    current_solution = {
        'route': route,
        'total_distance': total_distance,
        'city_names': city_names,
        'steps': solving_steps,
        'algorithm': algorithm,
        'time': elapsed_time,
        'nodes_explored': solver.nodes_explored,
        'operations': solver.operations
    }
    
    print(f"\n✅ Hoàn thành! Distance: {total_distance:.2f} km, Time: {time_display}, Nodes: {solver.nodes_explored}, Ops: {solver.operations}")
    
    return jsonify({
        'success': True,
        'route': [city_names[i] for i in route],
        'total_distance': total_distance,
        'steps': solving_steps,
        'algorithm': algorithm,
        'time': elapsed_time,
        'nodes_explored': solver.nodes_explored,
        'operations': solver.operations
    })


@app.route('/api/compare', methods=['POST'])
def compare_algorithms():
    """Chạy tất cả các thuật toán và trả về kết quả so sánh."""
    global current_cities
    
    if len(current_cities) < 2:
        return jsonify({'error': 'Cần ít nhất 2 thành phố'}), 400
    
    print("\n📊 Bắt đầu so sánh các thuật toán...")
    
    # Tính ma trận khoảng cách
    calculator = OSRMDistanceCalculator()
    distance_matrix = calculator.get_distance_matrix(current_cities)
    city_names = list(current_cities.keys())
    
    results = {}
    
    # Chạy từng thuật toán
    algorithms = {
        'Greedy Best-First Search': GreedyBestFirstSearchTSP,
        'Uniform Cost Search (UCS)': UniformCostSearchTSP,
        'A* Algorithm': AStarTSP
    }
    
    for name, AlgorithmClass in algorithms.items():
        print(f"\n  🔄 Đang chạy {name}...")
        solver = AlgorithmClass(distance_matrix, city_names, current_cities)
        
        import time
        # Sử dụng perf_counter() cho độ chính xác cao hơn
        start_time = time.perf_counter()
        route, total_distance = solver.solve(start_city=0, step_callback=None)
        elapsed_time = time.perf_counter() - start_time
        
        # Hiển thị thời gian theo đơn vị phù hợp
        if elapsed_time < 0.001:
            time_display = f"{elapsed_time*1000000:.2f}µs"  # microseconds
            time_value = round(elapsed_time * 1000000, 2)  # µs
            time_unit = 'µs'
        elif elapsed_time < 1:
            time_display = f"{elapsed_time*1000:.3f}ms"  # milliseconds
            time_value = round(elapsed_time * 1000, 3)  # ms
            time_unit = 'ms'
        else:
            time_display = f"{elapsed_time:.4f}s"  # seconds
            time_value = round(elapsed_time, 4)  # s
            time_unit = 's'
        
        results[name] = {
            'distance': round(total_distance, 2),
            'time': time_value,
            'time_unit': time_unit,
            'time_display': time_display,
            'nodes': solver.nodes_explored,
            'operations': solver.operations,
            'route': [city_names[i] for i in route]
        }
        
        print(f"    ✓ {name}: {total_distance:.2f} km, {time_display}, {solver.nodes_explored} nodes, {solver.operations} ops")
    
    print("\n✅ So sánh hoàn thành!")
    
    return jsonify({
        'success': True,
        'results': results
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset lại toàn bộ"""
    global current_cities, current_solution, solving_steps
    
    current_cities = DEFAULT_CITIES.copy()
    current_solution = None
    solving_steps = []
    
    return jsonify({'success': True, 'cities': list(current_cities.items())})


def initialize_app():
    """Khởi tạo ứng dụng"""
    global current_cities
    current_cities = DEFAULT_CITIES.copy()
    
    print("="*70)
    print("🚀 TRAVELING SALESMAN PROBLEM - GREEDY BEST-FIRST SEARCH")
    print("="*70)
    print("\n📍 Đang khởi động server...")
    print("🌐 Truy cập: http://localhost:5000")
    print("\n💡 Tính năng:")
    print("   ✓ Thêm/xóa địa điểm bằng cách click trên bản đồ")
    print("   ✓ Xem quá trình tìm kiếm với animation")
    print("   ✓ Hiển thị g(n) và h(n) cho mỗi bước")
    print("="*70)


if __name__ == "__main__":
    initialize_app()
    # webbrowser.open('http://localhost:5000')  # Comment out để tránh conflict
    app.run(debug=True, port=5000, host='127.0.0.1')  # debug=True để auto-reload khi save file
