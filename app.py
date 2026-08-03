import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import time
import os
import base64
from coupler_engine import run_simulation

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

import streamlit.components.v1 as components

# --- GOOGLE ANALYTICS TRACKING ---
def inject_google_analytics(measurement_id):
    ga_code = f"""
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{measurement_id}');
    </script>
    """
    components.html(ga_code, height=0, width=0)

# הפעלת קוד המעקב עם הקוד המזהה שלך
inject_google_analytics("G-7776KX662W")



st.set_page_config(
    page_title="Photonic Coupler Solver (Si / Si3N4 / Al2O3 / SiO2)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UPDATED TITLE ---
st.title("⚡ Photonic Directional & Ring Coupler Solver")
st.markdown("### Integrated Optics Mode Solver & Coupling Analysis (`Si / Si3N4 / Al2O3 / SiO2`)")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🧪 Material Selection")
core_material = st.sidebar.selectbox(
    "Core Material",
    options=[
        "Si3N4 (Stoichiometric)",
        "SiN (Low Stress)",
        "Al2O3 (Alumina)",
        "Si (Silicon)"
    ],
    index=0
)

st.sidebar.header("🛠️ Coupler Parameters")
w_single = st.sidebar.number_input("Waveguide Width w [μm]", value=1.0, step=0.1)
h_core = st.sidebar.number_input("Waveguide Height h [μm]", value=0.3, step=0.05)
gap = st.sidebar.number_input("Coupler Gap [μm]", value=0.3, step=0.05)
coupler_L = st.sidebar.number_input("Straight Length L [μm]", value=35.0, step=5.0)
ring_R = st.sidebar.number_input("Ring Radius R [μm] (0=Straight)", value=100.0, step=10.0)
bottom_oxide = st.sidebar.number_input("Bottom Oxide Height [μm]", value=4.0, step=0.5)
top_oxide = st.sidebar.number_input("Top Oxide Height [μm]", value=1.0, step=0.1)

st.sidebar.header("🎯 Loss / Q_L Settings")
loss_1 = st.sidebar.number_input("Loss 1 [dB/cm]", value=0.5, step=0.1)
loss_2 = st.sidebar.number_input("Loss 2 [dB/cm]", value=1.5, step=0.1)
loss_3 = st.sidebar.number_input("Loss 3 [dB/cm]", value=5.0, step=0.5)
custom_losses = [loss_1, loss_2, loss_3]

st.sidebar.header("🔬 Simulation Settings")
lambda_start = st.sidebar.number_input("Start Wavelength [μm]", value=1.5, step=0.05)
lambda_end = st.sidebar.number_input("End Wavelength [μm]", value=1.6, step=0.05)
n_lambda = st.sidebar.slider("Wavelength Points", min_value=3, max_value=21, value=11, step=2)
polarization = st.sidebar.selectbox("Polarization", options=["ex", "ey"], index=0)
res_mode = st.sidebar.selectbox("Mesh Resolution", options=["lr (0.02μm)", "mr (0.01μm)", "hr (0.005μm)"], index=0)

run_btn = st.sidebar.button("🚀 Run Simulation", type="primary", use_container_width=True)

def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()

def generate_pdf_report(d, fig_dict):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1E3A8A'), spaceAfter=8)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1E3A8A'), spaceBefore=8, spaceAfter=4)
    normal_style = styles['Normal']
    
    elements = []
    
    elements.append(Paragraph(f"Integrated Photonics Coupler Report - {d['core_material']}", title_style))
    elements.append(Paragraph("Complete breakdown of optical parameters, mode cross-sections, dispersion, and loss analysis.", normal_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("1. Simulation & Material Parameters", heading_style))
    param_data = [
        ["Parameter", "Value", "Parameter", "Value"],
        ["Core Material", f"{d['core_material']}", "Ring Radius (R)", f"{d['ring_R']} um"],
        ["Waveguide Width (w)", f"{d['w_single']} um", "Bottom Oxide", f"{d['bottom_oxide']} um"],
        ["Core Height (h)", f"{d['h_core']} um", "Top Oxide", f"{d['top_oxide']} um"],
        ["Gap", f"{d['gap']} um", "Polarization", f"{d['polarization'].upper()}"],
        ["Coupler Length (L)", f"{d['coupler_L']} um", "Wavelength Span", f"{d['lambda_vec'][0]:.2f} - {d['lambda_vec'][-1]:.2f} um"]
    ]
    t_param = Table(param_data, colWidths=[130, 110, 130, 110])
    t_param.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_param)
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("2. Key Results (Central Wavelength)", heading_style))
    res_data = [
        ["Metric", "Value"],
        ["Central Wavelength", f"{d['lambda_center_val']:.3f} um"],
        ["Coupling Coefficient (kappa)", f"{d['kappa_vec'][d['idx_center']]:.4f} um^-1"],
        ["Residual Length (L_res)", f"{d['l_residual_vec'][d['idx_center']]:.2f} um"],
        ["Power Transferred (P_cross)", f"{d['p_cross_vec'][d['idx_center']]:.1f} %"],
        [f"Loaded Q (Q_L at {d['alpha_db_vals'][0]} dB/cm)", f"{d['QL_vals'][0]/1e3:.1f} k"],
        [f"Loaded Q (Q_L at {d['alpha_db_vals'][1]} dB/cm)", f"{d['QL_vals'][1]/1e3:.1f} k"],
        [f"Loaded Q (Q_L at {d['alpha_db_vals'][2]} dB/cm)", f"{d['QL_vals'][2]/1e3:.1f} k"]
    ]
    t_res = Table(res_data, colWidths=[240, 240])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_res)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("3. Cross-Sections & Mode Profiles", heading_style))
    img_index = RLImage(io.BytesIO(fig_to_bytes(fig_dict['index'])), width=235, height=155)
    img_even = RLImage(io.BytesIO(fig_to_bytes(fig_dict['even'])), width=235, height=155)
    img_odd = RLImage(io.BytesIO(fig_to_bytes(fig_dict['odd'])), width=235, height=155)
    img_1d = RLImage(io.BytesIO(fig_to_bytes(fig_dict['1d'])), width=235, height=155)
    
    t_modes = Table([[img_index, img_even], [img_odd, img_1d]], colWidths=[240, 240])
    t_modes.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('PADDING', (0, 0), (-1, -1), 2)]))
    elements.append(t_modes)
    
    elements.append(PageBreak())
    elements.append(Paragraph("4. Dispersion & Optical Coupling Curves", heading_style))
    img_disp = RLImage(io.BytesIO(fig_to_bytes(fig_dict['disp'])), width=235, height=155)
    img_kappa = RLImage(io.BytesIO(fig_to_bytes(fig_dict['kappa'])), width=235, height=155)
    t_disp = Table([[img_disp, img_kappa]], colWidths=[240, 240])
    t_disp.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('PADDING', (0, 0), (-1, -1), 2)]))
    elements.append(t_disp)
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("5. Power Transfer & Ring Coupling Analysis", heading_style))
    img_power = RLImage(io.BytesIO(fig_to_bytes(fig_dict['power'])), width=235, height=155)
    img_loss = RLImage(io.BytesIO(fig_to_bytes(fig_dict['loss'])), width=235, height=155)
    t_power = Table([[img_power, img_loss]], colWidths=[240, 240])
    t_power.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('PADDING', (0, 0), (-1, -1), 2)]))
    elements.append(t_power)
    
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# --- EXECUTION & DISPLAY ---
if run_btn or 'sim_results' in st.session_state:
    if run_btn:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total):
            pct = int((current / total) * 100)
            progress_bar.progress(pct)
            status_text.markdown(f"⏳ **Calculating Wavelength {current} of {total} ({pct}%)...**")

        results = run_simulation(
            w_single, h_core, gap, coupler_L, ring_R,
            lambda_start, lambda_end, n_lambda, polarization, res_mode, top_oxide, bottom_oxide,
            core_material, progress_callback=update_progress
        )
        
        status_text.success("✅ Simulation completed successfully!")
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
        alpha_db_vals = np.array(custom_losses)
        alpha_cm = alpha_db_vals * (np.log(10) / 10.0)
        L_ring_cm = results['L_ring_um'] * 1e-4
        round_trip_loss_pct = (1.0 - np.exp(-alpha_cm * L_ring_cm)) * 100.0
        
        neff_avg_vec = (results['neff_even'] + results['neff_odd']) / 2.0
        lambda_cm_center = results['lambda_center_val'] * 1e-4
        dneff_dlambda = (neff_avg_vec[-1] - neff_avg_vec[0]) / ((results['lambda_vec'][-1] - results['lambda_vec'][0]) * 1e-4)
        n_group = neff_avg_vec[results['idx_center']] - lambda_cm_center * dneff_dlambda
        
        Q0_vals = (2.0 * np.pi * n_group) / (lambda_cm_center * alpha_cm)
        QL_vals = Q0_vals / 2.0
        
        results['alpha_db_vals'] = alpha_db_vals
        results['round_trip_loss_pct'] = round_trip_loss_pct
        results['QL_vals'] = QL_vals
        
        st.session_state['sim_results'] = results

    d = st.session_state['sim_results']

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Central Coupling (κ)", f"{d['kappa_vec'][d['idx_center']]:.4f} μm⁻¹")
    m2.metric("Residual Length (L_res)", f"{d['l_residual_vec'][d['idx_center']]:.2f} μm")
    m3.metric("Cross Power Transferred", f"{d['p_cross_vec'][d['idx_center']]:.1f} %")
    m4.metric(f"Q_L (at α = {d['alpha_db_vals'][1]} dB/cm)", f"{d['QL_vals'][1]/1e3:.1f} k")

    st.markdown("---")
    st.subheader(f"📥 Export Data & Report ({d['core_material']})")
    
    df_results = pd.DataFrame({
        "Wavelength_um": d['lambda_vec'],
        "Neff_Even": d['neff_even'],
        "Neff_Odd": d['neff_odd'],
        "Kappa_1per_um": d['kappa_vec'],
        "L_residual_um": d['l_residual_vec'],
        "L_total_um": d['l_total_vec'],
        "P_cross_percent": d['p_cross_vec'],
        "P_bar_percent": d['p_bar_vec']
    })
    
    def draw_boxes(ax):
        for l, r in [(d['box1_l'], d['box1_r']), (d['box2_l'], d['box2_r'])]:
            ax.plot([l, r, r, l, l], [d['b_y'], d['b_y'], d['t_y'], d['t_y'], d['b_y']], 'k--', lw=1.5)

    fig_idx, ax_idx = plt.subplots(figsize=(6, 4))
    im_idx = ax_idx.imshow(np.sqrt(d['eps_center']).T, origin='lower', extent=[d['xc'][0], d['xc'][-1], d['yc'][0], d['yc'][-1]], cmap='viridis', aspect='auto')
    fig_idx.colorbar(im_idx, ax=ax_idx, label='Index (n)')
    draw_boxes(ax_idx)
    ax_idx.set_title(f"Index Profile ({d['core_material']} @ λ={d['lambda_center_val']:.3f}μm)")

    fig_even, ax_even = plt.subplots(figsize=(6, 4))
    im_even = ax_even.imshow(d['phi_even'].T, origin='lower', extent=[d['xc'][0], d['xc'][-1], d['yc'][0], d['yc'][-1]], cmap='jet', vmin=0, vmax=1, aspect='auto')
    fig_even.colorbar(im_even, ax=ax_even, label='Field')
    draw_boxes(ax_even)
    ax_even.set_title(f"Symmetric (Even) Mode ({d['polarization'].upper()})")

    fig_odd, ax_odd = plt.subplots(figsize=(6, 4))
    im_odd = ax_odd.imshow(d['phi_odd'].T, origin='lower', extent=[d['xc'][0], d['xc'][-1], d['yc'][0], d['yc'][-1]], cmap='jet', vmin=-1, vmax=1, aspect='auto')
    fig_odd.colorbar(im_odd, ax=ax_odd, label='Field')
    draw_boxes(ax_odd)
    ax_odd.set_title(f"Antisymmetric (Odd) Mode ({d['polarization'].upper()})")

    fig_1d, ax_1d = plt.subplots(figsize=(6, 4))
    ax_1d.plot(d['xc'], d['phi_even'][:, d['mid_y_idx']], 'b-', lw=2, label='Even')
    ax_1d.plot(d['xc'], d['phi_odd'][:, d['mid_y_idx']], 'r--', lw=2, label='Odd')
    ax_1d.grid(True)
    ax_1d.legend()
    ax_1d.set_title("1D Field Profiles at Core Center")

    fig_disp, ax_disp = plt.subplots(figsize=(6, 4))
    ax_disp.plot(d['lambda_vec'], d['neff_even'], 'bo-', lw=2, label='n_eff Even')
    ax_disp.plot(d['lambda_vec'], d['neff_odd'], 'r^-', lw=2, label='n_eff Odd')
    ax_disp.grid(True)
    ax_disp.legend()
    ax_disp.set_xlabel('Wavelength [μm]')
    ax_disp.set_ylabel('Effective Index (n_eff)')
    ax_disp.set_title("Supermode Dispersion Curves")

    fig_kappa, ax_kappa_left = plt.subplots(figsize=(6, 4))
    ax_kappa_right = ax_kappa_left.twinx()
    ax_kappa_left.plot(d['lambda_vec'], d['kappa_vec'], 'kd-', lw=2, label='Kappa')
    ax_kappa_right.plot(d['lambda_vec'], d['l_residual_vec'], 'ms-', lw=2, label='L_residual')
    ax_kappa_left.grid(True)
    ax_kappa_left.set_xlabel('Wavelength [μm]')
    ax_kappa_left.set_ylabel('κ [μm⁻¹]', color='k')
    ax_kappa_right.set_ylabel('L_residual [μm]', color='m')
    ax_kappa_left.set_title("Coupling Coefficient κ & Residual Length")

    fig_power, ax_power = plt.subplots(figsize=(7, 4))
    ax_power.plot(d['lambda_vec'], d['p_cross_vec'], 'ro-', lw=2, label='Cross Port Power')
    ax_power.plot(d['lambda_vec'], d['p_bar_vec'], 'bo-', lw=2, label='Bar Port Power')
    ax_power.grid(True)
    ax_power.set_ylim(0, 105)
    ax_power.set_xlabel('Wavelength [μm]')
    ax_power.set_ylabel('Power Transfer [%]')
    ax_power.legend()
    ax_power.set_title("Power Transfer Ratio vs. Wavelength")

    fig_loss, ax_loss = plt.subplots(figsize=(7, 4))
    ax_loss.plot(d['lambda_vec'], d['p_cross_vec'], 'ro-', lw=2.5, label='Coupled Power P_cross')
    colors_list = ['g--', 'm--', 'k--']
    for k in range(3):
        loss_v = d['round_trip_loss_pct'][k]
        ql_v = d['QL_vals'][k] / 1e3
        alpha_db = d['alpha_db_vals'][k]
        label_text = f"Loss = {loss_v:.3f}% (α={alpha_db}dB/cm, QL≈{ql_v:.1f}k)"
        ax_loss.axhline(loss_v, color=colors_list[k][0], linestyle='--', lw=1.8, label=label_text)
    ax_loss.grid(True)
    ax_loss.set_xlabel('Wavelength [μm]')
    ax_loss.set_ylabel('Power [%]')
    ax_loss.legend(fontsize=8)
    ax_loss.set_title(f"Ring Coupling vs. Loss & Critical Q_L (L_ring = {d['L_ring_um']:.1f} μm)")

    all_figs = {
        'index': fig_idx, 'even': fig_even, 'odd': fig_odd, '1d': fig_1d,
        'disp': fig_disp, 'kappa': fig_kappa, 'power': fig_power, 'loss': fig_loss
    }

    pdf_bytes = generate_pdf_report(d, all_figs)

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        csv_bytes = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Download Raw Data (CSV)", data=csv_bytes, file_name="multi_material_results.csv", mime="text/csv", use_container_width=True)
    with col_exp2:
        st.download_button("📕 Download Comprehensive PDF Report", data=pdf_bytes, file_name="multi_material_report.pdf", mime="application/pdf", type="primary", use_container_width=True)

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["🖼️ Cross-Sections & Modes", "📈 Dispersion & Coupling", "⚡ Power Transfer", "🎯 Loss & Critical Q_L"])

    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.pyplot(fig_idx)
            st.download_button("💾 Save Index Profile PNG", data=fig_to_bytes(fig_idx), file_name="index_profile.png", mime="image/png")
            st.pyplot(fig_odd)
            st.download_button("💾 Save Odd Mode PNG", data=fig_to_bytes(fig_odd), file_name="odd_mode.png", mime="image/png")
        with col_b:
            st.pyplot(fig_even)
            st.download_button("💾 Save Even Mode PNG", data=fig_to_bytes(fig_even), file_name="even_mode.png", mime="image/png")
            st.pyplot(fig_1d)
            st.download_button("💾 Save 1D Profile PNG", data=fig_to_bytes(fig_1d), file_name="1d_profiles.png", mime="image/png")

    with tab2:
        col_c, col_d = st.columns(2)
        with col_c:
            st.pyplot(fig_disp)
            st.download_button("💾 Save Dispersion Graph PNG", data=fig_to_bytes(fig_disp), file_name="dispersion.png", mime="image/png")
        with col_d:
            st.pyplot(fig_kappa)
            st.download_button("💾 Save Kappa Graph PNG", data=fig_to_bytes(fig_kappa), file_name="kappa_coupling.png", mime="image/png")

    with tab3:
        st.pyplot(fig_power)
        st.download_button("💾 Save Power Transfer PNG", data=fig_to_bytes(fig_power), file_name="power_transfer.png", mime="image/png")

    with tab4:
        st.pyplot(fig_loss)
        st.download_button("💾 Save Ring Loss PNG", data=fig_to_bytes(fig_loss), file_name="ring_loss_QL.png", mime="image/png")

    for fig_obj in all_figs.values():
        plt.close(fig_obj)

else:
    # --- REFERENCE MODAL DISTRIBUTIONS & BENCHMARK PREVIEW ---
    st.info("👈 Select core material and physical geometry in the sidebar, then click **Run Simulation** 🚀")
    
    st.markdown("### 🔬 Reference Modal Profiles & Numerical Benchmarks 🎨")
    st.markdown("Below are standard reference solutions calculated for a symmetric dual-waveguide directional coupler structure:")

    preview_items = [
        {"file": "index_profile.png", "title": "1. Cross-Sectional Refractive Index Distribution n(x,y) 📐"},
        {"file": "even_mode.png", "title": "2. Symmetric Supermode Field Distribution (Quasi-TE Even) ⚡"},
        {"file": "odd_mode.png", "title": "3. Antisymmetric Supermode Field Distribution (Quasi-TE Odd) 🌊"},
        {"file": "1d_profiles.png", "title": "4. 1D Transverse Field Profiles at Core Center Cutline 📊"},
        {"file": "dispersion.png", "title": "5. Supermode Dispersion Characteristics n_eff(λ) 📈"},
        {"file": "ring_loss_QL.png", "title": "6. Power Coupling & Cavity Quality Factor Q_L vs. Loss 🎯"}
    ]
    
    valid_items = [item for item in preview_items if os.path.exists(item["file"])]
    
    if valid_items:
        # Pure HTML/CSS Carousel for Dynamic Reference Display
        encoded_slides = []
        for idx, item in enumerate(valid_items):
            with open(item["file"], "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode()
            encoded_slides.append(f"""
                <div class="mySlides fade" style="display: {'block' if idx==0 else 'none'}; text-align: center;">
                    <div style="font-weight: 600; font-size: 15px; margin-bottom: 10px; color: #0F172A; font-family: sans-serif;">
                        {item['title']}
                    </div>
                    <img src="data:image/png;base64,{b64}" style="max-width: 82%; height: auto; border-radius: 8px; border: 1px solid #CBD5E1; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                </div>
            """)

        carousel_html = f"""
        <div id="slideshow-container" style="max-width: 760px; position: relative; margin: 10px auto; padding: 18px; background: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0;">
            {''.join(encoded_slides)}
        </div>
        <script>
            let slideIndex = 0;
            showSlides();
            function showSlides() {{
                let i;
                let slides = document.getElementsByClassName("mySlides");
                for (i = 0; i < slides.length; i++) {{
                    slides[i].style.display = "none";  
                }}
                slideIndex++;
                if (slideIndex > slides.length) {{slideIndex = 1}}    
                if (slides[slideIndex-1]) {{
                    slides[slideIndex-1].style.display = "block";  
                }}
                setTimeout(showSlides, 3000); // Switch every 3.0 seconds
            }}
        </script>
        """
        st.components.v1.html(carousel_html, height=490)
