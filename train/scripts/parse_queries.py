"""
Reads the movie_judgments.txt file and outputs a CSV file with query_id and query
"""

import csv

TRAIN_DATA_BASE_PATH = './train/data'

input_file = f"{TRAIN_DATA_BASE_PATH}/movie_judgments.txt"
output_file = f"{TRAIN_DATA_BASE_PATH}/queries.csv"

with open(input_file, 'r') as infile:
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['query_id', 'query'])
        
        for line in infile:
            if line.startswith('# qid'):
                # Parse the line to extract query_id and query
                # Example line: # qid:1: rambo*1
                parts = line.split(':')
                query_id = parts[1].strip()
                query = parts[2].split('*')[0].strip()
                
                writer.writerow([query_id, query])

print(f"CSV file '{output_file}' has been created with the extracted queries.")