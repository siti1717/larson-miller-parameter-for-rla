import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - 2¼ Cr - 1 Mo Steel (Input T Manual, Data dari Excel)")

uploaded_file = st.file_uploader(
    label="Upload Excel data spline (x1,y1,x2,y2 dalam 1 baris)",
    help="File Excel harus berisi 4 kolom: x1 (P), y1 (Stress1), x2 (Temperature °F), y2 (Stress2)",
    type=["xlsx", "xls"]
)

T_input = st.number_input("Masukkan temperatur operasi (°F):", min_value=0.0, step=1.0)

if uploaded_file and T_input > 0:
    # === BACA DATA ===
    df = pd.read_excel(uploaded_file, header=None)
    x1 = np.array([30.31,30.69,31.07,31.45,31.83,32.12,32.26,32.62,32.94,33.27,33.53,33.80,34.03,34.17,34.46,34.72,34.86,35.16,35.32,35.62,35.87,36.10,36.42,36.74,37.09,37.45,37.83,38.09]) 
    y1 = np.array([48.61,46.85,44.77,42.43,39.84,37.95,36.65,33.95,31.24,27.81,25.05,21.90,19.72,18.23,16.83,15.52,14.46,13.28,12.24,11.22,9.99,9.29,8.60,7.93,7.27,6.72,5.95,5.74])

    # === SPLINE INTERPOLATION ===
    cs_TtoStress = CubicSpline(x2, y2, extrapolate=True)
    y1_rev = y1[::-1]
    x1_rev = x1[::-1]
    cs_StresstoP = CubicSpline(y1_rev, x1_rev, extrapolate=True)

    # === PERHITUNGAN ===
    Stress_val = cs_TtoStress(T_input)
    P_val = cs_StresstoP(Stress_val)
    t_hours = 10 ** ((P_val * 1000 / (T_input + 459.67)) - 20)
    t_years = t_hours / (24 * 365)

    # === TABEL HASIL ===
    df_out = pd.DataFrame({
        "Keterangan": [
            "x (LMP spline P)",
            "Temperature (°F)",
            "Stress (ksi)",
            "P (LMP)",
            "t_prediksi (jam)",
            "t_prediksi (tahun)"
        ],
        "Nilai": [
            ", ".join(map(lambda v: f"{v:.3f}", x1)),
            f"{T_input:.2f}",
            f"{Stress_val:.3f}",
            f"{P_val:.3f}",
            f"{t_hours:.3e}",
            f"{t_years:.3f}"
        ]
    })

    st.success("✅ Perhitungan selesai!")
    st.dataframe(df_out)

    # --- DOWNLOAD EXCEL ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name='LMP_Result')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Hasil",
        data=output,
        file_name="LMP_SinglePoint_Calc.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif not uploaded_file:
    st.warning("📂 Upload dulu file Excel spline (x1,y1,x2,y2).")
elif T_input == 0:
    st.info("✏️ Masukkan temperatur (°F) untuk mulai menghitung.")

