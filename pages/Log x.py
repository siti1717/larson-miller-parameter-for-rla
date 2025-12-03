import streamlit as st
import numpy as np

st.title("Calculate Temperature (T) from Larson–Miller Equation")

st.markdown("""
Equation:
\[
\log x = -7.1438 + 2.1761 \times 10^{-4} \, T \, (20 + \log t)
\]

Where:
- **x** = oxide thickness (mm)  
- **t** = time (hours) — converted automatically from years  
- **T** = temperature in °R (Rankine)
""")

# --- Input from user ---
x = st.number_input("Enter oxide thickness (mm):", min_value=0.0, step=0.01)
t_years = st.number_input("Enter exposure time (years):", min_value=0.0, step=0.1)

if x > 0 and t_years > 0:
    # Convert years to hours
    t_hours = t_years * 365 * 24

    # Calculate components
    logx = np.log10(x)
    logt = np.log10(t_hours)
    
    numerator = logx + 7.1438
    denominator = 2.1761e-4 * (20 + logt)
    
    T_rankine = numerator / denominator
    T_fahrenheit = T_rankine - 459.67
    T_celsius = (T_fahrenheit - 32) * 5/9

    st.success("✅ Calculation completed!")
    st.write(f"**log x** = {logx:.5f}")
    st.write(f"**log t (hours)** = {logt:.5f}")
    st.write(f"**T (Rankine)** = {T_rankine:.2f} °R")
    st.write(f"**T (Fahrenheit)** = {T_fahrenheit:.2f} °F")
    st.write(f"**T (Celsius)** = {T_celsius:.2f} °C")

    # Optional: show explanation
    st.markdown(f"""
    ---
    **Computation steps:**
    - Convert time: {t_years} years × 365 × 24 = {t_hours:.0f} hours  
    - log(x) = {logx:.5f}  
    - log(t) = {logt:.5f}  
    - Numerator = log(x) + 7.1438 = {numerator:.4f}  
    - Denominator = 2.1761×10⁻⁴ × (20 + log t) = {denominator:.6f}  
    - T = Numerator / Denominator = {T_rankine:.2f} °R  
    - T = {T_fahrenheit:.2f} °F = {T_celsius:.2f} °C
    """)

else:
    st.info("✏️ Please enter positive values for both oxide thickness and exposure time to start calculation.")
