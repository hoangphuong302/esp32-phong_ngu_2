# 🌡️ esp32-phong_ngu_2 — Cảm Biến Điều Hòa Phòng Ngủ 1

> **ESPHome firmware cho cảm biến nhiệt độ / độ ẩm tích hợp điều khiển điều hòa từ xa, thuộc hệ sinh thái Nhà Sam Aura Smart Home.**

[![ESPHome](https://img.shields.io/badge/Platform-ESPHome-green)](https://esphome.io)
[![Board](https://img.shields.io/badge/Board-ESP32--C3-blue)](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/)
[![Architecture](https://img.shields.io/badge/Architecture-HTTP_Push-orange)](#kiến-trúc-mạng)

---

## 📋 Tổng quan

Thiết bị đặt cố định trong phòng ngủ tại nhà Sam. Chip ESP32-C3 kết nối WiFi và **hoàn toàn tự vận hành** — không cần máy tính trung gian, không cần Home Assistant phải cùng mạng. Cứ mỗi 60 giây, thiết bị tự đo và đẩy dữ liệu lên server công khai `nhasam.id.vn`, từ đó cập nhật vào Home Assistant.

### Tính năng chính

- Đo nhiệt độ phòng (BMP280) với độ chính xác ±0.5°C
- Đo độ ẩm tương đối (AHT20) với độ chính xác ±2%
- Đo áp suất khí quyển (BMP280)
- **Phát hiện trạng thái điều hòa** bằng cách đo điện áp ngược tại đèn LED báo hiệu trên bảng mạch điều hòa (GPIO1/ADC)
- Điều khiển điều hòa qua tín hiệu hồng ngoại IR từ lệnh của HA
- Tự gửi dữ liệu mỗi 60 giây qua HTTPS, không phụ thuộc bất kỳ máy nào
- Khôi phục tự động khi mất WiFi qua fallback AP

---

## ⚡ Kiến trúc mạng

Thiết bị và Home Assistant **không cùng mạng LAN**. Vì vậy kiến trúc dùng là **HTTP Push** — thiết bị chủ động gửi ra ngoài, không phải HA kéo vào.

```
ESP32-C3 (Phòng ngủ - WiFi 3324)
    │
    │  POST HTTPS mỗi 60s
    ▼
https://nhasam.id.vn/aura-api/esp-push
    │
    │  Cập nhật entity states
    ▼
Home Assistant (nơi khác)
```

> ❌ **Không dùng ESPHome native API** — native API yêu cầu HA phải reach được IP nội bộ của ESP32, không hoạt động khi khác mạng.

---

## 🔧 Phần cứng

| Linh kiện | Vai trò | Kết nối |
|---|---|---|
| **ESP32-C3 DevKitM-1** | Vi điều khiển chính | — |
| **BMP280** | Nhiệt độ + Áp suất | I2C SDA=GPIO2, SCL=GPIO3, địa chỉ 0x77 |
| **AHT20** | Độ ẩm | I2C SDA=GPIO2, SCL=GPIO3, địa chỉ 0x38 |
| **IR Transmitter** | Phát tín hiệu điều hòa | GPIO4, 38kHz carrier |
| **LED x2** | Báo hiệu phát IR | GPIO8 (inverted), GPIO10 (inverted) |
| **Dây nối đến LED điều hòa** | Đọc điện áp ngược tại LED báo hiệu điều hòa đang chạy | GPIO1 (ADC, attenuation 11dB) |

### Sơ đồ kết nối I2C

BMP280 và AHT20 dùng chung một bus I2C (GPIO2/GPIO3) nhờ địa chỉ khác nhau:
- BMP280 → `0x77`
- AHT20 → `0x38`

---

## 🔄 Cơ chế hoạt động

### 1. Khởi động

Khi cắm điện, ESP32 kết nối vào WiFi `3324 2.4ghz` (ưu tiên cao nhất) hoặc `3324_2.4ghz`. Không scan toàn bộ kênh nhờ `fast_connect: true` — giúp boot nhanh hơn và tiết kiệm điện.

### 2. Đọc cảm biến

Cứ mỗi **60 giây**, BMP280 và AHT20 đọc dữ liệu qua I2C. Bộ lọc delta được áp dụng — giá trị chỉ cập nhật nội bộ khi thay đổi đủ lớn:

| Cảm biến | Ngưỡng delta |
|---|---|
| Nhiệt độ | > 0.2°C |
| Độ ẩm | > 0.5% |
| Áp suất | > 0.5 hPa |

**Điện áp LED báo hiệu điều hòa (GPIO1/ADC)** đọc mỗi **5 phút**. ESP32-C3 nối vào mạch LED báo hiệu trên bo mạch điều hòa. Bo mạch dùng kiểu **active-low** — khi LED sáng (điều hòa chạy), bo mạch kéo mạch LED về GND, khiến GPIO1 đọc thấp hoặc **nhảy liên tục 0–1.4V** do LED được PWM/quét multiplexed bởi chip điều hòa. Khi LED tắt (điều hòa dừng), chân thả nổi và GPIO1 đọc ổn định **≈1.4V**.

> ⚠️ **Logic ngược:** Điện áp CAO ổn định = tắt, điện áp THẤP hoặc NHẢY = đang chạy. Đặc điểm nhảy 0–1.4V khi chạy thực ra là dấu hiệu nhận dạng rất tin cậy — bo mạch điều hòa đang PWM cái LED.

### 3. Gửi dữ liệu lên HA

Cứ mỗi **60 giây**, script `push_sensors_to_ha` chạy:
1. Đóng gói nhiệt độ, độ ẩm, áp suất thành JSON
2. POST lên `https://nhasam.id.vn/aura-api/esp-push`
3. Server nhận → gọi HA REST API → cập nhật entity states

Payload JSON mẫu:
```json
{
  "device_key": "cam-bien-pn2",
  "sensors": {
    "sensor.cam_bien_dieu_hoa_nhiet_do": {
      "state": 28.50,
      "unit": "°C",
      "class": "temperature",
      "name": "Nhiệt độ phòng ngủ 2"
    },
    "sensor.cam_bien_dieu_hoa_do_am": {
      "state": 65.0,
      "unit": "%",
      "class": "humidity",
      "name": "Độ ẩm phòng ngủ 2"
    }
  }
}
```

### 4. Điều khiển điều hòa qua IR (Chuẩn phát xung hồng ngoại)

Khi người dùng bấm nút trên HA (hoặc automation chạy), HA gọi service `esphome.cam_bien_dieu_hoa_transmit_raw` kèm:
- `code`: mảng số nguyên biểu diễn tín hiệu IR chuẩn (raw).

#### ⚠️ QUY TẮC PHÁT XUNG HỒNG NGOẠI CHUẨN TRÊN ESPHOME:
Để ESPHome truyền thành công lệnh hồng ngoại tới mắt nhận của điều hòa, cấu hình và dữ liệu phát xung phải tuân theo các quy tắc nghiêm ngặt sau:

1. **Khởi tạo Sóng Mang (Carrier Frequency)**:
   - Trong file cấu hình YAML, component `remote_transmitter` bắt buộc phải có thuộc tính `carrier_frequency: 38kHz` để ESP32 khởi tạo bộ tạo sóng mang phần cứng (hardware carrier generator) lúc boot. 
   - Nếu thiếu cấu hình này trong YAML, ESPHome sẽ mặc định tần số phát là `0Hz` (baseband raw pulses không có sóng mang) khiến mắt nhận hồng ngoại trên điều hòa không thể nhận diện được lệnh.

2. **Quy tắc về dấu của Mảng Xung (Signed alternating pulses)**:
   - ESPHome nhận dữ liệu phát hồng ngoại dưới dạng mảng số nguyên có dấu (`std::vector<int32_t>`).
   - Trong đó: **Số dương đại diện cho Mark** (thời gian phát sóng mang 38kHz) và **Số âm đại diện cho Space** (thời gian nghỉ/tắt sóng mang) tính bằng micro giây.
   - Khi giải mã các chuỗi Broadlink Base64 (thường chứa mảng số nguyên toàn bộ là số dương), **bắt buộc phải đổi dấu các phần tử ở vị trí lẻ (chỉ số 1, 3, 5...) thành dấu âm** (Ví dụ: `[9000, -4500, 560, -560, 560, -1680]`). 
   - Nếu gửi mảng toàn bộ số dương cho ESPHome, nó sẽ phát một dải sóng mang liên tục không có khoảng nghỉ, dẫn đến việc điều hòa bỏ qua lệnh.

3. **Cơ chế Mã hóa Giao thức Điều hòa Midea (Midea AC IR Protocol)**:
   Mã lệnh hồng ngoại của điều hòa Midea sử dụng giao thức truyền **48-bit (6 bytes)** với cơ chế kiểm tra lỗi bitwise đảo ngược và lặp lại hai khung truyền (double frame).
   
   - **Cấu trúc Khung Dữ liệu (6 Bytes)**:
     - **Byte 0**: Mã định danh hãng (Custom Code) cố định là `4D` (nhận diện LSB-first).
     - **Byte 1**: Mã kiểm tra định danh hãng cố định là `B2` (đảo ngược bitwise của `4D` để chống nhiễu).
     - **Byte 2**: Tốc độ quạt (Fan speed) & Chế độ hoạt động (Mode).
       - **Auto speed**: `FD` (nibble quạt `1011` LSB-first)
       - **Low speed**: `F9` (nibble quạt `1001` LSB-first)
       - **Mid speed**: `FA` (nibble quạt `0101` LSB-first)
       - **High speed**: `FC` (nibble quạt `0011` LSB-first)
     - **Byte 3**: Mã kiểm tra lỗi tốc độ quạt & chế độ (đảo ngược bitwise của Byte 2).
     - **Byte 4**: Nhiệt độ cài đặt & cấu hình phụ (Ví dụ: `03` tương ứng với 25°C chế độ Cool).
     - **Byte 5**: Mã kiểm tra lỗi nhiệt độ (đảo ngược bitwise của Byte 4).
   
   - **Quy tắc Mã hóa Độ rộng Xung (Pulse Width Modulation)**:
     - **Tần số sóng mang (Carrier)**: 38kHz.
     - **Khung truyền**: Phát 2 khung giống hệt nhau (Frame 1 và Frame 2) ngăn cách bởi khoảng nghỉ trung gian `inter_frame_space` khoảng `-5220 us`.
     - **Xung Header**: Xung dương `4380 us` (Mark) theo sau bởi xung âm `-4400 us` (Space).
     - **Logic 0**: Xung dương `540 us` theo sau bởi xung âm `-560 us`.
     - **Logic 1**: Xung dương `540 us` theo sau bởi xung âm `-1650 us`.
     - **Xung kết thúc (Stop Bit)**: Xung dương `540 us` và kết thúc toàn chuỗi bằng xung âm `-65535 us`.
   
   - **⚠️ Lưu ý về lỗi quạt gió High khi bật điều hòa**:
     Trong các bộ cấu hình SmartIR (như file `1383.json` cũ), tốc độ `low` thường bị nhầm lẫn với tốc độ `auto` (Byte 2 = `FD` thay vị `F9`). Khi phòng đang nóng và điều hòa nhận lệnh quạt `auto`, nó sẽ tự động chạy ở tốc độ gió tối đa (High) để làm mát nhanh, gây hiểu lầm là điều hòa chạy sai tốc độ. Việc sửa Byte 2 thành `F9` giúp điều hòa chạy đúng tốc độ gió thấp nhẹ nhàng ngay khi bật.

ESP32 nhận lệnh, phát tín hiệu IR qua GPIO4, đồng thời **nháy 2 LED trong 80ms** để báo hiệu đã xử lý.


### 5. Chẩn đoán (diagnostics)

Cứ mỗi 5 phút, thiết bị gửi thêm:
- **Uptime** — thời gian chạy liên tục
- **WiFi RSSI** — cường độ tín hiệu WiFi
- **IP Address** — địa chỉ IP hiện tại
- **Connected SSID** — tên mạng đang kết nối

---

## ⚙️ Tối ưu điện và nhiệt

| Cài đặt | Giá trị | Lý do |
|---|---|---|
| `power_save_mode` | `LIGHT` | Ngủ nhẹ giữa beacon (~100ms cycle), ổn định, không drop packet |
| `output_power` | `13dB` | Đủ phủ trong nhà, không làm nóng module RF |
| `logger baud_rate` | `0` | Tắt UART, giảm tải CPU |
| `logger level` | `WARN` | Chỉ log lỗi, không log thừa |
| `i2c scan` | `false` | Đã biết địa chỉ cố định, bỏ scan mỗi boot |
| `update_interval` | `60s` (sensor), `300s` (diagnostics) | Nhiệt độ thay đổi chậm, không cần poll nhanh |

---

## 🛟 Khôi phục khi mất WiFi

Khi không kết nối được WiFi, ESP32 tự bật **Fallback AP**:

- **SSID:** `ESP-CamBien-PN2`
- **Password:** `cambiendh1`

Kết nối vào AP này rồi truy cập `192.168.4.1` trên trình duyệt để cấu hình lại WiFi mà không cần cắm cáp USB.

---

## 📁 Cấu trúc file

```
esp32-phong_ngu_2/
├── esp32-cam_bien_dieu_hoa.yaml   → Firmware chính (HTTP Push, khác mạng)
├── esp32-phong_ngu_2.yaml          → Firmware cũ (native API, cùng LAN)
└── README.md
```

> `esp32-cam_bien_dieu_hoa.yaml` là file firmware đang dùng cho production.
> `esp32-phong_ngu_2.yaml` là phiên bản cũ dùng native API — chỉ dùng khi thiết bị và HA cùng mạng LAN.

---

## 🚀 Hướng dẫn clone và chạy

### Bước 1 — Cài đặt ESPHome

```bash
pip install esphome
```

### Bước 2 — Clone repo

```bash
git clone https://github.com/hoangphuong302/esp32-phong_ngu_2.git
cd esp32-phong_ngu_2
```

### Bước 3 — Chỉnh sửa cấu hình

Mở `esp32-cam_bien_dieu_hoa.yaml` và thay các giá trị sau:

| Mục cần thay | Vị trí trong file | Giá trị mẫu |
|---|---|---|
| Tên WiFi | `wifi.networks[].ssid` | `"Ten-WiFi-Cua-Ban"` |
| Mật khẩu WiFi | `wifi.networks[].password` | `"MatKhauWiFi"` |
| URL server nhận data | `http_request.post.url` | `"https://your-server.com/api/esp-push"` |
| Tên thiết bị | `esphome.name` | `"cam-bien-phong-ngu"` |

### Bước 4 — Flash lần đầu qua USB

```bash
esphome run esp32-cam_bien_dieu_hoa.yaml
```

Chọn cổng COM khi được hỏi.

### Bước 5 — Flash OTA từ lần sau

Nếu thiết bị và máy tính cùng mạng:
```bash
esphome run esp32-cam_bien_dieu_hoa.yaml --device [IP-cua-thiet-bi]
```

---

## 📡 Entities trong Home Assistant

Sau khi thiết bị push thành công, các entity sau sẽ xuất hiện trong HA:

| Entity ID | Loại | Đơn vị |
|---|---|---|
| `sensor.cam_bien_dieu_hoa_nhiet_do` | Nhiệt độ | °C |
| `sensor.cam_bien_dieu_hoa_do_am` | Độ ẩm | % |
| `sensor.cam_bien_dieu_hoa_ap_suat` | Áp suất | hPa |
| `sensor.cam_bien_dieu_hoa_dien_ap` | Điện áp tại LED báo hiệu điều hòa (GPIO1 ADC) | V |
| `sensor.cam_bien_dieu_hoa_uptime` | Thời gian hoạt động | s |
| `sensor.cam_bien_dieu_hoa_wifi_rssi` | Cường độ WiFi | dBm |

---

## 🔄 Quy trình cập nhật firmware

```bash
# Sửa file YAML
# Commit
git add -A
git commit -m "v1.x.x: Mô tả thay đổi"
git push origin main

# Flash OTA nếu cùng mạng
esphome run esp32-cam_bien_dieu_hoa.yaml --device [IP]
```

### Quy ước version: `MAJOR.MINOR.PATCH`
- **PATCH**: Điều chỉnh nhỏ (interval, threshold, log level)
- **MINOR**: Thêm sensor, thêm entity
- **MAJOR**: Đổi board, đổi kiến trúc

---

*Dự án này là một phần của hệ sinh thái **Nhà Sam Aura** — Smart Home tại Hà Nội.*
*README cập nhật lần cuối: 2026-06-01*
