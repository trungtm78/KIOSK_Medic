# Admin Service – Database Tables Explanation

## 1. TENANTS
Đây là bảng trung tâm quản lý toàn bộ thông tin định danh của các tổ chức/đơn vị (tenant).  
Bao gồm: mã định danh, tên, trạng thái (active/suspended…), gói dịch vụ, timezone, locale, logo.  
Tất cả các bảng khác đều liên kết khóa ngoại (FK) về bảng này.

---

## 2. TENANT_FEATURES
Quản lý **feature flags** theo từng tenant.  
Cho phép kiểm soát việc bật/tắt tính năng độc lập cho mỗi tenant, đảm bảo triển khai (rollout) có thể thực hiện theo từng đơn vị mà không ảnh hưởng toàn hệ thống.

---

## 3. TENANT_QUOTAS
Quản lý **quota/giới hạn** sử dụng cho tenant.  
Ví dụ: số lượt phát số thứ tự tối đa mỗi tháng, số lượng quầy hoạt động, v.v.  
Có hỗ trợ chính sách reset: theo ngày, tháng, hoặc không reset.

---

## 4. TENANT_CONNECTIONS
Mapping giữa tenant và datasource của từng domain service.  
Ví dụ: tenant A ánh xạ đến schema `hospital_a_pricing`, tenant B sử dụng database riêng.  
Cho phép Admin Service định tuyến đúng dữ liệu khi domain service được gọi.

---

## 5. ROLES / PERMISSIONS / ROLE_PERMISSIONS
Catalog RBAC toàn cục của hệ thống:  
- **ROLES**: Các vai trò chuẩn (ADMIN, OPERATOR, VIEWER).  
- **PERMISSIONS**: Các quyền chi tiết (TENANT.READ, PRICING.WRITE...).  
- **ROLE_PERMISSIONS**: Ánh xạ vai trò ↔ quyền.  

Các role có thể được sử dụng chung và override trong phạm vi từng tenant.

---

## 6. TENANT_USERS
Danh sách người dùng thuộc mỗi tenant.  
Liên kết với Identity Provider (Keycloak, Azure AD, …) thông qua `user_sub`.  
Được sử dụng để cấp quyền đăng nhập vào portal quản trị của tenant.

---

## 7. TENANT_USER_ROLES
Quản lý việc gán vai trò (role) cho từng user trong phạm vi tenant.  
Ví dụ: cùng một user có thể là **ADMIN** tại tenant X nhưng chỉ là **VIEWER** tại tenant Y.

---

## 8. API_KEYS
Quản lý API key cho các kết nối máy–máy (machine-to-machine).  
Ví dụ: kiosk hoặc BFF gọi Admin API bằng API key thay vì OAuth user.  
Key được lưu dưới dạng hash an toàn, không lưu trữ bản gốc.

---

## 9. SETTINGS
Catalog các loại cấu hình mặc định (global settings) của hệ thống.  
Ví dụ: `ui.default_language`, `queue.max_ticket_per_day`.  
Mỗi config có thể kèm theo giá trị mặc định dạng JSON.

---

## 10. TENANT_SETTINGS
Override cấu hình theo các scope: global → tenant → facility → device.  
Ví dụ: ngôn ngữ mặc định hệ thống là en-US, nhưng tenant B override thành vi-VN, và riêng facility C của tenant B lại dùng en-US.  
Cho phép tùy biến nhiều tầng, áp dụng theo độ ưu tiên.

---

## 11. WEBHOOKS
Quản lý webhook đăng ký theo tenant để nhận sự kiện thay đổi.  
Ví dụ: khi quota thay đổi hoặc feature được bật/tắt, webhook sẽ thông báo tới domain service để refresh cache.  
Đảm bảo hệ thống hoạt động theo hướng event-driven, tránh việc domain service phải polling.

---

## 12. AUDIT_LOGS
Lưu trữ lịch sử thay đổi và hành động quan trọng.  
Ghi nhận: ai (user_sub/API key) đã thực hiện, hành động gì, thay đổi entity nào, vào thời điểm nào.  
Ví dụ: “User X tại tenant Y bật feature eKYC vào 2025-10-01”.  
Cần thiết cho mục đích compliance, forensic, và rollback.
