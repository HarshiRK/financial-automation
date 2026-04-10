import streamlit as st
import pandas as pd

# 1. PAGE SETTINGS
st.set_page_config(page_title="Statutory Financial Automation", layout="wide")

st.title("📊 Schedule III Financial Engine")
st.markdown("---")

# 2. FILE UPLOADERS
st.sidebar.header("📁 Step 1: Logic Configuration")
mapping_file = st.sidebar.file_uploader("Upload your Master Mapping Sheet", type=['csv', 'xlsx'])

st.header("📂 Step 2: Client Data Upload")
tb_file = st.file_uploader("Upload Client Trial Balance (CSV)", type=['csv'])

# 3. THE ENGINE
if mapping_file and tb_file:
    # Load the Mapping Master (Handles both CSV and Excel)
    if mapping_file.name.endswith('.csv'):
        df_map = pd.read_csv(mapping_file)
    else:
        df_map = pd.read_excel(mapping_file)
        
    # Load the Trial Balance (Assuming it's a CSV with 'Particulars' and 'Amount')
    df_tb = pd.read_csv(tb_file)
    
    # Cleaning column names and text
    df_tb['Particulars'] = df_tb['Particulars'].str.strip()
    df_map['Tally_Item'] = df_map['Tally_Item'].str.strip()

    # 4. MAPPING PROCESS
    # This merges your logic with the actual client data
    final_df = pd.merge(df_tb, df_map, left_on='Particulars', right_on='Tally_Item', how='left')

    # 5. ERROR HANDLING (Sustainability Check)
    missing_items = final_df[final_df['Statement'].isna()]['Particulars'].unique()
    
    if len(missing_items) > 0:
        st.error(f"🚨 ALERT: {len(missing_items)} new items found that are NOT in your Master Mapping!")
        st.info("Add these ledgers to your mapping sheet and re-upload to continue.")
        st.write("Missing Ledgers:", missing_items)
    else:
        st.success("✅ All ledger items successfully recognized!")

        # 6. CALCULATIONS
        # Formula: Actual Value = (Trial Balance Amount) * (Master Sign)
        # This handles Drawings, Discounts, and Returns automatically
        final_df['Report_Amount'] = final_df['Amount'] * final_df['Sign']

        # 7. GENERATING THE SCHEDULE III VIEW
        report = final_df.groupby(['Statement', 'Major_Head', 'Sub_Head', 'Schedule_III_Line_Item']).agg({
            'Report_Amount': 'sum'
        }).reset_index()

        # Display Sections
        col_bs, col_pl = st.columns(2)
        
        with col_bs:
            st.subheader("🏢 Balance Sheet (Part I)")
            bs_display = report[report['Statement'] == 'Balance Sheet']
            st.dataframe(bs_display[['Major_Head', 'Sub_Head', 'Schedule_III_Line_Item', 'Report_Amount']], use_container_width=True)
            
        with col_pl:
            st.subheader("📈 Profit & Loss (Part II)")
            pl_display = report[report['Statement'] == 'Profit & Loss']
            st.dataframe(pl_display[['Major_Head', 'Sub_Head', 'Schedule_III_Line_Item', 'Report_Amount']], use_container_width=True)

        # 8. DOWNLOAD FEATURE
        csv_report = report.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Final Schedule III Report",
            data=csv_report,
            file_name="Schedule_III_Output.csv",
            mime='text/csv'
        )
