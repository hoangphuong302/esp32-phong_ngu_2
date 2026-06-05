import os

file_path = "esp32-cam_bien_dieu_hoa.yaml"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the sensors_json entry
old_json_line = '"\\"sensor.cam_bien_dh_ngu_2_dien_ap\\":{\\"state\\":" + std::string(volt) + ",\\"unit\\":\\"V\\",\\"class\\":\\"voltage\\",\\"name\\":\\"\\\\u0110i\\\\u1ec7n \\\\u00e1p LED\\"},"'
new_json_line = '"\\"sensor.cam_bien_dh_ngu_2_nhiet_do\\":{\\"state\\":" + std::string(local_t) + ",\\"unit\\":\\"\\\\u00b0C\\",\\"class\\":\\"temperature\\",\\"name\\":\\"Nhi\\\\u1ec7t \\\\u0111\\\\u1ed9 ph\\\\u00f2ng ng\\\\u1ee7 2\\"},"\n              "\\"sensor.cam_bien_dh_ngu_2_dien_ap\\":{\\"state\\":" + std::string(volt) + ",\\"unit\\":\\"V\\",\\"class\\":\\"voltage\\",\\"name\\":\\"\\\\u0110i\\\\u1ec7n \\\\u00e1p LED\\"},"'

if old_json_line in content:
    content = content.replace(old_json_line, new_json_line)
    print("Succeeded replacing JSON line!")
else:
    # Try with raw string representation
    print("Failed to find JSON line directly. Searching for substrings...")
    for line in content.splitlines():
        if "cam_bien_dh_ngu_2_dien_ap" in line and "sensors_json" not in line:
            print("Found line:", repr(line))

# Replace the history entry
# We can match it using a multi-line pattern or find the exact block and replace it
# Let's search for "uptime, t_str, h_str, v_str, cpu_str"
old_history = """          char entry[256];
          snprintf(entry, sizeof(entry),
            "{\\\"uptime\\\":%u,\\\"temp\\\":%s,\\\"humidity\\\":%s,\\\"voltage\\\":%s,\\\"cpu_temp\\\":%s},\",
            uptime, t_str, h_str, v_str, cpu_str
          );""".replace('\\\"', '"')

new_history = """          char entry[256];
          snprintf(entry, sizeof(entry),
            "{\\\"uptime\\\":%u,\\\"temp\\\":%s,\\\"humidity\\\":%s,\\\"local_temp\\\":%s,\\\"voltage\\\":%s,\\\"cpu_temp\\\":%s},\",
            uptime, t_str, h_str, local_t_str, v_str, cpu_str
          );""".replace('\\\"', '"')

# Let's also replace the variable definition in history lambda
old_history_vars = """          float temp = id(g_xiaomi_temp);
          float hum = id(g_xiaomi_humid);
          float volt = id(led_mean).state;
          float cpu = id(cpu_temp).state;
          uint32_t uptime = millis() / 1000;

          char t_str[16], h_str[16], v_str[16], cpu_str[16];
          if (std::isnan(temp)) strcpy(t_str, "null"); else snprintf(t_str, sizeof(t_str), "%.1f", temp);
          if (std::isnan(hum)) strcpy(h_str, "null"); else snprintf(h_str, sizeof(h_str), "%.1f", hum);"""

new_history_vars = """          float temp = id(g_xiaomi_temp);
          float hum = id(g_xiaomi_humid);
          float local_temp = id(cb_temp).state;
          float volt = id(led_mean).state;
          float cpu = id(cpu_temp).state;
          uint32_t uptime = millis() / 1000;

          char t_str[16], h_str[16], local_t_str[16], v_str[16], cpu_str[16];
          if (std::isnan(temp)) strcpy(t_str, "null"); else snprintf(t_str, sizeof(t_str), "%.1f", temp);
          if (std::isnan(hum)) strcpy(h_str, "null"); else snprintf(h_str, sizeof(h_str), "%.1f", hum);
          if (std::isnan(local_temp)) strcpy(local_t_str, "null"); else snprintf(local_t_str, sizeof(local_t_str), "%.2f", local_temp);"""

if old_history_vars in content:
    content = content.replace(old_history_vars, new_history_vars)
    print("Succeeded replacing history variables!")
else:
    print("Failed to find history variables pattern!")

if old_history in content:
    content = content.replace(old_history, new_history)
    print("Succeeded replacing history entry!")
else:
    print("Failed to find history entry pattern!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
