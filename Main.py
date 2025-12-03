import streamlit as st

st.markdown("""
# 🧭 **User Guide – Larson–Miller Parameter Web Application**

---

## **1️⃣ Temperature Calculation (°R)**

### **Option A – Using Excel Input**
- Go to the **“Temperature Excel”** page.  
- Upload an Excel or CSV file containing **oxide thickness values (mm)**.  
- Enter the **exposure time (years)** in the input field.  
- The system will automatically:
  - Convert thickness from **mm → mils**.  
  - Convert time from **years → hours**.  
  - Calculate the **operating temperature (°R)** using the Larson–Miller oxidation equation:  
    \[
    T = \\frac{\\log(x \\times 39.37) + 7.1438}{2.1761\\times10^{-4}\\,(20 + \\log(t\\times8760))}
    \]
  - Display results in °R, °F, and °C.  
  - Allow you to **download the results as an Excel file**.

### **Option B – Manual Input on the Web**
- Go to the **“Temperature Manual”** page.  
- Enter **oxide thickness (mm)** and **exposure time (years)** manually.  
- The system performs the same conversion and calculation as above and displays results directly on screen.

---

## **2️⃣ Select Material Model**
From the **sidebar**, choose one of the following material models:

| Model Name | Material Type |
|-------------|----------------|
| **Mean 1** | 1¼ Cr – ½ Mo–Si Steel |
| **Mean 2** | 2¼ Cr – 1 Mo Steel |
| **Minimum 1** | 1¼ Cr – ½ Mo–Si Steel *(Minimum Curve)* |
| **Minimum 2** | 2¼ Cr – 1 Mo Steel *(Minimum Curve)* |

---

## **3️⃣ Upload Creep Data (Stress & Temperature)**
- Upload an Excel file containing:
  - **Column 1:** Stress values (ksi)  
  - **Column 2:** Operating temperature (°F)  
- The program will read both columns automatically.

---

## **4️⃣ Input Operating Temperature for Stress-based Calculation**
- Enter the **reference operating temperature (°F)** in the interface.  
- This temperature is used for calculating remaining life based on actual stress data.

---

## **5️⃣ Automatic Computations**
The system will automatically compute both methods:

| Path | Input | Interpolation & Computation | Output |
|------|--------|------------------------------|---------|
| **From Temperature** | Temperature (°F) | `T → Stress → P → Remaining Life` | Life (hours & years) |
| **From Stress** | Stress (ksi) | `Stress → P → Remaining Life` | Life (hours & years) |

---

## **6️⃣ Output Results**

| Column | Description |
|:--------|:-------------|
| **Temperature (°F)** | Operating temperature from input file |
| **P from T** | Larson–Miller Parameter derived from temperature spline |
| **Life from T (hours, max 200000)** | Predicted remaining life (capped at 200,000 hours) |
| **Life from T (years)** | Remaining life converted to years |
| **Input Stress (ksi)** | Actual stress values from file |
| **P from Stress** | Parameter from stress spline |
| **Life from Stress (hours, max 200000)** | Remaining life prediction from stress |
| **Life from Stress (years)** | Converted lifetime in years |

---

## **7️⃣ Download Results**
After computation, click **📥 Download Excel Result**  
to export all data (Temperature, Stress, P, and Life predictions) into an Excel report.

---


## **📘 Example Output**

| Temperature (°F) | P from T | Life (hours) | Life (years) | Stress (ksi) | P from Stress | Life (hours) | Life (years) | Status |
|-----------------:|----------:|--------------:|--------------:|---------------:|---------------:|---------------:|---------------:|
| 970.4 | 35.71 | 93,241 | 10,64 | 4.69 | 42.47 | 200,000 | 22.8 | 
| 970.4 | 35.71 | 93,241 | 10,64 | 4.92 | 40.92 | 200,000 | 22.8 | 
""")








