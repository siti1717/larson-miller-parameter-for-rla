import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - 1¼ Cr - ½ Mo Steel (T & t input dari interface)")

uploaded_file = st.file_uploader(
    label="Upload Excel data spline (x2, y2 untuk T→Stress)",
    help="File Excel berisi dua kolom: x2 (Temperature °F) dan y2 (Stress ksi)",
    type=["xlsx", "xls"]
)

T_input = st.text_input("Masukkan nilai temperatur (°F), contoh: 900, 950, 1000:")
t_years_input = st.number_input("Masukkan waktu operasi (tahun):", min_value=0.0, step=0.1)

if uploaded_file and T_input and t_years_input > 0:
    # === BACA DATA SPLINE ===
    df = pd.read_excel(uploaded_file)
    x2 = df.iloc[:, 0].to_numpy()
    y2 = df.iloc[:, 1].to_numpy()
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
