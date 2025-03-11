import sys

import pandas as pd


df = pd.read_csv(sys.stdin)
df.to_markdown(buf=sys.stdout, tablefmt='github', index=False)
