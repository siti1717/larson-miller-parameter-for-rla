import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - 1¼ Cr - ½ Mo Steel (Dual Spline: Temperature & Stress)")

st.markdown("""
This tool calculates **Larson–Miller Parameter (P)** using two separate spline correlations:
1. **Temperature-based spline**  
2. **Stress-based spline**  

Both datasets are uploaded independently via Excel files.
""")

# === Upload Temperature Excel ===
uploaded_temp = st.file_uploader(
    label="Upload an Excel file for Temperature (°F)",
    help="The file should contain one column with temperature values in °F.",
    type=["xlsx", "xls"]
)

# === Upload Stress Excel ===
uploaded_stress = st.file_uploader(
    label="Upload an Excel file for Stress (ksi)",
    help="The file should contain one column with stress values in ksi.",
    type=["xlsx", "xls"]
)

# --- SPLINE 1: Temperature → P (use your x2,y2 data) ---
x2 = np.array([
    427.00938639356104,533.863950267865,640.5369779181265,747.0870294166173,
    823.918728223842,838.4923750229345,851.7011434943004,862.9059831055836,
    873.4507112736203,883.9943351660085,890.7113744469356,901.9328678896384,
    912.8662277367607,923.7637366457648,934.6701443610918,945.5880591535613,
    956.5121110538397,966.0686107639804,993.3369408556557,1000.4932109968408,
    1013.3573406508535,1026.9211857081007,1041.1951754385966,1056.132344044696,
    1071.761748476545,1085.9573296785275
])
y2 = np.array([
    48.63221464134243,46.885451342721545,44.765242097498955,42.392053340062304,
    36.8987839319856,33.94161979261263,30.653268566954907,27.51896618447742,
    24.55398606811145,21.572441817017186,19.702561000201648,18.85089757519347,
    17.619057295741847,16.21513251332179,14.85392200125338,13.547945459467279,
    12.271427035165068,11.144654041406007,9.796949646778195,9.118862911165674,
    8.457933485957398,7.79618607878723,7.108590441621292,6.507864488808227,
    5.924271539996955,5.424856371263967
])
cs_TtoP = CubicSpline(x2, y2, extrapolate=True)

# --- SPLINE 2: Stress → P (use your x1,y1 data) ---
x1 = np.array([
    30.31,30.69,31.07,31.45,31.83,32.12,32.26,32.62,32.94,33.27,33.53,33.80,
    34.03,34.17,34.46,34.72,34.86,35.16,35.32,35.62,35.87,36.10,36.42,36.74,
    37.09,37.45,37.83,38.09
])
y1 = np.array([
    48.61,46.85,44.77,42.43,39.84,37.95,36.65,33.95,31.24,27.81,25.05,21.90,
    19.72,18.23,16.83,15.52,14.46,13.28,12.24,11.22,9.99,9.29,8.60,7.93,
    7.27,6.72,5.95,5.74
])
y1_rev = y1[::-1]
x1_rev = x1[::-1]
cs_StressToP = CubicSpline(y1_rev, x1_rev, extrapolate=True)

# === PROCESS BOTH FILES ===
if uploaded_temp and uploaded_stress:
    df_temp = pd.read_excel(uploaded_temp)
    df_stress = pd.read_excel(uploaded_stress)

    T_vals = df_temp.iloc[:, 0].dropna().to_numpy()
    Stress_vals = df_stress.iloc[:, 0].dropna().to_numpy()

    # Interpolate to get P
    P_from_T = cs_TtoP(T_vals)
    P_from_Stress = cs_StressToP(Stress_vals)

    # Combine both results
    df_out = pd.DataFrame({
        "Temperature (°F)": T_vals,
        "P (from Temperature Spline)": P_from_T,
        "Stress (ksi)": Stress_vals,
        "P (from Stress Spline)": P_from_Stress
    })

    st.success("✅ Calculations completed using both splines!")
    st.dataframe(df_out)

    # --- DOWNLOAD EXCEL RESULT ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='Dual_Spline_Result')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Result",
        data=output,
        file_name="LMP_Dual_Spline_Result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif not uploaded_temp:
    st.warning("📂 Please upload the Temperature Excel file.")
elif not uploaded_stress:
    st.warning("📂 Please upload the Stress Excel file.")
