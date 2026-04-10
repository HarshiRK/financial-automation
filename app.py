import streamlit as st
import pandas as pd

st.set_page_config(page_title="Schedule III Generator", layout="wide")
st.title("📑 Official Schedule III Statement Generator")

mapping_file = st.sidebar.file_uploader("1. Upload Mapping Master", type=['csv', 'xlsx'])
tb_file = st.file_uploader("2. Upload Trial Balance (CSV)", type=['csv'])

if mapping_file and tb_file:
    # Load Data
    df_map = pd.read_csv(mapping_file) if mapping_file.name.endswith('.csv') else pd.read_excel(mapping_file)
    df_tb = pd.read_csv(tb_file)
    
    # Auto-detect Amount Column
    num_cols = df_tb.select_dtypes(include=['number']).columns.tolist()
    df_tb['Amt'] = df_tb[num_cols[0]].fillna(0) if num_cols else 0
    df_tb['Particulars'] = df_tb.iloc[:, 0].astype(str).str.strip()
    df_map['Tally_Item'] = df_map['Tally_Item'].astype(str).str.strip()

    # Merge Logic
    merged = pd.merge(df_tb, df_map, left_on='Particulars', right_on='Tally_Item', how='left')
    merged['Final_Value'] = merged['Amt'] * merged['Sign'].fillna(1)

    # CREATE THE SCHEDULE III FORMAT
    def show_statement(stmt_name):
        st.subheader(f"--- {stmt_name} ---")
        subset = merged[merged['Statement'] == stmt_name]
        
        # This groups the data into the Official Schedule III Rows
        report = subset.groupby(['Major_Head', 'Schedule_III_Line_Item'])['Final_Value'].sum().reset_index()
        
        # Formatting for Excel Copy-Paste
        report.columns = ['Category', 'Particulars (As per Schedule III)', 'Amount (in ₹)']
        st.table(report) 
        return report

    # Display Balance Sheet
    bs_final = show_statement('Balance Sheet')
    
    # Display Profit & Loss
    pl_final = show_statement('Profit & Loss')

    # DOWNLOAD BUTTON FOR EXCEL
    full_report = pd.concat([bs_final, pl_final])
    st.download_button("📩 Download for Excel Copy-Paste", full_report.to_csv(index=False), "Schedule_III_Format.csv")
