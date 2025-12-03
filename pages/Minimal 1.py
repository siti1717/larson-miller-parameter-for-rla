import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - 1¼ Cr - ½ Mo Steel (Temperature → Stress → P → Life)")

st.markdown("""
This app calculates **creep remaining life** using two interpolation splines:
1. **Temperature spline:** Temperature → Stress  
2. **Stress spline:** Stress → Larson–Miller Parameter (P)  

📘 Notes:
- Temperature values are read from the **second column** of the uploaded Excel file.  
- Results are limited to **200,000 hours** maximum.
""")

# === Upload Excel File ===
uploaded_temp = st.file_uploader(
    label="Upload Temperature Excel file (Temperature °F in 2nd column):",
    type=["xlsx", "xls"]
)

# === Spline Data ===
# Spline 1: Temperature → Stress
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
sort_idx = np.argsort(x2)
x2_sorted = x2[sort_idx]
y2_sorted = y2[sort_idx]
cs_TtoStress = CubicSpline(x2_sorted, y2_sorted, extrapolate=True)

# Spline 2: Stress → P
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

# === Processing ===
if uploaded_temp:
    df_T = pd.read_excel(uploaded_temp)
    T_vals = df_T.iloc[:, 1].dropna().to_numpy()

    # === Step 1: Temperature → Stress ===
    Stress_from_T = cs_TtoStress(T_vals)

    # === Step 2: Stress → P ===
    P_from_T = cs_StressToP(Stress_from_T)

    # === Step 3: P → Life ===
    T_rankine = T_vals + 459.67
    t_hours = 10 ** ((P_from_T * 1000 / T_rankine) - 20)
    t_hours = np.minimum(t_hours, 200000)
    t_years = t_hours / (24 * 365)

    # === Step 4: Status SAFE / REPLACE ===
    status = np.where(t_years >= 5, "SAFE", "REPLACE")

    # === Output Table ===
    df_out = pd.DataFrame({
        "Temperature (°F)": T_vals,
        "Stress from T (ksi)": Stress_from_T,
        "Larson–Miller Parameter (P)": P_from_T,
        "Predicted Life (hours, max 200000)": t_hours,
        "Predicted Life (years)": t_years,
        "Status": status
    })

    st.success("✅ Calculation completed successfully using Temperature → Stress → P path!")
    st.dataframe(df_out)

    # === Download Excel ===
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='T_Stress_P_Life')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Result",
        data=output,
        file_name="LMP_Temp_to_Stress_to_P.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("📂 Please upload the Temperature Excel file (values in 2nd column).")
