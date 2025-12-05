import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - Mean 2¼ Cr - 1 Mo Steel (Temperature & Stress Comparison)")

st.markdown("""
This tool calculates **creep remaining life** for **2¼ Cr - 1 Mo Steel**  
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
x2 = np.array([647.9948773792842, 723.1762057394435, 767.7412437945786, 809.5734512770026, 820.3246865450068, 831.0751422366335, 841.8220898345618, 852.5797566076797, 863.314279707093, 874.0741390387722, 884.8184880487759, 895.5568278242035, 901.9223125634308, 904.9974972722604, 914.9440278341881, 924.7728585297236, 932.4328960989432, 941.6996107968649, 952.0688741899924, 960.2459993150579, 968.4735920585147, 977.3490247357526, 986.4627180599721, 995.9402343004808, 1005.9652224270133, 1016.5522307370725, 1026.961228491988, 1038.0201588619204, 1048.597011036386, 1059.1324140437314, 1068.682680067022, 1078.2184193763296, 1087.773057067658, 1095.3089545235812, 1104.3389237811339])
y2 = np.array([41.16899268277241, 39.261109251906184, 38.480996915729776, 35.946722814875685, 34.23103112345649, 32.50177480307025, 30.71147765233225, 29.107694149891266, 27.101210724990835, 25.53557774151969, 23.700065160891512, 21.759991898642298, 20.96336228796936, 20.29096598073388, 19.641462021324717, 18.805833754346338, 18.284365805818894, 17.391518981907993, 16.678037555775376, 15.969621258114223, 15.309751835304844, 14.373433583959894, 13.450919789592561, 12.293678381160149, 11.225373903472295, 10.443970554220058, 9.732950759926492, 9.233424903288459, 8.814286048999925, 8.279089526775813, 7.845921348510359, 7.372078371094304, 6.951150863335236, 6.598574495068583, 6.138781322394376])
sort_idx = np.argsort(x2)
x2_sorted = x2[sort_idx]
y2_sorted = y2[sort_idx]
cs_TtoStress = CubicSpline(x2_sorted, y2_sorted, extrapolate=True)

# === SPLINE 2: Stress → P ===
x1 = np.array([39.88825817532335, 39.68376513382161, 39.46675925723602, 39.2402144882997, 39.0706179008769, 38.853062609208024, 38.60977469932019, 38.37980206274372, 38.14960223946269, 37.996096237690196, 37.76354432971555, 37.530836213571654, 37.2859225591119, 37.103488019921926, 36.87073752358008, 36.65081634086327, 36.40778461917052, 36.15385973465942, 35.9768803936525, 35.73189920132813, 35.567891387190755, 35.312646181834495, 35.056064571773284, 34.819218919158345, 34.5701261714958, 34.36016131159488, 33.945401279561196, 33.797114803435285, 33.526170778043834, 33.255321378754914, 32.98384031950884, 32.712927016877956, 32.44144227090062, 32.17051053461339, 31.973166691145003, 31.746424447439274, 31.46930241626292, 31.19148946433794, 30.914631239265606])
y1 = np.array([4.9361487281789955, 5.3252093574953925, 5.768064077245143, 6.115111271519403, 6.528899317101139, 6.911318377689668, 7.323561333506579, 7.770278403916638, 8.192004936824187, 8.822615770680642, 9.253059397074917, 9.665539084004912, 10.104587814268445, 10.825060573428459, 11.640272501761267, 12.54581466453859, 13.093980154991051, 13.982461317566994, 14.831740476510973, 15.489004240139991, 16.16265691839456, 16.980873481075392, 17.72954338104425, 18.615961874980584, 19.154908530918085, 20.063082024988066, 22.624365734752757, 23.281525583162235, 25.117333417751283, 27.018433263085534, 28.483687737990792, 30.34069427736724, 31.80340490769801, 33.64769222420202, 34.856624074363594, 36.26785213592496, 37.99766644657701, 39.261109251906184, 41.16899268277241])
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

