# Import bảng giá dịch vụ vào Directory Service

Script import CSV để đổ dữ liệu dịch vụ + giá vào DB directory.

## Yêu cầu môi trường
- Container/venv có `sqlalchemy` và biến môi trường `DIRECTORY_DATABASE_URL` đã cấu hình.
- File CSV với header:
  `hospital_id,service_code,service_name,unit,category_name,payer_type,price,currency,effective_from,effective_to,notes,status`
  (file mẫu: `core-service/app/knowledgebases/hospital_1/service_price.csv`).

## Chạy trong container
```bash
# từ thư mục repo (có docker-compose.yml)
docker compose exec core-service bash

# trong container (đường dẫn app đã mount tại /app)
python /app/scripts/import_service_prices.py \
  --csv /app/knowledgebases/hospital_1/service_price.csv \
  --hospital-id 1
```

Tham số:
- `--csv`: đường dẫn CSV trong container.
- `--hospital-id` (tùy chọn): override hospital_id cho toàn bộ file (nếu CSV không có hoặc muốn ép về một bệnh viện).

## Tác vụ của script
- Tạo/cập nhật `ServiceCategory` theo `category_name` + `hospital_id` nếu chưa có.
- Tạo/cập nhật `Service` theo `service_code` + `hospital_id`; cập nhật tên và gắn category nếu thiếu.
- Upsert `ServicePrice` theo (service_id, hospital_id, payer_type, area_tag, effective_from, effective_to); giá và ĐVT được lưu, ĐVT thêm vào `notes`.

## Build index FAISS cho tra cứu dịch vụ (tùy chọn)
Sau khi import dịch vụ/giá, có thể build index FAISS để search nhanh:
```bash
docker compose exec core-service bash -lc "python /app/scripts/build_service_index.py --hospital-id 1"
```
Index/metadata lưu tại `/app/data/indexes/service-faiss.index` và `service-metadata.json`; API `/prices/lookup` sẽ ưu tiên dùng index này nếu có, fallback DB LIKE khi thiếu.

## Lưu ý
- Nếu thay đổi schema của `SERVICE_PRICES`, đảm bảo đã migrate DB trước khi import.
- `payer_type` nên đặt cùng giá trị bạn dùng trong enum/logic (ví dụ: `BHYT`, `TU_CHI_TRA`).
