import subprocess
from datetime import datetime

input_file = "canales.txt"
output_file = f"revision_{datetime.now().strftime('%Y%m%d')}.txt"

with open(input_file) as f:
    urls = [line.strip() for line in f if line.strip()]

results = []

for url in urls:
    try:
        result = subprocess.run(
            ["yt-dlp", "-g", url],
            capture_output=True,
            text=True,
            timeout=20
        )
        stream = result.stdout.strip()
        if stream:
            results.append(f"{url} -> {stream}")
        else:
            results.append(f"{url} -> ERROR")
    except Exception as e:
        results.append(f"{url} -> FAIL")

with open(output_file, "w") as f:
    f.write("\n".join(results))

print(f"Archivo generado: {output_file}")
