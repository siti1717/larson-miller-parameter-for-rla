import streamlit as st 
import pandas as pd
import numpy as np
from io import BytesIO

st.title("Larson–Miller Calculator: T in Rankine (°R)")

# Upload Excel or CSV file
uploaded_file = st.file_uploader(
    label="Upload data file (first column = thickness (mm))",
    type=["xlsx", "xls", "csv"]
)

# Input t (years)
t_value = st.number_input("Enter the value of t (years)", min_value=0.0, format="%.6f")

if uploaded_file is not None and t_value > 0:
    # Detect file type and read accordingly
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = ['x'] + list(df.columns[1:])

    if (df['x'] <= 0).any():
        st.error("❌ There is a value of x ≤ 0. Log10 cannot be calculated.")
    else:
        # Convert x from mm to mil and calculate temperature in Rankine
        df['T (°R)'] = (np.log10(df['x'] / 25.4) + 7.1438) / ((2.1761e-4) * (20 + np.log10(t_value)))

        st.success("✅ Calculation completed successfully!")
        st.dataframe(df)

        # Export results to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
            workbook = writer.book
            worksheet = writer.sheets['Results']
            fmt = workbook.add_format({'num_format': '0.0000'})
            worksheet.set_column('B:B', 20, fmt)  # format the T(°R) column

        st.download_button(
            label="📥 Download Excel Result",
            data=output.getvalue(),
            file_name="Temperature_Calculation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif uploaded_file is None:
    st.info("ℹ️ Please upload an Excel or CSV file first.")
elif t_value == 0:
    st.warning("⚠️ Enter a value for t (years) greater than 0.")
