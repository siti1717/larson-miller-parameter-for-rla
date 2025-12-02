import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - Minimal 1¼ Cr - ½ Mo Steel (T → Stress, P)")

# Ubah type menjadi xlsx dan xls
uploaded_file = st.file_uploader(
    label="Upload an Excel file (second column = Temperature (°F))",
    help="Calculations in LMP use Rankine",
    type=["xlsx", "xls"]
)

if uploaded_file:
    # Baca Excel, otomatis baca sheet pertama
    df = pd.read_excel(uploaded_file)
    T_values = df.iloc[:, 1].to_numpy()  # membaca dari kolom kedua

    # === DATA SPLINE ===
    x1 = np.array([30.31,30.69,31.07,31.45,31.83,32.12,32.26,32.62,32.94,33.27,33.53,33.80,34.03,34.17,34.46,34.72,34.86,35.16,35.32,35.62,35.87,36.10,36.42,36.74,37.09,37.45,37.83,38.09])
    y1 = np.array([48.61,46.85,44.77,42.43,39.84,37.95,36.65,33.95,31.24,27.81,25.05,21.90,19.72,18.23,16.83,15.52,14.46,13.28,12.24,11.22,9.99,9.29,8.60,7.93,7.27,6.72,5.95,5.74])
    
    cs_TtoStress = CubicSpline(x2, y2, extrapolate=True)
    # Balik array sehingga x (y1 sebelumnya) meningkat
    y1_rev = y1[::-1]  # 3.79 → 35.95
    x1_rev = x1[::-1]  # urutannya ikut dibalik
    cs_StresstoP = CubicSpline(y1_rev, x1_rev, extrapolate=True)

    Stress_vals = 946,4
    P_vals = cs_StresstoP(Stress_vals)

    t_hours = 10 ** ((P_vals * 1000 / (T_values + 459.67)) - 20)
    t_years = t_hours / (24 * 365)

    df_out = pd.DataFrame({
        "Temperature (°F)": T_values,
        "Stress (ksi)": Stress_vals,
        "P": P_vals,
        "t_prediksi (jam)": t_hours,
        "t_prediksi (tahun)": t_years
    })

    st.success("✅ Calculation completed!")
    st.dataframe(df_out)

    # --- DOWNLOAD EXCEL ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='Mean2')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Result",
        data=output,
        file_name="LMP_Calculator_Minimal1.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


