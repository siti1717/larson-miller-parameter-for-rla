import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - 2¼ Cr - 1 Mo Steel (Stress → P from Master Curve)")

# --- Upload Excel: only one column (Stress ksi) ---
uploaded_file = st.file_uploader(
    label="Upload an Excel file (first column = Stress (ksi))",
    help="The file should contain only one column with stress values in ksi.",
    type=["xlsx", "xls"]
)

# --- Manual temperature input ---
T_input = st.number_input("Enter operating temperature (°F):", min_value=0.0, step=1.0)

if uploaded_file and T_input > 0:
    # === READ STRESS VALUES FROM EXCEL ===
    df = pd.read_excel(uploaded_file)
    Stress_vals = df.iloc[:, 0].dropna().to_numpy()

    # === MASTER CURVE DATA (from reference graph) ===
    x1 = np.array([30.31,30.69,31.07,31.45,31.83,32.12,32.26,32.62,32.94,33.27,33.53,33.80,34.03,34.17,34.46,34.72,34.86,35.16,35.32,35.62,35.87,36.10,36.42,36.74,37.09,37.45,37.83,38.09])
    y1 = np.array([48.61,46.85,44.77,42.43,39.84,37.95,36.65,33.95,31.24,27.81,25.05,21.90,19.72,18.23,16.83,15.52,14.46,13.28,12.24,11.22,9.99,9.29,8.60,7.93,7.27,6.72,5.95,5.74])

    # === INTERPOLATION: Stress → P ===
    # reverse arrays so stress increases
    y1_rev = y1[::-1]
    x1_rev = x1[::-1]
    cs_StressToP = CubicSpline(y1_rev, x1_rev, extrapolate=True)

    # === COMPUTE P for each stress value ===
    P_vals = cs_StressToP(Stress_vals)

    # === CALCULATE CREEP LIFE ===
    T_rankine = T_input + 459.67
    t_hours = 10 ** ((P_vals * 1000 / T_rankine) - 20)
    t_years = t_hours / (24 * 365)

    # === OUTPUT TABLE ===
    df_out = pd.DataFrame({
        "Stress (ksi)": Stress_vals,
        "Temperature (°F)": [T_input] * len(Stress_vals),
        "Larson–Miller Parameter (P)": P_vals,
        "Predicted Life (hours)": t_hours,
        "Predicted Life (years)": t_years
    })

    st.success("✅ Calculation completed successfully using the master curve interpolation!")
    st.dataframe(df_out)

    # --- DOWNLOAD EXCEL ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='LMP_Result')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Result",
        data=output,
        file_name="LMP_Stress_to_P_MasterCurve.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif not uploaded_file:
    st.warning("📂 Please upload an Excel file containing the stress (ksi) column.")
elif T_input == 0:
    st.info("✏️ Please enter the operating temperature (°F) to start the calculation.")
