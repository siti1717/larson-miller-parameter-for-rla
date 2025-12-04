import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - Minimal 2¼ Cr - 1 Mo Steel (Temperature & Stress Comparison)")

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
x2 = np.array([
    545.405572353056, 653.9883415579502, 762.549781547553, 808.4876843379607, 823.5477103312786, 838.5928310297592, 853.6394895761198, 862.5468819413431, 866.4920232747363, 881.490314623568, 893.0851877430509, 903.2625611281592, 918.0414640942442, 932.8253103280549, 946.9408102142831, 959.5695789314095, 969.2707653817099, 971.880987285952, 981.1416329532357, 996.139968399819, 1008.9974661273653, 1024.1058673411828, 1038.531513410888, 1052.941382767146, 1062.294952503441, 1081.042861333256, 1094.7410655861886, 1103.2065371603187
])
y2 = np.array([ 36.24045970924414, 33.894295324244965, 31.487799983951597, 29.222195168668783, 26.967733835716764, 24.409204488082047, 21.88204723720031, 20.71890190792564, 19.89815652480719, 18.726873831315615, 17.857725329514054, 17.174710545734705, 15.989477146176458, 14.838352293922881, 13.764713273604414, 12.748595573036233, 11.762172236171146, 11.503577543290618, 10.607533029519104, 10.079316398072603, 9.37803521869047, 8.041729603233701, 7.379917030103183, 6.992128496968409, 6.0820125518561845, 5.424157004573981, 5.015066026410565, 4.80])
sort_idx = np.argsort(x2)
x2_sorted = x2[sort_idx]
y2_sorted = y2[sort_idx]
cs_TtoStress = CubicSpline(x2_sorted, y2_sorted, extrapolate=True)

# === SPLINE 2: Stress → P ===
x1 = np.array([ 30.662508800855083, 31.056214207546063, 31.449842277589227, 31.843423945643703, 32.267756129281054, 32.65379032418171, 33.03990039654814, 33.38612667022212, 33.77095795436528, 34.26570433243227, 34.64037527472527, 35.01437496327202, 35.37094578215902, 35.72685623200329, 36.250985768044586, 36.457060379707436, 36.744702479892354, 37.096752985301016, 37.43150027380854, 37.78360962387768, 38.06771890060796, 38.41519396463551, 38.76295312282654, 39.00004745812638, 39.14128245783074, 39.48776816967716, 39.81590516032247 ])
y1 = np.array([ 35.95854533923345, 33.56977096155785, 31.120673998587414, 28.635383484440077, 26.01738328264409, 23.43557663202501, 20.914092566700766, 19.5262987012987, 18.346925133689833, 16.95707601222307, 15.90093277310924, 14.670263559969442, 13.597163865546221, 12.352368220015286, 10.588636363636361, 9.95987394957983, 9.12658421251124, 8.49052228486331, 7.845856823742153, 7.20185086692905, 6.635006914158065, 6.009467077970427, 5.346995000531855, 5.003723008190619, 4.7476771840811764, 4.250753131441254, 3.7946250198192466 ]) 
y1_rev = y1[::-1]
x1_rev = x1[::-1]
cs_StressToP = CubicSpline(y1_rev, x1_rev, extrapolate=True)

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
        file_name="LMP_Temperature_Stress_Comparison_Minimal2.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("📂 Please upload an Excel file with Stress (col 1) and Temperature (col 2).")
