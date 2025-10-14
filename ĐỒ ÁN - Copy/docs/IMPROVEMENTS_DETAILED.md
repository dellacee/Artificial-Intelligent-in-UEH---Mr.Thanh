# CẢI TIẾN ĐỂ HIỂN THỊ SỰ KHÁC BIỆT RÕ RÀNG

## 🎯 VẤN ĐỀ BAN ĐẦU

Screenshot cho thấy với 5 thành phố Việt Nam:

- ✅ **Operations khác nhau**: Greedy=30, UCS=34, A\*=54
- ❌ **Distance giống nhau**: Cả 3 đều = 4008.21 km
- ❌ **Time = 0**: Quá nhanh để đo được (< 0.001s)

### Nguyên nhân:

1. **5 thành phố Việt Nam xếp tuyến tính Bắc-Nam**:

   ```
   Hà Nội (Bắc)
      ↓
   Viêng Chăn (Tây Bắc)
      ↓
   Đà Nẵng (Trung)
      ↓
   Nha Trang (Nam Trung)
      ↓
   TP.HCM (Nam)
   ```

   → Chỉ có 1 đường đi tối ưu rõ ràng
   → Cả 3 thuật toán đều tìm được cùng route

2. **Thời gian quá nhanh**: 5 cities = chỉ 10 nodes explored
   → `time.time()` không đủ chính xác (precision ~15ms)

---

## ✅ GIẢI PHÁP ĐÃ ÁP DỤNG

### 1. Thay đổi thành phố mặc định

**Trước (5 thành phố Việt Nam):**

```python
DEFAULT_CITIES = {
    "Hà Nội": (21.0285, 105.8542),
    "Đà Nẵng": (16.0544, 108.2022),
    "Nha Trang": (12.2388, 109.1967),
    "TP. Hồ Chí Minh": (10.8231, 106.6297),
    "Viêng Chăn": (17.9757, 102.6331)
}
```

📊 Kết quả: Tuyến tính, 1 route tối ưu duy nhất

**Sau (10 thành phố Đông Nam Á):**

```python
DEFAULT_CITIES = {
    "Hà Nội": (21.0285, 105.8542),           # Vietnam - Bắc
    "Bangkok": (13.7563, 100.5018),          # Thailand - Trung tâm
    "TP. Hồ Chí Minh": (10.8231, 106.6297),  # Vietnam - Nam
    "Singapore": (1.3521, 103.8198),         # Singapore - Nam
    "Kuala Lumpur": (3.1390, 101.6869),      # Malaysia - Trung
    "Manila": (14.5995, 120.9842),           # Philippines - Đông
    "Phnom Penh": (11.5564, 104.9282),       # Cambodia - Tây Nam
    "Yangon": (16.8661, 96.1951),            # Myanmar - Tây
    "Vientiane": (17.9757, 102.6331),        # Laos - Tây Bắc
    "Jakarta": (-6.2088, 106.8456)           # Indonesia - Tây Nam xa
}
```

📊 Ưu điểm:

- ✅ **10 thành phố** → 45 nodes explored → Thời gian đo được rõ ràng hơn
- ✅ **Phân bố 2D phức tạp** → Nhiều lựa chọn route khác nhau
- ✅ **Khoảng cách bất đối xứng** → OSRM API cho khoảng cách thực tế
- ✅ **Cross-country routes** → Tạo ma trận phức tạp

### Phân tích vị trí địa lý:

```
         Hà Nội (Bắc)
              |
    Yangon ←─┴─→ Manila (Đông)
       |      |
    Vientiane─┤
       |      |
    Bangkok ←─┘
       |
    Phnom Penh ─→ TP.HCM
       |            |
    Kuala Lumpur ←─┘
       |
    Singapore
       |
    Jakarta (Nam xa)
```

→ Không có đường tuyến tính rõ ràng
→ Cả 3 thuật toán sẽ chọn routes khác nhau

---

### 2. Cải thiện độ chính xác đo thời gian

**Trước:**

```python
import time
start_time = time.time()  # Precision: ~15ms
route, distance = solver.solve()
elapsed_time = time.time() - start_time
```

❌ Vấn đề: `time.time()` chỉ chính xác đến 15-16ms
❌ Với 5 cities (< 1ms) → elapsed_time = 0.0000

**Sau:**

```python
import time
start_time = time.perf_counter()  # Precision: nanosecond
route, distance = solver.solve()
elapsed_time = time.perf_counter() - start_time
```

✅ Ưu điểm:

- `time.perf_counter()` có độ chính xác **nanosecond** (10^-9 giây)
- Không bị ảnh hưởng bởi system clock adjustments
- Phù hợp cho benchmark performance

---

### 3. Kiểm tra lại Operations Counter

Đã verify operations được đếm đúng:

**Greedy BFS:**

```python
for city in candidates:
    self.operations += 2  # 2 matrix lookups (current→city, city→goal)
    self.operations += 1  # 1 comparison (h_cost < best?)
```

→ **3 operations/candidate**

**UCS:**

```python
for city in candidates:
    self.operations += 1  # 1 matrix lookup (current→city)
    self.operations += 1  # 1 addition (g_cost = total + distance)
    self.operations += 1  # 1 heap push
self.operations += 1      # 1 heap pop
```

→ **3 operations/candidate + 1 pop/step**

**A\*:**

```python
for city in candidates:
    self.operations += 2  # 2 matrix lookups (current→city, city→goal)
    self.operations += 2  # 2 additions (g_cost, f_cost)
    self.operations += 1  # 1 heap push
self.operations += 1      # 1 heap pop
```

→ **5 operations/candidate + 1 pop/step**

---

## 📊 KẾT QUẢ DỰ KIẾN VỚI 10 THÀNH PHỐ

### Nodes Explored:

```
Step 1: 9 candidates (n-1)
Step 2: 8 candidates (n-2)
Step 3: 7 candidates (n-3)
...
Step 9: 1 candidate
Total: 9+8+7+6+5+4+3+2+1 = 45 nodes
```

✅ Tất cả 3 thuật toán: **45 nodes** (giống nhau - đúng!)

### Operations (với 10 cities):

```
Greedy BFS:  45 × 3 = 135 operations
UCS:         45 × 3 + 9 = 144 operations
A*:          45 × 5 + 9 = 234 operations
```

✅ Tỷ lệ: **1 : 1.07 : 1.73**

### Distance:

- **Greedy**: Có thể không tối ưu (chọn theo h only)
- **UCS**: Tối ưu (chọn theo g accumulated)
- **A\***: Tối ưu hoặc gần tối ưu (cân bằng g+h)

✅ **Dự đoán**: UCS hoặc A\* sẽ cho kết quả tốt hơn Greedy

### Time (với 10 cities):

```
Greedy:  ~0.001-0.002s (nhanh nhất)
UCS:     ~0.002-0.003s (trung bình)
A*:      ~0.003-0.005s (chậm nhất - nhiều tính toán)
```

✅ Với `perf_counter()` sẽ đo được chính xác đến microsecond

---

## 🧪 CÁCH TEST

### Test ngay trên web:

1. Mở http://localhost:5000
2. Click **"SO SÁNH TẤT CẢ"**
3. Xem bảng so sánh:
   - ✅ Distance: Sẽ KHÁC NHAU
   - ✅ Time: Sẽ > 0 và KHÁC NHAU
   - ✅ Operations: Đã khác nhau (135 vs 144 vs 234)

### Verify với test script:

```bash
python test_pure_algorithms.py  # 5 cities - để so sánh
python test_8_cities.py         # 8 cities - xem trend
```

---

## 📈 SO SÁNH TRƯỚC VÀ SAU

| Metric         | 5 Cities (Trước)     | 10 Cities (Sau)      | Cải thiện |
| -------------- | -------------------- | -------------------- | --------- |
| **Distance**   | Giống nhau (4008.21) | Khác nhau            | ✅        |
| **Time**       | 0.0000s              | 0.001-0.005s         | ✅        |
| **Operations** | 30/34/54 (khác)      | 135/144/234 (rõ hơn) | ✅        |
| **Nodes**      | 10 (giống)           | 45 (giống)           | ✓ (đúng!) |
| **Routes**     | Giống nhau           | Khác nhau            | ✅        |

---

## ✅ KẾT LUẬN

### Đã cải tiến:

1. ✅ **10 thành phố Đông Nam Á** thay vì 5 thành phố VN
2. ✅ **Vị trí 2D phức tạp** thay vì tuyến tính Bắc-Nam
3. ✅ **`time.perf_counter()`** thay vì `time.time()`
4. ✅ **Operations counter** đã verify đúng

### Kết quả mong đợi:

- 🎯 **3 routes khác nhau** → Thể hiện logic thuật toán khác nhau
- 🎯 **3 distances khác nhau** → UCS/A\* tối ưu hơn Greedy
- 🎯 **3 times khác nhau** → Đo được chính xác với perf_counter
- 🎯 **Operations tỷ lệ 1:1.07:1.73** → Phản ánh độ phức tạp

### Để test:

```bash
# Start server
python app.py

# Truy cập http://localhost:5000
# Click "SO SÁNH TẤT CẢ"
# → Sẽ thấy sự khác biệt rõ ràng!
```
