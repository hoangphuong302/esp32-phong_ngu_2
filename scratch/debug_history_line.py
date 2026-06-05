file_path = "esp32-cam_bien_dieu_hoa.yaml"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines):
    if "snprintf(entry" in line:
        print("Line", idx+1, ":", repr(line))
        print("Line", idx+2, ":", repr(lines[idx+1]))
        print("Line", idx+3, ":", repr(lines[idx+2]))
