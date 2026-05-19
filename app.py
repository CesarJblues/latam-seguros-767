import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# 1. BASE DE DATOS (Configura tus restricciones aquí)
# ==============================================================================
BASE_DATOS_MANUAL = {
    "Convertido BCF": {
        "2L": {"AFT_IN": 1747, "FWD_IN": 2800, "SIDE_FWD": 2000},
        "14": {"FWD_IN": 4000, "AFT_IN": 3800}
    },
    "Freighter F": {
        "2L": {"FWD_IN": 3492, "AFT_IN": 3000},
        "10R": {"FWD_IN": 6032}
    }
}

# ==============================================================================
# 2. MOTOR DE CÁLCULO
# ==============================================================================
def obtener_restriccion(avion, pos, inoperativos):
    if not inoperativos:
        return "3855 KG", "Operación Normal. Todos los seguros operativos."
    
    data_avion = BASE_DATOS_MANUAL.get(avion, {})
    data_pos = data_avion.get(pos, {})
    valores = [data_pos[f] for f in inoperativos if f in data_pos]
    
    if valores:
        return f"{min(valores)} KG", f"Restricción aplicada según manual: {', '.join(inoperativos)}"
    else:
        return "⚠️ N/A", "Esta combinación de fallas no está configurada. Agrégala en el código."

# ==============================================================================
# 3. INTERFAZ VISUAL (MAPA)
# ==============================================================================
def dibujar_mapa():
    # Definición de las posiciones en el plano
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
        width=300, height=500, plot_bgcolor="white", showlegend=False, 
        margin=dict(l=0,r=0,t=0,b=0), clickmode='event+select'
    )
    return fig

# ==============================================================================
# 4. APLICACIÓN PRINCIPAL
# ==============================================================================
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")
st.title("✈️ Calculadora de Restricciones 767")

avion = st.sidebar.selectbox("Seleccione Aeronave:", ["Convertido BCF", "Freighter F"])

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Mapa del Avión")
    mapa = st.plotly_chart(dibujar_mapa(), use_container_width=True, on_select="rerun")
    pos_sel = "2L" # Por defecto
    if mapa and "selection" in mapa and mapa["selection"]["points"]:
        pos_sel = mapa["selection"]["points"][0]["customdata"]
    st.info(f"Posición seleccionada: **{pos_sel}**")

with col2:
    st.subheader(f"Configuración de Seguros ({pos_sel})")
    inoperativos = []
    
    # Layout de la paleta
    c_izq, c_centro, c_der = st.columns([1, 2, 1])
    with c_centro:
        if st.toggle("FWD Inboard"): inoperativos.append("FWD_IN")
        st.markdown("<div style='background:#f0f2f6; border:2px solid #1c3d5a; height:100px; display:flex; align-items:center; justify-content:center; border-radius:10px;'>📦 PALETA</div>", unsafe_allow_html=True)
        if st.toggle("AFT Inboard"): inoperativos.append("AFT_IN")
    
    with c_izq:
        st.write("<br><br>")
        if st.toggle("Lateral FWD"): inoperativos.append("SIDE_FWD")

    # Resultado
    st.divider()
    peso, motivo = obtener_restriccion(avion, pos_sel, inoperativos)
    st.metric(label="Carga Máxima Permitida", value=peso)
    st.caption(motivo)
