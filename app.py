import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURACIÓN Y BASE DE DATOS (AQUÍ CARGAS TUS DATOS DEL MANUAL)
# ==============================================================================
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")

# Estructura: BASE_DATOS_MANUAL[TipoAvion][Posicion][Seguro_Falla] = Peso_Restringido
BASE_DATOS_MANUAL = {
    "Convertido BCF": {
        "2L": {"AFT_IN": 1747, "FWD_IN": 2800}, 
        "14": {"FWD_IN": 4000, "AFT_IN": 3800}
    },
    "Freighter F": {
        "2L": {"FWD_IN": 3492, "AFT_IN": 3000},
        "10R": {"FWD_IN": 6032}
    }
}

# ==============================================================================
# LÓGICA DE NEGOCIO
# ==============================================================================
def obtener_restriccion(avion, pos, inoperativos):
    # Si no hay fallas, no hay restricción
    if not inoperativos:
        return "3855 KG", "Operación Normal. Todos los seguros operativos."
    
    # Consulta la base de datos
    data_avion = BASE_DATOS_MANUAL.get(avion, {})
    data_pos = data_avion.get(pos, {})
    
    # Busca la restricción más severa (el menor peso entre los seguros fallados)
    pesos_aplicables = [data_pos[f] for f in inoperativos if f in data_pos]
    
    if pesos_aplicables:
        return f"{min(pesos_aplicables)} KG", f"Restricción aplicada según manual para fallos: {', '.join(inoperativos)}"
    else:
        return "Pendiente", "Esta combinación de fallas aún no está registrada en el sistema."

def dibujar_mapa():
    posiciones = {
        "1": {"x": [1.5], "y": [10]}, "2L": {"x": [1], "y": [9]}, "2R": {"x": [2], "y": [9]},
        "3L": {"x": [1], "y": [8]}, "3R": {"x": [2], "y": [8]}, "10L": {"x": [1], "y": [4]}, 
        "10R": {"x": [2], "y": [4]}, "14": {"x": [1.5], "y": [2]}
    }
    fig = go.Figure()
    for nombre, datos in posiciones.items():
        color = 'royalblue' if "L" in nombre else ('orange' if "R" in nombre else 'green')
        fig.add_trace(go.Scatter(
            x=datos["x"], y=datos["y"], mode='markers+text',
            marker=dict(size=40, symbol='square', color=color, line=dict(width=2, color='white')),
            text=[nombre], textfont=dict(color="white", size=12),
            customdata=[nombre], name=nombre
        ))
    fig.update_layout(
        xaxis=dict(range=[0, 3], visible=False), yaxis=dict(range=[0, 11], visible=False),
        width=300, height=500, plot_bgcolor="white", showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
        clickmode='event+select'
    )
    return fig

# ==============================================================================
# UI PRINCIPAL
# ==============================================================================
# Sidebar Auth
st.sidebar.header("🔐 Acceso Corporativo")
correo = st.sidebar.text_input("Correo:")
password = st.sidebar.text_input("Contraseña:", type="password")
if st.sidebar.button("Login"):
    st.session_state.autenticado = (correo.endswith("@latam.com"))

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if st.session_state.autenticado:
    st.title("✈️ Calculadora de Restricciones 767")
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        mapa = st.plotly_chart(dibujar_mapa(), use_container_width=True, on_select="rerun")
        pos_sel = None
        if mapa and "selection" in mapa and mapa["selection"]["points"]:
            pos_sel = mapa["selection"]["points"][0]["customdata"]
            
    with col2:
        avion = st.selectbox("Aeronave:", ["Convertido BCF", "Freighter F"])
        if pos_sel:
            st.subheader(f"Configuración Posición {pos_sel}")
            inoperativos = []
            
            # Layout Toggles
            c1, c2, c3 = st.columns([1,2,1])
            with c2:
                if st.toggle("FWD Inboard"): inoperativos.append("FWD_IN")
                st.markdown("<div style='height:100px; border:3px dashed gray; text-align:center;'>📦 PALETA</div>", unsafe_allow_html=True)
                if st.toggle("AFT Inboard"): inoperativos.append("AFT_IN")
            
            with c1:
                if st.toggle("Lateral FWD"): inoperativos.append("SIDE_FWD")
            
            # Cálculo
            peso, motivo = obtener_restriccion(avion, pos_sel, inoperativos)
            st.warning(f"**Carga Máxima:** {peso}")
            st.caption(motivo)
        else:
            st.info("Selecciona una posición en el mapa.")
else:
    st.info("Inicia sesión para acceder.")
