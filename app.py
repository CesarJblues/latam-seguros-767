import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# 1. ESTRUCTURA DE DATOS (Mapeo Side-by-Side)
# ==============================================================================
# La clave es la posición (ej: "2L", "2R"). Aquí debes cargar los pesos de tus PDFs
BASE_DATOS = {
    "Convertido BCF": {
        "2L": {"FWD_IN": 2800, "AFT_IN": 1747}, "2R": {"FWD_IN": 2800, "AFT_IN": 1747},
        "14": {"FWD_IN": 4000, "AFT_IN": 3800}
    },
    "Freighter F": {
        "2L": {"FWD_IN": 3492, "AFT_IN": 3000}, "2R": {"FWD_IN": 3492, "AFT_IN": 3000}
    }
}

# ==============================================================================
# 2. DIBUJO REAL DEL DECK (Side-by-Side Longitudinal)
# ==============================================================================
def dibujar_mapa():
    fig = go.Figure()
    # Definimos filas longitudinales. L en X=1, R en X=2
    # El eje Y representa la longitud del deck
    for i in range(1, 16):
        # Posiciones L
        fig.add_trace(go.Scatter(x=[1], y=[16-i], mode='markers+text', 
            marker=dict(size=30, color='royalblue'), text=[f"{i}L"], customdata=[f"{i}L"], name=f"{i}L"))
        # Posiciones R
        fig.add_trace(go.Scatter(x=[2], y=[16-i], mode='markers+text', 
            marker=dict(size=30, color='orange'), text=[f"{i}R"], customdata=[f"{i}R"], name=f"{i}R"))
            
    fig.update_layout(height=1000, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False, range=[0,3]), yaxis=dict(visible=False), clickmode='event+select')
    return fig

# ==============================================================================
# 3. INTERFAZ Y CÁLCULOS
# ==============================================================================
st.set_page_config(layout="wide")
st.title("✈️ Calculadora de Restricciones 767")

if 'pos_sel' not in st.session_state: st.session_state.pos_sel = "2L"

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Layout Side-by-Side")
    mapa = st.plotly_chart(dibujar_mapa(), use_container_width=True, on_select="rerun")
    if mapa and "selection" in mapa and mapa["selection"]["points"]:
        st.session_state.pos_sel = mapa["selection"]["points"][0]["customdata"]
    st.success(f"Posición Activa: **{st.session_state.pos_sel}**")

with col2:
    st.subheader(f"Configuración {st.session_state.pos_sel}")
    inoperativos = []
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.toggle("FWD Inboard"): inoperativos.append("FWD_IN")
        st.markdown("<div style='border:2px dashed gray; padding:20px; text-align:center;'>📦 PALETA</div>", unsafe_allow_html=True)
        if st.toggle("AFT Inboard"): inoperativos.append("AFT_IN")
    
    # Motor de búsqueda
    avion = st.radio("Aeronave:", ["Convertido BCF", "Freighter F"], horizontal=True)
    reglas = BASE_DATOS.get(avion, {}).get(st.session_state.pos_sel, {})
    valores = [reglas[f] for f in inoperativos if f in reglas]
    
    if valores:
        st.error(f"### Restricción: {min(valores)} KG")
    else:
        st.success("### Operación Normal")
