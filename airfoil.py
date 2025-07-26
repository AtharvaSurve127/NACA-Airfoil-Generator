import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

st.title("NACA Airfoil Generator")

# Sidebar Inputs
t_c = st.sidebar.slider("Thickness-to-Chord Ratio (t/c)", 0.01, 0.5, 0.12, 0.01)
m_c = st.sidebar.slider("Maximum Camber-to-Chord Ratio (m/c)", 0.0, 1.00, 0.04, 0.01)
p_c = st.sidebar.slider("Position of Maximum Camber (p/c)", 0.0, 0.9, 0.4, 0.1)
chord_length_mm = st.sidebar.number_input("Chord Length (mm)", min_value=10, max_value=5000, value=300, step=10)
c = chord_length_mm / 1000.0  # Convert to meters
n_points = st.sidebar.slider("Number of Points", 100, 400, 400, 10)
re = st.sidebar.slider("Reynold Number", 100000, 3000000, 500000, 10000)
mach = st.sidebar.slider("Mach Number", 0.1, 0.7, 0.5, 0.01)
alfa = st.sidebar.slider("Angle of Attack (°)", -5.0, 5.0, 1.0, 0.1)
invert_airfoil = st.sidebar.checkbox("Invert Airfoil (For Automotive Downforce)", value=False)

# Airfoil name
naca_name = f"{int(m_c*100)}{int(p_c*10)}{int(t_c*100)}"
st.sidebar.markdown(f"### NACA {naca_name}")

# Normalized x
x = np.linspace(0, 1, n_points)
x_c = x * c

# Thickness distribution (normalized)
y_t = (5 * t_c) * (0.2969 * np.sqrt(x) - 0.1260 * x -
                   0.3516 * x**2 + 0.2843 * x**3 -
                   0.1015 * x**4)

# Camber line (normalized)
y_camber = np.zeros_like(x)
if p_c != 0:
    for i in range(len(x)):
        if x[i] <= p_c:
            y_camber[i] = (m_c / (p_c**2)) * (2 * p_c * x[i] - x[i]**2)
        else:
            y_camber[i] = (m_c / ((1 - p_c)**2)) * ((1 - 2 * p_c) + 2 * p_c * x[i] - x[i]**2)

# Upper and lower surface (normalized)
y_upper = y_camber + y_t
y_lower = y_camber - y_t

# Invert airfoil
if invert_airfoil:
    y_upper = -y_upper
    y_lower = -y_lower
    y_camber = -y_camber

# Force trailing edge closure
x_upper = x[::-1]
x_lower = x[1:]
y_upper_fixed = y_upper[::-1]
y_lower_fixed = y_lower[1:]

# Close trailing edge
y_upper_fixed[0] = 0
y_lower_fixed[-1] = 0

# Combine
x_full = np.concatenate((x_upper, x_lower)) * c
y_full = np.concatenate((y_upper_fixed, y_lower_fixed)) * c

# Plotting
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x_full, y_full, label='Airfoil Surface', color='blue')
ax.plot(x * c, y_camber * c, label='Camber Line', color='green')
ax.axhline(0, color='black', lw=0.5, ls='--')
ax.axvline(0, color='black', lw=0.5, ls='--')
ax.set_title(f'NACA {naca_name} Airfoil{" (Inverted)" if invert_airfoil else ""}')
ax.set_xlabel('Chord Position (x)')
ax.set_ylabel('Thickness (y)')
ax.set_xlim(0, c)
ax.set_ylim(y_full.min() * 1.1, y_full.max() * 1.1)
ax.grid()
ax.legend()
ax.axis('equal')
st.pyplot(fig)

# Show preview
st.write("First 10 Airfoil Coordinates (x, y):")
st.dataframe(pd.DataFrame(np.column_stack((x_full, y_full))[:10], columns=["x (m)", "y (m)"]))

# Save .dat
with open('airfoil.dat', 'w') as f:
    for x_val, y_val in zip(x_full, y_full):
        f.write(f"{x_val:.10f} {y_val:.10f}\n")

# Download .dat
with open('airfoil.dat', 'rb') as f:
    st.download_button("Download .dat for XFOIL or CNC", data=f, file_name='airfoil.dat')

# Save .csv for SolidWorks (in mm)
airfoil_3d = np.column_stack((x_full * 1000, y_full * 1000, np.zeros_like(x_full)))  # mm export
df_export = pd.DataFrame(airfoil_3d)
df_export.to_csv('airfoil_solidworks.csv', index=False, header=False)

with open('airfoil_solidworks.csv', 'rb') as f:
    st.download_button("Download CSV for SolidWorks", data=f, file_name='airfoil_solidworks.csv')

# XFOIL + Lift/Drag Calculation
st.write("Calculate Aerodynamic Coefficients and Forces")
if st.button("Calculate"):

    if os.path.exists("polar_file.txt"):
        os.remove("polar_file.txt")

    with open("input_file.in", 'w') as input_file:
        input_file.write("LOAD airfoil.dat\n\n")
        input_file.write("PANE\n")
        input_file.write("OPER\n")
        input_file.write(f"Visc {re}\n")
        input_file.write(f"Mach {mach}\n")
        input_file.write("PACC\n")
        input_file.write("polar_file.txt\n\n")
        input_file.write("ITER 100\n")
        input_file.write(f"Alfa {alfa} \n\n")
        input_file.write("quit\n")

    subprocess.call("xfoil.exe < input_file.in", shell=True)

    try:
        with open('polar_file.txt', 'r') as file:
            for line in file:
                if '------' in line:
                    next_line = next(file)
                    values = next_line.split()
                    alpha = float(values[0])
                    CL = float(values[1])
                    CD = float(values[2])
                    CDp = float(values[3])
                    CM = float(values[4])
                    break

        # Physical constants
        mu = 1.81e-5     # air viscosity (kg/m·s)
        rho = 1.225      # air density (kg/m³)

        # Velocity from Reynolds number
        V = re * mu / (rho * c)

        # Assume unit span (2D section)
        span = 1.0
        S = c * span

        # Forces
        L = 0.5 * rho * V**2 * S * CL
        D = 0.5 * rho * V**2 * S * CD

        # Output
        st.write(f"**Velocity:** {V:.2f} m/s")
        st.write(f"**Lift Coefficient (Cl):** {CL}")
        st.write(f"**Drag Coefficient (Cd):** {CD}")
        st.write(f"**Moment Coefficient (Cm):** {CM}")
        st.write(f"**Lift-to-Drag Ratio (L/D):** {CL/CD:.2f}")
        st.write(f"**Lift Force (L):** {L:.2f} N")
        st.write(f"**Drag Force (D):** {D:.2f} N")

    except Exception as e:
        st.error("Failed to parse XFOIL output.")
        st.code(str(e))
