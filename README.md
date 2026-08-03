# ⚡ Photonic Directional & Ring Coupler Solver

A comprehensive 2D Semi-Vectorial Finite Difference (SVFD) mode solver and coupled-mode theory analysis framework for integrated photonics. Built with **Python** and deployed as an interactive web dashboard via **Streamlit Cloud**.

Supports core waveguide designs in **Silicon ($\text{Si}$)**, **Stoichiometric Silicon Nitride ($\text{Si}_3\text{N}_4$)**, **Low-Stress Silicon Nitride ($\text{SiN}$)**, and **Alumina ($\text{Al}_2\text{O}_3$)** over a Thermal Oxide ($\text{SiO}_2$) cladding.

---

## 🌟 Key Features

* **Multi-Material Support:** Dynamic dispersion calculations using Sellmeier and Cauchy optical models for:
  * Stoichiometric $\text{Si}_3\text{N}_4$
  * Low-Stress $\text{SiN}$
  * Alumina ($\text{Al}_2\text{O}_3$) (ALUVIA PDK model)
  * Crystalline Silicon ($\text{Si}$)
* **2D SVFD Mode Solver:** Full cross-sectional modal analysis calculating symmetric (even) and antisymmetric (odd) supermodes ($E_x$ and $E_y$ polarizations).
* **Coupled Mode Theory (CMT):** Computes wavelength-dependent coupling coefficients ($\kappa$), residual coupling length ($L_{\text{res}}$), and power transfer ratios ($P_{\text{cross}}$ / $P_{\text{bar}}$).
* **Ring Resonator Analysis:** Critical coupling evaluation, loaded quality factors ($Q_L$), and round-trip loss estimates.
* **Interactive Preview Gallery:** Auto-looping dynamic slideshow displaying input refractive index profile and output field distributions before running simulations.
* **Real-time Progress Tracker:** Live wavelength computation counter and percentage progress indicator.
* **Automated PDF & CSV Export:** Generates multi-page comprehensive PDF summary reports with styled data tables and embedded high-resolution plots, alongside raw CSV data export.

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
