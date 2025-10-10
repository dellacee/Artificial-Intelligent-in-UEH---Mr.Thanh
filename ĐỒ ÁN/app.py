"""
Flask Application - TSP Solver với Greedy Best-First Search
"""
import webbrowser
from flask import Flask, render_template, jsonify, request

from models import OSRMDistanceCalculator, GreedyBestFirstSearchTSP
from config import DEFAULT_CITIES


app = Flask(__name__)

# Global variables
current_cities = {}
current_solution = None
solving_steps = []


@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Lấy danh sách thành phố"""
    return jsonify(list(current_cities.items()))


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


@app.route('/api/solve', methods=['POST'])
def solve_tsp():
    """Giải bài toán TSP"""
    global current_solution, solving_steps
    
    if len(current_cities) < 2:
        return jsonify({'error': 'Cần ít nhất 2 thành phố'}), 400
    
    solving_steps = []
    
    print("\n🚀 Bắt đầu giải bài toán TSP...")
    
    # Tính ma trận khoảng cách
    calculator = OSRMDistanceCalculator()
    distance_matrix = calculator.get_distance_matrix(current_cities)
    
    # Giải TSP
    city_names = list(current_cities.keys())
    solver = GreedyBestFirstSearchTSP(distance_matrix, city_names, current_cities)
    
    def step_callback(step_info):
        solving_steps.append(step_info)
    
    route, total_distance = solver.solve(start_city=0, step_callback=step_callback)
    
    current_solution = {
        'route': route,
        'total_distance': total_distance,
        'city_names': city_names,
        'steps': solving_steps
    }
    
    print("\n✅ Hoàn thành!")
    
    return jsonify({
        'success': True,
        'route': [city_names[i] for i in route],
        'total_distance': total_distance,
        'steps': solving_steps
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
    webbrowser.open('http://localhost:5000')
    app.run(debug=False, port=5000)
