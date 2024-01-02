#!/bin/zsh

path_to_chats="path/to/chat/history"
output_dir="cleaned_chats"

python_script="clean_chat.py"

echo "Path to chats: $path_to_chats"
echo "Output directory: $output_dir"
echo "Python script to run: $python_script"

total_files=$(find "$path_to_chats" -maxdepth 1 -name "*.txt" | wc -l)
echo "Total files to process: $total_files"

counter=0

draw_progress_bar() {
    local progress_bar_width=50
    local progress=$(($1 * progress_bar_width / $2))
    local remaining=$(($progress_bar_width - progress))

    printf -v bar '%*s' "$progress" ''
    bar=${bar// /█}
    printf -v empty_bar '%*s' "$remaining" ''
    empty_bar=${empty_bar// /░}

    printf "\rProgress: [%s%s] %d/%d" "$bar" "$empty_bar" "$1" "$2"
}

for txtfile in "$path_to_chats"/*.txt; do
    if [[ -f "$txtfile" ]]; then
        filename=$(basename "$txtfile" .txt)
        python "$python_script" "$path_to_chats" "$output_dir" --name "$filename"
        ((counter++))
        draw_progress_bar $counter $total_files
    fi
done

echo -e "\nProcessing complete."
