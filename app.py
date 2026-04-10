import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Monthly Schedule III", layout="wide")
st.title("📅 Monthly Comparative Schedule III Generator")

mapping_file = st.sidebar.file_uploader("1. Upload Mapping Master", type=['csv', 'xlsx'])
tb_file = st.sidebar.file_uploader("2. Upload Monthly Trial Balance (CSV)", type=['csv'])

if mapping_file and tb_file:
    # 1. LOAD & CLEAN TRIAL BALANCE
    # We read the CSV and drop rows that are completely empty
    df_tb = pd.read_csv(tb_file).dropna(how='all').reset_index(drop=True)
    
    # If Tally added empty rows at the top, this finds the REAL header row
    if "Particulars" not in df_tb.columns:
        # Find the row that actually contains the word 'Particulars'
        for i, row in df_tb.iterrows():
            if row.astype(str).str.contains('Particulars', case=False).any():
                df_tb.columns = df_tb.iloc[i]
                df_tb = df_tb.iloc[i+1:].reset_index(drop=True)
                break

    # 2. LOAD MAPPING
    df_map = pd.read_csv(mapping_file) if mapping_file.name.endswith('.csv') else pd.read_excel(mapping_file)
    
    # 3. IDENTIFY MONTH/AMOUNT COLUMNS
    # We convert columns to numeric, ignoring the text column 'Particulars'
    for col in df_tb.columns:
        if col != 'Particulars':
            df_tb[col] = pd.to_numeric(df_tb[col], errors='coerce').fillna(0)
    
    month_cols = df_tb.select_dtypes(include=[np.number]).columns.tolist()

    # 4. CLEAN TEXT FOR MATCHING
    df_tb['Particulars'] = df_tb['Particulars'].astype(str).str.strip()
    df_map['Tally_Item'] = df_map['Tally_Item'].astype(str).str.strip()

    # 5. MERGE & APPLY SIGN
    merged = pd.merge(df_tb, df_map, left_on='Particulars', right_on='Tally_Item', how='left')
    
    for month in month_cols:
        merged[month] = merged[month] * merged['Sign'].fillna(1)

    # 6. DISPLAY FORMATTED TABLES
    def show_final_table(stmt):
        st.subheader(f"--- {stmt} ---")
        subset = merged[merged['Statement'] == stmt]
        
        # Group by Official Schedule III Line Item
        report = subset.groupby(['Major_Head', 'Schedule_III_Line_Item'])[month_cols].sum().reset_index()
        
        # Show as a clean table for copy-pasting
        st.table(report)
        return report

    bs_final = show_final_table('Balance Sheet')
    pl_final = show_final_table('Profit & Loss')

    # DOWNLOAD
    full_report = pd.concat([bs_final, pl_final])
    st.download_button("📥 Download Excel Ready File", full_report.to_csv(index=False), "Monthly_Report.csv")
