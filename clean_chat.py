import json
import re
import os
import argparse

you = "你的微信名"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--name')
    args = parser.parse_args()
    return args


def process_chat_file(file_path, name, you):
    conversation_entries = []
    current_instruction = ''
    current_output = ''
    expecting_output = False

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Parse the line
            match = re.match(r'(.+) \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\):(.+)', line)
            if not match:
                continue

            speaker, message = match.groups()

            # Escape backslashes, special characters, and remove any unwanted content
            message = message.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n')
            message = re.sub(r'\[.*?\]|-------.*', '', message).strip()
            if not message:
                continue

            if speaker == name:
                if expecting_output:
                    # Previous instruction didn't get an output, save it with an empty input
                    if current_instruction:
                        conversation_entries.append({'instruction': current_instruction, 'input': '', 'output': ''})
                    current_instruction = message
                    expecting_output = False
                else:
                    # Append to current instruction
                    current_instruction += " " + message
            elif speaker == you:
                if not expecting_output:
                    # Start of an output
                    current_output = message
                    expecting_output = True
                else:
                    # Append to current output
                    current_output += " " + message

                if current_instruction and current_output:
                    conversation_entries.append({'instruction': current_instruction, 'input': '', 'output': current_output})
                    current_instruction = ''
                    current_output = ''
                    expecting_output = False

    # Handle last instruction if it didn't get an output
    if current_instruction:
        conversation_entries.append({'instruction': current_instruction, 'input': '', 'output': ''})

    return conversation_entries


def write_json(data, output_dir, output_file):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, output_file), 'w', encoding='utf-8') as file:


        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    args = parse_args()
    # Process the chat file and write the output
    conversation_entries = process_chat_file(os.path.join(args.input_dir, args.name+'.txt'), args.name, you)
    output_file = args.name + '.json'
    write_json(conversation_entries, args.output_dir, output_file)