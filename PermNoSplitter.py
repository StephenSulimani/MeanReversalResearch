import pandas as pd

daily_data = pd.read_csv("daily_data_full.csv")

prev_perm_no = None

perm_no_df = pd.DataFrame(columns=["date", "close"])

for _, row in daily_data.iterrows():
    if row["permno"] != prev_perm_no and prev_perm_no is not None:
        perm_no_df = pd.DataFrame(columns=["date", "close"])

    perm_no_df = perm_no_df._append({"date": row["date"], "close": row["prc"]}, ignore_index=True)
    
    prev_perm_no = row["permno"] 

    perm_no_df.to_csv(f"permno/{row['permno']}.csv", index=False)

