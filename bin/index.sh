#!/bin/bash

JSON_FILE_PATH="tmdb_es.json.zip"
ES_ENDPOINT="http://localhost:9200"

cd data

# Extract filename without .zip extension
filename=$(basename "$JSON_FILE_PATH" .zip)

if [ -e "$filename" ]; then
    echo "$filename already exists. Skipping unzip."
else
    unzip ${JSON_FILE_PATH}
fi 

cd ..

# Create index mappings
if curl -s -X GET "${ES_ENDPOINT}/tmdb" -o /dev/null ; then
    echo "Index 'tmdb' already exists. Skipping creation."
else
    curl -X PUT "${ES_ENDPOINT}/tmdb?pretty" -H 'Content-Type: application/json' -d '@index.json'
    echo "Created index mappings..."
fi

# Bulk index movie data
curl -XPOST "${ES_ENDPOINT}/tmdb/_bulk?pretty" -H "Content-Type: application/x-ndjson" --data-binary '@data/tmdb_es.json'

echo "Indexed data..."
