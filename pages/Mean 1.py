import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter – Mean 1/4Cr–1/2Mo Steel (Dual Method)")

st.markdown("""
This tool calculates creep remaining life using two independent paths:

1️⃣ **From Temperature:**  
Temperature → Stress → P → Remaining Life  

2️⃣ **From Stress:**  
Stress → P → Remaining Life  

All predicted life values are capped at **200,000 hours**.
""")

# ===============================
# SPLINE 1: Temperature → Stress
# ===============================
T_data = np.array([
435.471080531951,544.2288553510618,652.7828024367839,722.073779084554,
799.8798773741471,813.6776099967445,826.7775693035835,840.5590406430772,
852.9318472503944,865.3007995267072,876.9911986058792,887.4464488956502,
894.3859542859288,927.5655089622055,938.5271349919278,949.4887610216501,
960.4503870513723,972.7822163348098,983.0587407376745,991.9650618868237,
998.7505934141816,1018.7497302662812,1033.034828017781,1048.0341806568556,
1063.4620862284753,1078.74714082258,1089.460964136205
])

Stress_from_T_data = np.array([
65.82277489523892,61.66838491169956,56.82971610892781,54.45956541427073,
49.107151023418766,46.37462249267522,43.665152129817436,40.698461122379975,
37.588985801217035,34.424008113590254,31.558858301941456,28.531805273833655,
26.911494252873553,19.36415263192078,18.11516610211266,16.652543032670856,
15.477455934811498,14.121633909211717,12.949900134449337,12.208723858152055,
10.93780539851059,9.354577552018089,8.674828439030058,7.99915926365912,
7.3641186443299524,6.734037287576307,6.304345192531194
])

cs_TtoStress = CubicSpline(T_data, Stress_from_T_data, extrapolate=True)

# ===============================
# SPLINE 2: Stress → P
# ===============================
Stress_data = np.array([
48.61,46.85,44.77,42.43,39.84,37.95,36.65,33.95,
31.24,27.81,25.05,21.90,19.72,18.23,16.83,15.52,
14.46,13.28,12.24,11.22,9.99,9.29,8.60,7.93,
7.27,6.72,5.95,5.74
])

P_data = np.array([
30.31,30.69,31.07,31.45,31.83,32.12,32.26,32.62,
32.94,33.27,33.53,33.80,34.03,34.17,34.46,34.72,
34.86,35.16,35.32,35.62,35.87,36.10,36.42,36.74,
37.09,37.45,37.83,38.09
])

cs_StressToP = CubicSpline(Stress_data[::-1], P_data[::-1], extrapolate=True)

# ===============================
# FILE UPLOAD
# ===============================
uploaded_file = st.file_uploader(
    "Upload Excel file (Column 1 = Stress (ksi), Column 2 = Temperature (°F))",
    type=["xlsx", "xls"]
)

T_ref = st.number_input("Reference temperature for stress-based life (°F)", value=950.0)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    Stress_vals = pd.to_numeric(df.iloc[:,0], errors='coerce').dropna().to_numpy()
    T_vals = pd.to_numeric(df.iloc[:,1], errors='coerce').dropna().to_numpy()

    # ===============================
    # PATH 1: From Temperature
    # ===============================
    Stress_from_T = cs_TtoStress(T_vals)
    P_from_T = cs_StressToP(Stress_from_T)

    T_rankine = T_vals + 459.67
    life_T_hours = 10 ** ((P_from_T * 1000 / T_rankine) - 20)
    life_T_hours = np.minimum(life_T_hours, 200000)
    life_T_years = life_T_hours / (24*365)

    # ===============================
    # PATH 2: From Stress
    # ===============================
    P_from_S = cs_StressToP(Stress_vals)

    T_ref_R = T_ref + 459.67
    life_S_hours = 10 ** ((P_from_S * 1000 / T_ref_R) - 20)
    life_S_hours = np.minimum(life_S_hours, 200000)
    life_S_years = life_S_hours / (24*365)

    # ===============================
    # OUTPUT TABLE
    # ===============================
    df_out = pd.DataFrame({
        "Temperature (°F)": T_vals,
        "P from T": P_from_T,
        "Life from T (hours)": life_T_hours,
        "Life from T (years)": life_T_years,
        "Input Stress (ksi)": Stress_vals,
        "P from Stress": P_from_S,
        "Life from Stress (hours)": life_S_hours,
        "Life from Stress (years)": life_S_years
    })

    st.success("✅ Dual calculation completed successfully!")
    st.dataframe(df_out)

    # DOWNLOAD
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_out.to_excel(writer, index=False)

    st.download_button(
        "📥 Download Excel Result",
        output.getvalue(),
        file_name="Larson_Miller_Dual_Method.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Upload file to begin calculation.")
