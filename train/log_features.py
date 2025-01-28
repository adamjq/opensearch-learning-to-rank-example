import csv
import os
import requests
import json
from query import get_os_query, ACTIVE_FEATURES

# File paths
input_csv = 'train/data/queries.csv'
judgments_file = 'train/data/movie_judgments.txt'
output_csv = 'train/data/training_set.csv'

def parse_judgments(filename):
    """Parse judgment file into dict of {qid: {doc_id: grade}}"""
    judgments = {}
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Parse lines like: "4 qid:1 # 7555 rambo"
            parts = line.split()
            if len(parts) >= 4:
                grade = int(parts[0])
                qid = parts[1].split(':')[1]  # Get "1" from "qid:1"
                doc_id = parts[3]  # Get the document ID
                
                if qid not in judgments:
                    judgments[qid] = {}
                judgments[qid][doc_id] = grade
    
    return judgments

# Add some debug printing
judgments = parse_judgments(judgments_file)
print("Loaded judgments for queries:", list(judgments.keys()))
print("\nSample judgments for first query:", list(judgments.get('1', {}).items())[:5])

# Read queries from CSV
with open(input_csv, mode='r') as infile:
    reader = csv.DictReader(infile)
    queries = [(row['query_id'], row['query']) for row in reader]

print("\nFirst few queries from CSV:")
for qid, query in queries[:5]:
    print(f"query_id: {qid}, query: {query}")

if os.path.exists(output_csv):
    os.remove(output_csv)
    print(f"\n{output_csv} deleted")

# Track matches/mismatches
total_docs = 0
matched_judgments = 0

# Prepare to write results to CSV with additional judgment column
with open(output_csv, mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['query_id', 'doc_id', 'relevance_grade'] + ACTIVE_FEATURES)

    for query_id, query_text in queries:
        query = get_os_query(query_text)
        response = requests.get(
            'http://localhost:9200/tmdb/_search?pretty=true',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(query)
        )
        response.raise_for_status()
        result = response.json()

        if len(result['hits']['hits']) == 0:
            print(f"No results found for query: {query_text}")
            continue

        for doc in result['hits']['hits']:
            total_docs += 1
            # Get relevance grade from judgments if available
            grade = judgments.get(query_id, {}).get(doc['_id'], 0)
            if grade > 0:
                matched_judgments += 1
                print(f"Found judgment: query_id={query_id}, doc_id={doc['_id']}, grade={grade}")
            
            row = [query_id, doc['_id'], grade]
            log_entries = doc['fields']['_ltrlog'][0]['log_entry1']

            for feat in ACTIVE_FEATURES:
                feat_value = next(
                    (entry.get('value', 0.0) for entry in log_entries if entry['name'] == feat),
                    0.0
                )
                row.append(feat_value)
                
            writer.writerow(row)

print(f"\nFeature logging complete.")
print(f"Total documents processed: {total_docs}")
print(f"Documents with matching judgments: {matched_judgments}")
print(f"Judgment match rate: {(matched_judgments/total_docs)*100:.2f}%")