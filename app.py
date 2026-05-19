import streamlit as st
import plotly.graph_objects as go

# 1. Configuración de la pestaña
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")
st.title("✈️ Calculadora de Restricciones 767")

# 2. MÓDULO DE SEGURIDAD
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/LATAM_logo.svg/1024px-LATAM_logo.svg.png", width=150)
st.sidebar.header("🔐 Acceso Corporativo")
correo = st.sidebar.text_input("Correo Institucional:")
password = st.sidebar.text_input("Contraseña:", type="password")
btn_login = st.sidebar.button("Iniciar Sesión")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if btn_login:
    if correo.endswith("@latam.com") and password != "":
        st.session_state.autenticado = True
        st.sidebar.success("Acceso autorizado.")
    elif not correo.endswith("@latam.com") and correo != "":
        st.sidebar.error("Acceso denegado. Debe usar correo de LATAM.")

# 3. FUNCIÓN DEL MAPA VISUAL
def dibujar_mapa():
    posiciones = {
        "1": {"x": [1.5], "y": [10]}, "2L": {"x": [1], "y": [9]}, "2R": {"x": [2], "y": [9]},
        "3L": {"x": [1], "y": [8]}, "3R": {"x": [2], "y": [8]}, "10L": {"x": [1], "y": [4]}, 
        "10R": {"x": [2], "y": [4]}, "14": {"x": [1.5], "y": [2]} # Muestra simplificada
    }
    fig = go.Figure()
    for nombre, datos in posiciones.items():
        color = 'royalblue' if "L" in nombre else ('orange' if "R" in nombre else 'green')
        fig.add_trace(go.Scatter(
            x=datos["x"], y=datos["y"], mode='markers+text',
            marker=dict(size=45, symbol='square', color=color, line=dict(width=2, color='white')),
            text=[nombre], textposition="middle center", textfont=dict(color="white", size=12),
            name=f"Posición {nombre}", hoverinfo="text"
        ))
    fig.update_layout(
        title="Plano Main Deck", xaxis=dict(showgrid=False, range=[0, 3], visible=False),
        yaxis=dict(showgrid=False, range=[0, 11], visible=False),
        width=300, height=500, plot_bgcolor="white", showlegend=False, margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig

# 4. LA APLICACIÓN PRINCIPAL
if st.session_state.autenticado:
    st.write("---")
    
    # Base de datos simulada
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
    
    # Dividimos la pantalla en dos columnas (Mapa a la izquierda, Menús a la derecha)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.plotly_chart(dibujar_mapa(), use_container_width=True)
        
    with col2:
        st.subheader("Configuración de Falla")
        avion = st.selectbox("1. Tipo de Aeronave:", ["Seleccionar..."] + list(manuales.keys()))
        
        if avion != "Seleccionar...":
            pos = st.selectbox("2. Posición (Cut):", ["Seleccionar..."] + list(manuales[avion].keys()))
            if pos != "Seleccionar...":
                falla = st.selectbox("3. Seguro Dañado:", ["Seleccionar..."] + list(manuales[avion][pos].keys()))
                
                if falla != "Seleccionar...":
                    restriccion = manuales[avion][pos][falla]
                    st.write("---")
                    st.error("🚨 **ALERTA DE RESTRICCIÓN (MEL)**")
                    st.markdown(f"### Peso máximo en {pos}: **{restriccion}**")
else:
    st.info("👈 Por favor, inicie sesión en el menú lateral izquierdo para utilizar la herramienta.")
