import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y DISEÑO CAFÉ 32
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
        width: 60px;
        height: 60px;
    }

    .header-title-box h1 {
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        color: var(--verde-cafe);
        margin: 0;
        font-size: 22px;
    }

    .header-title-box p {
        margin: 0;
        color: var(--texto-mutado);
        font-size: 13px;
        font-weight: 600;
    }

    .stButton>button {
        background-color: var(--verde-cafe) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
    }

    .stButton>button:hover {
        background-color: var(--verde-hover) !important;
    }

    .role-badge {
        background-color: var(--verde-claro);
        color: var(--verde-cafe);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        border: 1px solid rgba(29, 51, 40, 0.15);
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
# BASE DE DATOS Y CATALOGO
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
        CREATE TABLE IF NOT EXISTS registros_diarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            empleado_apertura TEXT,
            empleado_cierre TEXT,
            producto TEXT,
            categoria TEXT,
            unidad TEXT,
            ingreso REAL,
            sobrante REAL,
            merma REAL,
            motivo_merma TEXT,
            observaciones TEXT
        )
    ''')
    
    c.execute("SELECT COUNT(*) FROM catalogo")
    if c.fetchone()[0] == 0:
        items = [
            ("Panificación", "Pan", "Kg"), ("Panificación", "Galleta", "Kg"),
            ("Panificación", "Criollos", "Kg"), ("Panificación", "Chipá", "Kg"),
            ("Panificación", "Cuernitos", "Kg"), ("Panificación", "Bizcochitos", "Kg"),
            ("Panificación", "Pan de molde blanco", "Unidad"), ("Panificación", "Pan de molde con semillas", "Unidad"),
            ("Panificación", "Pinchadas", "Unidad"), ("Panificación", "Pan arabe x4", "Unidad"),
            ("Panificación", "Pan pebete x4", "Unidad"), ("Panificación", "Pan de hamburguesa x2", "Unidad"),
            ("Panificación", "Pan de lomita x2", "Unidad"),
            ("Especiales", "Prepizza", "Unidad"), ("Especiales", "Pizzetta", "Unidad"),
            ("Especiales", "Pebete relleno", "Unidad"), ("Especiales", "Arabe relleno", "Unidad"),
            ("Especiales", "Medialuna xl", "Unidad"), ("Especiales", "Medialuna xl rellena", "Unidad"),
            ("Especiales", "Sandwich de miga comun", "Unidad"), ("Especiales", "Sandwich de miga especial", "Unidad"),
            ("Especiales", "Sandwich de miga con pollo", "Unidad"), ("Especiales", "Panes de molde", "Unidad"),
            ("Cuartos", "Grisines", "Unidad"), ("Cuartos", "Palmeras", "Unidad"),
            ("Cuartos", "Pepas", "Unidad"), ("Cuartos", "Fosforitos", "Unidad"), ("Cuartos", "Primaveras", "Unidad"),
            ("Individuales", "Cookies classics", "Unidad"), ("Individuales", "Cookies de doble chocolate", "Unidad"),
            ("Individuales", "Cookies black", "Unidad"), ("Individuales", "Cookies oreo", "Unidad"),
            ("Individuales", "Cookies red velvet", "Unidad"), ("Individuales", "Muffins de arandanos", "Unidad"),
            ("Individuales", "Muffins de vainilla y ddl", "Unidad"), ("Individuales", "Muffins de chocolate", "Unidad"),
            ("Individuales", "Alfajores marplatenses", "Unidad"), ("Individuales", "Alfajores marplatenses glaseados", "Unidad"),
            ("Individuales", "Alfajores de cafe", "Unidad"), ("Individuales", "Alfajores de maicena", "Unidad"),
            ("Individuales", "Alfajores brownie", "Unidad"), ("Individuales", "Alfajores de coco", "Unidad"),
            ("Individuales", "Brownies", "Unidad"), ("Individuales", "Lemons", "Unidad"), ("Individuales", "Boudin del dia", "Unidad"),
            ("Facturas", "Medialunas de manteca", "Unidad"), ("Facturas", "Medialunas de grasa", "Unidad"),
            ("Facturas", "Surtidas de manteca", "Unidad"), ("Facturas", "Surtidas de grasa", "Unidad"),
            ("Facturas", "Churrines-vigilantes", "Unidad"), ("Facturas", "Hojaldres", "Unidad"),
            ("Facturas", "Pan de leche", "Unidad"), ("Facturas", "Tortillas negras", "Unidad"),
            ("Facturas", "Rolls de canela", "Unidad"), ("Facturas", "Donas simples", "Unidad"), ("Facturas", "Donas rellenas", "Unidad"),
            ("Porciones de Torta", "Chocotorta", "Unidad"), ("Porciones de Torta", "Torta vasca", "Unidad"),
            ("Porciones de Torta", "Key lime pie", "Unidad"), ("Porciones de Torta", "Tiramisu", "Unidad"),
            ("Porciones de Torta", "Cheesecake", "Unidad"), ("Porciones de Torta", "Matilda", "Unidad"),
            ("Porciones de Torta", "Selva negra", "Unidad"), ("Porciones de Torta", "Red velvet", "Unidad"),
            ("Porciones de Torta", "Lemon pie", "Unidad"), ("Porciones de Torta", "Tarta de frutillas", "Unidad"),
            ("Porciones de Torta", "Carrot cake", "Unidad"), ("Porciones de Torta", "Cheesecake frutos rojos", "Unidad"),
            ("Porciones de Torta", "Cheesecake de oreo", "Unidad"),
            ("Pasteleria", "Pastafrola", "Unidad"), ("Pasteleria", "Milhojas", "Unidad"),
            ("Pasteleria", "Milhojas chicas", "Unidad"), ("Pasteleria", "Tortas de vainilla", "Unidad"),
            ("Pasteleria", "Tortas de vainilla chicas", "Unidad"), ("Pasteleria", "Tortas de chocolate", "Unidad"),
            ("Pasteleria", "Torta de chocolate chicas", "Unidad"), ("Pasteleria", "Tarta Sofi", "Unidad"),
            ("Pasteleria", "Tarta de coco", "Unidad"), ("Pasteleria", "Porcion de pastafrola", "Unidad"),
            ("Pasteleria", "Porcion de milhojas", "Unidad"),
            ("Otros", "Masitas secas por peso", "Kg"), ("Otros", "Masitas secas en bandeja", "Unidad"),
            ("Otros", "Bombones por peso", "Kg"), ("Otros", "Bombones en bandeja", "Unidad"),
            ("Otros", "Paleta de chocolate", "Unidad")
        ]
        c.executemany("INSERT INTO catalogo (categoria, producto, unidad_medida) VALUES (?, ?, ?)", items)
        
    conn.commit()
    conn.close()

init_db()

EMPLEADOS = [
    "Candela Nasca", "Lucia Crispens", "Israel Cabrera",
    "Priscila Frick", "Ariana Torres", "Melania Classen"
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
# GESTIÓN DE SESIÓN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""

def login(usuario, password):
    # Sin tilde para evitar errores al tipear
    if usuario == "panaderia@cafe32" and password == "1234":
        st.session_state.logged_in = True
        st.session_state.user_role = "empleado"
        st.session_state.username = usuario
        st.rerun()
    elif usuario == "administrador@cafe32" and password == "cafe32":
        st.session_state.logged_in = True
        st.session_state.user_role = "admin"
        st.session_state.username = usuario
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
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; background-color: #FAF8F5; padding: 35px; border-radius: 16px; border: 2px solid #E2DDD5; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                {LOGO_32_SVG}
                <h1 style="color: #1D3328; font-family: 'Montserrat', sans-serif; font-weight: 800; margin-top: 15px; margin-bottom: 5px; font-size: 26px;">CAFÉ 32</h1>
                <p style="color: #6B7280; font-weight: 600; font-size: 14px; margin-bottom: 20px;">Control Integral de Panadería & Stock</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Usuario", placeholder="panaderia@cafe32 o administrador@cafe32")
            pass_input = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if submit_login:
                login(user_input, pass_input)
    st.stop()

# ==========================================
# ENCABEZADO Y MENÚ PRINCIPAL
# ==========================================
role_text = "Administrador" if st.session_state.user_role == 'admin' else "Personal de Turno"

st.markdown(f"""
    <div class="header-banner">
        <div class="logo-32-container">
            {LOGO_32_SVG}
            <div class="header-title-box">
                <h1>CAFÉ 32</h1>
                <p>Sistema Operativo de Control Diario</p>
            </div>
        </div>
        <div>
            <span class="role-badge">{role_text}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"**Usuario conectado:** `{st.session_state.username}`")
    st.markdown("---")
    menu_options = ["Planilla Diaria (Turnos)", "Reportes e Historial (Admin)"] if st.session_state.user_role == "admin" else ["Planilla Diaria (Turnos)"]
    menu = st.radio("Navegación", menu_options)
    st.markdown("---")
    if st.button("Cerrar Sesión", use_container_width=True):
        logout()

# ==========================================
# MÓDULO 1: PLANILLA DIARIA (APERTURA Y CIERRE)
# ==========================================
if menu == "Planilla Diaria (Turnos)":
    st.markdown("<div class='section-header'>PLANILLA DE CONTROL DIARIO</div>", unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_actual = st.date_input("Fecha de Control", value=datetime.today())
    with col_f2:
        modo_turno = st.selectbox("Momento del Registro", ["Apertura de Turno (Ingresos)", "Cierre de Turno (Sobrantes & Mermas)"])
    
    conn = sqlite3.connect(DB_FILE)
    df_cat = pd.read_sql("SELECT * FROM catalogo", conn)
    conn.close()
    
    categorias = df_cat['categoria'].unique()
    cat_seleccionada = st.selectbox("Filtrar por Categoría", categorias)
    
    productos_filtrados = df_cat[df_cat['categoria'] == cat_seleccionada]
    
    with st.form("form_turno"):
        if "Apertura" in modo_turno:
            st.subheader("Registro de Ingresos de Mercadería (Inicio)")
            emp_apertura = st.selectbox("Empleado que Abre", EMPLEADOS)
            
            ingresos_input = {}
            for idx, row in productos_filtrados.iterrows():
                ingresos_input[row['producto']] = st.number_input(f"Ingreso de {row['producto']} ({row['unidad_medida']})", min_value=0.0, step=0.5)
            
            obs = st.text_area("Observaciones de Apertura")
            submitted = st.form_submit_button("Guardar Apertura", use_container_width=True)
            
            if submitted:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                for prod, cant in ingresos_input.items():
                    unidad = productos_filtrados[productos_filtrados['producto'] == prod]['unidad_medida'].values[0]
                    c.execute("""
                        INSERT INTO registros_diarios (fecha, empleado_apertura, producto, categoria, unidad, ingreso, sobrante, merma, observaciones)
                        VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)
                    """, (str(fecha_actual), emp_apertura, prod, cat_seleccionada, unidad, cant, obs))
                conn.commit()
                conn.close()
                st.success("¡Ingresos de apertura guardados correctamente!")
        
        else:
            st.subheader("Registro de Cierre, Sobrantes y Mermas (Fin de Turno)")
            emp_cierre = st.selectbox("Empleado que Cierra", EMPLEADOS)
            
            cierre_data = {}
            for idx, row in productos_filtrados.iterrows():
                st.markdown(f"**{row['producto']} ({row['unidad_medida']})**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    sob = st.number_input(f"Sobrante {row['producto']}", min_value=0.0, step=0.5, key=f"sob_{row['producto']}")
                with c2:
                    mer = st.number_input(f"Merma {row['producto']}", min_value=0.0, step=0.5, key=f"mer_{row['producto']}")
                with c3:
                    mot = st.text_input(f"Motivo merma {row['producto']}", placeholder="Caído, roto, etc.", key=f"mot_{row['producto']}")
                cierre_data[row['producto']] = (sob, mer, mot)
            
            obs_cierre = st.text_area("Observaciones Generales de Cierre")
            submitted_cierre = st.form_submit_button("Guardar Cierre y Calcular", use_container_width=True)
            
            if submitted_cierre:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                for prod, data in cierre_data.items():
                    c.execute("""
                        UPDATE registros_diarios 
                        SET empleado_cierre = ?, sobrante = ?, merma = ?, motivo_merma = ?, observaciones = ?
                        WHERE fecha = ? AND producto = ?
                    """, (emp_cierre, data[0], data[1], data[2], obs_cierre, str(fecha_actual), prod))
                conn.commit()
                conn.close()
                st.success("¡Cierre registrado y mermas calculadas exitosamente!")

# ==========================================
# MÓDULO 2: REPORTES ADMINISTRATIVOS
# ==========================================
elif menu == "Reportes e Historial (Admin)" and st.session_state.user_role == "admin":
    st.markdown("<div class='section-header'>REPORTES Y CONTROL ADMINISTRATIVO TOTAL</div>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_FILE)
    df_reg = pd.read_sql("SELECT * FROM registros_diarios", conn)
    conn.close()
    
    if not df_reg.empty:
        filtro_fecha = st.date_input("Seleccionar Fecha de Reporte", value=datetime.today())
        df_filtrado = df_reg[df_reg['fecha'] == str(filtro_fecha)]
        
        if not df_filtrado.empty:
            st.dataframe(df_filtrado[['fecha', 'empleado_apertura', 'empleado_cierre', 'categoria', 'producto', 'unidad', 'ingreso', 'sobrante', 'merma', 'motivo_merma', 'observaciones']], use_container_width=True)
        else:
            st.info("No hay registros cargados para la fecha seleccionada.")
    else:
        st.info("Aún no existen registros guardados en el sistema.")
