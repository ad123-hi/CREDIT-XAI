import json

with open("loan-default.ipynb", "r", encoding="utf-8") as f:
    notebook = json.load(f)

with open("notebook_content.txt", "w", encoding="utf-8") as out:
    for idx, cell in enumerate(notebook["cells"]):
        out.write(f"=== Cell {idx} ({cell['cell_type']}) ===\n")
        out.write("".join(cell["source"]))
        out.write("\n" + "="*40 + "\n\n")
