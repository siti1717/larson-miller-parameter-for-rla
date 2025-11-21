import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - Mean 2¼ Cr - 1 Mo Steel (T → Stress, P)")

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
    x1 = np.array([ 30.662508800855083, 31.056214207546063, 31.449842277589227, 31.843423945643703, 32.267756129281054, 32.65379032418171, 33.03990039654814, 33.38612667022212, 33.77095795436528, 34.26570433243227, 34.64037527472527, 35.01437496327202, 35.37094578215902, 35.72685623200329, 36.250985768044586, 36.457060379707436, 36.744702479892354, 37.096752985301016, 37.43150027380854, 37.78360962387768, 38.06771890060796, 38.41519396463551, 38.76295312282654, 39.00004745812638, 39.14128245783074, 39.48776816967716, 39.81590516032247 ]) # P 
    y1 = np.array([ 35.95854533923345, 33.56977096155785, 31.120673998587414, 28.635383484440077, 26.01738328264409, 23.43557663202501, 20.914092566700766, 19.5262987012987, 18.346925133689833, 16.95707601222307, 15.90093277310924, 14.670263559969442, 13.597163865546221, 12.352368220015286, 10.588636363636361, 9.95987394957983, 9.12658421251124, 8.49052228486331, 7.845856823742153, 7.20185086692905, 6.635006914158065, 6.009467077970427, 5.346995000531855, 5.003723008190619, 4.7476771840811764, 4.250753131441254, 3.7946250198192466 ]) # Stress (ksi) 
    x2 = np.array([ 545.405572353056, 653.9883415579502, 762.549781547553, 808.4876843379607, 823.5477103312786, 838.5928310297592, 853.6394895761198, 862.5468819413431, 866.4920232747363, 881.490314623568, 893.0851877430509, 903.2625611281592, 918.0414640942442, 932.8253103280549, 946.9408102142831, 959.5695789314095, 969.2707653817099, 971.880987285952, 981.1416329532357, 996.139968399819, 1008.9974661273653, 1024.1058673411828, 1038.531513410888, 1052.941382767146, 1062.294952503441, 1081.042861333256, 1094.7410655861886, 1103.2065371603187 ]) # T 
    y2 = np.array([ 36.24045970924414, 33.894295324244965, 31.487799983951597, 29.222195168668783, 26.967733835716764, 24.409204488082047, 21.88204723720031, 20.71890190792564, 19.89815652480719, 18.726873831315615, 17.857725329514054, 17.174710545734705, 15.989477146176458, 14.838352293922881, 13.764713273604414, 12.748595573036233, 11.762172236171146, 11.503577543290618, 10.607533029519104, 10.079316398072603, 9.37803521869047, 8.041729603233701, 7.379917030103183, 6.992128496968409, 6.0820125518561845, 5.424157004573981, 5.015066026410565, 4.80]) # P

    cs_TtoStress = CubicSpline(x2, y2, extrapolate=True)
    # Balik array sehingga x (y1 sebelumnya) meningkat
    y1_rev = y1[::-1]  # 3.79 → 35.95
    x1_rev = x1[::-1]  # urutannya ikut dibalik
    cs_StresstoP = CubicSpline(y1_rev, x1_rev, extrapolate=True)

    Stress_vals = cs_TtoStress(T_values)
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
        file_name="LMP_Calculator_Minimal2.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
