import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - Minimal 1¼ Cr - ½ Mo Steel (Temperature & Stress Comparison)")

st.markdown("""
This tool calculates **creep remaining life** for **1¼ Cr - ½ Mo Steel**  
using two independent methods:


1. **From Temperature (°F):** Temperature → Stress → P → Life  
2. **From Stress (ksi):** Stress → P → Life  

📘 Notes:
- Temperature values are read from the **second column (column B)** of the uploaded Excel file.  
- Stress values are read from the **first column (column A)** of the uploaded Excel file.  
- All life predictions are capped at **200,000 hours** maximum.
""")

# === Upload Excel File ===
uploaded_file = st.file_uploader(
    label="Upload Excel file (Stress in 1st col, Temperature (°F) in 2nd col):",
    type=["xlsx", "xls"]
)

# === SPLINE 1: Temperature → Stress ===
x2 = np.array([427.00938639356104,533.863950267865,640.5369779181265,747.0870294166173,823.918728223842,838.4923750229345,851.7011434943004,862.9059831055836,873.4507112736203,883.9943351660085,890.7113744469356,901.9328678896384,912.8662277367607,923.7637366457648,934.6701443610918,945.5880591535613,956.5121110538397,966.0686107639804,993.3369408556557,1000.4932109968408,1013.3573406508535,1026.9211857081007,1041.1951754385966,1056.132344044696,1071.761748476545,1085.9573296785275])
y2 = np.array([48.63221464134243,46.885451342721545,44.765242097498955,42.392053340062304,36.8987839319856,33.94161979261263,30.653268566954907,27.51896618447742,24.55398606811145,21.572441817017186,19.702561000201648,18.85089757519347,17.619057295741847,16.21513251332179,14.85392200125338,13.547945459467279,12.271427035165068,11.144654041406007,9.796949646778195,9.118862911165674,8.457933485957398,7.79618607878723,7.108590441621292,6.507864488808227,5.924271539996955,5.424856371263967])
sort_idx = np.argsort(x2)
x2_sorted = x2[sort_idx]
y2_sorted = y2[sort_idx]
cs_TtoStress = CubicSpline(x2_sorted, y2_sorted, extrapolate=True)

# === SPLINE 2: Stress → P ===
x1 = np.array([30.31,30.69,31.07,31.45,31.83,32.12,32.26,32.62,32.94,33.27,33.53,33.80,34.03,34.17,34.46,34.72,34.86,35.16,35.32,35.62,35.87,36.10,36.42,36.74,37.09,37.45,37.83,38.09])
y1 = np.array([48.61,46.85,44.77,42.43,39.84,37.95,36.65,33.95,31.24,27.81,25.05,21.90,19.72,18.23,16.83,15.52,14.46,13.28,12.24,11.22,9.99,9.29,8.60,7.93,7.27,6.72,5.95,5.74])
cs_StressToP = CubicSpline(y1, x1, extrapolate=True)

# === PROCESS FILE ===
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # --- Baca kolom: Stress & Temperature ---
    Stress_vals = df.iloc[:, 0].dropna().to_numpy()
    T_vals = df.iloc[:, 1].dropna().to_numpy()

    # === PATH 1: From Temperature ===
    Stress_from_T = cs_TtoStress(T_vals)
    P_from_T = cs_StressToP(Stress_from_T)

    T_rankine = T_vals + 459.67
    t_hours_T = 10 ** ((P_from_T * 1000 / T_rankine) - 20)
    t_hours_T = np.minimum(t_hours_T, 200000)
    t_years_T = t_hours_T / (24 * 365)
    status_T = np.where(t_years_T >= 5, "SAFE", "REPLACE")

    # === PATH 2: From Stress ===
    P_from_S = cs_StressToP(Stress_vals)
    T_ref = st.number_input(
        "Enter reference temperature (°F) for stress-based life (default 950):",
        min_value=0.0, step=1.0, value=950.0
    )
    T_ref_R = T_ref + 459.67

    t_hours_S = 10 ** ((P_from_S * 1000 / T_ref_R) - 20)
    t_hours_S = np.minimum(t_hours_S, 200000)
    t_years_S = t_hours_S / (24 * 365)
    status_S = np.where(t_years_S >= 5, "SAFE", "REPLACE")

    # === OUTPUT TABLE ===
    df_out = pd.DataFrame({
        "Temperature (°F)": T_vals,
        "P from T": P_from_T,
        "Life from T (hours, max 200000)": t_hours_T,
        "Life from T (years)": t_years_T,
        "Input Stress (ksi)": Stress_vals,
        "P from Stress": P_from_S,
        "Life from Stress (hours, max 200000)": t_hours_S,
        "Life from Stress (years)": t_years_S
    })

    st.success("✅ Dual calculation completed successfully!")
    st.dataframe(df_out)

    # === DOWNLOAD EXCEL ===
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='Dual_Result')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Result",
        data=output,
        file_name="LMP_Temperature_Stress_Comparison_Mean2.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("📂 Please upload an Excel file with Stress (col 1) and Temperature (col 2).")
