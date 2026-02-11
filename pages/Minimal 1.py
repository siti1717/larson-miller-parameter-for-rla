import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline
from io import BytesIO

st.title("Larson–Miller Parameter - Minimal 1¼ Cr - ½ Mo Steel")

st.markdown("""
This tool calculates **creep remaining life** using two independent methods:

1️⃣ **From Temperature (°F):**  
Temperature → Stress → P → Remaining Life  

2️⃣ **From Stress (ksi):**  
Stress → P → Remaining Life  

All life predictions are capped at **200,000 hours**.
""")

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader(
    "Upload Excel file (Column 1 = Stress (ksi), Column 2 = Temperature (°F))",
    type=["xlsx", "xls"]
)

# =========================================================
# SPLINE 1: Temperature → Stress
# =========================================================
x2 = np.array([
42
