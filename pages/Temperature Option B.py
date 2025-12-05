import streamlit as st
import numpy as np

st.title("Larson–Miller Temperature Calculator")

# --- Persamaan Utama  ---
st.latex(r"""
\log x = -7.1438 + 2.1761\times10^{-4}\,T\,(20 + \log t)
""")

# --- Teks Penjelasan Lanjutan  ---
st.markdown("""
Where:
- **x** = oxide thickness (in mils, converted automatically from mm)  
- **t** = exposure time (in hours, converted automatically from years)  
- **T** = temperature in °Rankine (°R)
---
**Formula used in this calculator:**
""")

# --- User Inputs ---
x_mm = st.number_input("Enter oxide thickness (mm):", min_value=0.0, step=0.01, format="%.4f")
t_years = st.number_input("Enter exposure time (years):", min_value=0.0, step=0.1, format="%.2f")

# --- Calculation ---
if x_mm > 0 and t_years > 0:
    # Convert units
    x_mils = x_mm * 39.3701     # mm → mils
    t_hours = t_years * 365 * 24  # years → hours

    # Compute
    logx = np.log10(x_mils)
    logt = np.log10(t_hours)
    numerator = logx + 7.1438
    denominator = 2.1761e-4 * (20 + logt)

    T_rankine = numerator / denominator
    T_fahrenheit = T_rankine - 459.67
    T_celsius = (T_fahrenheit - 32) * 5 / 9

    # Display results
    st.success("✅ Calculation completed!")
    st.markdown(f"""
    **Results:**
    - Oxide thickness (converted): `{x_mils:.4f}` mils  
    - log(x): `{logx:.5f}`  
    - log(t): `{logt:.5f}`  
    - **T (Rankine)** = `{T_rankine:.2f}` °R  
    - **T (Fahrenheit)** = `{T_fahrenheit:.2f}` °F  
    - **T (Celsius)** = `{T_celsius:.2f}` °C
    """)

    # Detailed explanation
    st.markdown("---")
    st.markdown(f"""
    **Computation steps:**
    1. Convert thickness: {x_mm} mm × 39.3701 = {x_mils:.4f} mils  
    2. Convert time: {t_years} years × 365 × 24 = {t_hours:.0f} hours  
    3. log(x) = {logx:.5f}  
    4. log(t) = {logt:.5f}  
    5. Numerator = log(x) + 7.1438 = {numerator:.4f}  
    6. Denominator = 2.1761×10⁻⁴ × (20 + log t) = {denominator:.6f}  
    7. **T = Numerator / Denominator = {T_rankine:.2f} °R = {T_fahrenheit:.2f} °F = {T_celsius:.2f} °C**
    """)

else:
    st.info("✏️ Please enter positive values for both thickness (mm) and exposure time (years).")
