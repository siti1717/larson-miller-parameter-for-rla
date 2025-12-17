import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter with Oxide Effect (1¼ Cr – ½ Mo Steel)")

st.markdown("""
This tool calculates **creep remaining life** considering  
the **thermal effect of oxide layer** on metal temperature.

✔ Oxide increases thermal resistance  
✔ Metal temperature increases  
✔ Remaining life decreases (physically consistent)
""")

# ================= USER INPUT =================
st.sidebar.header("Oxide & Thermal Parameters")

oxide_thickness_mm = st.sidebar.number_input(
    "Oxide thickness (mm)",
    min_value=0.0, step=0.01, value=0.20
)

heat_flux = st.sidebar.number_input(
    "Heat flux q (W/m²)",
    min_value=1e3, step=1000.0, value=150000.0
)

k_oxide = st.sidebar.number_input(
    "Oxide thermal conductivity k (W/m·K)",
    min_value=0.1, step=0.1, value=2.0
)

# Convert units
oxide_thickness_m = oxide_thickness_mm / 1000.0

# ================= UPLOAD FILE =================
uploaded_file = st.file_uploader(
    "Upload Excel file (Stress [ksi] in col 1, Fluid Temperature [°F] in col 2)",
    type=["xlsx", "xls"]
)

# ================= SPLINES =================
# Temperature → Stress
x2 = np.array([
    427, 534, 641, 747, 824, 838, 852, 863, 873, 884,
    891, 902, 913, 924, 935, 946, 957, 966, 993,
    1000, 1013, 1027, 1041, 1056, 1072, 1086
])
y2 = np.array([
    48.6, 46.9, 44.8, 42.4, 36.9, 33.9, 30.7, 27.5,
    24.6, 21.6, 19.7, 18.9, 17.6, 16.2, 14.9, 13.5,
    12.3, 11.1, 9.8, 9.1, 8.5, 7.8, 7.1, 6.5, 5.9, 5.4
])
cs_TtoStress = CubicSpline(x2, y2, extrapolate=True)

# Stress → P
x1 = np.array([
    30.31,30.69,31.07,31.45,31.83,32.12,32.26,32.62,
    32.94,33.27,33.53,33.80,34.03,34.17,34.46,34.72,
    34.86,35.16,35.32,35.62,35.87,36.10,36.42,36.74,
    37.09,37.45,37.83,38.09
])
y1 = np.array([
    48.61,46.85,44.77,42.43,39.84,37.95,36.65,33.95,
    31.24,27.81,25.05,21.90,19.72,18.23,16.83,15.52,
    14.46,13.28,12.24,11.22,9.99,9.29,8.60,7.93,
    7.27,6.72,5.95,5.74
])
cs_StressToP = CubicSpline(y1[::-1], x1[::-1], extrapolate=True)

# ================= PROCESS =================
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    Stress_vals = df.iloc[:, 0].to_numpy()
    T_fluid_F = df.iloc[:, 1].to_numpy()

    # ===== OXIDE TEMPERATURE RISE =====
    deltaT_oxide_K = heat_flux * oxide_thickness_m / k_oxide
    deltaT_oxide_F = deltaT_oxide_K * 9 / 5

    T_metal_F = T_fluid_F + deltaT_oxide_F

    # ===== LMP CALCULATION =====
    Stress_from_T = cs_TtoStress(T_metal_F)
    P_vals = cs_StressToP(Stress_from_T)

    T_rankine = T_metal_F + 459.67
    t_hours = 10 ** ((P_vals * 1000 / T_rankine) - 20)
    t_hours = np.minimum(t_hours, 200000)
    t_years = t_hours / (24 * 365)

    status = np.where(t_years >= 5, "SAFE", "REPLACE")

    # ===== OUTPUT =====
    df_out = pd.DataFrame({
        "Fluid Temp (°F)": T_fluid_F,
        "Metal Temp (°F)": T_metal_F,
        "ΔT Oxide (°F)": deltaT_oxide_F,
        "Stress from T (ksi)": Stress_from_T,
        "LMP (P)": P_vals,
        "Remaining Life (hours)": t_hours,
        "Remaining Life (years)": t_years,
        "Status": status
    })

    st.success("✅ Oxide-aware creep calculation completed")
    st.dataframe(df_out)

    # ===== DOWNLOAD =====
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_out.to_excel(writer, index=False, sheet_name="Oxide_LMP")
    output.seek(0)

    st.download_button(
        "📥 Download Result",
        data=output,
        file_name="LMP_with_Oxide_Effect.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("📂 Upload Excel file to start calculation")
