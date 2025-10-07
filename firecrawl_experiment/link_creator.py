import os

OUTPUT_DIR = "firecrawl_inputs"
MAX_LINES = 100

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir():
    if not filename.endswith(".txt"):
        continue

    filepath = filename
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    base_name = os.path.splitext(filename)[0]

    for i in range(0, len(lines), MAX_LINES):
        chunk = lines[i:i + MAX_LINES]
        out_name = f"{base_name}_part{i // MAX_LINES + 1}.txt"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.writelines(chunk)
