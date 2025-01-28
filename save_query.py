import json
import sys
import argparse
from train.query import get_os_query

# Parse arguments
parser = argparse.ArgumentParser(description='Generate OpenSearch LTR query')
parser.add_argument('query', nargs='?', default="rambo", help='Search query text')
parser.add_argument('--rescore', action='store_true', help='Use model rescoring')

args = parser.parse_args()

# Generate query
example_query = get_os_query(args.query, model_rescore=args.rescore)

# Save to file with appropriate name
filename = 'example-ltr-rescore.json' if args.rescore else 'example-ltr.json'
with open(filename, 'w') as f:
    json.dump(example_query, f, indent=2)