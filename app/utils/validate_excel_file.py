import pandas as pd


# COLUMN_MAPPING = {
#     "postoffices":"postoffices",
#     "small_env_dom": "small_env_dom",
#     "Small Envelope For.": "small_env_for",
#     "Large Envelope Dom.": "large_env_dom",
#     "Large Envelope For.": "large_env_for",
#     }

COLUMN_MAPPING = {
    "postoffices":"postoffices",
    "small_env_dom": "small_env_dom",
    "Small Envelope For.": "small_env_for",
    "Large Envelope Dom.": "large_env_dom",
    "Large Envelope For.": "large_env_for",
    "post card dom.": "post_card_dom",
    "post card for.": "post_card_for",
    "small packet dom.": "small_packet_dom",
    "small packet for.": "small_sacket_for",
    "printed paper dom.": "printed_paper_dom",
    "printed paper for.": "printed_paper_for",
    "articles of the blind dom.": "articles_of_blind_dom",
    "articles of the blind for.": "articles_of_Blind_for",
}


def validate_and_clean_excel_sheet(df: pd.DataFrame) -> pd.DataFrame:
    print("validate_and_clean_excel_sheet function",)
    for i in range(min(15, len(df))):  # Only scan first 15 rows to find headers
        
        header_row = df.iloc[i] # type: ignore
        normalized = [str(col) for col in header_row] # type: ignore
        

        if any(col in normalized for col in COLUMN_MAPPING.keys()):
            print("inside forlop")
            df.columns = normalized
            df = df.iloc[i + 1 :]  # Slice rows below header
            df = df.reset_index(drop=True)

            # Rename columns to standard names
            df = df.rename(columns={k: COLUMN_MAPPING[k] for k in normalized if k in COLUMN_MAPPING})

            # Drop columns not in mapped headers
            df = df[[col for col in df.columns if col in COLUMN_MAPPING.values()]]
            return df

    raise ValueError("Valid headers not found in the sheet.")
