import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.title("Larson–Miller Parameter - 2¼ Cr - 1 Mo Steel (Input Stress Excel, Temperatur Manual)")

uploaded_file = st.file_uploader(
    label="Upload Excel berisi 1 kolom (Stress ksi)",
    help="File hanya berisi satu kolom nilai stress dalam ksi.",
    type=["xlsx", "xls"]
)

T_input = st.number_input("Masukkan temperatur operasi (°F):", min_value=0.0, step=1.0)

if uploaded_file and T_input > 0:
    # === BACA DATA STRESS DARI EXCEL ===
    df = pd.read_excel(uploaded_file)
    Stress_vals = df.iloc[:, 0].dropna().to_numpy()

    # === ASUMSI EMPIRIS UNTUK MATERIAL 2¼ Cr - 1 Mo ===
    # Hubungan empiris: P ~ 40 - 0.15 * Stress
    P_vals = 40 - 0.15 * Stress_vals

    # === HITUNG UMUR CREEP ===
    T_rankine = T_input + 459.67
    t_hours = 10 ** ((P_vals * 1000 / T_rankine) - 20)
    t_years = t_hours / (24 * 365)

    # === OUTPUT TABEL ===
    df_out = pd.DataFrame({
        "Stress (ksi)": Stress_vals,
        "Temperature (°F)": [T_input] * len(Stress_vals),
        "P": P_vals,
        "t_prediksi (jam)": t_hours,
        "t_prediksi (tahun)": t_years
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
        file_name="LMP_InputStress_ManualT.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif not uploaded_file:
    st.warning("📂 Upload dulu file Excel berisi kolom stress (ksi).")
elif T_input == 0:
    st.info("✏️ Masukkan temperatur (°F) untuk mulai menghitung.")
