// API Base URL - Có thể override nếu frontend chạy trên port khác
let API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000';

console.log('✅ [INIT] API_BASE_URL:', API_BASE_URL);

// Helper function để tạo API URL
function apiUrl(endpoint) {
    const url = API_BASE_URL + endpoint;
    console.log(`🔧 [apiUrl] "${endpoint}" => "${url}"`);
    return url;
}

let map;
let markers = {};
let routeLine = null;
let currentStepIndex = 0;
let animationInterval = null;

// Khởi tạo bản đồ
function initMap() {
    map = L.map('map').setView([16.0, 107.0], 6);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Click vào bản đồ để thêm địa điểm
    map.on('click', function(e) {
        const lat = e.latlng.lat.toFixed(4);
        const lng = e.latlng.lng.toFixed(4);
        const cityName = prompt(`Thêm địa điểm mới tại (${lat}, ${lng})\n\nNhập tên địa điểm:`);
        
        if (cityName && cityName.trim()) {
            addCity(cityName.trim(), lat, lng);
        }
    });

    // Load cities ban đầu
    loadCities();
}

// Load danh sách thành phố
async function loadCities() {
    console.log('🔍 [loadCities] START');
    try {
        const url = apiUrl('/api/cities');
        console.log('📡 [loadCities] Fetching:', url);
        
        const response = await fetch(url);
        console.log('📊 [loadCities] Response:', response.status, response.ok);
        
        const cities = await response.json();
        console.log('✅ [loadCities] Data received:', cities.length, 'cities');
        console.log('📦 [loadCities] First city:', cities[0]);
        
        // Clear markers
        Object.values(markers).forEach(marker => map.removeLayer(marker));
        markers = {};
        
        // Add markers
        cities.forEach(([name, coords]) => {
            addMarker(name, coords[0], coords[1]);
        });
        
        // Update city list UI
        updateCityList(cities);
    } catch (error) {
        console.error('Error loading cities:', error);
    }
}

// Thêm marker lên bản đồ
function addMarker(name, lat, lng, isHighlight = false) {
    const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background: ${isHighlight ? '#2d6b3d' : '#fff'};
            width: 20px;
            height: 20px;
            border: 3px solid ${isHighlight ? '#fff' : '#2d6b3d'};
            display: flex;
            align-items: center;
            justify-content: center;
            color: ${isHighlight ? '#fff' : '#2d6b3d'};
            font-weight: bold;
            font-size: 10px;
            font-family: 'Courier New', monospace;
        ">●</div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });

    const marker = L.marker([lat, lng], { icon: icon })
        .bindPopup(`<div style="font-family: 'Courier New', monospace;">
            <strong>${name}</strong><br>
            Lat: ${lat}<br>
            Lng: ${lng}
        </div>`)
        .addTo(map);
    
    markers[name] = marker;
    return marker;
}

// Update danh sách thành phố
function updateCityList(cities) {
    const cityList = document.getElementById('city-list');
    const cityCount = document.getElementById('city-count');
    
    cityCount.textContent = cities.length;
    cityList.innerHTML = '';
    
    cities.forEach(([name, coords]) => {
        const div = document.createElement('div');
        div.className = 'city-item';
        div.id = `city-${name}`;
        div.innerHTML = `
            <div>
                <div class="city-name">${name}</div>
                <div class="city-coords">${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}</div>
            </div>
            <button class="delete-btn" onclick="deleteCity('${name}')">
                <i class="fas fa-trash"></i>
            </button>
        `;
        cityList.appendChild(div);
    });
}

// Thêm thành phố mới
async function addCity(name, lat, lng) {
    try {
        const response = await fetch(apiUrl('/api/cities'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, lat, lng })
        });
        
        const data = await response.json();
        if (data.success) {
            await loadCities();
        }
    } catch (error) {
        console.error('Error adding city:', error);
        alert('Lỗi khi thêm địa điểm!');
    }
}

// Xóa thành phố
async function deleteCity(name) {
    if (!confirm(`Bạn có chắc muốn xóa "${name}"?`)) return;
    
    try {
        const response = await fetch(apiUrl(`/api/cities/${encodeURIComponent(name)}`), {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            await loadCities();
            // Clear result
            document.getElementById('result-box').classList.remove('show');
        }
    } catch (error) {
        console.error('Error deleting city:', error);
        alert('Lỗi khi xóa địa điểm!');
    }
}

// Giải bài toán TSP
async function solveTSP() {
    const solveBtn = document.getElementById('solve-btn');
    const statusMessage = document.getElementById('status-message');
    const algorithm = document.getElementById('algorithm-select').value;
    
    // Disable button
    solveBtn.disabled = true;
    solveBtn.innerHTML = '[PROCESSING...]';
    
    // Show status
    statusMessage.textContent = '🔍 Đang tính toán ma trận khoảng cách...';
    statusMessage.classList.add('show');
    
    // Hide old results
    document.getElementById('result-section').style.display = 'none';
    document.getElementById('calculation-section').style.display = 'none';
    document.getElementById('comparison-section').style.display = 'none';
    
    // Clear all old layers (lines and labels)
    map.eachLayer(function(layer) {
        if (layer instanceof L.Polyline || (layer instanceof L.Marker && layer.options.icon && layer.options.icon.options.className === 'distance-label')) {
            map.removeLayer(layer);
        }
    });
    
    try {
        // Start solving
        const response = await fetch(apiUrl('/api/solve'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ algorithm: algorithm })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update status
            statusMessage.textContent = '✅ Hoàn thành! Đang vẽ animation...';
            
            // Show results with animation
            await animateSolution(data);
            
            // Display final result
            displayResult(data);
            
            // Hide status after animation
            statusMessage.classList.remove('show');
        } else {
            alert(data.error || 'Có lỗi xảy ra!');
        }
    } catch (error) {
        console.error('Error solving TSP:', error);
        alert('Lỗi khi giải bài toán!');
    } finally {
        // Re-enable button
        solveBtn.disabled = false;
        solveBtn.innerHTML = '[RUN] GIẢI BÀI TOÁN';
        statusMessage.classList.remove('show');
    }
}

// Animate giải pháp từng bước
async function animateSolution(data) {
    const steps = data.steps;
    const calculationSteps = document.getElementById('calculation-steps');
    const calculationSection = document.getElementById('calculation-section');
    
    calculationSection.style.display = 'block';
    calculationSteps.innerHTML = '';
    
    // Get city coordinates
    const response = await fetch(apiUrl('/api/cities'));
    const cities = await response.json();
    const cityMap = Object.fromEntries(cities);
    
    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        
        // Highlight current city in sidebar
        document.querySelectorAll('.city-item').forEach(item => {
            item.classList.remove('highlighted');
        });
        
        if (step.current) {
            const currentCityElem = document.getElementById(`city-${step.current}`);
            if (currentCityElem) {
                currentCityElem.classList.add('highlighted');
                currentCityElem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
        
        // Add calculation step to sidebar
        const stepDiv = document.createElement('div');
        stepDiv.className = 'step-item active';
        stepDiv.id = `calc-step-${i}`;
        
        let stepHTML = `<div class="step-header">BƯỚC ${step.step}: ${step.current || 'Bắt đầu'}</div>`;
        
        if (step.candidates && step.candidates.length > 0) {
            const algorithm = document.getElementById('algorithm-select').value;
            const algName = algorithm === 'greedy' ? 'Greedy BFS' : (algorithm === 'best-first' ? 'UCS' : 'A*');
            stepHTML += `<div class="step-candidates">Đánh giá (${algName}):<br>`;
            step.candidates.forEach(c => {
                const heuristic = c.heuristic !== undefined ? c.heuristic : 'N/A';
                const g = c.g !== undefined ? c.g : c.distance;
                const f = c.f !== undefined ? c.f : 'N/A';
                stepHTML += `  • ${c.city}:<br>`;
                if (algorithm === 'greedy') {
                    stepHTML += `    - h(n) = ${heuristic.toFixed(2)} km ⭐<br>`;
                } else if (algorithm === 'best-first') {
                    stepHTML += `    - g(n) = ${g.toFixed(2)} km ⭐<br>`;
                } else {
                    stepHTML += `    - g(n) = ${g.toFixed(2)} km<br>`;
                    stepHTML += `    - h(n) = ${heuristic.toFixed(2)} km<br>`;
                    stepHTML += `    - f(n) = ${f.toFixed(2)} km ⭐<br>`;
                }
            });
            stepHTML += '</div>';
            
            if (step.next) {
                const hInfo = step.heuristic !== undefined ? ` (h=${step.heuristic.toFixed(2)} km - nhỏ nhất)` : '';
                stepHTML += `<div class="step-chosen">→ CHỌN: ${step.next}${hInfo}<br>Chi phí: ${step.distance.toFixed(2)} km</div>`;
            }
        } else if (step.next) {
            stepHTML += `<div class="step-chosen">→ Quay về: ${step.next} (${step.distance.toFixed(2)} km)</div>`;
        }
        
        stepDiv.innerHTML = stepHTML;
        calculationSteps.appendChild(stepDiv);
        
        // Scroll to latest step
        stepDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
        
        // Highlight marker on map
        await loadCities();
        if (step.current_idx !== undefined && data.route[step.step] !== undefined) {
            const cityName = data.route[step.step];
            const city = cities.find(c => c[0] === cityName);
            
            if (city) {
                if (markers[cityName]) {
                    map.removeLayer(markers[cityName]);
                }
                addMarker(cityName, city[1][0], city[1][1], true);
            }
        }
        
        // Draw line from current to next
        if (step.next && step.current) {
            const currentCoords = cityMap[step.current];
            const nextCoords = cityMap[step.next];
            
            if (currentCoords && nextCoords) {
                // Draw the new segment
                const newLine = L.polyline([
                    [currentCoords[0], currentCoords[1]],
                    [nextCoords[0], nextCoords[1]]
                ], {
                    color: '#2d6b3d',
                    weight: 3,
                    opacity: 0.8
                }).addTo(map);
                
                // Add label for distance
                const midLat = (currentCoords[0] + nextCoords[0]) / 2;
                const midLng = (currentCoords[1] + nextCoords[1]) / 2;
                
                L.marker([midLat, midLng], {
                    icon: L.divIcon({
                        className: 'distance-label',
                        html: `<div style="
                            background: #2d6b3d;
                            color: #fff;
                            padding: 3px 8px;
                            font-size: 11px;
                            font-weight: bold;
                            border: 1px solid #2d6b3d;
                            white-space: nowrap;
                        ">${step.distance.toFixed(1)} km</div>`,
                        iconSize: [60, 20]
                    })
                }).addTo(map);
            }
        }
        
        // Remove active class from previous step
        if (i > 0) {
            const prevStep = document.getElementById(`calc-step-${i-1}`);
            if (prevStep) {
                prevStep.classList.remove('active');
            }
        }
        
        // Wait for animation
        await new Promise(resolve => setTimeout(resolve, 1200));
    }
    
    // Remove active class from last step
    const lastStep = document.getElementById(`calc-step-${steps.length-1}`);
    if (lastStep) {
        lastStep.classList.remove('active');
    }
}

// Hiển thị kết quả cuối cùng
async function displayResult(data) {
    const resultSection = document.getElementById('result-section');
    const totalDistance = document.getElementById('total-distance');
    const routeSteps = document.getElementById('route-steps');
    
    // Show result section
    resultSection.style.display = 'block';
    
    // Display distance
    totalDistance.textContent = `${data.total_distance.toFixed(2)} km`;
    
    // Display route
    routeSteps.innerHTML = '';
    data.route.forEach((city, index) => {
        const div = document.createElement('div');
        div.className = 'route-step';
        div.innerHTML = `[${index + 1}] ${city}`;
        routeSteps.appendChild(div);
    });
    
    // Fit map to route
    const response = await fetch(apiUrl('/api/cities'));
    const cities = await response.json();
    const cityMap = Object.fromEntries(cities);
    
    const routeCoords = data.route.map(cityName => {
        const coords = cityMap[cityName];
        return [coords[0], coords[1]];
    });
    
    map.fitBounds(L.latLngBounds(routeCoords), { padding: [50, 50] });
}

// Switch giữa các tình huống
async function switchScenario(scenarioId) {
    try {
        console.log(`🔄 Switching to Scenario ${scenarioId}...`);
        
        const response = await fetch(apiUrl(`/api/scenario/${scenarioId}`), {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update UI: toggle active class
            document.querySelectorAll('.scenario-btn').forEach(btn => {
                btn.classList.remove('active');
                btn.style.background = '#2d6b3d';
                btn.style.color = '#fff';
            });
            
            const activeBtn = document.getElementById(`scenario-${scenarioId}`);
            activeBtn.classList.add('active');
            activeBtn.style.background = '#fff';
            activeBtn.style.color = '#2d6b3d';
            
            // Clear map
            map.eachLayer(function(layer) {
                if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                    map.removeLayer(layer);
                }
            });
            
            // Hide results
            document.getElementById('result-section').style.display = 'none';
            document.getElementById('calculation-section').style.display = 'none';
            document.getElementById('comparison-section').style.display = 'none';
            
            // Load new cities
            await loadCities();
            
            console.log(`✅ Switched to Scenario ${scenarioId}: ${data.cities.length} cities`);
        } else {
            alert('Lỗi khi chuyển tình huống!');
        }
    } catch (error) {
        console.error('Error switching scenario:', error);
        alert('Lỗi khi chuyển tình huống!');
    }
}

// Reset tất cả
async function resetAll() {
    if (!confirm('Bạn có chắc muốn đặt lại tất cả?')) return;
    
    try {
        const response = await fetch(apiUrl('/api/reset'), {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            // Clear all layers except base map
            map.eachLayer(function(layer) {
                if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                    map.removeLayer(layer);
                }
            });
            
            routeLine = null;
            
            // Hide result sections
            document.getElementById('result-section').style.display = 'none';
            document.getElementById('calculation-section').style.display = 'none';
            
            // Reload cities
            await loadCities();
        }
    } catch (error) {
        console.error('Error resetting:', error);
        alert('Lỗi khi đặt lại!');
    }
}

// So sánh tất cả thuật toán
async function compareAllAlgorithms() {
    const compareBtn = document.getElementById('compare-btn');
    const statusMessage = document.getElementById('status-message');
    
    // Disable button
    compareBtn.disabled = true;
    compareBtn.innerHTML = '[COMPARING...]';
    
    // Show status
    statusMessage.textContent = '📊 Đang chạy tất cả thuật toán...';
    statusMessage.classList.add('show');
    
    // Hide other sections
    document.getElementById('result-section').style.display = 'none';
    document.getElementById('calculation-section').style.display = 'none';
    
    try {
        const response = await fetch(apiUrl('/api/compare'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayComparison(data.results);
            document.getElementById('comparison-section').style.display = 'block';
            statusMessage.classList.remove('show');
        } else {
            alert(data.error || 'Có lỗi xảy ra!');
        }
    } catch (error) {
        console.error('Error comparing algorithms:', error);
        alert('Lỗi khi so sánh thuật toán!');
    } finally {
        compareBtn.disabled = false;
        compareBtn.innerHTML = '[COMPARE] SO SÁNH TẤT CẢ';
        statusMessage.classList.remove('show');
    }
}

// Hiển thị kết quả so sánh
function displayComparison(results) {
    const resultsDiv = document.getElementById('comparison-results');
    const chartsDiv = document.getElementById('comparison-charts');
    
    // Tạo bảng so sánh
    let html = '<table class="comparison-table"><thead><tr>';
    html += '<th>Thuật toán</th><th>Khoảng cách (km)</th><th>Thời gian</th><th>Operations</th>';
    html += '</tr></thead><tbody>';
    
    // Tìm giá trị tốt nhất
    let bestDistance = Infinity;
    let bestTime = Infinity;
    let bestOps = Infinity;
    
    Object.values(results).forEach(r => {
        if (r.distance < bestDistance) bestDistance = r.distance;
        if (r.time < bestTime) bestTime = r.time;
        if (r.operations < bestOps) bestOps = r.operations;
    });
    
    Object.keys(results).forEach(algo => {
        const r = results[algo];
        const distClass = r.distance === bestDistance ? ' comparison-best' : '';
        const timeClass = r.time === bestTime ? ' comparison-best' : '';
        const opsClass = r.operations === bestOps ? ' comparison-best' : '';
        
        // Format time với đơn vị phù hợp
        const timeDisplay = r.time_display || `${r.time.toFixed(4)}s`;
        
        html += `<tr>
            <td><strong>${algo}</strong></td>
            <td class="${distClass}">${r.distance}</td>
            <td class="${timeClass}">${timeDisplay}</td>
            <td class="${opsClass}">${r.operations}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    resultsDiv.innerHTML = html;
    
    // Tạo biểu đồ
    chartsDiv.innerHTML = '';
    
    // Biểu đồ khoảng cách
    const distanceChart = createBarChart('Khoảng cách (km)', results, 'distance', bestDistance);
    chartsDiv.appendChild(distanceChart);
    
    // Biểu đồ thời gian
    const timeChart = createBarChart('Thời gian (s)', results, 'time', bestTime);
    chartsDiv.appendChild(timeChart);
    
    // Biểu đồ operations
    const opsChart = createBarChart('Số phép tính (operations)', results, 'operations', bestOps);
    chartsDiv.appendChild(opsChart);
}

// Tạo biểu đồ thanh
function createBarChart(title, results, key, bestValue) {
    const container = document.createElement('div');
    container.className = 'chart-container';
    
    const titleDiv = document.createElement('div');
    titleDiv.className = 'chart-title';
    titleDiv.textContent = title;
    container.appendChild(titleDiv);
    
    // Tìm giá trị max để scale
    let maxValue = 0;
    Object.values(results).forEach(r => {
        if (r[key] > maxValue) maxValue = r[key];
    });
    
    Object.keys(results).forEach(algo => {
        const value = results[algo][key];
        const percentage = (value / maxValue) * 100;
        
        const barDiv = document.createElement('div');
        barDiv.className = 'chart-bar';
        
        const labelDiv = document.createElement('div');
        labelDiv.className = 'chart-label';
        labelDiv.textContent = algo.replace(' Search', '').replace(' Algorithm', '');
        
        const fillDiv = document.createElement('div');
        fillDiv.className = 'chart-bar-fill';
        fillDiv.style.width = `${percentage}%`;
        if (value === bestValue) {
            fillDiv.style.background = '#2d6b3d';
        } else {
            fillDiv.style.background = '#999';
        }
        
        const valueDiv = document.createElement('div');
        valueDiv.className = 'chart-value';
        valueDiv.textContent = value;
        
        barDiv.appendChild(labelDiv);
        barDiv.appendChild(fillDiv);
        barDiv.appendChild(valueDiv);
        
        container.appendChild(barDiv);
    });
    
    return container;
}

// Initialize when page loads
window.onload = function() {
    initMap();
};
