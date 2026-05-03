import requests
import time

TIMEOUT = 6

def is_working(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, stream=True)
        return r.status_code in [200, 301, 302]
    except:
        return False

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    result = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF"):
            extinf = lines[i]
            url = lines[i+1].strip()

            print(f"Checking: {url}")

            if is_working(url):
                result.append(extinf)
                result.append(url + "\n")
            else:
                print(f"❌ Caído: {url}")

            i += 2
        else:
            if i == 0:
                result.append("#EXTM3U\n")
            i += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(result)

# Ejecutar sobre todos los archivos
import glob

with open("master.m3u8", "w", encoding="utf-8") as master:
    master.write("#EXTM3U\n")

for file in glob.glob("pais/*.m3u8"):
    if file == "master.m3u8":
        continue

    temp_output = f"clean_{file}"
    process_file(file, temp_output)

    with open(temp_output, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]  # quitar #EXTM3U duplicado

    with open("master.m3u8", "a", encoding="utf-8") as master:
        master.writelines(lines)
