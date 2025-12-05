import streamlit as st 
import pandas as pd
import numpy as np
from io import BytesIO

st.title("Larson–Miller Calculator: Temperature (T) in Rankine (°R)")

st.markdown("This calculator computes **temperature (T)** from the Larson–Miller oxidation equation:")

# Menggunakan st.latex untuk persamaan utama
st.latex(r"""
\log x = -7.1438 + 2.1761\times10^{-4}\,T\,(20 + \log t)
""")

st.markdown("""
Where:
- **x** = oxide thickness (in mils, converted automatically from mm)  
- **t** = exposure time (in hours, converted automatically from years)  
- **T** = temperature in °Rankine (°R)
---
**Formula used in this calculator:**
""")

# Menggunakan st.latex untuk persamaan yang diformulasikan ulang
st.latex(r"""
T = \frac{\log(x\times39.37) + 7.1438}{2.1761\times10^{-4}\,(20 + \log(t\times8760))}
""")

st.markdown("---")

# === Upload Excel or CSV file ===
uploaded_file = st.file_uploader(
    label="📂 Upload data file (first column = oxide thickness (mm))",
    type=["xlsx", "xls", "csv"]
)

# === Input operation time (years) ===
t_value = st.number_input("Enter exposure time (years):", min_value=0.0, step=0.1, format="%.3f")

if uploaded_file is not None and t_value > 0:
    # Read file depending on type
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Rename first column
    df.columns = ['x_mm'] + list(df.columns[1:])

    if (df['x_mm'] <= 0).any():
        st.error("❌ Some values of thickness (x) ≤ 0. Log10 cannot be calculated.")
    else:
        # --- Conversion ---
        df['x_mils'] = df['x_mm'] * 39.3701      # mm → mils
        t_hours = t_value * 365 * 24             # years → hours

        # --- Calculation ---
        logx = np.log10(df['x_mils'])
        logt = np.log10(t_hours)

        df['T (°R)'] = (logx + 7.1438) / (2.1761e-4 * (20 + logt))
        df['T (°F)'] = df['T (°R)'] - 459.67
        df['T (°C)'] = (df['T (°F)'] - 32) * 5/9

        st.success("✅ Calculation completed successfully!")
        st.dataframe(df)

        # --- Export to Excel ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
            workbook = writer.book
            worksheet = writer.sheets['Results']
            fmt = workbook.add_format({'num_format': '0.0000'})
            worksheet.set_column('B:D', 20, fmt)

        st.download_button(
            label="📥 Download Excel Result",
            data=output.getvalue(),
            file_name="Larson_Miller_Temperature_Result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif uploaded_file is None:
    st.info("ℹ️ Please upload an Excel or CSV file containing oxide thickness (mm).")
elif t_value == 0:
    st.warning("⚠️ Please enter an exposure time (years) greater than 0.")



