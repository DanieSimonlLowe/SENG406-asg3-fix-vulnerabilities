#!/bin/sh

# Term to search for
SEARCH_TERM="| safe"

# Directory to search (can be . for the entire repository)
DIRECTORY_TO_SEARCH="./templates"



# Find files containing the term
if grep -r -q "$SEARCH_TERM" "$DIRECTORY_TO_SEARCH"; then
    echo "Commit aborted: The term '$SEARCH_TERM' was found in the following files:"
    grep -r --color=always "$SEARCH_TERM" "$DIRECTORY_TO_SEARCH"
    echo "This could lead to serverside template injection."
    exit 1
fi

echo "templates checked"