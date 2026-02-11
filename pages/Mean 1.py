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
x2 = np.array([435.471080531951,544.2288553510618,652.7828024367839,722.073779084554,799.8798773741471,813.6776099967445,826.7775693035835,840.5590406430772,852.9318472503944,865.3007995267072,876.9911986058792,887.4464488956502,894.3859542859288,927.5655089622055,938.5271349919278,949.4887610216501,960.4503870513723,972.7822163348098,983.0587407376745,991.9650618868237,998.7505934141816,1018.7497302662812,1033.034828017781,1048.0341806568556,1063.4620862284753,1078.74714082258,1089.460964136205])
y2 = np.array([65.82277489523892,61.66838491169956,56.82971610892781,54.45956541427073,49.107151023418766,46.37462249267522,43.665152129817436,40.698461122379975,37.588985801217035,34.424008113590254,31.558858301941456,28.531805273833655,26.911494252873553,19.36415263192078,18.11516610211266,16.652543032670856,15.477455934811498,14.121633909211717,12.949900134449337,12.208723858152055,10.93780539851059,9.354577552018089,8.674828439030058,7.99915926365912,7.3641186443299524,6.734037287576307,6.304345192531194])
sort_idx = np.argsort(x2)
x2_sorted = x2[sort_idx]
y2_sorted = y2[sort_idx]
cs_TtoStress = CubicSpline(x2_sorted, y2_sorted, extrapolate=True)

# === SPLINE 2: Stress → P ===
x1 = np.array([30.53330299071438,30.898331260138082,31.26258364405217,31.51106744421907,31.742796483302115,31.991160123305225,32.28652450090744,32.65249307479224,32.94806919615682,33.20866150518618,33.5035783361646,33.79851034286099,34.31891477218454,34.56132071297331,34.693231557595816,34.95825771324864,35.22328386890146,35.505978434931144,35.845211914166754,36.08940962955055,36.40744101633394,36.65479876160991,36.9728301483933,37.30852994555354,37.66189815309064,37.90925589836661,38.142700509840466,38.54191107943643,38.75966229921605])
y1 = np.array([64.39162137412214,60.15011392155821,55.1327209593789,51.841673256093785,48.96229267156458,46.91556795131846,44.331562933703424,41.44277783708765,38.714270463176184,36.18697788779759,33.08267499377246,29.987022258994337,24.487729529198248,21.665200971495672,19.443337977283658,18.12832674686997,16.910863750970066,15.694663993223127,14.261701755613068,12.9113139508677,11.642257246404967,10.62572567671539,9.717952900054964,9.066839258389383,8.419586491583924,8.039126721468985,7.68111832534807,7.026316328654328,6.713995943204868])
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
