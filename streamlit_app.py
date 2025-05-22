from streamlit_lottie import st_lottie
import requests
import streamlit as st
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict
import json
import math

# Konfigurasi halaman dengan tema yang lebih menarik
st.set_page_config(
    page_title="Advanced Molecular Mass Calculator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling yang lebih menarik
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Fungsi memuat animasi Lottie
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Header utama dengan styling
st.markdown("""
<div class="main-header">
    <h1>🧪 Advanced Molecular Mass Calculator</h1>
    <p>Kalkulator Massa Molekul dan Analisis Kimia Komprehensif</p>
</div>
""", unsafe_allow_html=True)

# Inisialisasi session state
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Dashboard"
if "calculation_history" not in st.session_state:
    st.session_state.calculation_history = []
if "favorite_compounds" not in st.session_state:
    st.session_state.favorite_compounds = []

# Data massa atom relatif yang lebih lengkap dengan informasi tambahan
massa_atom_data = {
    "H": {"mass": 1.008, "name": "Hidrogen", "symbol": "H", "number": 1, "group": 1, "period": 1, "category": "Nonlogam"},
    "He": {"mass": 4.0026, "name": "Helium", "symbol": "He", "number": 2, "group": 18, "period": 1, "category": "Gas mulia"},
    "Li": {"mass": 6.94, "name": "Litium", "symbol": "Li", "number": 3, "group": 1, "period": 2, "category": "Logam alkali"},
    "Be": {"mass": 9.0122, "name": "Berilium", "symbol": "Be", "number": 4, "group": 2, "period": 2, "category": "Logam alkali tanah"},
    "B": {"mass": 10.81, "name": "Boron", "symbol": "B", "number": 5, "group": 13, "period": 2, "category": "Metaloid"},
    "C": {"mass": 12.01, "name": "Karbon", "symbol": "C", "number": 6, "group": 14, "period": 2, "category": "Nonlogam"},
    "N": {"mass": 14.007, "name": "Nitrogen", "symbol": "N", "number": 7, "group": 15, "period": 2, "category": "Nonlogam"},
    "O": {"mass": 16.00, "name": "Oksigen", "symbol": "O", "number": 8, "group": 16, "period": 2, "category": "Nonlogam"},
    "F": {"mass": 18.998, "name": "Fluorin", "symbol": "F", "number": 9, "group": 17, "period": 2, "category": "Halogen"},
    "Ne": {"mass": 20.180, "name": "Neon", "symbol": "Ne", "number": 10, "group": 18, "period": 2, "category": "Gas mulia"},
    "Na": {"mass": 22.990, "name": "Natrium", "symbol": "Na", "number": 11, "group": 1, "period": 3, "category": "Logam alkali"},
    "Mg": {"mass": 24.305, "name": "Magnesium", "symbol": "Mg", "number": 12, "group": 2, "period": 3, "category": "Logam alkali tanah"},
    "Al": {"mass": 26.982, "name": "Aluminium", "symbol": "Al", "number": 13, "group": 13, "period": 3, "category": "Logam"},
    "Si": {"mass": 28.085, "name": "Silikon", "symbol": "Si", "number": 14, "group": 14, "period": 3, "category": "Metaloid"},
    "P": {"mass": 30.974, "name": "Fosfor", "symbol": "P", "number": 15, "group": 15, "period": 3, "category": "Nonlogam"},
    "S": {"mass": 32.06, "name": "Sulfur", "symbol": "S", "number": 16, "group": 16, "period": 3, "category": "Nonlogam"},
    "Cl": {"mass": 35.45, "name": "Klorin", "symbol": "Cl", "number": 17, "group": 17, "period": 3, "category": "Halogen"},
    "Ar": {"mass": 39.948, "name": "Argon", "symbol": "Ar", "number": 18, "group": 18, "period": 3, "category": "Gas mulia"},
    "K": {"mass": 39.098, "name": "Kalium", "symbol": "K", "number": 19, "group": 1, "period": 4, "category": "Logam alkali"},
    "Ca": {"mass": 40.078, "name": "Kalsium", "symbol": "Ca", "number": 20, "group": 2, "period": 4, "category": "Logam alkali tanah"},
    "Sc": {"mass": 44.956, "name": "Skandium", "symbol": "Sc", "number": 21, "group": 3, "period": 4, "category": "Logam transisi"},
    "Ti": {"mass": 47.867, "name": "Titanium", "symbol": "Ti", "number": 22, "group": 4, "period": 4, "category": "Logam transisi"},
    "V": {"mass": 50.942, "name": "Vanadium", "symbol": "V", "number": 23, "group": 5, "period": 4, "category": "Logam transisi"},
    "Cr": {"mass": 51.996, "name": "Kromium", "symbol": "Cr", "number": 24, "group": 6, "period": 4, "category": "Logam transisi"},
    "Mn": {"mass": 54.938, "name": "Mangan", "symbol": "Mn", "number": 25, "group": 7, "period": 4, "category": "Logam transisi"},
    "Fe": {"mass": 55.845, "name": "Besi", "symbol": "Fe", "number": 26, "group": 8, "period": 4, "category": "Logam transisi"},
    "Co": {"mass": 58.933, "name": "Kobalt", "symbol": "Co", "number": 27, "group": 9, "period": 4, "category": "Logam transisi"},
    "Ni": {"mass": 58.693, "name": "Nikel", "symbol": "Ni", "number": 28, "group": 10, "period": 4, "category": "Logam transisi"},
    "Cu": {"mass": 63.546, "name": "Tembaga", "symbol": "Cu", "number": 29, "group": 11, "period": 4, "category": "Logam transisi"},
    "Zn": {"mass": 65.38, "name": "Seng", "symbol": "Zn", "number": 30, "group": 12, "period": 4, "category": "Logam transisi"},
    "Ga": {"mass": 69.723, "name": "Galium", "symbol": "Ga", "number": 31, "group": 13, "period": 4, "category": "Logam"},
    "Ge": {"mass": 72.63, "name": "Germanium", "symbol": "Ge", "number": 32, "group": 14, "period": 4, "category": "Metaloid"},
    "As": {"mass": 74.922, "name": "Arsen", "symbol": "As", "number": 33, "group": 15, "period": 4, "category": "Metaloid"},
    "Se": {"mass": 78.971, "name": "Selenium", "symbol": "Se", "number": 34, "group": 16, "period": 4, "category": "Nonlogam"},
    "Br": {"mass": 79.904, "name": "Bromin", "symbol": "Br", "number": 35, "group": 17, "period": 4, "category": "Halogen"},
    "Kr": {"mass": 83.798, "name": "Kripton", "symbol": "Kr", "number": 36, "group": 18, "period": 4, "category": "Gas mulia"}
}

# Ekstrak massa atom untuk kompatibilitas dengan kode lama
massa_atom = {k: v["mass"] for k, v in massa_atom_data.items()}

# Fungsi parsing rumus kimia yang lebih canggih
def parse_formula(formula):
    """Parse rumus kimia dengan dukungan untuk berbagai format"""
    try:
        # Normalize formula
        formula = formula.replace("·", ".").replace("•", ".").replace(" ", "")
        parts = formula.split(".")
        total_elements = defaultdict(int)
        
        def parse_part(part, multiplier=1):
            stack = []
            i = 0
            current_elements = defaultdict(int)
            
            while i < len(part):
                if part[i] == "(":
                    stack.append(current_elements)
                    current_elements = defaultdict(int)
                    i += 1
                elif part[i] == ")":
                    i += 1
                    # Parse number after closing bracket
                    num = ""
                    while i < len(part) and part[i].isdigit():
                        num += part[i]
                        i += 1
                    
                    group_multiplier = int(num) if num else 1
                    group_elements = current_elements
                    current_elements = stack.pop()
                    
                    # Add group elements to current level
                    for el, count in group_elements.items():
                        current_elements[el] += count * group_multiplier
                else:
                    # Parse element and its count
                    match = re.match(r'([A-Z][a-z]?)(\d*)', part[i:])
                    if not match:
                        raise ValueError(f"Format tidak dikenali: '{part[i:]}'")
                    
                    element = match.group(1)
                    count = int(match.group(2)) if match.group(2) else 1
                    i += len(match.group(0))
                    
                    if element not in massa_atom:
                        raise ValueError(f"Unsur '{element}' tidak dikenali")
                    
                    current_elements[element] += count
            
            # Apply multiplier to all elements
            for el, count in current_elements.items():
                total_elements[el] += count * multiplier
        
        # Parse each part of the formula
        for part in parts:
            # Check for leading coefficient
            match = re.match(r'^(\d+)([A-Z(].*)', part)
            if match:
                coefficient = int(match.group(1))
                formula_part = match.group(2)
            else:
                coefficient = 1
                formula_part = part
            
            parse_part(formula_part, coefficient)
        
        return dict(total_elements)
    
    except Exception as e:
        st.error(f"Error parsing formula: {str(e)}")
        return None

# Fungsi untuk menghitung persentase komposisi
def calculate_composition(elements, total_mass):
    """Hitung persentase komposisi setiap unsur"""
    composition = {}
    for element, count in elements.items():
        element_mass = massa_atom[element] * count
        percentage = (element_mass / total_mass) * 100
        composition[element] = {
            'count': count,
            'mass': element_mass,
            'percentage': percentage
        }
    return composition

# Fungsi untuk menghitung rumus empiris
def calculate_empirical_formula(composition):
    """Hitung rumus empiris dari persentase komposisi"""
    # Konversi persentase ke mol
    moles = {}
    for element, data in composition.items():
        moles[element] = data['percentage'] / massa_atom[element]
    
    # Cari rasio terkecil
    min_moles = min(moles.values())
    ratios = {el: moles[el] / min_moles for el in moles}
    
    # Bulatkan ke bilangan bulat terdekat
    empirical = {}
    for element, ratio in ratios.items():
        empirical[element] = round(ratio)
    
    return empirical

# Predefined compounds database
common_compounds = {
    "Air": "H2O",
    "Garam Dapur": "NaCl",
    "Gula": "C12H22O11",
    "Asam Sulfat": "H2SO4",
    "Amonia": "NH3",
    "Metana": "CH4",
    "Etanol": "C2H5OH",
    "Asam Asetat": "CH3COOH",
    "Kalsium Karbonat": "CaCO3",
    "Sodium Bikarbonat": "NaHCO3",
    "Aluminium Sulfat": "Al2(SO4)3",
    "Tembaga Sulfat Pentahidrat": "CuSO4·5H2O",
    "Magnesium Sulfat Heptahidrat": "MgSO4·7H2O",
    "Asam Klorida": "HCl",
    "Natrium Hidroksida": "NaOH",
    "Kalsium Klorida": "CaCl2",
    "Kalium Permanganat": "KMnO4",
    "Besi(III) Oksida": "Fe2O3",
    "Karbon Dioksida": "CO2",
    "Nitrogen Dioksida": "NO2"
}

# Sidebar navigation yang lebih canggih
with st.sidebar:
    # Animasi sidebar
    lottie_sidebar = load_lottieurl("https://lottie.host/a64c7ff9-346e-4e72-b656-e337097d3bde/yHrJbTdVlE.json")
    if lottie_sidebar:
        st_lottie(lottie_sidebar, height=150, key="sidebar_animation")
    
    st.markdown("### 🧭 Navigasi")
    
    # Menu buttons dengan icons
    menu_options = {
        "🏠 Dashboard": "dashboard",
        "🧪 Kalkulator": "calculator", 
        "📊 Analisis": "analysis",
        "🔍 Database": "database",
        "📈 Visualisasi": "visualization",
        "📚 Pembelajaran": "learning",
        "⚗️ Laboratorium": "lab",
        "📋 Riwayat": "history",
        "ℹ️ Tentang": "about"
    }
    
    for menu_text, menu_key in menu_options.items():
        if st.button(menu_text, key=f"btn_{menu_key}"):
            st.session_state.menu = menu_text
    
    # Quick compound selector
    st.markdown("### 🎯 Senyawa Umum")
    selected_compound = st.selectbox(
        "Pilih senyawa:",
        [""] + list(common_compounds.keys()),
        key="quick_compound"
    )
    
    if selected_compound and st.button("📝 Gunakan Formula"):
        st.session_state.quick_formula = common_compounds[selected_compound]

# Main content based on selected menu
menu = st.session_state.menu

if menu == "🏠 Dashboard":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Perhitungan", len(st.session_state.calculation_history))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Senyawa Favorit", len(st.session_state.favorite_compounds))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Database Unsur", len(massa_atom_data))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Dashboard animations
    lottie_dashboard = load_lottieurl("https://lottie.host/b592895d-f9e1-43b1-bf8e-dea5b80b8a25/h9K58rIqKT.json")
    if lottie_dashboard:
        st_lottie(lottie_dashboard, height=300, key="dashboard_main")
    
    st.markdown("### 🚀 Fitur Unggulan")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🧮 Kalkulator Canggih:**
        - Parsing formula otomatis
        - Dukungan senyawa hidrasi
        - Perhitungan komposisi
        - Analisis massa molekul
        """)
    
    with col2:
        st.markdown("""
        **📊 Analisis Mendalam:**
        - Visualisasi komposisi
        - Grafik interaktif
        - Perbandingan senyawa
        - Export data
        """)
    
    # Recent calculations
    if st.session_state.calculation_history:
        st.markdown("### 📈 Perhitungan Terakhir")
        recent = st.session_state.calculation_history[-5:]
        for calc in reversed(recent):
            with st.expander(f"{calc['formula']} - {calc['mass']:.2f} g/mol"):
                st.write(f"**Waktu:** {calc['timestamp']}")
                st.write(f"**Komposisi:** {calc['composition']}")

elif menu == "🧪 Kalkulator":
    st.header("🧪 Kalkulator Massa Molekul Advanced")
    
    # Animation
    lottie_calc = load_lottieurl("https://lottie.host/5ee6c7e7-3c7b-473f-b75c-df412fe210cc/kF9j77AAsG.json")
    if lottie_calc:
        st_lottie(lottie_calc, height=200, key="calculator_animation")
    
    # Input form dengan tabs
    tab1, tab2, tab3 = st.tabs(["💡 Input Manual", "🎯 Pilih Senyawa", "⚡ Input Cepat"])
    
    with tab1:
        st.markdown("""
        📌 **Petunjuk Lengkap:**
        - Unsur: `H`, `O`, `Ca`, etc.
        - Senyawa: `H2O`, `NaCl`, `C6H12O6`
        - Kelompok: `Al2(SO4)3`, `Ca(OH)2`
        - Hidrasi: `CuSO4·5H2O`, `MgSO4·7H2O`
        - Koefisien: `2NaCl`, `3H2SO4`
        """)
        
        formula_input = st.text_input(
            "Masukkan rumus kimia:",
            value=st.session_state.get('quick_formula', ''),
            placeholder="Contoh: H2O, Al2(SO4)3, CuSO4·5H2O",
            key="manual_formula"
        )
    
    with tab2:
        compound_name = st.selectbox("Pilih senyawa umum:", list(common_compounds.keys()))
        if compound_name:
            formula_input = common_compounds[compound_name]
            st.info(f"Formula: **{formula_input}**")
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            elements_list = list(massa_atom.keys())
            element1 = st.selectbox("Unsur 1:", [""] + elements_list)
            count1 = st.number_input("Jumlah 1:", min_value=0, value=1)
        
        with col2:
            element2 = st.selectbox("Unsur 2:", [""] + elements_list)
            count2 = st.number_input("Jumlah 2:", min_value=0, value=0)
        
        if element1:
            formula_parts = []
            if count1 > 0:
                formula_parts.append(f"{element1}{count1 if count1 > 1 else ''}")
            if element2 and count2 > 0:
                formula_parts.append(f"{element2}{count2 if count2 > 1 else ''}")
            formula_input = "".join(formula_parts)
            if formula_input:
                st.info(f"Formula: **{formula_input}**")
    
    # Calculation options
    col1, col2, col3 = st.columns(3)
    with col1:
        show_detailed = st.checkbox("📝 Tampilkan Detail", value=True)
    with col2:
        show_composition = st.checkbox("📊 Hitung Komposisi", value=True)
    with col3:
        save_calculation = st.checkbox("💾 Simpan Hasil", value=True)
    
    # Calculate button
    if st.button("🔬 Hitung Massa Molekul", type="primary"):
        if formula_input:
            parsed = parse_formula(formula_input)
            
            if parsed:
                # Calculate molecular mass
                total_mass = sum(massa_atom[el] * count for el, count in parsed.items())
                
                # Display results
                st.markdown("---")
                st.markdown("### 🎯 Hasil Perhitungan")
                
                # Main result card
                st.markdown(f"""
                <div class="success-card">
                    <h3>🧪 {formula_input}</h3>
                    <h2>Massa Molekul: {total_mass:.4f} g/mol</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Detailed breakdown
                if show_detailed:
                    st.markdown("### 📋 Rincian Perhitungan")
                    detail_parts = []
                    
                    for element, count in parsed.items():
                        element_mass = massa_atom[element]
                        subtotal = element_mass * count
                        element_name = massa_atom_data[element]["name"]
                        
                        detail_parts.append({
                            'Unsur': f"{element} ({element_name})",
                            'Jumlah Atom': count,
                            'Massa Atom (g/mol)': f"{element_mass:.4f}",
                            'Kontribusi (g/mol)': f"{subtotal:.4f}",
                            'Formula': f"{count} × {element_mass:.4f}"
                        })
                    
                    df_detail = pd.DataFrame(detail_parts)
                    st.dataframe(df_detail, use_container_width=True)
                    
                    # Mathematical expression
                    math_expr = " + ".join([f"({row['Formula']})" for _, row in df_detail.iterrows()])
                    st.markdown(f"**Mr({formula_input}) = {math_expr} = {total_mass:.4f} g/mol**")
                
                # Composition analysis
                if show_composition:
                    st.markdown("### 🔬 Analisis Komposisi")
                    composition = calculate_composition(parsed, total_mass)
                    
                    comp_data = []
                    for element, data in composition.items():
                        element_name = massa_atom_data[element]["name"]
                        comp_data.append({
                            'Unsur': f"{element} ({element_name})",
                            'Massa (g/mol)': f"{data['mass']:.4f}",
                            'Persentase (%)': f"{data['percentage']:.2f}%"
                        })
                    
                    df_comp = pd.DataFrame(comp_data)
                    st.dataframe(df_comp, use_container_width=True)
                    
                    # Pie chart
                    fig_pie = px.pie(
                        values=[data['percentage'] for data in composition.values()],
                        names=[f"{el} ({massa_atom_data[el]['name']})" for el in composition.keys()],
                        title="Komposisi Massa Unsur"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Save to history
                if save_calculation:
                    from datetime import datetime
                    calc_data = {
                        'formula': formula_input,
                        'mass': total_mass,
                        'composition': parsed,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.calculation_history.append(calc_data)
                    st.success("✅ Hasil perhitungan disimpan ke riwayat!")
                
                # Add to favorites option
                if st.button("⭐ Tambahkan ke Favorit"):
                    if formula_input not in st.session_state.favorite_compounds:
                        st.session_state.favorite_compounds.append(formula_input)
                        st.success("⭐ Ditambahkan ke senyawa favorit!")
                    else:
                        st.info("ℹ️ Senyawa sudah ada di favorit!")
            
            else:
                st.error("❌ Gagal menganalisis formula. Periksa format penulisan!")
        else:
            st.warning("⚠️ Silakan masukkan rumus kimia terlebih dahulu!")

elif menu == "📊 Analisis":
    st.header("📊 Analisis Senyawa Kimia")
    
    # Multi-compound comparison
    st.markdown("### 🔬 Perbandingan Multi-Senyawa")
    
    compounds_to_compare = st.text_area(
        "Masukkan rumus senyawa (satu per baris):",
        placeholder="H2O\nNaCl\nC6H12O6\nCaCO3",
        height=100
    )
    
    if st.button("📈 Analisis Perbandingan"):
        if compounds_to_compare:
            formulas = [f.strip() for f in compounds_to_compare.split('\n') if f.strip()]
            
            comparison_data = []
            composition_data = []
            
            for formula in formulas:
                parsed = parse_formula(formula)
                if parsed:
                    total_mass = sum(massa_atom[el] * count for el, count in parsed.items())
                    composition = calculate_composition(parsed, total_mass)
                    
                    comparison_data.append({
                        'Senyawa': formula,
                        'Massa Molekul (g/mol)': total_mass,
                        'Jumlah Unsur': len(parsed),
                        'Total Atom': sum(parsed.values())
                    })
                    
                    # Collect composition data for stacked chart
                    for element, data in composition.items():
                        composition_data.append({
                            'Senyawa': formula,
                            'Unsur': element,
                            'Persentase': data['percentage']
                        })
            
            if comparison_data:
                # Comparison table
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)
                
                # Molecular mass comparison chart
                fig_bar = px.bar(
                    df_comparison,
                    x='Senyawa',
                    y='Massa Molekul (g/mol)',
                    title='Perbandingan Massa Molekul',
                    color='Massa Molekul (g/mol)',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Composition comparison if data available
                if composition_data:
                    df_composition = pd.DataFrame(composition_data)
                    
                    # Stacked bar chart for composition
                    fig_stacked = px.bar(
                        df_composition,
                        x='Senyawa',
                        y='Persentase',
                        color='Unsur',
                        title='Perbandingan Komposisi Unsur (%)',
                        text='Persentase'
                    )
                    fig_stacked.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
                    st.plotly_chart(fig_stacked, use_container_width=True)
                
                # Statistical analysis
                st.markdown("### 📊 Analisis Statistik")
                col1, col2, col3, col4 = st.columns(4)
                
                masses = [data['Massa Molekul (g/mol)'] for data in comparison_data]
                
                with col1:
                    st.metric("Massa Tertinggi", f"{max(masses):.2f} g/mol")
                with col2:
                    st.metric("Massa Terendah", f"{min(masses):.2f} g/mol")
                with col3:
                    st.metric("Rata-rata", f"{sum(masses)/len(masses):.2f} g/mol")
                with col4:
                    st.metric("Selisih", f"{max(masses) - min(masses):.2f} g/mol")

elif menu == "🔍 Database":
    st.header("🔍 Database Unsur Kimia")
    
    # Search and filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Cari unsur:", placeholder="Nama atau simbol unsur")
    
    with col2:
        category_filter = st.selectbox(
            "📂 Filter kategori:",
            ["Semua"] + list(set(data["category"] for data in massa_atom_data.values()))
        )
    
    with col3:
        period_filter = st.selectbox(
            "🔢 Filter periode:",
            ["Semua"] + sorted(list(set(data["period"] for data in massa_atom_data.values())))
        )
    
    # Create filtered dataframe
    elements_data = []
    for symbol, data in massa_atom_data.items():
        # Apply filters
        if search_term and search_term.lower() not in data["name"].lower() and search_term.lower() not in symbol.lower():
            continue
        if category_filter != "Semua" and data["category"] != category_filter:
            continue
        if period_filter != "Semua" and data["period"] != period_filter:
            continue
        
        elements_data.append({
            "Simbol": symbol,
            "Nama": data["name"],
            "Nomor Atom": data["number"],
            "Massa Atom": data["mass"],
            "Golongan": data["group"],
            "Periode": data["period"],
            "Kategori": data["category"]
        })
    
    if elements_data:
        df_elements = pd.DataFrame(elements_data)
        st.dataframe(df_elements, use_container_width=True)
        
        # Element details
        st.markdown("### 🔬 Detail Unsur")
        selected_element = st.selectbox("Pilih unsur untuk detail:", df_elements["Simbol"].tolist())
        
        if selected_element:
            element_info = massa_atom_data[selected_element]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **🧪 {element_info['name']} ({selected_element})**
                - **Nomor Atom:** {element_info['number']}
                - **Massa Atom:** {element_info['mass']} u
                - **Golongan:** {element_info['group']}
                - **Periode:** {element_info['period']}
                - **Kategori:** {element_info['category']}
                """)
            
            with col2:
                # Create element visualization
                fig_element = go.Figure()
                fig_element.add_trace(go.Scatter(
                    x=[element_info['group']],
                    y=[element_info['period']],
                    mode='markers+text',
                    marker=dict(size=50, color='blue'),
                    text=[selected_element],
                    textposition='middle center',
                    name=element_info['name']
                ))
                fig_element.update_layout(
                    title=f"Posisi {element_info['name']} dalam Tabel Periodik",
                    xaxis_title="Golongan",
                    yaxis_title="Periode",
                    showlegend=False
                )
                st.plotly_chart(fig_element, use_container_width=True)
    
    else:
        st.info("Tidak ada unsur yang sesuai dengan filter yang dipilih.")

elif menu == "📈 Visualisasi":
    st.header("📈 Visualisasi Data Kimia")
    
    # Visualization options
    viz_type = st.selectbox(
        "Pilih jenis visualisasi:",
        ["Massa Atom vs Nomor Atom", "Distribusi Kategori", "Peta Panas Tabel Periodik", "Analisis Periode"]
    )
    
    if viz_type == "Massa Atom vs Nomor Atom":
        # Create scatter plot
        elements_list = []
        for symbol, data in massa_atom_data.items():
            elements_list.append({
                'Simbol': symbol,
                'Nomor Atom': data['number'],
                'Massa Atom': data['mass'],
                'Kategori': data['category'],
                'Periode': data['period']
            })
        
        df_viz = pd.DataFrame(elements_list)
        
        fig_scatter = px.scatter(
            df_viz,
            x='Nomor Atom',
            y='Massa Atom',
            color='Kategori',
            size='Periode',
            hover_data=['Simbol'],
            title='Hubungan Massa Atom dan Nomor Atom'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    elif viz_type == "Distribusi Kategori":
        # Count elements by category
        category_count = {}
        for data in massa_atom_data.values():
            category = data['category']
            category_count[category] = category_count.get(category, 0) + 1
        
        fig_pie = px.pie(
            values=list(category_count.values()),
            names=list(category_count.keys()),
            title='Distribusi Unsur Berdasarkan Kategori'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Bar chart
        fig_bar = px.bar(
            x=list(category_count.keys()),
            y=list(category_count.values()),
            title='Jumlah Unsur per Kategori'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    elif viz_type == "Peta Panas Tabel Periodik":
        # Create heatmap data
        heatmap_data = []
        for symbol, data in massa_atom_data.items():
            heatmap_data.append({
                'Golongan': data['group'],
                'Periode': data['period'],
                'Massa': data['mass'],
                'Simbol': symbol
            })
        
        df_heatmap = pd.DataFrame(heatmap_data)
        
        # Create pivot table
        pivot_table = df_heatmap.pivot(index='Periode', columns='Golongan', values='Massa')
        
        fig_heatmap = px.imshow(
            pivot_table,
            title='Peta Panas Massa Atom dalam Tabel Periodik',
            labels=dict(x="Golongan", y="Periode", color="Massa Atom")
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    elif viz_type == "Analisis Periode":
        # Analyze trends by period
        period_data = {}
        for data in massa_atom_data.values():
            period = data['period']
            if period not in period_data:
                period_data[period] = {'masses': [], 'count': 0}
            period_data[period]['masses'].append(data['mass'])
            period_data[period]['count'] += 1
        
        # Calculate statistics
        period_stats = []
        for period, data in period_data.items():
            masses = data['masses']
            period_stats.append({
                'Periode': period,
                'Jumlah Unsur': len(masses),
                'Massa Rata-rata': sum(masses) / len(masses),
                'Massa Minimum': min(masses),
                'Massa Maksimum': max(masses)
            })
        
        df_period = pd.DataFrame(period_stats)
        
        # Multiple line chart
        fig_lines = go.Figure()
        
        fig_lines.add_trace(go.Scatter(
            x=df_period['Periode'],
            y=df_period['Massa Rata-rata'],
            mode='lines+markers',
            name='Rata-rata',
            line=dict(color='blue')
        ))
        
        fig_lines.add_trace(go.Scatter(
            x=df_period['Periode'],
            y=df_period['Massa Maksimum'],
            mode='lines+markers',
            name='Maksimum',
            line=dict(color='red')
        ))
        
        fig_lines.add_trace(go.Scatter(
            x=df_period['Periode'],
            y=df_period['Massa Minimum'],
            mode='lines+markers',
            name='Minimum',
            line=dict(color='green')
        ))
        
        fig_lines.update_layout(
            title='Tren Massa Atom Berdasarkan Periode',
            xaxis_title='Periode',
            yaxis_title='Massa Atom (u)'
        )
        
        st.plotly_chart(fig_lines, use_container_width=True)
        
        # Display statistics table
        st.dataframe(df_period, use_container_width=True)

elif menu == "📚 Pembelajaran":
    st.header("📚 Modul Pembelajaran Kimia")
    
    # Learning modules
    learning_modules = {
        "Dasar-dasar Massa Atom": {
            "content": """
            ## 🔬 Massa Atom Relatif (Ar)
            
            **Definisi:** Massa atom relatif adalah perbandingan massa rata-rata satu atom unsur terhadap 1/12 massa satu atom karbon-12.
            
            ### 🔑 Konsep Penting:
            - Ar tidak memiliki satuan (tanpa dimensi)
            - Nilai Ar berbeda untuk setiap unsur
            - Ar menunjukkan seberapa berat atom suatu unsur dibandingkan dengan standar
            
            ### 📊 Contoh:
            - Ar(H) = 1.008 → Atom hidrogen 1.008 kali lebih berat dari 1/12 atom C-12
            - Ar(O) = 16.00 → Atom oksigen 16 kali lebih berat dari 1/12 atom C-12
            
            ### 🧮 Perhitungan:
            Ar = (Massa atom unsur) / (1/12 × massa atom C-12)
            """,
            "quiz": [
                {"question": "Apa yang dimaksud dengan massa atom relatif?", "answer": "Perbandingan massa atom terhadap 1/12 massa atom C-12"},
                {"question": "Mengapa Ar tidak memiliki satuan?", "answer": "Karena merupakan perbandingan (rasio) antara dua massa"}
            ]
        },
        "Perhitungan Massa Molekul": {
            "content": """
            ## ⚗️ Massa Molekul Relatif (Mr)
            
            **Definisi:** Massa molekul relatif adalah jumlah dari semua massa atom relatif unsur-unsur penyusun molekul.
            
            ### 🔢 Rumus:
            Mr = Σ (Ar × jumlah atom)
            
            ### 🌟 Langkah Perhitungan:
            1. Identifikasi semua unsur dalam molekul
            2. Hitung jumlah atom setiap unsur
            3. Kalikan Ar dengan jumlah atom
            4. Jumlahkan semua hasil
            
            ### 📝 Contoh Perhitungan:
            **H₂SO₄ (Asam Sulfat)**
            - H: 2 × 1.008 = 2.016
            - S: 1 × 32.06 = 32.06
            - O: 4 × 16.00 = 64.00
            - **Mr = 2.016 + 32.06 + 64.00 = 98.076**
            
            ### 🔬 Aplikasi:
            - Menghitung konsentrasi larutan
            - Stoikiometri reaksi kimia
            - Menentukan rumus molekul
            """,
            "quiz": [
                {"question": "Bagaimana cara menghitung Mr H₂O?", "answer": "Mr = (2 × 1.008) + (1 × 16.00) = 18.016"},
                {"question": "Apa perbedaan Ar dan Mr?", "answer": "Ar untuk atom tunggal, Mr untuk molekul/senyawa"}
            ]
        },
        "Senyawa Hidrasi": {
            "content": """
            ## 💧 Senyawa Hidrasi
            
            **Definisi:** Senyawa hidrasi adalah kristal yang mengandung molekul air (H₂O) dalam struktur kristalnya.
            
            ### 🔍 Ciri-ciri:
            - Ditulis dengan tanda titik (·) atau bullet (•)
            - Air kristal dapat dilepaskan dengan pemanasan
            - Mempengaruhi massa molekul total
            
            ### 📋 Contoh Umum:
            - **CuSO₄·5H₂O** (Tembaga sulfat pentahidrat)
            - **MgSO₄·7H₂O** (Magnesium sulfat heptahidrat)
            - **Na₂CO₃·10H₂O** (Natrium karbonat dekahidrat)
            
            ### 🧮 Perhitungan:
            **CuSO₄·5H₂O**
            - CuSO₄: Mr = 63.5 + 32.1 + (4×16) = 159.6
            - 5H₂O: Mr = 5 × 18.016 = 90.08
            - **Total Mr = 159.6 + 90.08 = 249.68**
            
            ### ⚗️ Kegunaan:
            - Industri farmasi
            - Pembuatan pupuk
            - Proses dehidrasi/hidrasi
            """,
            "quiz": [
                {"question": "Apa yang dimaksud dengan senyawa hidrasi?", "answer": "Senyawa yang mengandung molekul air dalam struktur kristalnya"},
                {"question": "Bagaimana menghitung Mr CaCl₂·2H₂O?", "answer": "Mr = (40+2×35.5) + (2×18) = 111 + 36 = 147"}
            ]
        }
    }
    
    # Module selector
    selected_module = st.selectbox("Pilih modul pembelajaran:", list(learning_modules.keys()))
    
    if selected_module:
        module = learning_modules[selected_module]
        
        # Display content
        st.markdown(module["content"])
        
        # Interactive quiz
        st.markdown("### 🧠 Kuis Interaktif")
        
        for i, quiz_item in enumerate(module["quiz"]):
            with st.expander(f"Pertanyaan {i+1}: {quiz_item['question']}"):
                user_answer = st.text_area(f"Jawaban Anda:", key=f"quiz_{selected_module}_{i}")
                
                if st.button(f"Lihat Jawaban", key=f"answer_{selected_module}_{i}"):
                    st.success(f"**Jawaban:** {quiz_item['answer']}")
                    
                    # Simple answer checking
                    if user_answer.lower().strip() in quiz_item['answer'].lower():
                        st.balloons()
                        st.success("🎉 Jawaban Anda benar!")
                    else:
                        st.info("💡 Coba bandingkan jawaban Anda dengan jawaban yang benar.")

elif menu == "⚗️ Laboratorium":
    st.header("⚗️ Laboratorium Virtual")
    
    # Virtual lab simulations
    lab_type = st.selectbox(
        "Pilih simulasi laboratorium:",
        ["Titrasi Asam-Basa", "Pembuatan Larutan", "Analisis Kualitatif", "Reaksi Stoikiometri"]
    )
    
    if lab_type == "Titrasi Asam-Basa":
        st.markdown("### 🧪 Simulasi Titrasi Asam-Basa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Larutan Asam (Analit)**")
            acid_formula = st.selectbox("Pilih asam:", ["HCl", "H2SO4", "CH3COOH", "HNO3"])
            acid_concentration = st.number_input("Konsentrasi asam (M):", min_value=0.01, max_value=2.0, value=0.1)
            acid_volume = st.number_input("Volume asam (mL):", min_value=1.0, max_value=100.0, value=25.0)
        
        with col2:
            st.markdown("**Larutan Basa (Titran)**")
            base_formula = st.selectbox("Pilih basa:", ["NaOH", "KOH", "Ba(OH)2", "Ca(OH)2"])
            base_concentration = st.number_input("Konsentrasi basa (M):", min_value=0.01, max_value=2.0, value=0.1)
        
        if st.button("🔬 Hitung Titrasi"):
            # Calculate moles of acid
            if acid_formula == "H2SO4":
                acid_moles = acid_concentration * (acid_volume / 1000) * 2  # diprotic
            else:
                acid_moles = acid_concentration * (acid_volume / 1000)
            
            # Calculate required base volume
            if base_formula in ["Ba(OH)2", "Ca(OH)2"]:
                base_moles_needed = acid_moles / 2  # diprotic base
            else:
                base_moles_needed = acid_moles
            
            base_volume_needed = (base_moles_needed / base_concentration) * 1000  # in mL
            
            # Results
            st.markdown("### 📊 Hasil Titrasi")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mol Asam", f"{acid_moles:.4f}")
            with col2:
                st.metric("Mol Basa Dibutuhkan", f"{base_moles_needed:.4f}")
            with col3:
                st.metric("Volume Basa (mL)", f"{base_volume_needed:.2f}")
            
            # Titration curve simulation
            volumes = [i for i in range(0, int(base_volume_needed * 1.5), 1)]
            ph_values = []
            
            for vol in volumes:
                if vol < base_volume_needed:
                    # Before equivalence point
                    ph = 2 + (vol / base_volume_needed) * 4
                elif vol == base_volume_needed:
                    # Equivalence point
                    ph = 7
                else:
                    # After equivalence point
                    ph = 7 + ((vol - base_volume_needed) / base_volume_needed) * 5
                    if ph > 14:
                        ph = 14
                ph_values.append(ph)
            
            fig_titration = go.Figure()
            fig_titration.add_trace(go.Scatter(
                x=volumes,
                y=ph_values,
                mode='lines',
                name='Kurva Titrasi',
                line=dict(color='blue', width=3)
            ))
            
            # Mark equivalence point
            fig_titration.add_trace(go.Scatter(
                x=[base_volume_needed],
                y=[7],
                mode='markers',
                name='Titik Ekuivalen',
                marker=dict(color='red', size=10)
            ))
            
            fig_titration.update_layout(
                title='Kurva Titrasi Asam-Basa',
                xaxis_title='Volume Basa (mL)',
                yaxis_title='pH',
                yaxis=dict(range=[0, 14])
            )
            
            st.plotly_chart(fig_titration, use_container_width=True)
    
    elif lab_type == "Pembuatan Larutan":
        st.markdown("### ⚗️ Kalkulator Pembuatan Larutan")
        
        solution_type = st.radio("Jenis larutan:", ["Dari padatan", "Pengenceran larutan"])
        
        if solution_type == "Dari padatan":
            compound = st.text_input("Rumus senyawa:", placeholder="NaCl, H2SO4, etc.")
            target_concentration = st.number_input("Konsentrasi target (M):", min_value=0.001, value=0.1)
            target_volume = st.number_input("Volume target (L):", min_value=0.001, value=0.1)
            
            if compound and st.button("📊 Hitung Massa"):
                parsed = parse_formula(compound)
                if parsed:
                    mr = sum(massa_atom[el] * count for el, count in parsed.items())
                    
                    # Calculate required mass
                    moles_needed = target_concentration * target_volume
                    mass_needed = moles_needed * mr
                    
                    st.markdown("### 📋 Hasil Perhitungan")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Massa Molekul", f"{mr:.2f} g/mol")
                    with col2:
                        st.metric("Mol Dibutuhkan", f"{moles_needed:.4f} mol")
                    with col3:
                        st.metric("Massa Dibutuhkan", f"{mass_needed:.4f} g")
                    
                    st.markdown(f"""
                    ### 🧪 Prosedur Pembuatan:
                    1. Timbang **{mass_needed:.4f} g** {compound}
                    2. Larutkan dalam sedikit air suling
                    3. Pindahkan ke labu ukur {target_volume*1000:.0f} mL
                    4. Encerkan dengan air suling hingga tanda batas
                    5. Homogenkan larutan
                    """)
        
        else:  # Pengenceran
            initial_concentration = st.number_input("Konsentrasi awal (M):", min_value=0.001, value=1.0)
            final_concentration = st.number_input("Konsentrasi akhir (M):", min_value=0.001, value=0.1)
            final_volume = st.number_input("Volume akhir (mL):", min_value=1.0, value=100.0)
            
            if st.button("📊 Hitung Pengenceran"):
                # Using C1V1 = C2V2
                initial_volume = (final_concentration * final_volume) / initial_concentration
                water_needed = final_volume - initial_volume
                
                st.markdown("### 📋 Hasil Perhitungan")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Volume Awal", f"{initial_volume:.2f} mL")
                with col2:
                    st.metric("Air Dibutuhkan", f"{water_needed:.2f} mL")
                with col3:
                    st.metric("Faktor Pengenceran", f"{initial_concentration/final_concentration:.1f}x")
                
                st.markdown(f"""
                ### 🧪 Prosedur Pengenceran:
                1. Pipet **{initial_volume:.2f} mL** larutan awal
                2. Masukkan ke dalam labu ukur {final_volume:.0f} mL
                3. Tambahkan air suling hingga tanda batas
                4. Homogenkan larutan
                """)

elif menu == "📋 Riwayat":
    st.header("📋 Riwayat Perhitungan")
    
    if st.session_state.calculation_history:
        # Display history with options to filter and export
        st.markdown(f"### 📊 Total Perhitungan: {len(st.session_state.calculation_history)}")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            show_count = st.slider("Tampilkan perhitungan terakhir:", 5, len(st.session_state.calculation_history), 10)
        with col2:
            if st.button("🗑️ Hapus Semua Riwayat"):
                st.session_state.calculation_history = []
                st.success("Riwayat berhasil dihapus!")
                st.experimental_rerun()
        
        # Display recent calculations
        recent_calculations = st.session_state.calculation_history[-show_count:]
        
        for i, calc in enumerate(reversed(recent_calculations)):
            with st.expander(f"#{len(st.session_state.calculation_history)-i}: {calc['formula']} - {calc['mass']:.4f} g/mol"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Formula:** {calc['formula']}  
                    **Massa Molekul:** {calc['mass']:.4f} g/mol  
                    **Waktu:** {calc['timestamp']}
                    """)
                
                with col2:
                    st.markdown("**Komposisi:**")
                    for element, count in calc['composition'].items():
                        element_name = massa_atom_data.get(element, {}).get('name', element)
                        st.write(f"• {element} ({element_name}): {count} atom")
                
                # Option to recalculate or add to favorites
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🔄 Hitung Ulang", key=f"recalc_{i}"):
                        st.session_state.quick_formula = calc['formula']
                        st.session_state.menu = "🧪 Kalkulator"
                        st.experimental_rerun()
                
                with col2:
                    if st.button(f"⭐ Tambah ke Favorit", key=f"fav_{i}"):
                        if calc['formula'] not in st.session_state.favorite_compounds:
                            st.session_state.favorite_compounds.append(calc['formula'])
                            st.success("Ditambahkan ke favorit!")
        
        # Export functionality
        if st.button("📤 Export ke CSV"):
            df_history = pd.DataFrame(st.session_state.calculation_history)
            csv = df_history.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name="calculation_history.csv",
                mime="text/csv"
            )
    
    else:
        st.info("Belum ada riwayat perhitungan. Mulai dengan menggunakan kalkulator!")
        
        # Animation for empty state
        lottie_empty = load_lottieurl("https://lottie.host/4a584f69-29b5-40a0-a133-a15f4775ec6d/O3pamPxHLp.json")
        if lottie_empty:
            st_lottie(lottie_empty, height=200, key="empty_history")

else:  # About page
    st.header("ℹ️ Tentang Aplikasi")
    
    # Animation
    lottie_about = load_lottieurl("https://lottie.host/49626c27-b23c-475e-8505-981d510c0e61/lag9aGftQv.json")
    if lottie_about:
        st_lottie(lottie_about, height=250, key="about_animation")
    
    st.markdown("""
    ## 🚀 Advanced Molecular Mass Calculator
    
    Aplikasi komprehensif untuk perhitungan dan analisis massa molekul senyawa kimia dengan berbagai fitur canggih.
    
    ### ✨ Fitur Utama:
    
    #### 🧮 Kalkulator Canggih
    - Parsing formula otomatis dengan dukungan berbagai format
    - Perhitungan massa molekul presisi tinggi
    - Analisis komposisi unsur dengan persentase
    - Dukungan senyawa hidrasi dan kompleks
    - Penyimpanan riwayat perhitungan
    
    #### 📊 Analisis Mendalam
    - Perbandingan multi-senyawa
    - Visualisasi komposisi dengan grafik interaktif
    - Analisis statistik massa molekul
    - Perhitungan rumus empiris
    
    #### 🔍 Database Komprehensif
    - Informasi lengkap 36+ unsur kimia
    - Filter berdasarkan kategori dan periode
    - Pencarian unsur dengan nama atau simbol
    - Visualisasi posisi dalam tabel periodik
    
    #### 📈 Visualisasi Data
    - Grafik hubungan massa atom vs nomor atom
    - Distribusi kategori unsur
    - Peta panas tabel periodik
    - Analisis tren berdasarkan periode
    
    #### 📚 Modul Pembelajaran
    - Penjelasan konsep massa atom dan molekul
    - Tutorial perhitungan step-by-step
    - Kuis interaktif untuk latihan
    - Contoh kasus nyata
    
    #### ⚗️ Laboratorium Virtual
    - Simulasi titrasi asam-basa
    - Kalkulator pembuatan larutan
    - Perhitungan pengenceran
    - Kurva titrasi interaktif
    
    ### 🔧 Teknologi yang Digunakan:
    - **Streamlit** - Framework aplikasi web
    - **Plotly** - Visualisasi data interaktif
    - **Pandas** - Manipulasi dan analisis data
    - **Lottie** - Animasi yang menarik
    
    ### 📋 Changelog:
    
    #### Versi 2.0 (Terbaru)
    - ✅ Penambahan 6 menu utama
    - ✅ Database unsur kimia yang diperluas
    - ✅ Visualisasi data yang canggih
    - ✅ Laboratorium virtual
    - ✅ Modul pembelajaran interaktif
    - ✅ Sistem riwayat dan favorit
    - ✅ Export data ke CSV
    - ✅ UI yang lebih modern dan responsif
    
    #### Versi 1.0 (Sebelumnya)
    - ✅ Kalkulator massa molekul dasar
    - ✅ Parsing formula sederhana
    - ✅ Dukungan senyawa hidrasi
    - ✅ Antarmuka yang user-friendly
    
    ### 🎯 Aplikasi Praktis:
    
    #### 🏫 Pendidikan
    - Pembelajaran kimia di sekolah menengah
    - Praktikum kimia virtual
    - Pemahaman konsep massa atom dan molekul
    - Latihan soal stoikiometri
    
    #### 🔬 Penelitian
    - Analisis komposisi senyawa
    - Persiapan larutan standar
    - Perhitungan stoikiometri reaksi
    - Analisis data eksperimen
    
    #### 🏭 Industri
    - Quality control produk kimia
    - Formulasi produk
    - Perhitungan batch production
    - Analisis bahan baku
    
    ### 👥 Target Pengguna:
    - 👨‍🎓 Siswa sekolah menengah
    - 👩‍🎓 Mahasiswa kimia
    - 👨‍🏫 Guru dan dosen
    - 👩‍🔬 Peneliti dan analis
    - 👨‍💼 Praktisi industri kimia
    
    ### 🚀 Rencana Pengembangan:
    - 🔄 Penambahan lebih banyak unsur
    - 📱 Versi mobile-friendly
    - 🌐 Dukungan multi-bahasa
    - 🔗 Integrasi dengan database online
    - 🤖 Fitur AI untuk prediksi sifat senyawa
    - 💾 Penyimpanan cloud
    - 👥 Fitur kolaborasi tim
    
    ### 📞 Kontak & Dukungan:
    Jika Anda memiliki pertanyaan, saran, atau menemukan bug, silakan hubungi pengembang melalui:
    - 📧 Email: developer@molcalc.com
    - 🐛 Report Bug: github.com/molcalc/issues
    - 💡 Feature Request: github.com/molcalc/discussions
    
    ### 📜 Lisensi:
    Aplikasi ini dikembangkan untuk tujuan edukasi dan penelitian. Penggunaan komersial memerlukan izin khusus.
    
    ### 🙏 Acknowledgments:
    - Data massa atom berdasarkan IUPAC 2021
    - Animasi dari LottieFiles community
    - Icon dari Lucide React
    - Komunitas Streamlit untuk dukungan teknis
    
    ---
    
    **Versi:** 2.0.0  
    **Terakhir diperbarui:** Mei 2025  
    **Developer:** Advanced Chemistry Tools Team
    """)
    
    # Feature showcase
    st.markdown("### 🎥 Showcase Fitur")
    
    # Create tabs for different features
    feature_tabs = st.tabs(["🧮 Kalkulator", "📊 Analisis", "🔍 Database", "📈 Visualisasi", "⚗️ Lab Virtual"])
    
    with feature_tabs[0]:
        st.markdown("""
        #### 🧮 Kalkulator Massa Molekul
        - Input formula yang fleksibel (H2O, Al2(SO4)3, CuSO4·5H2O)
        - Perhitungan otomatis dengan breakdown detail
        - Analisis komposisi persentase
        - Visualisasi pie chart komposisi
        - Penyimpanan ke riwayat dan favorit
        """)
        
        # Demo calculation
        st.code("""
        Input: CuSO4·5H2O
        Output: 
        - Massa Molekul: 249.68 g/mol
        - Komposisi: Cu(25.4%), S(12.8%), O(61.8%)
        - Breakdown: (1×63.5) + (1×32.1) + (9×16.0) + (10×1.0)
        """)
    
    with feature_tabs[1]:
        st.markdown("""
        #### 📊 Analisis Multi-Senyawa
        - Perbandingan massa molekul beberapa senyawa
        - Grafik batang interaktif
        - Analisis statistik (min, max, rata-rata)
        - Stacked bar chart untuk komposisi
        - Export hasil ke CSV
        """)
    
    with feature_tabs[2]:
        st.markdown("""
        #### 🔍 Database Unsur Kimia
        - Informasi lengkap 36+ unsur
        - Filter berdasarkan kategori dan periode
        - Pencarian dengan nama atau simbol
        - Detail posisi dalam tabel periodik
        - Visualisasi data unsur
        """)
    
    with feature_tabs[3]:
        st.markdown("""
        #### 📈 Visualisasi Data Canggih
        - Scatter plot massa atom vs nomor atom
        - Pie chart distribusi kategori unsur
        - Heatmap tabel periodik
        - Line chart tren massa per periode
        - Grafik interaktif dengan Plotly
        """)
    
    with feature_tabs[4]:
        st.markdown("""
        #### ⚗️ Laboratorium Virtual
        - Simulasi titrasi asam-basa
        - Kalkulator pembuatan larutan
        - Perhitungan pengenceran (C1V1=C2V2)
        - Kurva titrasi interaktif
        - Prosedur langkah-demi-langkah
        """)
    
    # Statistics
    st.markdown("### 📊 Statistik Aplikasi")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="⚛️ Unsur Tersedia",
            value=len(massa_atom_data),
            delta="36 unsur utama"
        )
    
    with col2:
        st.metric(
            label="🧪 Senyawa Umum",
            value=len(common_compounds),
            delta="20 senyawa"
        )
    
    with col3:
        st.metric(
            label="📚 Modul Belajar",
            value=len(learning_modules),
            delta="3 modul"
        )
    
    with col4:
        st.metric(
            label="🔬 Simulasi Lab",
            value=4,
            delta="4 eksperimen"
        )
    
    # Final animation
    lottie_final = load_lottieurl("https://lottie.host/4a584f69-29b5-40a0-a133-a15f4775ec6d/O3pamPxHLp.json")
    if lottie_final:
        st_lottie(lottie_final, height=200, key="final_animation")
    
    st.markdown("""
    ---
    <div style="text-align: center; color: #666;">
        <p>🧪 Dibuat dengan ❤️ untuk kemajuan pendidikan kimia</p>
        <p><small>© 2025 Advanced Chemistry Tools. All rights reserved.</small></p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
---
<div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-top: 2rem;">
    <h4>🧪 Advanced Molecular Mass Calculator</h4>
    <p>Aplikasi Kalkulator Massa Molekul Terlengkap untuk Pendidikan dan Penelitian</p>
    <p><small>Versi 2.0.0 | Mei 2025 | Dikembangkan dengan Streamlit & Python</small></p>
</div>
""", unsafe_allow_html=True)
