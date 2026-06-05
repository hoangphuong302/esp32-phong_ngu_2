file_path = "esp32-cam_bien_dieu_hoa.yaml"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

find_str = '            "{\\"uptime\\":%u,\\"temp\\":%s,\\"humidity\\":%s,\\"voltage\\":%s,\\"cpu_temp\\":%s},",'
replace_str = '            "{\\"uptime\\":%u,\\"temp\\":%s,\\"humidity\\":%s,\\"local_temp\\":%s,\\"voltage\\":%s,\\"cpu_temp\\":%s},",'

if find_str in content:
    content = content.replace(find_str, replace_str)
    print("Succeeded replacing history snprintf line!")
else:
    print("Failed to find history snprintf line!")

# Also replace variables usage in next line
find_vars = '            uptime, t_str, h_str, v_str, cpu_str'
replace_vars = '            uptime, t_str, h_str, local_t_str, v_str, cpu_str'

if find_vars in content:
    content = content.replace(find_vars, replace_vars)
    print("Succeeded replacing history vars line!")
else:
    print("Failed to find history vars line!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
