import streamlit as st 
import pandas as pd
import numpy as np
from io import BytesIO

st.title("Larson–Miller Calculator: Temperature (T) in Rankine (°R)")

uploaded_file = st.file_uploader(
    label="Upload data file (first column = oxide thickness (mm))",
    type=["xlsx", "xls", "csv"]
)

t_years = st.number_input("Enter exposure time (years):", min_value=0.0, step=0.1)

if uploaded_file is not None and t_years > 0:
    # Read file
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = ['x'] + list(df.columns[1:])

    # Convert units
    df['x_mils'] = df['x'] * 39.3701      # mm → mils
    t_hours = t_years * 365 * 24          # years → hours

    # Calculate temperature in Rankine
    logx = np.log10(df['x_mils'])
    logt = np.log10(t_hours)

    df['T (°R)'] = (logx + 7.1438) / (2.1761e-4 * (20 + logt))
    df['T (°F)'] = df['T (°R)'] - 459.67
    df['T (°C)'] = (df['T (°F)'] - 32) * 5/9

    st.success("✅ Calculation completed successfully!")
    st.dataframe(df)

    # Download Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Result",
        data=output.getvalue(),
        file_name="LMP_Temperature_Result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif uploaded_file is None:
    st.info("ℹ️ Please upload an Excel or CSV file first.")
elif t_years == 0:
    st.warning("⚠️ Enter a value for t (years) greater than 0.")
