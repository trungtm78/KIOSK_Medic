# 🧭 Hướng dẫn sử dụng Gephi để vẽ sơ đồ bệnh viện

## 1. Cài đặt Gephi
- Tải tại: [https://gephi.org/](https://gephi.org/)  
- Cài đặt như phần mềm bình thường (Windows/Linux/Mac).  
- Yêu cầu: Java 11 (Gephi kèm theo sẵn).

---

## 2. Tạo Project mới
- Mở Gephi → **File > New Project**.  
- Tab **Overview** sẽ hiển thị canvas trống.

---

## 3. Thêm Node (POI)
- Vào tab **Data Laboratory** → chọn **Nodes**.  
- Thêm dòng mới:
  - **Id**: mã POI (vd: `LOBBY_A`, `ELEV_C1`).  
  - **Label**: tên hiển thị (vd: `Sảnh A`).  
- Có thể thêm **columns (attributes)**:
  - `building` (A, B, C)  
  - `floor` (1, 2, …)  
  - `category` (entrance, lobby, clinic, elevator, pharmacy, …)

👉 Cách thêm column: Data Laboratory → **Add Column**.

---

## 4. Thêm Edge (kết nối)
- Trong **Data Laboratory** → chọn **Edges**.  
- Thêm dòng mới:
  - **Source**: `poi_id` đầu.  
  - **Target**: `poi_id` cuối.  
  - **Type**: Directed / Undirected (nếu đi 2 chiều thì chọn Undirected).  
- Có thể thêm attributes cho edge:
  - `distance_m` (độ dài, mét).  
  - `via` (Hall, Elevator, Stair, Skybridge).  
  - `indoor` (True/False).  
  - `notes` (ghi chú).

---

## 5. Vẽ sơ đồ trực quan
- Quay lại **Overview**.  
- Node sẽ hiển thị dưới dạng chấm, edge là đường nối.  
- Dùng chuột kéo node để bố trí theo layout thực.  
- Panel **Layout** (bên trái) hỗ trợ auto sắp xếp:
  - **ForceAtlas2** → dàn đều node.  
  - Hoặc kéo thủ công cho giống sơ đồ bệnh viện.

---

## 6. Tô màu & phân tầng
- Vào **Appearance** (bên trái):
  - Chọn **Nodes → Partition** → tô màu theo `building` hoặc `floor`.  
  - Chọn **Edges → Partition** → tô màu theo `via`.

---

## 7. Import file `.gexf`
- Vào **File → Open…**.  
- Chọn file `.gexf` (vd: `hospital_graph.gexf`).  
- Hộp thoại Import xuất hiện → chọn **As Graph** → **OK**.  
- Graph sẽ hiện trong tab **Overview**.

---

## 8. Export dữ liệu
- **File → Export → Graph file → .gexf** (định dạng chuẩn).  
- Hoặc xuất CSV:
  - Trong **Data Laboratory** → **Export Table** (Nodes/Edges).  

---

## 9. Quy trình làm việc gợi ý cho nhân viên
1. Mỗi phòng / khu vực = 1 node.  
2. Đường đi (corridor, thang máy, cầu thang, skybridge) = 1 edge.  
3. Nếu nhiều tầng:
   - Tạo node `ELEV_C1` (tầng 1) và `ELEV_C2` (tầng 2).  
   - Nối chúng bằng edge có `via=elevator`.  
4. Sau khi hoàn thành → Export `.gexf` → gửi cho team kỹ thuật để convert thành `poi.csv` và `map_edges.csv`.

---
