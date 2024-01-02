import json
import os
import argparse
def check_integrity(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # # Filter out entries that don't strictly contain "instruction" and "output" keys
        # valid_data = [entry for entry in data if isinstance(entry, dict) and
        #               set(entry.keys()) == {"instruction", "output"}]
        #
        # # Write the valid data back to the file
        # with open(json_file, 'w', encoding='utf-8') as file:
        #     json.dump(valid_data, file, ensure_ascii=False, indent=4)

        print(f"Finished checking")

    except json.JSONDecodeError as e:
        print(f"Error processing {json_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path")
    args = parser.parse_args()
    check_integrity(args.data_path)
