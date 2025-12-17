import streamlit as st
import numpy as np
import pandas as pd
st.title("Larson–Miller Plot with Oxide-Based Temperature")

st.markdown("""
**Material:** 1¼ Cr – ½ Mo Steel  
**X-axis:** Larson–Miller Parameter (LMP)  
**Y-axis:** Hoop Stress (ksi)  
**Top axis:** Metal Temperature (°F) derived from oxide growth
""")

# ================= USER INPUT =================
st.sidebar.header("Input Parameters")

P_psi = st.sidebar.number_input("Internal pressure P (psi)", value=1800.0)
Di_in = st.sidebar.number_input("Inner diameter Di (inch)", value=2.0)
t_nom_mm = st.sidebar.number_input("Nominal thickness (mm)", value=5.5)

oxide_mm = st.sidebar.slider("Oxide thickness (mm)", 0.05, 1.00, 0.30)
exposure_years = st.sidebar.number_input("Exposure time (years)", value=20.0)

# ================= UNIT CONVERSION =================
t_nom_in = t_nom_mm / 25.4
t_oxide_in = oxide_mm / 25.4
t_eff = t_nom_in - t_oxide_in

# ================= HOOP STRESS =================
sigma_hoop = (P_psi * Di_in) / (2 * t_eff)  # psi
sigma_hoop_ksi = sigma_hoop / 1000

# ================= OXIDE-BASED TEMPERATURE =================
# Oxide growth equation (Rankine)
x_mils = oxide_mm * 39.37
t_hours = exposure_years * 8760

T_rankine = (
    (np.log10(x_mils) + 7.1438) /
    (2.1761e-4 * (20 + np.log10(t_hours)))
)

T_F = T_rankine - 459.67

# ================= LMP RANGE =================
log_tr = np.linspace(3, 5.3, 50)  # rupture time range
tr_hours = 10 ** log_tr

LMP = T_rankine * (20 + np.log10(tr_hours))

stress_curve = np.full_like(LMP, sigma_hoop_ksi)

# ================= PLOT =================
fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(LMP, stress_curve, linewidth=2)
ax.set_xlabel("Larson–Miller Parameter, LMP")
ax.set_ylabel("Hoop Stress (ksi)")
ax.grid(True)

# ===== TOP AXIS: TEMPERATURE =====
ax_top = ax.twiny()
ax_top.set_xlim(ax.get_xlim())
ax_top.set_xlabel("Metal Temperature (°F)")
ax_top.set_xticks([LMP.min(), LMP.mean(), LMP.max()])
ax_top.set_xticklabels([
    f"{T_F:.0f}",
    f"{T_F:.0f}",
    f"{T_F:.0f}"
])

st.pyplot(fig)

# ================= OUTPUT SUMMARY =================
st.markdown("### 🔎 Calculation Summary")

df_summary = pd.DataFrame({
    "Parameter": [
        "Oxide thickness (mm)",
        "Effective thickness (mm)",
        "Hoop stress (ksi)",
        "Metal temperature (°F)",
        "Exposure time (years)"
    ],
    "Value": [
        oxide_mm,
        t_eff * 25.4,
        sigma_hoop_ksi,
        T_F,
        exposure_years
    ]
})

st.table(df_summary)

