import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.set_page_config(page_title="Larson–Miller Dual Spline Calculator", layout="wide")

st.title("Larson–Miller Parameter - 1¼ Cr - ½ Mo Steel")
st.subheader("Dual Spline Mode: Temperature → P and Stress → P")

st.markdown("""
This tool calculates **Larson–Miller Parameter (P)** and **predicted life** using:
1. **Temperature-based spline** (input temperature manually)
2. **Stress-based spline** (upload Excel stress data)

---
""")

# === SPLINE TEMPERATURE DATA ===
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
cs_TtoStress = CubicSpline(x2, y2, extrapolate=True)

# === SPLINE STRESS DATA ===
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

# === INPUT: TEMPERATURE SECTION ===
st.header("1️⃣ Temperature-based Calculation")
T_input = st.number_input("Enter operating temperature (°F):", min_value=0.0, step=1.0)

if T_input > 0:
    Stress_from_T = cs_TtoStress(T_input)
    P_from_T = cs_StressToP(Stress_from_T)

    T_rankine = T_input + 459.67
    t_hours_T = 10 ** ((P_from_T * 1000 / T_rankine) - 20)
    t_years_T = t_hours_T / (24 * 365)

    df_temp = pd.DataFrame({
        "Temperature (°F)": [T_input],
        "Stress (ksi)": [Stress_from_T],
        "P (from Temp)": [P_from_T],
        "Predicted Life (hours)": [t_hours_T],
        "Predicted Life (years)": [t_years_T]
    })

    st.success("✅ Temperature-based interpolation completed!")
    st.dataframe(df_temp)

# === INPUT: STRESS SECTION ===
st.header("2️⃣ Stress-based Calculation (Upload Excel)")

uploaded_file = st.file_uploader(
    label="Upload an Excel file (first column = Stress (ksi))",
    help="The file should contain only one column with stress values in ksi.",
    type=["xlsx", "xls"]
)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    Stress_vals = df.iloc[:, 0].dropna().to_numpy()
    P_vals = cs_StressToP(Stress_vals)

    # Default: use T_input if available
    if T_input > 0:
        T_rankine = T_input + 459.67
    else:
        T_rankine = 1000  # default assumption if not input

    t_hours = 10 ** ((P_vals * 1000 / T_rankine) - 20)
    t_years = t_hours / (24 * 365)

    df_stress = pd.DataFrame({
        "Stress (ksi)": Stress_vals,
        "Temperature (°F)": [T_input if T_input > 0 else np.nan] * len(Stress_vals),
        "P (from Stress)": P_vals,
        "Predicted Life (hours)": t_hours,
        "Predicted Life (years)": t_years
    })

    st.success("✅ Stress-based interpolation completed!")
    st.dataframe(df_stress)

    # --- DOWNLOAD BOTH RESULTS ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if T_input > 0:
            df_temp.to_excel(writer, index=False, sheet_name='From_Temperature')
        df_stress.to_excel(writer, index=False, sheet_name='From_Stress')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Results (Both Methods)",
        data=output,
        file_name="LMP_DualSpline_Results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
