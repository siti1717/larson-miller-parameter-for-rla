import streamlit as st

st.set_page_config(page_title="Larson-Miller Parameter", layout="wide")

st.title("🔬 Larson–Miller Parameter – Remaining Life Assessment")

st.markdown("""
Welcome to the **Larson–Miller Parameter (LMP)** application — a computational tool for performing **Remaining Life Assessment (RLA)** of piping and high-temperature components based on creep rupture data.

This application utilizes the **Larson–Miller Parameter method** to estimate the **residual life** of Cr–Mo steel materials operating under elevated temperatures.

### ⚙️ How to Use
1. Go to the **Temperature** menu to calculate the **operating temperature (°R)** based on the input data.  
2. Upload an **Excel (.xlsx)** file containing the **thickness values (mm)**.  
3. Select the appropriate **material model** from the sidebar menu:
   - Mean 1 : 1¼ Cr – ½ Mo–Si Steel  
   - Mean 2 : 2¼ Cr – 1 Mo Steel  
   - Minimum 1 : 1¼ Cr – ½ Mo–Si Steel  
   - Minimum 2 : 2¼ Cr – 1 Mo Steel  
4. Upload an **Excel or CSV file** containing the required **temperature data**.  
5. Input or confirm the **service time (years)** as needed.  
6. The system will automatically compute:
   - Stress–Temperature relationship  
   - Larson–Miller Parameter value  
   - Predicted rupture time  
   - Estimated **remaining service life**

---

This tool supports engineers, inspectors, and researchers in evaluating **creep damage** and predicting **the remaining operational life** of components such as **piping systems, pressure vessels, and boilers** operating at high temperatures.
""")


