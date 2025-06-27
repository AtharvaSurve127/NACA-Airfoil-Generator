# NACA 4-Digit Airfoil Generator

This project is a simple interactive web app for generating and visualizing NACA 4-digit airfoil shapes using Python, Streamlit, and Matplotlib.

## Features
- Interactive sliders to set airfoil parameters:
  - Thickness to Chord ratio (t/c)
  - Maximum Camber to Chord ratio (m/c)
  - Position of Maximum Camber (p/c)
  - Chord Length (c)
  - Number of points for plotting
- Real-time plotting of upper and lower airfoil surfaces and camber line
- Visualization updates instantly as you adjust parameters

## Requirements
- Python 3.7+
- [Streamlit](https://streamlit.io/)
- [Matplotlib](https://matplotlib.org/)
- [NumPy](https://numpy.org/)

## Installation
1. Clone or download this repository.
2. Install the required Python packages:
   ```sh
   pip install streamlit matplotlib numpy
   ```

## Usage
1. Open a terminal and navigate to the project directory:
   ```sh
   cd "D:/Projects/NACA Airfoil Generator"
   ```
2. Run the Streamlit app:
   ```sh
   streamlit run denklem.py
   ```
3. The app will open in your default web browser. Use the sidebar sliders to adjust airfoil parameters and see the updated plot.

## About NACA 4-Digit Airfoils
- The NACA 4-digit airfoil series is defined by four digits (e.g., NACA 2412):
  - 1st digit: Maximum camber as % of chord
  - 2nd digit: Position of maximum camber as tenths of chord
  - Last two digits: Maximum thickness as % of chord

## License
This project is for educational and research purposes. Feel free to use and modify it as needed. 
