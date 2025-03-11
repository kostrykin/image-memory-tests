import sys

import pandas as pd


df = pd.read_csv(sys.stdin)
df.to_markdown(buf=sys.stdout, tablefmt='grid', index=False)
