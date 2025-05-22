from streamlit_lottie import st_lottie
import requests
import streamlit as st
import re
from collections import defaultdict

# Fungsi memuat animasi Lottie dari URL
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Konfigurasi halaman
st.set_page_config(page_title="Kalkulator Massa Relatif", layout="centered")
st.title("Kalkulator Massa Relatif")

# Inisialisasi menu aktif jika belum ada
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Beranda"

# Fungsi untuk set menu saat tombol diklik
def set_menu_beranda():
    st.session_state.menu = "🏠 Beranda"

def set_menu_kalkulator():
    st.session_state.menu = "🧪 Kalkulator"

def set_menu_tentang():
    st.session_state.menu = "ℹ️ Tentang"

# Sidebar dengan animasi dan tombol navigasi
with st.sidebar:
    lottie_json = load_lottieurl("https://lottie.host/a64c7ff9-346e-4e72-b656-e337097d3bde/yHrJbTdVlE.json")
    if lottie_json:
        st_lottie(lottie_json, height=200, key="navigasi")

    if st.button("🏠 Beranda"):
        set_menu_beranda()
    if st.button("🧪 Kalkulator"):
        set_menu_kalkulator()
    if st.button("ℹ️ Tentang"):
        set_menu_tentang()

menu = st.session_state.menu

# Data massa atom relatif
massa_atom = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81, "C": 12.01,
    "N": 14.007, "O": 16.00, "F": 18.998, "Ne": 20.180, "Na": 22.990, "Mg": 24.305,
    "Al": 26.982, "Si": 28.085, "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.948,
    "K": 39.098, "Ca": 40.078, "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996,
    "Mn": 54.938, "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.63, "As": 74.922, "Se": 78.971, "Br": 79.904, "Kr": 83.798,
    "Rb": 85.468, "Sr": 87.62, "Y": 88.906, "Zr": 91.224, "Nb": 92.906, "Mo": 95.95,
    "Tc": 98, "Ru": 101.07, "Rh": 102.91, "Pd": 106.42, "Ag": 107.87, "Cd": 112.41,
    "In": 114.82, "Sn": 118.71, "Sb": 121.76, "Te": 127.60, "I": 126.90, "Xe": 131.29,
    "Cs": 132.91, "Ba": 137.33, "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24,
    "Pm": 145, "Sm": 150.36, "Eu": 151.96, "Gd": 157.25, "Tb": 158.93, "Dy": 162.50,
    "Ho": 164.93, "Er": 167.26, "Tm": 168.93, "Yb": 173.05, "Lu": 174.97, "Hf": 178.49,
    "Ta": 180.95, "W": 183.84, "Re": 186.21, "Os": 190.23, "Ir": 192.22, "Pt": 195.08,
    "Au": 196.97, "Hg": 200.59, "Tl": 204.38, "Pb": 207.2, "Bi": 208.98, "Po": 209,
    "At": 210, "Rn": 222, "Fr": 223, "Ra": 226, "Ac": 227, "Th": 232.04, "Pa": 231.04,
    "U": 238.03, "Np": 237, "Pu": 244, "Am": 243, "Cm": 247, "Bk": 247, "Cf": 251,
    "Es": 252, "Fm": 257, "Md": 258, "No": 259, "Lr": 266, "Rf": 267, "Db": 268,
    "Sg": 269, "Bh": 270, "Hs": 277, "Mt": 278, "Ds": 281, "Rg": 282, "Cn": 285,
    "Fl": 289, "Lv": 293, "Ts": 294, "Og": 294
}

# Fungsi parsing rumus kimia
def parse_formula(formula):
    formula = formula.replace("·", ".")
    parts = formula.split(".")
    total_elements = defaultdict(int)

    def parse(part, multiplier=1):
        stack = []
        i = 0
        while i < len(part):
            if part[i] == "(":
                stack.append(({}, multiplier))
                i += 1
            elif part[i] == ")":
                i += 1
                num = ""
                while i < len(part) and part[i].isdigit():
                    num += part[i]
                    i += 1
                group_multiplier = int(num) if num else 1
                group_dict, _ = stack.pop()
                for el, count in group_dict.items():
                    if stack:
                        stack[-1][0][el] = stack[-1][0].get(el, 0) + count * group_multiplier
                    else:
                        total_elements[el] += count * group_multiplier * multiplier
            else:
                match = re.match(r'([A-Z][a-z]?)(\d*)', part[i:])
                if not match:
                    st.warning(f"Format tidak dikenali: '{part[i:]}'")
                    return None
                el = match.group(1)
                count = int(match.group(2)) if match.group(2) else 1
                i += len(match.group(0))
                if el not in massa_atom:
                    st.warning(f"Unsur '{el}' tidak dikenali.")
                    return None
                if stack:
                    stack[-1][0][el] = stack[-1][0].get(el, 0) + count
                else:
                    total_elements[el] += count * multiplier

    for part in parts:
        match = re.match(r'^(\d+)([A-Z(].*)', part)
        mul = int(match.group(1)) if match else 1
        formula_part = match.group(2) if match else part
        parse(formula_part, multiplier=mul)

    return total_elements

# Menu konten utama
if menu == "🏠 Beranda":
    st.header("Selamat Datang di Kalkulator Massa Relatif")
    lottie_json = load_lottieurl("https://lottie.host/b592895d-f9e1-43b1-bf8e-dea5b80b8a25/h9K58rIqKT.json")
    if lottie_json:
        st_lottie(lottie_json, height=250, key="beranda")
    st.write("""
        Aplikasi ini membantu Anda menghitung massa relatif dari suatu unsur atau senyawa 
        berdasarkan rumus kimia yang diberikan. 
        Gunakan menu di samping untuk mulai menggunakan kalkulator atau mempelajari lebih lanjut.
    """)
    st.subheader("🔬 Tabel Periodik Unsur Kimia")
    st.image("https://wallpapercave.com/wp/wp2871063.jpg", caption="Tabel Periodik Unsur")

elif menu == "🧪 Kalkulator":
    st.header("Kalkulator Massa Relatif")
    st.markdown("""
    📌 **Petunjuk Penggunaan:**
    - Masukkan rumus kimia unsur atau senyawa, misalnya:
      - `H2O` untuk air
      - `Al2(SO4)3` untuk aluminium sulfat
      - `CuSO4·5H2O` untuk tembaga(II) sulfat pentahidrat
    - Gunakan tanda kurung `()` untuk kelompok atom.
    - Gunakan titik atau tanda `·` (tengah) untuk senyawa hidrasi.
    """)

    lottie_json = load_lottieurl("https://lottie.host/5ee6c7e7-3c7b-473f-b75c-df412fe210cc/kF9j77AAsG.json")
    if lottie_json:
        st_lottie(lottie_json, height=250, key="kalkulator")

    formula = st.text_input("Masukkan rumus kimia (misalnya: H2O, Al2(SO4)3, CuSO4·5H2O):")
    hitung = st.button("🔍 Hitung Massa Relatif")

    if hitung and formula:
        parsed = parse_formula(formula)
        if parsed:
            detail = []
            massa_total = 0
            for el, n in parsed.items():
                massa = massa_atom[el]
                subtotal = massa * n
                massa_total += subtotal
                detail.append(f"({n} × {massa:.3f})")
            st.markdown(f"**Mr({formula}) = {' + '.join(detail)} = {massa_total:.2f} g/mol**")
            st.success(f"Massa relatif dari {formula} adalah {massa_total:.2f} g/mol")
        else:
            st.error("Gagal menghitung. Pastikan rumus kimia valid dan elemen dikenali.")

elif menu == "ℹ️ Tentang":
    st.header("Tentang Aplikasi Ini")
    lottie_json = load_lottieurl("https://lottie.host/49626c27-b23c-475e-8505-981d510c0e61/lag9aGftQv.json")
    if lottie_json:
        st_lottie(lottie_json, height=250, key="tentang")

    st.write("""
        Aplikasi ini dikembangkan menggunakan Streamlit dan bertujuan untuk membantu siswa dan guru
        dalam menghitung massa relatif zat kimia secara cepat dan interaktif.Selain menghitung masa 
        relatif zat kimia, aplikasi ini juga dapat memberikan informasi tentang masa atom relatif (Ar).
    """)

    lottie_json2 = load_lottieurl("https://lottie.host/4a584f69-29b5-40a0-a133-a15f4775ec6d/O3pamPxHLp.json")
    if lottie_json2:
        st_lottie(lottie_json2, height=250, key="tentang2")

    st.header("Apa Itu Massa Relatif (Mr)?")
    st.write("""
    **Massa Relatif (Mr)** adalah jumlah dari massa atom relatif (Ar) semua unsur dalam rumus kimia suatu senyawa.

    - Mr tidak memiliki satuan karena merupakan perbandingan massa.
    - Mr dihitung dengan menjumlahkan massa relatif tiap atom dikalikan dengan jumlah atomnya dalam satu molekul.

    ### Contoh Perhitungan:
    Untuk air (**H₂O**):
    - Ar(H) = 1.008 → 2 × 1.008 = 2.016
    - Ar(O) = 16.00 → 1 × 16.00 = 16.00
    - **Mr(H₂O) = 2.016 + 16.00 = 18.016**

    ### Pentingnya Mr:
    - Membantu menghitung **massa molar** dalam gram per mol (g/mol).
    - Berguna dalam perhitungan stoikiometri, hukum dasar kimia, dan reaksi kimia.

    ### Perbedaan Ar dan Mr:
    - **Ar (massa atom relatif)**: massa satu atom relatif terhadap 1/12 massa karbon-12.
    - **Mr (massa relatif molekul)**: total massa atom dalam satu molekul senyawa.
    """)
