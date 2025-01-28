import json
import sys
from train.query import get_os_query

query_text = sys.argv[1] if len(sys.argv) > 1 else "rambo"

example_query = get_os_query(query_text)

# Save to file

with open('example-ltr.json', 'w') as f:
    json.dump(example_query, f, indent=2)