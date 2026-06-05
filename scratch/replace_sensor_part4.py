file_path = "esp32-cam_bien_dieu_hoa.yaml"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace dallas: pin: GPIO3
find_dallas_hub = """# 🌡️ Dallas 1-Wire Temperature Sensor (DS18B20) on GPIO3
dallas:
  - pin: GPIO3"""

replace_dallas_hub = """# 🌡️ Dallas 1-Wire Temperature Sensor (DS18B20) on GPIO3
one_wire:
  - platform: gpio
    pin: GPIO3
    id: dallas_hub"""

if find_dallas_hub in content:
    content = content.replace(find_dallas_hub, replace_dallas_hub)
    print("Succeeded replacing dallas hub!")
else:
    print("Failed to find dallas hub!")

# Replace platform: dallas to platform: dallas_temp and link to one_wire_id
find_dallas_sensor = """  - platform: dallas
    name: "Nhiệt độ phòng ngủ 2"
    id: cb_temp
    update_interval: 10s"""

replace_dallas_sensor = """  - platform: dallas_temp
    one_wire_id: dallas_hub
    name: "Nhiệt độ phòng ngủ 2"
    id: cb_temp
    update_interval: 10s"""

if find_dallas_sensor in content:
    content = content.replace(find_dallas_sensor, replace_dallas_sensor)
    print("Succeeded replacing dallas sensor!")
else:
    print("Failed to find dallas sensor!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
