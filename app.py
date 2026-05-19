import streamlit as st

# 1. Configuración de la pestaña y diseño
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="centered")

# 2. Títulos
st.title("✈️ Calculadora de Restricciones 767")
st.subheader("Main Deck Cargo System - Locks Inoperativos")

# 3. MÓDULO DE SEGURIDAD (Login Corporativo)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/LATAM_logo.svg/1024px-LATAM_logo.svg.png", width=150)
st.sidebar.header("🔐 Acceso Corporativo")
correo = st.sidebar.text_input("Correo Institucional:")
password = st.sidebar.text_input("Contraseña:", type="password")
btn_login = st.sidebar.button("Iniciar Sesión")

# Variables para guardar si el usuario ya entró
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Verificamos si el correo es de la aerolínea
if btn_login:
    if correo.endswith("@latam.com") and password != "":
        st.session_state.autenticado = True
        st.sidebar.success("Acceso autorizado.")
    elif not correo.endswith("@latam.com") and correo != "":
        st.sidebar.error("Acceso denegado. Debe usar un correo de LATAM Airlines.")
    else:
        st.sidebar.warning("Ingrese sus credenciales.")

# 4. LA APLICACIÓN PRINCIPAL (Solo se muestra si inició sesión)
if st.session_state.autenticado:
    st.success(f"Bienvenido inspector: {correo}")
    st.write("---")
    
    # Base de datos simulada (Luego le pondremos las 14 matrículas y todas las posiciones)
    manuales = {
        "Freighter F de Fábrica (Ej: CC-CXA)": {
            "Posición 2L": {"FWD": "3,492 KG", "AFT": "3,000 KG", "SIDE": "0 KG (No Load)"},
            "Posición 10R": {"FWD": "6,032 KG", "AFT": "5,500 KG", "SIDE": "2,000 KG"}
        },
        "Convertido BCF (Ej: N526LA)": {
            "Posición 2L (Ancra)": {"FWD": "2,800 KG", "AFT": "2,500 KG", "SIDE": "500 KG"},
            "Posición 14": {"FWD": "4,000 KG", "AFT": "3,800 KG", "SIDE": "1,000 KG"}
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        avion = st.selectbox("1. Tipo de Aeronave:", ["Seleccionar..."] + list(manuales.keys()))
    
    if avion != "Seleccionar...":
        with col2:
            pos = st.selectbox("2. Posición (Cut):", ["Seleccionar..."] + list(manuales[avion].keys()))
            
        if pos != "Seleccionar...":
            falla = st.selectbox("3. Seguro Dañado:", ["Seleccionar..."] + list(manuales[avion][pos].keys()))
            
            if falla != "Seleccionar...":
                restriccion = manuales[avion][pos][falla]
                
                # Alerta visual grande en la pantalla
                st.write("---")
                st.error("🚨 **ALERTA DE RESTRICCIÓN (MEL)**")
                st.markdown(f"### Peso máximo permitido en {pos}: **{restriccion}**")
                st.warning("Verifique las distancias de separación adyacentes según el manual.")
else:
    st.info("👈 Por favor, inicie sesión en el menú lateral izquierdo para utilizar la herramienta.")
