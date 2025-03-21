import pandas as pd


def get_row_by_date(df, target_date):
    """gets the row by date"""
    target_date = pd.to_datetime(target_date)

    if target_date in df.index:
        return df.loc[target_date]
    else:
        # Get the most recent date before the target date
        recent_date = df.index[df.index < target_date].max()
        if pd.isna(recent_date):
            return None  # No valid date found
        return df.loc[recent_date]
