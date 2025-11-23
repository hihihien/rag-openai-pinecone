import json

def compare_json(old, new, path=""):
    differences = []

    if isinstance(old, dict) and isinstance(new, dict):
        # Keys present in old but not in new
        for key in old.keys() - new.keys():
            differences.append(f"Removed: {path}.{key} -> {old[key]}")

        # Keys present in new but not in old
        for key in new.keys() - old.keys():
            differences.append(f"Added:   {path}.{key} -> {new[key]}")

        # Keys present in both
        for key in old.keys() & new.keys():
            differences += compare_json(old[key], new[key], f"{path}.{key}")

    elif isinstance(old, list) and isinstance(new, list):
        min_len = min(len(old), len(new))
        # Compare shared indices
        for i in range(min_len):
            differences += compare_json(old[i], new[i], f"{path}[{i}]")

        # Extra items
        if len(old) > len(new):
            for i in range(min_len, len(old)):
                differences.append(f"Removed: {path}[{i}] -> {old[i]}")

        if len(new) > len(old):
            for i in range(min_len, len(new)):
                differences.append(f"Added:   {path}[{i}] -> {new[i]}")

    else:
        if old != new:
            differences.append(
                f"Changed: {path} | old: {old} -> new: {new}"
            )

    return differences


if __name__ == "__main__":
    # Load your two files
    with open("Studiengang_BMI_2025.json", "r", encoding="utf-8") as f:
        old_json = json.load(f)

    with open("New_Studiengang_BMI_2025.json", "r", encoding="utf-8") as f:
        new_json = json.load(f)

    # Compare
    diffs = compare_json(old_json, new_json)

    # Save results
    with open("json_differences.txt", "w", encoding="utf-8") as out:
        for d in diffs:
            out.write(d + "\n")

    print("Done! Differences saved to json_differences.txt")
