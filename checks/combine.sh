#!/bin/bash

# Define source and destination directories
SOURCE_DIR="checks/pre-commit/"
DESTINATION_DIR=".git/hooks"
COMBINED_FILE="$DESTINATION_DIR/pre-commit"

rm "$COMBINED_FILE"
# Ensure the destination directory exists
mkdir -p "$DESTINATION_DIR"

# Create or clear the combined file
: > "$COMBINED_FILE"

# Iterate over all .sh files in the source directory and concatenate them
for file in "$SOURCE_DIR"/*.sh; do
    if [ -f "$file" ]; then
        cat "$file" >> "$COMBINED_FILE"
        echo "" >> "$COMBINED_FILE"  # Add a newline between files
    fi
done

echo "All .sh files from $SOURCE_DIR have been combined into $COMBINED_FILE"

