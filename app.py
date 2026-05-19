import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURACIÓN Y BASE DE DATOS (AQUÍ ES DONDE AGREGAS TUS DATOS DEL MANUAL)
# ==============================================================================
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")

# BASE DE DATOS: Si quieres agregar más datos, solo añade la línea aquí
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

def obtener_restriccion(avion, pos, inoperativos):
    if not inoperativos:
        return "3855 KG", "Operación Normal. Todos los seguros operativos."
    
    data_avion = BASE_DATOS_MANUAL.get(avion, {})
    data_pos = data_avion.get(pos, {})
    
    # Busca el valor más restrictivo entre los seguros fallados
    valores = [data_pos[f] for f in inoperativos if f in data_pos]
    
    if valores:
        return f"{min(valores)} KG", f"Restricción aplicada según manual para fallos: {', '.join(inoperativos)}"
    else:
        return "N/A", "Esta combinación de fallas no está en la base de datos."

# ==============================================================================
# INTERFAZ DE USUARIO (UI)
# ==============================================================================
st.title("✈️ Calculadora de Restricciones 767")

# Sidebar para Selección
avion = st.sidebar.selectbox("Seleccione Aeronave:", ["Convertido BCF", "Freighter F"])

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Selección de Posición")
    # Mapa interactivo simplificado
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1], y=[9], mode='markers+text', marker=dict(size=40, color='#1c3d5a'), text=["2L"]))
    fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False), clickmode='event+select')
    mapa = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    
    pos_sel = "2L" # Por defecto para el ejemplo, se puede expandir

with col2:
    st.subheader(f"Radiografía de la Paleta ({pos_sel})")
    
    # Layout de Toggles (La parte visual que te gustaba)
    c_izq, c_centro, c_der = st.columns([1, 2, 1])
    inoperativos = []
    
    with c_centro:
        st.markdown("<div style='text-align:center;'><b>⬆️ FWD ⬆️</b></div>", unsafe_allow_html=True)
        if st.toggle("FWD Inboard"): inoperativos.append("FWD_IN")
        
        # Caja representativa
        st.markdown("<div style='background:#f0f2f6; border:2px solid #1c3d5a; height:120px; display:flex; align-items:center; justify-content:center; border-radius:10px;'>📦 PALETA</div>", unsafe_allow_html=True)
        
        if st.toggle("AFT Inboard"): inoperativos.append("AFT_IN")
        st.markdown("<div style='text-align:center;'><b>⬇️ AFT ⬇️</b></div>", unsafe_allow_html=True)
        
    with c_izq:
        st.write("<br><br>")
        if st.toggle("Lateral FWD"): inoperativos.append("SIDE_FWD")

    # Resultado Final con estilo profesional
    st.divider()
    peso, motivo = obtener_restriccion(avion, pos_sel, inoperativos)
    
    st.metric(label="Carga Máxima Permitida", value=peso)
    st.info(motivo)
