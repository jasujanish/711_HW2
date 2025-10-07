import os
import re

def remove_lines_with_keyword(directory: str, keyword: str):
    """
    Removes all lines containing `keyword` from every .txt file in `directory`.
    """
    pattern = re.compile(rf"\b{re.escape(keyword)}\b", flags=re.IGNORECASE)
    for filename in os.listdir(directory):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            filtered_lines = [line for line in lines if not pattern.search(line)]
            removed_lines = [line for line in lines if pattern.search(line)]
            for f in removed_lines:
                if f is not None:
                    print(f, end = "")
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(filtered_lines)

            print(f"Cleaned: {filename} ({len(lines) - len(filtered_lines)} lines removed)")

        except Exception as e:
            print(e)
if __name__ == "__main__":
    directory = "firecrawl_inputs"
    keyword = "city-government"
    remove_lines_with_keyword(directory, keyword)
