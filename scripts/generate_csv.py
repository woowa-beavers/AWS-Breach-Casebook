import os, yaml, csv

rows = []

for root, _, files in os.walk("cases"):
    for file in files:
        if file.endswith(".md"):
            with open(os.path.join(root, file), encoding="utf-8") as f:
                data = yaml.safe_load(f.read().split("---")[1])
                rows.append(data)

with open("data/breach_master.csv","w",newline="",encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("done")