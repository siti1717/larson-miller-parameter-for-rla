import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter – Constant Stress Method (RLA Boiler)")

st.markdown("""
### 🔧 Method
- Stress dihitung dari **tekanan operasi (konstan)**
- Temperatur bervariasi (dari oxide / operasi)
- Remaining life **harus menurun monoton** terhadap temperatur
""")

# ===============================
# INPUT GEOMETRI & TEKANAN
# ===============================
P_bar = st.number_input("Operating pressure (bar)", value=66.0)
OD_mm = st.number_input("Outer diameter tube (mm)", value=50.8)
t_mm = st.number_input("Metal thickness (mm)", value=4.4)

# Konversi satuan
P = P_bar * 1e5        # bar → Pa
OD = OD_mm / 1000      # mm → m
t = t_mm / 1000        # mm → m

# Hoop stress
stress_Pa = (P * OD) / (2 * t)
stress_ksi = stress_Pa / 6.895e6

st.success(f"✅ Constant hoop stress = {stress_ksi:.2f} ksi")

# ===============================
# SPLINE: Stress → LMP
# ===============================
stress_data = np.array([
    48.61, 46.85, 44.77, 42.43, 39.84, 37.95, 36.65, 33.95,
    31.24, 27.81, 25.05, 21.90, 19.72, 18.23, 16.83, 15.52,
    14.46, 13.28, 12.24, 11.22, 9.99, 9.29, 8.60, 7.93,
    7.27, 6.72, 5.95, 5.74
])

P_data = np.array([
    30.31, 30.69, 31.07, 31.45, 31.83, 32.12, 32.26, 32.62,
    32.94, 33.27, 33.53, 33.80, 34.03, 34.17, 34.46, 34.72,
    34.86, 35.16, 35.32, 35.62, 35.87, 36.10, 36.42, 36.74,
    37.09, 37.45, 37.83, 38.09
])

cs_StressToP = CubicSpline(stress_data[::-1], P_data[::-1], extrapolate=True)

P_const = cs_StressToP(stress_ksi)

st.info(f"LMP (P) from constant stress = {P_const:.3f}")

# ===============================
# UPLOAD TEMPERATURE DATA
# ===============================
uploaded_file = st.file_uploader(
    "Upload Excel file (Temperature in °F, column A)",
    type=["xlsx", "xls"]
)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    T_F = df.iloc[:, 0].dropna().to_numpy()

    T_R = T_F + 459.67

    # Larson–Miller life
    life_hours = 10 ** ((P_const * 1000 / T_R) - 20)
    life_hours = np.minimum(life_hours, 200000)
    life_years = life_hours / (24 * 365)

    df_out = pd.DataFrame({
        "Temperature (°F)": T_F,
        "Constant Stress (ksi)": stress_ksi,
        "LMP (P)": P_const,
        "Remaining Life (hours)": life_hours,
        "Remaining Life (years)": life_years
    })

    st.success("✅ Remaining life calculated using CONSTANT STRESS method")
    st.dataframe(df_out)

    # Download
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_out.to_excel(writer, index=False)

    st.download_button(
        "📥 Download Result",
        output.getvalue(),
        file_name="RLA_Constant_Stress.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("Upload temperature data to proceed.")
