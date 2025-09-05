#test if jsonl has any big records and split them if necessary
import json
import os
import re
from pathlib import Path
from typing import List, Dict   

# Parameters
input_path = "backend/data/MHB_Alle_Studiengaenge/MHB_BTB_PO25/BTB_MHB_PO2025_chunks.jsonl"
output_path = Path(input_path).with_name("BTB_MHB_PO2025_chunks_split.jsonl")
max_chars = 8000
limit = 12000

long_records = []
short_records = []

# Step 1: Load and identify long records
with open(input_path, "r", encoding="utf-8") as infile:
    for line in infile:
        record = json.loads(line)
        text = record.get("text", "")
        if len(text.strip()) > limit:
            long_records.append(record)
        else:
            short_records.append(record)

# Step 2: Print info
print(f"Found {len(long_records)} records exceeding {limit} characters.")
for r in long_records:
    print(f"  [long] id: {r.get('id', '[no id]')} ({len(r['text'])} chars)")

# Step 3: Split long records
def split_text(text, max_length):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

new_records = []

for record in long_records:
    base_id = record.get("id", "no_id")
    chunks = split_text(record["text"], max_chars)
    for i, chunk in enumerate(chunks, 1):
        new_record = dict(record)  # shallow copy
        new_record["text"] = chunk
        new_record["id"] = f"{base_id}_part{i}"
        new_records.append(new_record)

# Step 4: Write everything back out
with open(output_path, "w", encoding="utf-8") as outfile:
    for record in short_records + new_records:
        outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"\nDone. Output written to: {output_path}")
