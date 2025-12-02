import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - 1¼ Cr - ½ Mo Steel (T & t input dari interface)")

uploaded_file = st.file_uploader(
    label="Upload Excel data spline (x1, y1 untuk T→Stress)",
    help="File Excel berisi dua kolom: x2 (Temperature °F) dan y2 (Stress ksi)",
    type=["xlsx", "xls"]
)

T_input = st.text_input("Masukkan nilai temperatur (°F), contoh: 900, 950, 1000:")
t_years_input = st.number_input("Masukkan waktu operasi (tahun):", min_value=0.0, step=0.1)

if uploaded_file and T_input and t_years_input > 0:
    # === BACA DATA SPLINE ===
    df = pd.read_excel(uploaded_file)
    x1 = np.array([30.31,30.69,31.07,31.45,31.83,32.12,32.26,32.62,32.94,33.27,33.53,33.80,34.03,34.17,34.46,34.72,34.86,35.16,35.32,35.62,35.87,36.10,36.42,36.74,37.09,37.45,37.83,38.09]) 
    y1 = np.array([48.61,46.85,44.77,42.43,39.84,37.95,36.65,33.95,31.24,27.81,25.05,21.90,19.72,18.23,16.83,15.52,14.46,13.28,12.24,11.22,9.99,9.29,8.60,7.93,7.27,6.72,5.95,5.74])
    cs_TtoStress = CubicSpline(x2, y2, extrapolate=True)

    # === KONVERSI INPUT ===
    T_values = np.array([float(x.strip()) for x in T_input.split(",")])
    t_hours = t_years_input * 24 * 365

    # === HITUNG STRESS ===
    Stress_vals = cs_TtoStress(T_values)

    # === HITUNG P MENGGUNAKAN LMP ===
    # P = T (20 + log10(t)) × 10^-3
    P_vals = (T_values + 459.67) * (20 + np.log10(t_hours)) * 1e-3

    # === OUTPUT DATA ===
    df_out = pd.DataFrame({
        "Temperature (°F)": T_values,
        "Stress (ksi)": Stress_vals,
        "t_input (tahun)": [t_years_input]*len(T_values),
        "t_input (jam)": [t_hours]*len(T_values),
        "P": P_vals
    })

    st.success("✅ Perhitungan selesai!")
    st.dataframe(df_out)

    # --- DOWNLOAD EXCEL ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='Hasil_LMP')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Hasil",
        data=output,
        file_name="LMP_Calculator_1_4Cr_1_2Mo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif not uploaded_file:
    st.warning("📂 Upload dulu file spline (T→Stress).")
elif not T_input:
    st.info("✏️ Masukkan temperatur (°F).")
elif t_years_input == 0:
    st.info("⏱️ Masukkan waktu operasi (tahun).")


