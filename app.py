
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Financial Engine", layout="wide")
st.title("📊 Schedule III Automation")

# Sidebar
mapping_file = st.sidebar.file_uploader("Upload Mapping Master", type=['csv', 'xlsx'])
tb_file = st.file_uploader("Upload Trial Balance", type=['csv', 'xlsx'])

if mapping_file and tb_file:
    # 1. Load Mapping
    df_map = pd.read_csv(mapping_file) if mapping_file.name.endswith('.csv') else pd.read_excel(mapping_file)
    # 2. Load Trial Balance
    df_tb = pd.read_csv(tb_file) if tb_file.name.endswith('.csv') else pd.read_excel(tb_file)
    
    # 3. FIX: Find the "Amount" column automatically
    # We look for columns that have numbers
    num_cols = df_tb.select_dtypes(include=['number']).columns.tolist()
    if num_cols:
        df_tb['Amount_Fixed'] = df_tb[num_cols[0]].fillna(0)
    else:
        st.error("Could not find any numbers in your Trial Balance. Please check your file!")
        st.stop()

    # 4. Cleaning
    df_tb['Particulars'] = df_tb.iloc[:, 0].astype(str).str.strip() # Assumes first column is the ledger name
    df_map['Tally_Item'] = df_map['Tally_Item'].astype(str).str.strip()

    # 5. Merge
    final_df = pd.merge(df_tb, df_map, left_on='Particulars', right_on='Tally_Item', how='left')

    # 6. Check for Missing
    missing = final_df[final_df['Statement'].isna()]['Particulars'].unique()
    if len(missing) > 5: # Only show if there's a lot of missing data
        st.warning(f"Unmapped items found: {list(missing[:5])}...")
    
    # 7. Math & Display
    # We multiply the found number by your 'Sign' column
    final_df['Report_Amount'] = final_df['Amount_Fixed'] * final_df['Sign'].fillna(1)
    
    report = final_df.dropna(subset=['Statement']).groupby(['Statement', 'Major_Head', 'Schedule_III_Line_Item']).agg({'Report_Amount': 'sum'}).reset_index()

    st.subheader("Final Schedule III Report")
    st.dataframe(report, use_container_width=True)
    st.download_button("Download Report", report.to_csv(index=False), "Financial_Report.csv")
