import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# BASE DE DATOS REAL (AQUÍ ES DONDE ACTUALIZAS PARA QUE NO SALGA EL ERROR)
# ==============================================================================
# Formato: "Avion": {"Posicion": {"CODIGO_FALLA": PESO_KG, "CODIGO_FALLA_2": PESO_KG}}
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
# LÓGICA DE CÁLCULO
# ==============================================================================
def obtener_restriccion(avion, pos, inoperativos):
    if not inoperativos:
        return "3855 KG", "Operación Normal. Todos los seguros operativos."
    
    # Buscamos en la base de datos
    data_avion = BASE_DATOS_MANUAL.get(avion, {})
    data_pos = data_avion.get(pos, {})
    
    # Buscamos el valor más restrictivo (el menor peso) para los fallos seleccionados
    valores = [data_pos[f] for f in inoperativos if f in data_pos]
    
    if valores:
        return f"{min(valores)} KG", f"Restricción aplicada según manual para fallos: {', '.join(inoperativos)}"
    else:
        return "⚠️ N/A", "Esta combinación específica aún no está configurada en la base de datos. Agrégala en el código."

# ==============================================================================
# INTERFAZ VISUAL (MAPA + TOGGLES)
# ==============================================================================
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")
st.title("✈️ Calculadora de Restricciones 767")

# ... (Insertar aquí tu código de login anterior si lo usas) ...

col1, col2 = st.columns([1, 1.5])

with col1:
    # Dibujo del Mapa (Reutilizado)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1], y=[9], mode='markers+text', marker=dict(size=40, color='royalblue'), text=["2L"]))
    fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False), clickmode='event+select')
    mapa = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    
    pos_sel = None
    if mapa and "selection" in mapa and mapa["selection"]["points"]:
        pos_sel = "2L" # Simplificado para el ejemplo

with col2:
    if pos_sel:
        avion = st.selectbox("Aeronave:", ["Convertido BCF", "Freighter F"])
        st.subheader(f"Configuración Posición {pos_sel}")
        
        inoperativos = []
        c_izq, c_centro, c_der = st.columns([1, 2, 1])
        
        with c_centro:
            if st.toggle("FWD Inboard"): inoperativos.append("FWD_IN")
            # Dibujo de la paleta
            st.markdown("<div style='background:#d9e2ec; height:100px; display:flex; align-items:center; justify-content:center; border:2px dashed gray;'>PALETA</div>", unsafe_allow_html=True)
            if st.toggle("AFT Inboard"): inoperativos.append("AFT_IN")
        
        with c_izq:
            if st.toggle("Lateral FWD"): inoperativos.append("SIDE_FWD")
            
        # Cálculo final
        peso, motivo = obtener_restriccion(avion, pos_sel, inoperativos)
        st.write("---")
        st.warning(f"### Carga Máxima: {peso}")
        st.caption(motivo)
