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
    x1 = np.array(df.iloc[0, 0::4].dropna())  # kolom 1, 5, 9, dst (P)
    y1 = np.array(df.iloc[0, 1::4].dropna())  # kolom 2, 6, 10, dst (Stress)
    x2 = np.array(df.iloc[0, 2::4].dropna())  # kolom 3, 7, 11, dst (T)
    y2 = np.array(df.iloc[0, 3::4].dropna())  # kolom 4, 8, 12, dst (Stress)

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
