import os, yaml, re, sys

VALID_CAUSE_TYPES = {
    "CRED_EXPOSURE","S3_MISCONFIG","IAM_ESCALATION",
    "SSRF_IMDS","SUPPLY_CHAIN","LOGGING_ABSENT",
    "RANSOMWARE","INSIDER","OTHER"
}

def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)

for root, _, files in os.walk("cases"):
    for file in files:
        if file.endswith(".md"):
            path = os.path.join(root, file)

            with open(path, encoding="utf-8") as f:
                content = f.read()

            if not content.startswith("---"):
                fail(f"{file} no frontmatter")

            data = yaml.safe_load(content.split("---")[1])

            if data["cause_type"] not in VALID_CAUSE_TYPES:
                fail(f"{file} invalid cause_type")

print("✅ validation passed")