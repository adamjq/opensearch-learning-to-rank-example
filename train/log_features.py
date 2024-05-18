import csv
import os
import requests
import json
from query import get_os_query, ACTIVE_FEATURES

# File paths
input_csv = 'train/data/queries.csv'
output_csv = 'train/data/feature_values.csv'

# OpenSearch settings
url = 'http://localhost:9200/tmdb/_search?pretty=true'
headers = {'Content-Type': 'application/json'}

# Read queries from CSV
with open(input_csv, mode='r') as infile:
    reader = csv.DictReader(infile)
    queries = [(row['query_id'], row['query']) for row in reader]

if(os.path.exists(output_csv) and os.path.isfile(output_csv)): 
    os.remove(output_csv) 
    print(f"{output_csv} deleted") 
else: 
    print(f"{output_csv} not found") 

# Prepare to write results to CSV
with open(output_csv, mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['query_id', 'doc_id'] + ACTIVE_FEATURES)

    for query_id, query_text in queries:

        query = get_os_query(query_text)
        response = requests.get(url, headers=headers, data=json.dumps(query))
        response.raise_for_status()

        result = response.json()

        if len(result['hits']['hits']) == 0:
            print(f"No results found for query: {query_text}")
            break

        for doc in result['hits']['hits']:
            row = [query_id, doc['_id']]
            log_entries = doc['fields']['_ltrlog'][0]['log_entry1']

            for feat in ACTIVE_FEATURES:
                feat_value = next((entry.get('value', '-') for entry in log_entries if entry['name'] == feat), '-')
                row.append(feat_value)
                
            writer.writerow(row)

print("Feature logging complete.")