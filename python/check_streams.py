import requests
import glob
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 6
MAX_WORKERS = 10

headers = {
    "User-Agent": "Mozilla/5.0"
}

def is_working(url):
    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=True
        )
        return r.status_code in [200, 301, 302]
    except:
        return False


def get_country_from_file(file_path):
    """
    Busca línea tipo:
    #PAIS_Peru
    """

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) >= 2:
            second = lines[1].strip()

            if second.startswith("#PAIS_"):
                return second.replace("#PAIS_", "").strip()

    except:
        pass

    return "Desconocido"


def ensure_group_title(extinf, country):
    """
    Agrega group-title si no existe.
    """

    if 'group-title=' in extinf:
        return extinf

    # Insertar después de #EXTINF:-1
    return extinf.replace(
        "#EXTINF:-1",
        f'#EXTINF:-1 group-title="{country}"'
    )


def parse_m3u(file_path):
    country = get_country_from_file(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entries = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF") and i + 1 < len(lines):

            extinf = lines[i].rstrip("\n")
            url = lines[i + 1].strip()

            # Agregar group-title si falta
            extinf = ensure_group_title(extinf, country)

            # asegurar salto de línea
            extinf += "\n"

            entries.append((extinf, url))

            i += 2
        else:
            i += 1

    return entries


def main():

    files = []
    files.extend(glob.glob("pais/*.m3u8"))
    files.extend(glob.glob("pais/*.m3u"))

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

    # Crear master
    with open("master.m3u8", "w", encoding="utf-8") as f:

        f.write("#EXTM3U\n\n")

        for extinf, url in working:

            f.write(extinf)
            f.write(url + "\n")

    # Guardar caídos
    with open("misc/dead.txt", "w", encoding="utf-8") as f:

        for url in dead:
            f.write(url + "\n")

    print("\n==============================")
    print(f"✔ Activos: {len(working)}")
    print(f"✖ Caídos: {len(dead)}")
    print("📄 Generado: master.m3u8")
    print("📄 Generado: misc/dead.txt")
    print("==============================\n")


if __name__ == "__main__":
    main()
