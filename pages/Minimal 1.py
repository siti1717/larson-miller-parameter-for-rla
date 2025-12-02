import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.title("Larson–Miller Parameter - Minimal 1¼ Cr - ½ Mo Steel (P → Stress)")

# --- File uploader ---
uploaded_file = st.file_uploader(
    label="Upload an Excel file (first column = Stress (ksi))",
    help="The file should contain only one column with stress values in ksi.",
    type=["xlsx", "xls"]
)

# --- Manual temperature input ---
T_input = st.number_input("Enter operating temperature (°F):", min_value=0.0, step=1.0)

if uploaded_file and T_input > 0:
    # === READ STRESS DATA FROM EXCEL ===
    df = pd.read_excel(uploaded_file)
    Stress_vals = df.iloc[:, 0].dropna().to_numpy()

    # === EMPIRICAL RELATIONSHIP FOR 2¼ Cr - 1 Mo STEEL ===
    # Empirical relationship: P ≈ 40 - 0.15 * Stress
    P_vals = 40 - 0.15 * Stress_vals

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

    st.success("✅ Calculation completed successfully!")
    st.dataframe(df_out)

    # --- DOWNLOAD EXCEL ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='LMP_Result')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Result",
        data=output,
        file_name="LMP_InputStress_ManualT.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif not uploaded_file:
    st.warning("📂 Please upload an Excel file containing the stress (ksi) column.")
elif T_input == 0:
    st.info("✏️ Please enter the operating temperature (°F) to start the calculation.")

