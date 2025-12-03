import streamlit as st
import numpy as np

st.title("Calculate Temperature (T) from Larson–Miller Equation")

st.markdown("""
Equation:
\[
\log x = -7.1438 + 2.1761 \times 10^{-4} \, T \, (20 + \log t)
\]
Where:
- **x** = stress (ksi)  
- **t** = time (hours)  
- **T** = temperature in °R (Rankine)
""")

# --- Input from user ---
x = st.number_input("Enter value of x (stress, ksi):", min_value=0.0, step=0.1)
t = st.number_input("Enter value of t (time, hours):", min_value=0.0, step=1.0)

if x > 0 and t > 0:
    # Calculate components
    logx = np.log10(x)
    logt = np.log10(t)
    
    numerator = logx + 7.1438
    denominator = 2.1761e-4 * (20 + logt)
    
    T_rankine = numerator / denominator
    T_fahrenheit = T_rankine - 459.67

    st.success("✅ Calculation completed!")
    st.write(f"**log x** = {logx:.5f}")
    st.write(f"**log t** = {logt:.5f}")
    st.write(f"**T (Rankine)** = {T_rankine:.2f} °R")
    st.write(f"**T (Fahrenheit)** = {T_fahrenheit:.2f} °F")

    # Optional: show explanation
    st.markdown(f"""
    ---
    **Computation steps:**
    - Numerator = log(x) + 7.1438 = {numerator:.4f}  
    - Denominator = 2.1761×10⁻⁴ × (20 + log t) = {denominator:.6f}  
    - T = Numerator / Denominator = {T_rankine:.2f} °R
    """)

else:
    st.info("✏️ Please enter positive values for both x and t to start calculation.")
