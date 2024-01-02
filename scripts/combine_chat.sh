#!/bin/zsh

output_dir="cleaned_chats"

combined_json="../data.json"

cd "$output_dir" || { echo "Failed to enter directory $output_dir"; exit 1; }

printf "[" > "$combined_json"

json_files=(*.json)

num_files=${#json_files[@]}

for (( i=0; i<$num_files; i++ )); do
    json_file=${json_files[$i]}
    if [[ -f "$json_file" ]]; then
        file_content=$(sed '1d;$d' "$json_file")
        printf "%s" "$file_content" >> "$combined_json"

        if [[ $i -lt $((num_files - 1)) ]]; then
            printf "," >> "$combined_json"
        fi
    fi
done

printf "]" >> "$combined_json"

echo "All JSON files have been combined into data.json outside the $output_dir"
