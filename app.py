import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y TEMA CAFÉ 32
# ==========================================
st.set_page_config(
    page_title="CAFÉ 32 - Control de Stock y Panadería",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Nunito:wght@400;600;700&display=swap');

    :root {
        --bg-hueso: #F5F2EB;
        --card-hueso: #FAF8F5;
        --verde-cafe: #1D3328;
        --verde-hover: #2B4C3C;
        --verde-claro: #E8EFEB;
        --texto-oscuro: #2C3531;
        --texto-mutado: #6B7280;
        --border-color: #E2DDD5;
    }

    .stApp {
        background-color: var(--bg-hueso);
        font-family: 'Nunito', sans-serif;
        color: var(--texto-oscuro);
    }

    section[data-testid="stSidebar"] {
        background-color: #EFEBE0 !important;
        border-right: 1px solid var(--border-color);
    }

    .header-banner {
        background-color: var(--card-hueso);
        border: 2px solid var(--border-color);
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 12px rgba(29, 51, 40, 0.04);
    }

    .logo-32-container {
        display: inline-flex;
        align-items: center;
        gap: 12px;
    }

    .logo-32-svg {
        width: 65px;
        height: 65px;
    }

    .header-title-box h1 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        color: var(--verde-cafe);
        margin: 0;
        font-size: 24px;
        letter-spacing: -0.5px;
    }

    .header-title-box p {
        margin: 0;
        color: var(--texto-mutado);
        font-size: 13px;
        font-weight: 600;
    }

    .custom-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    .stButton>button {
        background-color: var(--verde-cafe) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background-color: var(--verde-hover) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(29, 51, 40, 0.2);
    }

    .role-badge {
        background-color: var(--verde-claro);
        color: var(--verde-cafe);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid rgba(29, 51, 40, 0.15);
    }

    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }

    .section-header {
        font-family: 'Montserrat', sans-serif;
        color: var(--verde-cafe);
        font-weight: 700;
        font-size: 18px;
        border-left: 4px solid var(--verde-cafe);
        padding-left: 10px;
        margin-bottom: 15px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS LOCAL
# ==========================================
DB_FILE = "cafe32_panaderia.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            producto TEXT,
            unidad_medida TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora TEXT,
            tipo_accion TEXT,
            empleado TEXT,
            observaciones TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora TEXT,
            empleado TEXT,
            producto TEXT,
            categoria TEXT,
            unidad TEXT,
            ingreso REAL,
            sobrante REAL,
            merma REAL,
            motivo_merma TEXT
        )
    ''')
    
    c.execute("SELECT COUNT(*) FROM catalogo")
    if c.fetchone()[0] == 0:
        productos_iniciales = [
            ("Panificación por Kg", "Pan", "Kg"),
            ("Panificación por Kg", "Galleta", "Kg"),
            ("Panificación por Kg", "Criollos", "Kg"),
            ("Panificación por Kg", "Chipá", "Kg"),
            ("Panificación por Unidad", "Pan de molde blanco", "Unidad"),
            ("Especiales", "Prepizza", "Unidad"),
            ("Individuales", "Cookies classics", "Unidad"),
            ("Facturas", "Medialunas de manteca", "Unidad"),
            ("Porciones de Torta", "Chocotorta", "Unidad"),
            ("Pastelería", "Pastafrola", "Unidad")
        ]
        c.executemany("INSERT INTO catalogo (categoria, producto, unidad_medida) VALUES (?, ?, ?)", productos_iniciales)
        
    conn.commit()
    conn.close()

init_db()

EMPLEADOS = [
    "Candela Nasca",
    "Lucia Crispens",
    "Israel Cabrera",
    "Priscila Frick",
    "Ariana Torres",
    "Melania Classen"
]

LOGO_32_SVG = """
<svg class="logo-32-svg" viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="160" height="160" rx="20" fill="#1D3328"/>
    <path d="M35 45 H70 C85 45 85 65 70 65 H55 H70 C88 65 88 95 68 95 H35 V80 H65 C72 80 72 72 65 72 H48 V58 H65 C72 58 72 52 65 52 H35 V45 Z" fill="#F5F2EB"/>
    <path d="M85 45 H120 C130 45 135 55 125 68 L95 102 V115 H135 V100 H110 L130 78 C145 60 138 45 120 45 Z" fill="#F5F2EB"/>
    <path d="M68 65 L78 65 L73 72 Z" fill="#1D3328"/>
</svg>
"""

# ==========================================
# MANEJO DE SESIÓN Y LOGIN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""

def login(usuario, password):
    if usuario == "panadería@cafe32" and password == "1234":
        st.session_state.logged_in = True
        st.session_state.user_role = "empleado"
        st.session_state.username = usuario
        st.success("¡Bienvenido/a al Panel de Panadería!")
        st.rerun()
    elif usuario == "administrador@cafe32" and password == "cafe32":
        st.session_state.logged_in = True
        st.session_state.user_role = "admin"
        st.session_state.username = usuario
        st.success("¡Bienvenido/a Administrador!")
        st.rerun()
    else:
        st.error("Usuario o contraseña incorrectos")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""
    st.rerun()

# ==========================================
# PANTALLA DE LOGIN
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; background-color: #FAF8F5; padding: 30px; border-radius: 16px; border: 2px solid #E2DDD5; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                {LOGO_32_SVG}
                <h1 style="color: #1D3328; font-family: 'Montserrat', sans-serif; font-weight: 800; margin-top: 15px; margin-bottom: 5px;">CAFÉ 32</h1>
                <p style="color: #6B7280; font-weight: 600; margin-bottom: 25px;">Sistema Integrado de Control de Stock y Panadería</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Usuario", placeholder="ej. panadería@cafe32 o administrador@cafe32")
            pass_input = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if submit_login:
                login(user_input, pass_input)
    st.stop()

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.markdown(f"""
    <div class="header-banner">
        <div class="logo-32-container">
            {LOGO_32_SVG}
            <div class="header-title-box">
                <h1>CAFÉ 32</h1>
                <p>Gestión Inteligente de Panadería & Mermas</p>
            </div>
        </div>
        <div>
            <span class="role-badge">{'Administrador' if st.session_state.user_role == 'admin' else 'Empleado de Panadería'}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"**Usuario:** `{st.session_state.username}`")
    st.markdown("---")
    if st.button("Cerrar Sesión", use_container_width=True):
        logout()

if st.session_state.user_role == "empleado":
    st.markdown("<div class='section-header'>MÓDULO DE EMPLEADOS</div>", unsafe_allow_html=True)
    st.info("Funciones de empleado activas.")
elif st.session_state.user_role == "admin":
    st.markdown("<div class='section-header'>PANEL DE CONTROL ADMINISTRATIVO</div>", unsafe_allow_html=True)
    st.info("Funciones de administrador activas.")
