import requests
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 6
MAX_WORKERS = 10  # puedes subir a 20 si tienes muchas URLs

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def is_working(url):
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True, allow_redirects=True)
        return r.status_code in [200, 301, 302]
    except:
        return False

def parse_m3u(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entries = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF") and i + 1 < len(lines):
            extinf = lines[i]
            url = lines[i + 1].strip()
            entries.append((extinf, url))
            i += 2
        else:
            i += 1

    return entries

def main():
    files = glob.glob("pais/*.m3u8")

    all_entries = []
    for file in files:
        print(f"\n📂 Procesando: {file}")
        entries = parse_m3u(file)
        all_entries.extend(entries)

    print(f"\n🔎 Total streams a verificar: {len(all_entries)}\n")

    working = []
    dead = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_entry = {
            executor.submit(is_working, url): (extinf, url)
            for extinf, url in all_entries
        }

        for future in as_completed(future_to_entry):
            extinf, url = future_to_entry[future]
            try:
                if future.result():
                    print(f"✅ OK: {url}")
                    working.append((extinf, url))
                else:
                    print(f"❌ CAÍDO: {url}")
                    dead.append(url)
            except:
                print(f"⚠️ ERROR: {url}")
                dead.append(url)

    # Crear master.m3u8 en raíz
    with open("master.m3u8", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for extinf, url in working:
            f.write(extinf)
            f.write(url + "\n")

    # Guardar caídos
    with open("dead.txt", "w", encoding="utf-8") as f:
        for url in dead:
            f.write(url + "\n")

    print("\n==============================")
    print(f"✔ Activos: {len(working)}")
    print(f"✖ Caídos: {len(dead)}")
    print("📄 Generado: master.m3u8")
    print("📄 Generado: dead.txt")
    print("==============================\n")

if __name__ == "__main__":
    main()
