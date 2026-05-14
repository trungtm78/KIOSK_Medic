# Medic Agent

Nền tảng trợ lý y tế theo kiến trúc microservices, tập trung vào hội thoại, tra cứu dịch vụ, điều hướng và tích hợp giọng nói. Repo này chứa backend services, gateway, dữ liệu mẫu và tài liệu vận hành.

## Mục lục
- [Tổng quan](#tổng-quan)
- [Kiến trúc](#kiến-trúc)
  - [Luồng dữ liệu điển hình](#luồng-dữ-liệu-điển-hình)
  - [Danh sách dịch vụ](#danh-sách-dịch-vụ)
- [Yêu cầu](#yêu-cầu)
- [Cài đặt nhanh](#cài-đặt-nhanh)
  - [Clone repo](#clone-repo)
  - [Khởi chạy dịch vụ](#khởi-chạy-dịch-vụ)
  - [Kiểm tra trạng thái](#kiểm-tra-trạng-thái)
  - [Dịch vụ tùy chọn](#dịch-vụ-tùy-chọn)
- [Sử dụng](#sử-dụng)
  - [Web frontend](#web-frontend)
  - [API test](#api-test)
- [Cấu hình môi trường](#cấu-hình-môi-trường)
- [Chi tiết từng dịch vụ](#chi-tiết-từng-dịch-vụ)
  - [Database](#database)
  - [Chat service](#chat-service)
  - [Core service](#core-service)
  - [Gateway](#gateway)
  - [Speech-to-text](#speech-to-text)
  - [Admin service](#admin-service)
- [Dữ liệu và artifacts](#dữ-liệu-và-artifacts)
- [Huấn luyện model](#huấn-luyện-model)
- [Vận hành và lưu ý](#vận-hành-và-lưu-ý)
- [Troubleshooting](#troubleshooting)

## Tổng quan
Medic Agent cung cấp các API hội thoại và nghiệp vụ y tế như tra cứu dịch vụ, điều hướng, tư vấn triệu chứng, quản lý phiên hội thoại. Hệ thống được triển khai theo mô hình nhiều dịch vụ độc lập, dễ mở rộng và thay thế thành phần.

## Kiến trúc
### Luồng dữ liệu điển hình
1) Client gọi vào gateway.
2) Gateway định tuyến tới chat service hoặc core service.
3) Chat service điều phối luồng hội thoại, gọi core service để tra cứu khi cần.
4) Core service truy vấn DB/knowledge base, trả kết quả về chat service.
5) Chat service trả kết quả về client qua API hoặc streaming.

### Danh sách dịch vụ
- `medicagent-chat-service`: hội thoại, phân loại ý định, điều phối luồng.
- `medicagent-core-service`: nghiệp vụ tra cứu, directory, info lookup, navigation.
- `medicagent-gateway` (Kong): gateway routing, CORS, logging.
- `medicagent-db` (MySQL): dữ liệu hội thoại và nghiệp vụ.
- `medicagent-stt-zipformer-service`: speech-to-text realtime.
- `admin-service`, `ollama`: thành phần phụ trợ/tùy chọn.

## Yêu cầu
- Docker + Docker Compose
- (Tùy chọn) NVIDIA GPU + NVIDIA Container Toolkit cho LLM/STT
- Cổng mặc định: 3307 (MySQL), 8082 (chat), 8083 (core), 7080/7443 (gateway), 3000 (frontend), 7081/7082 (STT)

## Cài đặt nhanh

### Clone repo
```bash
git clone git@github.com:cybertech-vn/MedicAgent.git
cd MedicAgent
```

### Khởi chạy dịch vụ
1) Database (MySQL)
```bash
docker compose up -d medicagent-db --force-recreate
```

2) Core service
```bash
docker compose up -d medicagent-core-service
```

3) Chat service
```bash
docker compose up -d medicagent-chat-service
```

4) Frontend
```bash
cd ../MedicAgent_FE
docker compose up -d
```

5) Speech-to-text
```bash
docker compose up -d medicagent-stt-zipformer-service
```

6) Gateway
```bash
docker compose --profile gateway up -d medicagent-gateway
```

### Kiểm tra trạng thái
```bash
docker compose ps
```

Xem log nhanh:
```bash
docker compose logs -f medicagent-core-service
```

### Dịch vụ tùy chọn
Admin service (chưa triển khai đầy đủ)
```bash
docker compose up -d medicagent-admin-service
```

Ollama (LLM backend)
```bash
docker compose up -d medicagent-ollama
```

## Sử dụng
URL dùng `localhost` khi test local; nếu expose ra ngoài thì dùng `ip:port` hoặc domain HTTPS.

### Web frontend
- Truy cập: `https://localhost:7443`
- Frontend chạy trong network `medicagent_default`, cần chạy backend trước.

### API test
- Swagger UI:
  - Chat service (qua gateway): `https://localhost:7443/v1/chat/docs`
  - Core service (qua gateway): `https://localhost:7443/v1/core/docs`
- Streaming event mẫu:
  ```bash
  curl -N "https://localhost:7443/v1/chat/1001/stream"
  ```
- Gửi message mẫu:
  ```bash
  curl -X POST "https://localhost:7443/v1/chat/1001" \
    -H "Content-Type: application/json" \
    -H "X-Tenant-Id: 1" \
    -H "Idempotency-Key: test" \
    -d "{\"role\":\"user\",\"content\":\"Xin chào, tôi muốn tư vấn khám bệnh\"}"
  ```

## Cấu hình môi trường
- Compose đọc `.env` trong `MedicAgent/.env`.
- Override MySQL bằng `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_ROOT_PASSWORD`.
- Chat service và core service đọc biến môi trường từ `.env` và trong Docker Compose.

## Chi tiết từng dịch vụ

### Database
- MySQL lưu dữ liệu hội thoại, directory, queue, v.v.
- Init scripts nằm ở `data/mysql-init`.

Dump:
```bash
docker exec -i medicagent-db mysqldump -u root -p --databases chat_service medicagent-directory-db medicagent-queue-db > /home/thuantruong/01_MedicAgent/src/MedicAgent/data/dump/multi.sql
```

Restore:
```bash
docker exec -i medicagent-db mysql -u root -p<ROOT_PW> < /home/thuantruong/01_MedicAgent/src/MedicAgent/data/dump/multi.sql
```

### Chat service
Luồng hỗ trợ:
- Lấy số khám bệnh (issue ticket)
- Tra cứu thông tin (info lookup)
- Tư vấn khám bệnh (triage)

Thành phần chính:
- Orchestrating: điều phối hội thoại, gọi core service.
- State machine: định nghĩa trạng thái hội thoại và chuyển trạng thái.
- Intent classification: chọn luồng phù hợp (rule + ML).

Các phần quan trọng trong code:
- State machine config: `chat-service/app/core/state_machine/statechart.sismic.yaml`
- Action/guard/context: `chat-service/app/core/state_machine/`

### Core service
Chức năng:
- Directory service: danh bạ/phòng khám/bác sĩ.
- Infolookup service: dịch vụ, giá, hướng dẫn.
- Navigation service: gợi ý đường đi trong bệnh viện.

Multi-tenant:
- Các request cần `hospital_id`.
- Knowledge base có default và tenant-specific.
- Fallback về default khi không tìm thấy tenant.

Policy:
- Dùng Qdrant lưu/search vector, embedding với `AITeamVN/Vietnamese_Embedding`.
- Lần đầu gọi lookup sẽ embed dữ liệu trong `core-service/app/knowledgebases` (request đầu có thể chậm).
- Kết hợp semantic + lexical search.

### Gateway
- Routing + CORS + logging, hỗ trợ multi-tenant, API key/ACL.
- Prefix chuẩn: `/v1/chat`, `/v1/core`, `/v1/queue`, `/v1/directory`, `/v1/info/*`.
- Cấu hình Kong DB-less: `gateway/kong/kong.yaml`.

### Speech-to-text
- Nhận audio realtime và trả text qua websocket.
- Mặc định dùng Zipformer; có thể thay model nếu có ràng buộc thương mại.
- Nếu dùng GPU, cần NVIDIA Container Toolkit.

### Admin service
- Mục tiêu: quản trị cấu hình, kịch bản hội thoại, dữ liệu danh mục.
- Hiện chưa triển khai đầy đủ.

## Dữ liệu và artifacts
- `core-service/data/indexes`: FAISS index và metadata được build ở lần chạy đầu.
- `core-service/app/knowledgebases`: dữ liệu nền để embed/tra cứu.
- `data/dump`: file dump/restore MySQL.

## Huấn luyện model
Intent classification:
- Script: `chat-service/scripts/train_intent_classifier.py`
- Embedding: `AITeamVN/Vietnamese_Embedding`
- Classification: Logistic Regression

Syndrome classification:
- Script: `chat-service/scripts/train_syndrome_classifier.py`
- Embedding: `AITeamVN/Vietnamese_Embedding`
- Classification: Logistic Regression

Chạy nhanh:
```bash
python scripts/train_intent_classifier.py
python scripts/train_syndrome_classifier.py
```

Chạy đầy đủ:
```powershell
python scripts/train_intent_classifier.py `
  --data chat-service/data/intent_training_examples.jsonl `
  --output-dir chat-service/models/intent_classifier `
  --model-name AITeamVN/Vietnamese_Embedding
```

Model output lưu tại `MedicAgent/chat-service/models` và được mount vào container chat-service.

## Vận hành và lưu ý
- Lần đầu khởi chạy core-service sẽ tạo index FAISS và cache; dữ liệu nằm trong `core-service/data/indexes`.
- Nếu chạy container dưới quyền root, file sinh ra trong volume có thể thuộc root. Dùng `chown` để tránh lỗi `git pull`.
- Không chạy `docker compose up` với `sudo` để tránh file thuộc root trong repo.
- Khi cập nhật code, nên `docker compose up -d --build <service>` để build lại image.

## Troubleshooting
- `git pull` báo permission denied: kiểm tra file/dir thuộc root trong repo, chown lại bằng UID của bạn.
- Không truy cập được gateway: kiểm tra profile `gateway` và port 7443.
- STT lỗi GPU: kiểm tra NVIDIA Container Toolkit và quyền GPU.
- Dịch vụ không lên: xem log `docker compose logs -f <service>`.
