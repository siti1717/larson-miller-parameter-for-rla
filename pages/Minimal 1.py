import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
from io import BytesIO

# ============================================================
# TITLE & DESCRIPTION
# ============================================================
st.title("Larson–Miller Parameter – 1¼ Cr – ½ Mo Steel")
st.markdown("""
### Remaining Life Assessment using Larson–Miller Parameter (LMP)

This application calculates **creep remaining life** of **1¼ Cr – ½ Mo steel**
using two independent paths:

1. **Temperature-based path**  
   Temperature → Allowable Stress → LMP → Remaining Life  

2. **Stress-based path**  
   Stress → LMP → Remaining Life  

📌 **Notes**
- Stress values are read from **Column A**
- Temperature values (°F) are read from **Column B**
- Maximum life is limited to **200,000 hours**
- Interpolation uses **PCHIP (monotonic, no overshoot)**
""")

# ============================================================
# UPLOAD FILE
# ============================================================
uploaded_file = st.file_uploader(
    "Upload Excel file (Stress in col A, Temperature °F in col B)",
    type=["xlsx", "xls"]
)

# ============================================================
# DATA FOR INTERPOLATION
# ============================================================

# --- Temperature (°F) → Stress (ksi)
T_data = np.array([
    427.009, 533.864, 640.537, 747.087, 823.919, 838.492, 851.701,
    862.906, 873.451, 883.994, 890.711, 901.933, 912.866, 923.764,
    934.670, 945.588, 956.512, 966.069, 993.337, 1000.493,
    1013.357, 1026.921, 1041.195, 1056.132, 1071.762, 1085.957
])

Stress_data = np.array([
    48.63, 46.89, 44.77, 42.39, 36.90, 33.94, 30.65,
    27.52, 24.55, 21.57, 19.70, 18.85, 17.62, 16.22,
    14.85, 13.55, 12.27, 11.14, 9.80, 9.12,
    8.46, 7.80, 7.11, 6.51, 5.92, 5.42
])

# Sort (safety)
idx = np.argsort(T_data)
T_data = T_data[idx]
Stress_data = Stress_data[idx]

interp_T_to_Stress = PchipInterpolator(T_data, Stress_data)

# --- Stress (ksi) → LMP (P / 1000)
Stress_LMP = np.array([
    48.61, 46.85, 44.77, 42.43, 39.84, 37.95, 36.65,
    33.95, 31.24, 27.81, 25.05, 21.90, 19.72,
    18.23, 16.83, 15.52, 14.46, 13.28,
    12.24, 11.22, 9.99, 9.29, 8.60,
    7.93, 7.27, 6.72, 5.95, 5.74
])

P_LMP = np.array([
    30.31, 30.69, 31.07, 31.45, 31.83, 32.12, 32.26,
    32.62, 32.94, 33.27, 33.53, 33.80, 34.03,
    34.17, 34.46, 34.72, 34.86, 35.16,
    35.32, 35.62, 35.87, 36.10, 36.42,
    36.74, 37.09, 37.45, 37.83, 38.09
])

interp_Stress_to_P = PchipInterpolator(Stress_LMP[::-1], P_LMP[::-1])

# ============================================================
# PROCESS FILE
# ============================================================
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    Stress_input = df.iloc[:, 0].to_numpy()
    T_input = df.iloc[:, 1].to_numpy()

    # ========================================================
    # PATH 1 – TEMPERATURE BASED
    # ========================================================
    Stress_from_T = interp_T_to_Stress(T_input)
    P_from_T = interp_Stress_to_P(Stress_from_T)

    T_R = T_input + 459.67
    Life_hours_T = 10 ** ((P_from_T * 1000 / T_R) - 20)
    Life_hours_T = np.minimum(Life_hours_T, 200_000)
    Life_years_T = Life_hours_T / (24 * 365)

    # ========================================================
    # PATH 2 – STRESS BASED
    # ========================================================
    T_ref = st.number_input(
        "Reference temperature for stress-based calculation (°F)",
        value=950.0, step=1.0
    )

    T_ref_R = T_ref + 459.67
    P_from_S = interp_Stress_to_P(Stress_input)

    Life_hours_S = 10 ** ((P_from_S * 1000 / T_ref_R) - 20)
    Life_hours_S = np.minimum(Life_hours_S, 200_000)
    Life_years_S = Life_hours_S / (24 * 365)

    # ========================================================
    # OUTPUT TABLE
    # ========================================================
    result = pd.DataFrame({
        "Temperature (°F)": T_input,
        "Stress from Temperature (ksi)": Stress_from_T,
        "LMP from Temperature": P_from_T,
        "Life from Temperature (hours)": Life_hours_T,
        "Life from Temperature (years)": Life_years_T,
        "Input Stress (ksi)": Stress_input,
        "LMP from Stress": P_from_S,
        "Life from Stress (hours)": Life_hours_S,
        "Life from Stress (years)": Life_years_S
    })

    st.success("✅ Remaining life calculation completed successfully")
    st.dataframe(result)

    # ========================================================
    # DOWNLOAD
    # ========================================================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        result.to_excel(writer, index=False, sheet_name="LMP_Result")

    st.download_button(
        "📥 Download Result (Excel)",
        data=output.getvalue(),
        file_name="LMP_Remaining_Life_Result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("📂 Please upload Excel file to start calculation.")
