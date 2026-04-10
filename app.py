import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monthly Schedule III", layout="wide")
st.title("📅 Monthly Comparative Schedule III Generator")

mapping_file = st.sidebar.file_uploader("1. Upload Mapping Master", type=['csv', 'xlsx'])
tb_file = st.sidebar.file_uploader("2. Upload Monthly Trial Balance (CSV)", type=['csv'])

if mapping_file and tb_file:
    # Load Data
    df_map = pd.read_csv(mapping_file) if mapping_file.name.endswith('.csv') else pd.read_excel(mapping_file)
    df_tb = pd.read_csv(tb_file)
    
    # 1. IDENTIFY MONTHLY COLUMNS
    # This finds all columns that are numbers (the months)
    month_cols = df_tb.select_dtypes(include=['number']).columns.tolist()
    
    # 2. CLEAN TEXT FOR MATCHING
    df_tb['Particulars'] = df_tb.iloc[:, 0].astype(str).str.strip()
    df_map['Tally_Item'] = df_map['Tally_Item'].astype(str).str.strip()

    # 3. MERGE
    merged = pd.merge(df_tb, df_map, left_on='Particulars', right_on='Tally_Item', how='left')

    # 4. APPLY SIGNS TO ALL MONTHS
    # We multiply every month column by the 'Sign' column
    for month in month_cols:
        merged[month] = merged[month] * merged['Sign'].fillna(1)

    # 5. GENERATE MONTHLY TABLE
    def get_monthly_report(statement_name):
        st.subheader(f"--- {statement_name} ---")
        subset = merged[merged['Statement'] == statement_name]
        
        # Grouping by Schedule III Line and summing all months
        report = subset.groupby(['Major_Head', 'Schedule_III_Line_Item'])[month_cols].sum().reset_index()
        
        st.dataframe(report, use_container_width=True)
        return report

    # Display Balance Sheet and P&L with all 12 months
    bs_final = get_monthly_report('Balance Sheet')
    pl_final = get_monthly_report('Profit & Loss')

    # DOWNLOAD BUTTON
    full_report = pd.concat([bs_final, pl_final])
    st.download_button("📩 Download Monthly Excel Format", full_report.to_csv(index=False), "Monthly_Schedule_III.csv")
