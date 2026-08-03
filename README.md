

# ⚡ Photonic Directional & Ring Coupler Solver

A comprehensive 2D Semi-Vectorial Finite Difference (SVFD) mode solver and coupled-mode theory analysis framework for integrated photonics. Built with **Python** and deployed as an interactive web dashboard via **Streamlit Cloud**.

Supports core waveguide designs in **Silicon ($\text{Si}$)**, **Stoichiometric Silicon Nitride ($\text{Si}_3\text{N}_4$)**, **Low-Stress Silicon Nitride ($\text{SiN}$)**, and **Alumina ($\text{Al}_2\text{O}_3$)** over a Thermal Oxide ($\text{SiO}_2$) cladding.

---

## 🌟 Key Features

* **Multi-Material Support:** Dynamic dispersion calculations using Sellmeier and Cauchy optical models for $\text{Si}_3\text{N}_4$, $\text{SiN}$, $\text{Al}_2\text{O}_3$, and $\text{Si}$.
* **2D SVFD Mode Solver:** Full cross-sectional modal analysis calculating symmetric (even) and antisymmetric (odd) supermodes ($E_x$ and $E_y$ polarizations).
* **Coupled Mode Theory (CMT):** Computes wavelength-dependent coupling coefficients ($\kappa$), residual coupling length ($L_{\text{res}}$), and power transfer ratios ($P_{\text{cross}}$ / $P_{\text{bar}}$).
* **Ring Resonator Analysis:** Critical coupling evaluation, loaded quality factors ($Q_L$), and round-trip loss estimates.
* **Interactive Preview Gallery:** Auto-looping dynamic slideshow displaying input refractive index profile and output field distributions before running simulations.
* **Real-time Progress Tracker:** Live wavelength computation counter and percentage progress indicator.
* **Automated PDF & CSV Export:** Generates multi-page comprehensive PDF summary reports with styled data tables and embedded high-resolution plots, alongside raw CSV data export.

---

## 🔬 Mathematical Framework & Numerical Methods

### 1. 2D Semi-Vectorial Wave Equation (SVFD Solver)

The fundamental quasi-TE mode ($E_x$) is solved using the semi-vectorial wave equation derived from Maxwell's equations:

$$\frac{\partial}{\partial x} \left[ \frac{1}{n^2(x,y)} \frac{\partial (n^2 E_x)}{\partial x} \right] + \frac{\partial^2 E_x}{\partial y^2} + k_0^2 n^2(x,y) E_x = \beta^2 E_x$$

where $k_0 = \frac{2\pi}{\lambda}$, $\beta = k_0 n_{\text{eff}}$ is the propagation constant, and $n(x,y)$ is the 2D spatial refractive index distribution.

Discretizing this equation using standard 5-point finite differences yields a sparse matrix eigenvalue problem:

$$\mathbf{A} \mathbf{\Phi} = \beta^2 \mathbf{\Phi}$$

Solving for the two largest real eigenvalues yields the effective indices of the symmetric supermode ($n_{\text{eff, even}}$) and antisymmetric supermode ($n_{\text{eff, odd}}$).

---

### 2. Coupled Mode Theory (CMT) & Power Dynamics

The coupling coefficient $\kappa(\lambda)$ between the two symmetric coupled waveguides is calculated directly from the supermode index splitting:

$$\kappa(\lambda) = \frac{\pi}{\lambda} \left( n_{\text{eff, even}}(\lambda) - n_{\text{eff, odd}}(\lambda) \right)$$

For a directional coupler of straight length $L$ and ring radius $R$, the effective interaction length includes the residual coupling from the curved bend sections $L_{\text{res}}$:

$$L_{\text{res}}(\lambda) = \sqrt{\frac{\pi R}{\gamma(\lambda)}}, \quad \text{where } \gamma(\lambda) = k_0 \sqrt{n_{\text{avg}}^2 - n_{\text{clad}}^2}$$

$$L_{\text{total}}(\lambda) = L + L_{\text{res}}(\lambda)$$

The power transfer to the cross port ($P_{\text{cross}}$) and bar port ($P_{\text{bar}}$) is given by:

$$P_{\text{cross}}(\lambda) = \sin^2\left( \kappa(\lambda) \cdot L_{\text{total}}(\lambda) \right) \times 100\%$$

$$P_{\text{bar}}(\lambda) = \cos^2\left( \kappa(\lambda) \cdot L_{\text{total}}(\lambda) \right) \times 100\%$$

---

### 3. Material Dispersion Models

#### Stoichiometric $\text{Si}_3\text{N}_4$ & Low-Stress $\text{SiN}$ (Cauchy Models)

$$n(\lambda) = A + \frac{B}{\lambda^2}$$

* **Stoichiometric $\text{Si}_3\text{N}_4$:** $A = 1.9818$, $B = 0.014077\ \mu\text{m}^2$
* **Low-Stress $\text{SiN}$:** $A = 2.0870$, $B = 0.031091\ \mu\text{m}^2$

#### Alumina Core ($\text{Al}_2\text{O}_3$) (ALUVIA PDK Sellmeier Model)

$$n(\lambda) = \sqrt{\varepsilon_{\infty} + \frac{A \cdot \lambda^2}{\lambda^2 - E^2} - P \cdot \lambda^2}$$

* Parameters: $\varepsilon_{\infty} = 1.0$, $A = 1.912$, $E = 0.09566\ \mu\text{m}$, $P = 0.00306\ \mu\text{m}^{-2}$

#### Crystalline Silicon ($\text{Si}$) (Malitson Sellmeier Model)

$$n^2(\lambda) = 1 + \frac{A_1 \lambda^2}{\lambda^2 - B_1^2} + \frac{A_2 \lambda^2}{\lambda^2 - B_2^2} + \frac{A_3 \lambda^2}{\lambda^2 - B_3^2}$$

#### Cladding ($\text{SiO}_2$) (Thermal Silica Sellmeier Model)

$$n^2(\lambda) = 1 + \sum_{i=1}^{3} \frac{B_i \lambda^2}{\lambda^2 - C_i}$$

---

## 📸 Output Gallery Preview

The solver computes and displays:

1. **Input - Refractive Index Profile** ($n$)
2. **Output 1 - Symmetric (Even) Mode Profile**
3. **Output 2 - Antisymmetric (Odd) Mode Profile**
4. **Output 3 - 1D Core-Center Field Distributions**
5. **Output 4 - Supermode Dispersion Curves** ($n_{\text{eff}}$ vs. $\lambda$)
6. **Output 5 - Coupling Coefficient ($\kappa$) & Residual Length ($L_{\text{res}}$)**
7. **Output 6 - Power Transfer Spectrum ($P_{\text{cross}}$ / $P_{\text{bar}}$)**
8. **Output 7 - Ring Coupling vs. Loss & Loaded $Q_L$**

---

## 📁 Repository Structure

```text
├── app.py                      # Streamlit UI dashboard, progress tracking & PDF engine
├── coupler_engine.py           # SVFD solver, material dispersion models & CMT calculations
├── requirements.txt            # Python dependencies (Streamlit, SciPy, Matplotlib, ReportLab, etc.)
├── README.md                   # Project documentation
├── index_profile.png           # Preview image for main page gallery
├── even_mode.png               # Preview image for main page gallery
├── odd_mode.png                # Preview image for main page gallery
├── 1d_profiles.png             # Preview image for main page gallery
├── dispersion.png              # Preview image for main page gallery
└── ring_loss_QL.png            # Preview image for main page gallery

```

---

## 🚀 Local Installation & Running

To run the application locally on your machine:

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/multi_material_coupler_simulator.git
cd multi_material_coupler_simulator

```


2. **Install required dependencies:**
```bash
pip install -r requirements.txt

```


3. **Launch the Streamlit app:**
```bash
streamlit run app.py

```


4. Open your browser at `http://localhost:8501`.

---


