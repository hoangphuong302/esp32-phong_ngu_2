import os

file_path = "esp32-cam_bien_dieu_hoa.yaml"
if not os.path.exists(file_path):
    print("Error: file not found")
    exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Normalize line endings to LF for consistent matching
original_ending = "\r\n" if "\r\n" in content else "\n"
content = content.replace("\r\n", "\n")

# 1. Dallas Sensor replacement
find1 = """captive_portal:

# 📶 Bluetooth Tracker (Passive Mode to run cool)
esp32_ble_tracker:
  scan_parameters:
    interval: 400ms
    window: 80ms
    active: false

sensor:
  - platform: ble_rssi
    mac_address: FF:FF:DE:0D:04:AF
    name: "LED Strip RSSI"
    id: led_strip_rssi"""

replace1 = """captive_portal:

# 🌡️ Dallas 1-Wire Temperature Sensor (DS18B20) on GPIO3
dallas:
  - pin: GPIO3

# 📶 Bluetooth Tracker (Passive Mode to run cool)
esp32_ble_tracker:
  scan_parameters:
    interval: 400ms
    window: 80ms
    active: false

sensor:
  - platform: dallas
    name: "Nhiệt độ phòng ngủ 2"
    id: cb_temp
    update_interval: 10s
  - platform: ble_rssi
    mac_address: FF:FF:DE:0D:04:AF
    name: "LED Strip RSSI"
    id: led_strip_rssi"""

# 2. Push sensors lambda replacement
find2 = """            char volt[32], rssi[32], uptime_s[32], temp[32], humid[32], cpu_s[32];
            if (std::isnan(id(led_mean).state)) strcpy(volt, "null");
            else snprintf(volt, sizeof(volt), "%.3f", id(led_mean).state);

            if (std::isnan(id(cb_wifi_rssi).state)) strcpy(rssi, "null");
            else snprintf(rssi, sizeof(rssi), "%.1f", id(cb_wifi_rssi).state);

            if (std::isnan(id(cb_uptime).state)) strcpy(uptime_s, "null");
            else snprintf(uptime_s, sizeof(uptime_s), "%.0f", id(cb_uptime).state);

            if (std::isnan(id(g_xiaomi_temp))) strcpy(temp, "null");
            else snprintf(temp, sizeof(temp), "%.1f", id(g_xiaomi_temp));

            if (std::isnan(id(g_xiaomi_humid))) strcpy(humid, "null");
            else snprintf(humid, sizeof(humid), "%.1f", id(g_xiaomi_humid));

            if (std::isnan(id(cpu_temp).state)) strcpy(cpu_s, "null");
            else snprintf(cpu_s, sizeof(cpu_s), "%.1f", id(cpu_temp).state);

            std::string sensors_json = 
              "\\\"sensor.cam_bien_dh_ngu_2_dien_ap\\\":{\\\"state\\\":\\\" + std::string(volt) + \\\",\\\"unit\\\":\\\"V\\\",\\\"class\\\":\\\"voltage\\\",\\\"name\\\":\\\"\\\\u0110i\\\\u1ec7n \\\\u00e1p LED\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_wifi_rssi\\\":{\\\"state\\\":\\\" + std::string(rssi) + \\\",\\\"unit\\\":\\\"dBm\\\",\\\"class\\\":\\\"signal_strength\\\",\\\"name\\\":\\\"WiFi RSSI\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_uptime\\\":{\\\"state\\\":\\\" + std::string(uptime_s) + \\\",\\\"unit\\\":\\\"s\\\",\\\"class\\\":\\\"duration\\\",\\\"name\\\":\\\"Uptime\\\"},"
              "\\\"sensor.miaomiaoce_t2_aaaf_temperature\\\":{\\\"state\\\":\\\" + std::string(temp) + \\\",\\\"unit\\\":\\\"\\\\u00b0C\\\",\\\"class\\\":\\\"temperature\\\",\\\"name\\\":\\\"Nhi\\\\u1ec7t \\\\u0111\\\\u1ed9 Ban C\\\\u00f4ng\\\"},"
              "\\\"sensor.miaomiaoce_t2_aaaf_humidity\\\":{\\\"state\\\":\\\" + std::string(humid) + \\\",\\\"unit\\\":\\\"%%\\\",\\\"
              \\\"class\\\":\\\"humidity\\\",\\\"
              \\\"name\\\":\\\"\\\\u0110\\\\u1ed9 \\\\u1ea3m Ban C\\\\u00f4ng\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_nhiet_do_cpu\\\":{\\\"state\\\":\\\" + std::string(cpu_s) + \\\",\\\"unit\\\":\\\"\\\\u00b0C\\\",\\\"class\\\":\\\"temperature\\\",\\\"name\\\":\\\"Nhi\\\\u1ec7t \\\\u0111\\\\u1ed9 CPU\\\"};\""""

# Let's use simpler search for find2 to avoid double backslash mapping issues
find2_simple = """            char volt[32], rssi[32], uptime_s[32], temp[32], humid[32], cpu_s[32];
            if (std::isnan(id(led_mean).state)) strcpy(volt, "null");
            else snprintf(volt, sizeof(volt), "%.3f", id(led_mean).state);

            if (std::isnan(id(cb_wifi_rssi).state)) strcpy(rssi, "null");
            else snprintf(rssi, sizeof(rssi), "%.1f", id(cb_wifi_rssi).state);

            if (std::isnan(id(cb_uptime).state)) strcpy(uptime_s, "null");
            else snprintf(uptime_s, sizeof(uptime_s), "%.0f", id(cb_uptime).state);

            if (std::isnan(id(g_xiaomi_temp))) strcpy(temp, "null");
            else snprintf(temp, sizeof(temp), "%.1f", id(g_xiaomi_temp));

            if (std::isnan(id(g_xiaomi_humid))) strcpy(humid, "null");
            else snprintf(humid, sizeof(humid), "%.1f", id(g_xiaomi_humid));

            if (std::isnan(id(cpu_temp).state)) strcpy(cpu_s, "null");
            else snprintf(cpu_s, sizeof(cpu_s), "%.1f", id(cpu_temp).state);"""

replace2_simple = """            char volt[32], rssi[32], uptime_s[32], temp[32], humid[32], cpu_s[32], local_t[32];
            if (std::isnan(id(led_mean).state)) strcpy(volt, "null");
            else snprintf(volt, sizeof(volt), "%.3f", id(led_mean).state);

            if (std::isnan(id(cb_wifi_rssi).state)) strcpy(rssi, "null");
            else snprintf(rssi, sizeof(rssi), "%.1f", id(cb_wifi_rssi).state);

            if (std::isnan(id(cb_uptime).state)) strcpy(uptime_s, "null");
            else snprintf(uptime_s, sizeof(uptime_s), "%.0f", id(cb_uptime).state);

            if (std::isnan(id(g_xiaomi_temp))) strcpy(temp, "null");
            else snprintf(temp, sizeof(temp), "%.1f", id(g_xiaomi_temp));

            if (std::isnan(id(g_xiaomi_humid))) strcpy(humid, "null");
            else snprintf(humid, sizeof(humid), "%.1f", id(g_xiaomi_humid));

            if (std::isnan(id(cpu_temp).state)) strcpy(cpu_s, "null");
            else snprintf(cpu_s, sizeof(cpu_s), "%.1f", id(cpu_temp).state);

            if (std::isnan(id(cb_temp).state)) strcpy(local_t, "null");
            else snprintf(local_t, sizeof(local_t), "%.2f", id(cb_temp).state);"""

# 2b. sensors_json string replacement
find2_json = """            std::string sensors_json = 
              "\\\"sensor.cam_bien_dh_ngu_2_dien_ap\\\":{\\\"state\\\":\\\" + std::string(volt) + \\\",\\\"unit\\\":\\\"V\\\",\\\"class\\\":\\\"voltage\\\",\\\"name\\\":\\\"\\\\u0110i\\\\u1ec7n \\\\u00e1p LED\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_wifi_rssi\\\":{\\\"state\\\":\\\" + std::string(rssi) + \\\",\\\"unit\\\":\\\"dBm\\\",\\\"class\\\":\\\"signal_strength\\\",\\\"name\\\":\\\"WiFi RSSI\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_uptime\\\":{\\\"state\\\":\\\" + std::string(uptime_s) + \\\",\\\"unit\\\":\\\"s\\\",\\\"class\\\":\\\"duration\\\",\\\"name\\\":\\\"Uptime\\\"},"
              "\\\"sensor.miaomiaoce_t2_aaaf_temperature\\\":{\\\"state\\\":\\\" + std::string(temp) + \\\",\\\"unit\\\":\\\"\\\\u00b0C\\\",\\\"class\\\":\\\"temperature\\\",\\\"name\\\":\\\"Nhi\\\\u1ec7t \\\\u0111\\\\u1ed9 Ban C\\\\u00f4ng\\\"},"
              "\\\"sensor.miaomiaoce_t2_aaaf_humidity\\\":{\\\"state\\\":\\\" + std::string(humid) + \\\",\\\"unit\\\":\\\"%%\\\",\\\"
              \\\"class\\\":\\\"humidity\\\",\\\"
              \\\"name\\\":\\\"\\\\u0110\\\\u1ed9 \\\\u1ea3m Ban C\\\\u00f4ng\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_nhiet_do_cpu\\\":{\\\"state\\\":\\\" + std::string(cpu_s) + \\\",\\\"unit\\\":\\\"\\\\u00b0C\\\",\\\"class\\\":\\\"temperature\\\",\\\"name\\\":\\\"Nhi\\\\u1ec7t \\\\u0111\\\\u1ed9 CPU\\\"};\"""".replace('\\\"', '"').replace('\\\\', '\\')

replace2_json = """            std::string sensors_json = 
              "\\\"sensor.cam_bien_dh_ngu_2_nhiet_do\\\":{\\\"state\\\":\\\" + std::string(local_t) + \\\",\\\"unit\\\":\\\"\\\\u00b0C\\\",\\\"class\\\":\\\"temperature\\\",\\\"name\\\":\\\"Nhi\\\\u1ec7t \\\\u0111\\\\u1ed9 ph\\\\u00f2ng ng\\\\u1ee7 2\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_dien_ap\\\":{\\\"state\\\":\\\" + std::string(volt) + \\\",\\\"unit\\\":\\\"V\\\",\\\"class\\\":\\\"voltage\\\",\\\"name\\\":\\\"\\\\u0110i\\\\u1ec7n \\\\u00e1p LED\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_wifi_rssi\\\":{\\\"state\\\":\\\" + std::string(rssi) + \\\",\\\"unit\\\":\\\"dBm\\\",\\\"class\\\":\\\"signal_strength\\\",\\\"name\\\":\\\"WiFi RSSI\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_uptime\\\":{\\\"state\\\":\\\" + std::string(uptime_s) + \\\",\\\"unit\\\":\\\"s\\\",\\\"class\\\":\\\"duration\\\",\\\"name\\\":\\\"Uptime\\\"},"
              "\\\"sensor.miaomiaoce_t2_aaaf_temperature\\\":{\\\"state\\\":\\\" + std::string(temp) + \\\",\\\"unit\\\":\\\"\\\\u00b0C\\\",\\\"class\\\":\\\"temperature\\\",\\\"name\\\":\\\"Nhi\\\\u1ec7t \\\\u0111\\\\u1ed9 Ban C\\\\u00f4ng\\\"},"
              "\\\"sensor.miaomiaoce_t2_aaaf_humidity\\\":{\\\"state\\\":\\\" + std::string(humid) + \\\",\\\"unit\\\":\\\"%%\\\",\\\"
              \\\"class\\\":\\\"humidity\\\",\\\"
              \\\"name\\\":\\\"\\\\u0110\\\\u1ed9 \\\\u1ea3m Ban C\\\\u00f4ng\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_nhiet_do_cpu\\\":{\\\"state\\\":\\\" + std::string(cpu_s) + \\\",\\\"unit\\\":\\\"\\\\u00b0C\\\",\\\"class\\\":\\\"temperature\\\",\\\"name\\\":\\\"Nhi\\\\u1ec7t \\\\u0111\\\\u1ed9 CPU\\\"};\"""".replace('\\\"', '"').replace('\\\\', '\\')

# Let's verify sensors_json find strings directly in code
find2_json = """            std::string sensors_json = 
              "\\\"sensor.cam_bien_dh_ngu_2_dien_ap\\\":{\\\"state\\\":\\\" + std::string(volt) + \\\",\\\"unit\\\":\\\"V\\\",\\\"class\\\":\\\"voltage\\\",\\\"name\\\":\\\"\\\\u0110i\\\\u1ec7n \\\\u00e1p LED\\\"},\"""".replace('\\\"', '"').replace('\\\\', '\\').strip()

replace2_json = """            std::string sensors_json = 
              "\\\"sensor.cam_bien_dh_ngu_2_nhiet_do\\\":{\\\"state\\\":\\\" + std::string(local_t) + \\\",\\\"unit\\\":\\\"\\\\u00b0C\\\",\\\"class\\\":\\\"temperature\\\",\\\"name\\\":\\\"Nhi\\\\u1ec7t \\\\u0111\\u1ed9 ph\\\\u00f2ng ng\\\\u1ee7 2\\\"},"
              "\\\"sensor.cam_bien_dh_ngu_2_dien_ap\\\":{\\\"state\\\":\\\" + std::string(volt) + \\\",\\\"unit\\\":\\\"V\\\",\\\"class\\\":\\\"voltage\\\",\\\"name\\\":\\\"\\\\u0110i\\\\u1ec7n \\\\u00e1p LED\\\"},\"""".replace('\\\"', '"').replace('\\\\', '\\').strip()

# 3. History sampler lambda replacement
find3 = """      - lambda: |-
          float temp = id(g_xiaomi_temp);
          float hum = id(g_xiaomi_humid);
          float volt = id(led_mean).state;
          float cpu = id(cpu_temp).state;
          uint32_t uptime = millis() / 1000;

          char t_str[16], h_str[16], v_str[16], cpu_str[16];
          if (std::isnan(temp)) strcpy(t_str, "null"); else snprintf(t_str, sizeof(t_str), "%.1f", temp);
          if (std::isnan(hum)) strcpy(h_str, "null"); else snprintf(h_str, sizeof(h_str), "%.1f", hum);
          if (std::isnan(volt)) strcpy(v_str, "null"); else snprintf(v_str, sizeof(v_str), "%.3f", volt);
          if (std::isnan(cpu)) strcpy(cpu_str, "null"); else snprintf(cpu_str, sizeof(cpu_str), "%.1f", cpu);

          char entry[256];
          snprintf(entry, sizeof(entry),
            "{\\\"uptime\\\":%u,\\\"temp\\\":%s,\\\"humidity\\\":%s,\\\"voltage\\\":%s,\\\"cpu_temp\\\":%s},\",
            uptime, t_str, h_str, v_str, cpu_str
          )""".replace('\\\"', '"')

replace3 = """      - lambda: |-
          float temp = id(g_xiaomi_temp);
          float hum = id(g_xiaomi_humid);
          float local_temp = id(cb_temp).state;
          float volt = id(led_mean).state;
          float cpu = id(cpu_temp).state;
          uint32_t uptime = millis() / 1000;

          char t_str[16], h_str[16], local_t_str[16], v_str[16], cpu_str[16];
          if (std::isnan(temp)) strcpy(t_str, "null"); else snprintf(t_str, sizeof(t_str), "%.1f", temp);
          if (std::isnan(hum)) strcpy(h_str, "null"); else snprintf(h_str, sizeof(h_str), "%.1f", hum);
          if (std::isnan(local_temp)) strcpy(local_t_str, "null"); else snprintf(local_t_str, sizeof(local_t_str), "%.2f", local_temp);
          if (std::isnan(volt)) strcpy(v_str, "null"); else snprintf(v_str, sizeof(v_str), "%.3f", volt);
          if (std::isnan(cpu)) strcpy(cpu_str, "null"); else snprintf(cpu_str, sizeof(cpu_str), "%.1f", cpu);

          char entry[256];
          snprintf(entry, sizeof(entry),
            "{\\\"uptime\\\":%u,\\\"temp\\\":%s,\\\"humidity\\\":%s,\\\"local_temp\\\":%s,\\\"voltage\\\":%s,\\\"cpu_temp\\\":%s},\",
            uptime, t_str, h_str, local_t_str, v_str, cpu_str
          )""".replace('\\\"', '"')


print("Replacing dallas sensor config...")
if find1 in content:
    content = content.replace(find1, replace1)
    print("-> Succeeded 1")
else:
    print("-> Failed 1 (dallas tracker find pattern mismatch)")

print("Replacing push sensors variables...")
if find2_simple in content:
    content = content.replace(find2_simple, replace2_simple)
    print("-> Succeeded 2")
else:
    print("-> Failed 2 (push variables find pattern mismatch)")

print("Replacing sensors json key...")
if find2_json in content:
    content = content.replace(find2_json, replace2_json)
    print("-> Succeeded 2b")
else:
    print("-> Failed 2b (sensors json find pattern mismatch)")

print("Replacing history sampler...")
if find3 in content:
    content = content.replace(find3, replace3)
    print("-> Succeeded 3")
else:
    print("-> Failed 3 (history sampler find pattern mismatch)")

# Restore original line endings
if original_ending == "\r\n":
    content = content.replace("\n", "\r\n")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Finished!")
