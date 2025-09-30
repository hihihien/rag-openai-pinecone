#use to sort id from jsonl file
import json

# Read the JSONL file
with open('MMI.jsonl', 'r', encoding='utf-8') as file:
    data = [json.loads(line) for line in file]

# Sort the list by the 'id' field
sorted_data = sorted(data, key=lambda x: x['id'])

# Write the sorted data back to a new JSONL file
with open('sorted_output.jsonl', 'w', encoding='utf-8') as file:
    for item in sorted_data:
        file.write(json.dumps(item) + '\n')
