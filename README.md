# 🛌 esp32-phong_ngu_2 — Cảm Biến Điều Hòa Phòng Ngủ 2

> **ESPHome firmware cho cảm biến nhiệt độ / độ ẩm tích hợp điều khiển điều hòa từ xa và điều khiển LED chuột qua BLE, thuộc hệ sinh thái Nhà Sam Aura Smart Home.**

[![ESPHome](https://img.shields.io/badge/Platform-ESPHome-green)](https://esphome.io)
[![Board](https://img.shields.io/badge/Board-ESP32--C3-blue)](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/)
[![Architecture](https://img.shields.io/badge/Architecture-HTTP_Push-orange)](#kiến-trúc-mạng)

---

## 📋 Tổng quan

Thiết bị đặt cố định tại **Phòng Ngủ 2** tại nhà Sam. Chip ESP32-C3 kết nối WiFi và **hoàn toàn tự vận hành** — không cần máy tính trung gian, không cần Home Assistant phải cùng mạng. Cứ mỗi 60 giây, thiết bị tự đo và đẩy dữ liệu lên server công khai `nhasam.id.vn`, từ đó cập nhật vào Home Assistant.

### Tính năng chính

- Đo nhiệt độ phòng phòng ngủ 2 (nhiệt độ đầu dò DS18B20 1-Wire)
- **Phát hiện chính xác trạng thái điều hòa** bằng cách đo điện áp trung bình (Mean Voltage) tại đèn LED báo hiệu trên bảng mạch điều hòa (GPIO1/ADC)
- Điều khiển điều hòa qua tín hiệu hồng ngoại IR từ lệnh của HA
- **Điều khiển LED RGB Chuột qua BLE** (Bluetooth Low Energy) tích hợp cơ chế chung sống phần mềm (BLE/IR Coexistence)
- **Tự động điều chỉnh tần số quét** thích ứng (Adaptive Frequency): 5s khi có lệnh điều khiển IR, 60s bình thường.
- Tự gửi dữ liệu qua HTTPS, không phụ thuộc bất kỳ máy nào cùng mạng LAN
- Khôi phục tự động khi mất WiFi qua fallback AP
- **Đọc dữ liệu cảm biến nhiệt ẩm Xiaomi (Miaomiaoce T2)** qua BLE (sniff passive quảng cáo BLE có mã hóa bindkey), lọc tần suất cập nhật chậm 2 phút/lần và đẩy lên Home Assistant thành cảm biến ban công.

---

## ⚡ Kiến trúc mạng

Thiết bị và Home Assistant **không cùng mạng LAN**. Vì vậy kiến trúc dùng là **HTTP Push** — thiết bị chủ động gửi ra ngoài, không phải HA kéo vào.

```
ESP32-C3 (Phòng Ngủ 2 - WiFi 3324)
    │
    │  POST HTTPS (60s hoặc 5s khi có lệnh IR)
    ▼
https://nhasam.id.vn/aura-api/esp-push
    │
    │  Cập nhật thực thể trên Home Assistant
    ▼
Home Assistant (nơi khác)
```

---

## 🔧 Phần cứng & Sơ đồ nối chân

| Linh kiện | Vai trò | Kết nối |
|---|---|---|
| **ESP32-C3 DevKitM-1** | Vi điều khiển chính | — |
| **DS18B20** | Cảm biến nhiệt độ đầu dò | GPIO2 (One-Wire bus) |
| **IR Transmitter** | Phát tín hiệu điều hòa | GPIO4, 38kHz carrier |
| **LED x2** | Báo hiệu trạng thái phát IR | GPIO8 (inverted), GPIO10 (inverted) |
| **Dây nối đến LED điều hòa** | Đọc điện áp ngược tại LED báo hiệu điều hòa đang chạy | GPIO1 (ADC, attenuation 11dB) |

---

## 🔄 Các Cơ chế Hoạt động Cốt lõi

### 1. Cơ chế phát hiện trạng thái điều hòa Bật/Tắt (GPIO1)
Mạch LED báo trạng thái của điều hòa dùng kiểu kích hoạt mức thấp (**active-low**):
* **TẮT**: Đèn LED tắt $\rightarrow$ Chân GPIO1 thả nổi và được kéo lên cao bởi trở pull-up nội bộ $\rightarrow$ Điện áp ổn định cao **> 1.0V** (Khoảng 1.14V đến 1.40V tùy bo mạch).
* **BẬT**: Đèn LED sáng $\rightarrow$ Chip điều khiển trên bo mạch điều hòa kéo cathode của LED về GND $\rightarrow$ Điện áp chân GPIO1 giảm xuống thấp **< 0.8V** (Khoảng 0.0V đến 0.4V).
* **Logic nhận diện trong Firmware**:
  * **Xác nhận BẬT (ON)**: Khi điện áp trung bình `mean < 0.8f` liên tục trong **2 chu kỳ quét** (tương đương 10 giây).
  * **Xác nhận TẮT (OFF)**: Khi điện áp trung bình `mean > 1.0f` liên tục trong **3 chu kỳ quét** (tương đương 15 giây).
  * Việc sử dụng điện áp trung bình (`mean`) giúp nhận diện cực kỳ ổn định, chính xác 100%, khắc phục hoàn toàn hiện tượng kẹt trạng thái của thuật toán cũ khi LED sáng ổn định hoặc xung PWM có tần số cao làm triệt tiêu độ lệch chuẩn.

### 2. Cơ chế điều chỉnh tần số quét thích ứng (Adaptive Frequency)
Để cân bằng giữa việc tiết kiệm năng lượng, bảo vệ phần cứng và phản hồi tức thời lên giao diện:
* **Chế độ bình thường (Normal Mode)**: Dữ liệu cảm biến được gửi lên server mỗi **60 giây**.
* **Chế độ nhanh (Fast Mode)**: Khi nhận được lệnh hồng ngoại IR từ giao diện Web nhà Sam, cờ `g_fast_sensor_push` sẽ được bật trong vòng **2 phút** (120.000 ms). Tần suất gửi dữ liệu cảm biến được nâng lên mức **5 giây/lần** để lập tức phản hồi trạng thái nhiệt độ/độ ẩm/áp suất thay đổi lên giao diện. Sau 2 phút, thiết bị tự động quay lại chế độ 60 giây bình thường.

### 3. Cơ chế lưu giữ trạng thái AC gần nhất (Last Settings Retention)
* Khi người dùng nhấn nút đặt nhiệt độ hoặc tốc độ gió trên Web nhà Sam, Proxy Server (`aura_tailnet_proxy.mjs`) sẽ lưu các giá trị này vào bộ nhớ `lastAcSettings` theo từng phòng.
* Khi ESP32 phát hiện điều hòa bật lên qua cảm biến điện áp GPIO1, nó sẽ đẩy trạng thái `ac_state: "on"`. Proxy sẽ nhận bản tin này, lấy cấu hình đã lưu trong `lastAcSettings` để nạp ngược lại thực thể điều hòa trên Home Assistant, giúp hiển thị chính xác thông số cài đặt trước đó của người dùng.

### 4. Cơ chế điều khiển LED Chuột qua BLE & Software Coexistence
* ESP32 được cấu hình như một **BLE Client** để kết nối và điều khiển dải LED RGB của Chuột qua Bluetooth Low Energy (sử dụng service UUID `FFE5` và characteristic UUID `FFE9`).
* **⚠️ Vấn đề xung đột phần cứng**: Bộ thu phát Bluetooth BLE hoạt động trên băng tần 2.4GHz gây ra các ngắt (Interrupts) liên tục. Các ngắt BLE này có thể làm gián đoạn bộ đệm RMT (Remote Control) phần cứng của ESP32 đang phát xung hồng ngoại IR điều hòa ở chân GPIO4, gây méo xung IR khiến điều hòa không nhận lệnh.
* **Cơ chế chung sống phần mềm (Software Coexistence)**:
  Để bảo vệ toàn vẹn khung truyền IR, trước khi phát tín hiệu hồng ngoại, ESP32 sẽ:
  1. Kiểm tra trạng thái kết nối BLE, nếu đang kết nối thì chủ động ngắt kết nối BLE Client.
  2. Tạm dừng quét BLE (`id(ble_tracker)->stop_scan();`).
  3. Chờ `50ms` để các tác vụ BLE giải phóng CPU hoàn toàn.
  4. Thực hiện phát tín hiệu IR điều hòa qua mắt phát hồng ngoại (xung 38kHz).
  5. Chờ `200ms` đảm bảo sóng IR đã truyền xong.
  6. Khởi động lại quét BLE (`id(ble_tracker)->start_scan();`) và tự động kết nối lại BLE Client nếu có.

### 5. Điều khiển điều hòa qua IR (Chuẩn phát xung hồng ngoại)
Khi người dùng điều khiển từ giao diện, Home Assistant hoặc Proxy sẽ gọi dịch vụ phát xung hồng ngoại dưới dạng mảng số nguyên có dấu (`std::vector<int32_t>`):
- **Số dương**: Thời gian phát sóng mang 38kHz (Mark).
- **Số âm**: Thời gian nghỉ/tắt sóng mang (Space).
- **Giao thức Midea AC**: Sử dụng khung truyền 48-bit (6 bytes), gửi hai khung truyền giống hệt nhau ngăn cách bởi khoảng nghỉ `-5220 us`. Các xung bắt đầu (Header), Logic 0, Logic 1, Stop bit được cấu hình chính xác theo thông số chuẩn của hãng.


### 6. Cơ chế đọc cảm biến nhiệt ẩm Xiaomi qua BLE
* Thiết bị Bedroom 2 nằm gần ban công, nơi đặt cảm biến nhiệt ẩm Xiaomi (Miaomiaoce T2, MAC: `A4:C1:38:50:AA:AF`).
* ESP32 sử dụng driver `xiaomi_lywsd03mmc` tích hợp sẵn trong ESPHome để nhận các bản tin quảng cáo Bluetooth (MiBeacon) có mã hóa.
* Bản tin được giải mã trực tiếp trên ESP32 bằng Bindkey: `e0b40d6a649749b3116cd9326f00a2b5`.
* **Lọc tần số chậm**: Để tiết kiệm băng thông và tài nguyên hệ thống, dữ liệu từ cảm biến Xiaomi được áp dụng bộ lọc `throttle: 120s` (chỉ cập nhật tối đa 2 phút một lần). Dữ liệu này sau đó được đẩy chung vào bản tin HTTP Post định kỳ lên Home Assistant.

---

## ⚙️ Tối ưu điện và nhiệt

| Cài đặt | Giá trị | Lý do |
|---|---|---|
| `power_save_mode` | `LIGHT` | Ngủ nhẹ giữa các chu kỳ phát wifi, giảm nhiệt độ chip và độ nhiễu điện áp |
| `output_power` | `13dB` | Giới hạn công suất phát RF để chip chạy mát, ổn định điện áp cho ADC |
| `logger level` | `WARN` / `INFO` | Tối ưu tài nguyên CPU, chỉ log thông tin cần thiết |
| `update_interval` | Adaptive | Tránh lãng phí băng thông và giảm tải xử lý cho server |

---

## 🛟 Khôi phục khi mất WiFi

Khi không kết nối được WiFi, ESP32 tự bật **Fallback AP** để cấu hình lại:
* SSID: `ESP-CamBien-PN2`, Pass: `cambiendh2`
Kết nối vào mạng này, mở trình duyệt truy cập địa chỉ `192.168.4.1` để nạp cấu hình WiFi mới.

---

## 📁 Cấu trúc file

```
esp32-phong_ngu_2/
├── esp32-cam_bien_dieu_hoa.yaml   → Firmware chính (HTTP Push, khác mạng)
└── README.md
```

---

## 🚀 Hướng dẫn cài đặt và nạp firmware

### Bước 1 — Clone repo
```bash
git clone https://github.com/hoangphuong302/esp32-phong_ngu_2.git
cd esp32-phong_ngu_2
```

### Bước 2 — Chỉnh sửa cấu hình
Mở `esp32-cam_bien_dieu_hoa.yaml` và cấu hình các thông số WiFi:
```yaml
wifi:
  networks:
    - ssid: "Tên WiFi của bạn"
      password: "Mật khẩu WiFi"
```

### Bước 3 — Compile & Flash
```bash
# Nạp qua cáp USB lần đầu
esphome run esp32-cam_bien_dieu_hoa.yaml

# Nạp OTA từ các lần sau (khi cùng mạng LAN)
esphome run esp32-cam_bien_dieu_hoa.yaml --device [IP_CỦA_THIẾT_BỊ]
```

---

## ⚠️ NGUYÊN TẮC LÀM VIỆC NHIỀU MÁY (GIT WORKFLOW CƠ BẢN)

Để tránh xung đột code khi làm việc trên nhiều PC khác nhau:

1. **TRƯỚC KHI LÀM:** Luôn chạy lệnh kéo code mới nhất về:
   ```bash
   git pull
   ```
2. **SAU KHI LÀM XONG:** Đẩy code lên GitHub ngay lập tức:
   ```bash
   git add .
   git commit -m "Mô tả thay đổi"
   git push
   ```
3. **XỬ LÝ XUNG ĐỘT (CONFLICT):** Tuyệt đối không chạy lệnh `git reset --hard` hoặc xóa bỏ thay đổi của PC kia để đè code. Hãy giữ nguyên trạng thái và nhờ hỗ trợ gộp code (Merge) an toàn.

---
*Dự án này thuộc hệ sinh thái **Nhà Sam Aura** — Smart Home tại Hà Nội.*
*README cập nhật lần cuối: 2026-06-05*
