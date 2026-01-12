import json
import os

#  File paths 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
input_path = os.path.join(BASE_DIR, "data/processed_pdf/DAISY_MHB_chunks.jsonl")
output_path = os.path.join(BASE_DIR, "data/processed_pdf/BDAISY_MHB_chunks_normalized.jsonl")

def reformat_daisy_pdf_json(input_file: str, output_file: str):
    """Reformat DAISY processed_pdf data to match BMI-style structure."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    count = 0
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)

            # Extract section info
            major_section = data.get("major_section", "")
            sub_section = data.get("sub_section", "")

            # Build contextual sentence (German)
            context_sentence = ""
            if sub_section and major_section:
                context_sentence = (
                    f"\n\nDas Modul ist {sub_section} und sollte im {major_section} belegt werden."
                )
            elif sub_section:
                context_sentence = f"\n\nDas Modul ist {sub_section}."
            elif major_section:
                context_sentence = f"\n\nDas Modul sollte im {major_section} belegt werden."

            # Append contextual info to the text
            text = (data.get("text") or "").rstrip() + context_sentence

            # Build metadata structure
            metadata = {
                "module_id": data.get("module_id"),
                "module_name": data.get("title"),
                "studyProgramAbbrev": "BDAISY",
                "source_file": "Modulhandbuch_DAISY_V6-3_final.pdf",
                "pdf_page_start": data.get("pdf_page_start"),
                "pdf_page_end": data.get("pdf_page_end"),
            }

            # Create normalized JSON object
            new_obj = {
                "id": data.get("id"),
                "namespace": "BDAISY_pdf",
                "text": text,
                "metadata": metadata,
            }

            # Write one JSON object per line
            outfile.write(json.dumps(new_obj, ensure_ascii=False) + "\n")
            count += 1

    print(f"✅ Normalisierung abgeschlossen! {count} Datensätze gespeichert unter: {output_file}")

if __name__ == "__main__":
    reformat_daisy_pdf_json(input_path, output_path)

