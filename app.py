import streamlit as st
import plotly.graph_objects as go

# 1. Configuración
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

# 3. FUNCIÓN DEL MAPA 
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
            marker=dict(size=45, symbol='square', color=color, line=dict(width=2, color='white')),
            text=[nombre], textposition="middle center", textfont=dict(color="white", size=12),
            name=f"Posición {nombre}", customdata=[f"Posición {nombre}"], hoverinfo="text"
        ))
    fig.update_layout(
        title="Plano Main Deck", xaxis=dict(showgrid=False, range=[0, 3], visible=False),
        yaxis=dict(showgrid=False, range=[0, 11], visible=False),
        width=300, height=500, plot_bgcolor="white", showlegend=False, margin=dict(l=0, r=0, t=30, b=0),
        clickmode='event+select'
    )
    return fig

# 4. LA APLICACIÓN PRINCIPAL
if st.session_state.autenticado:
    st.write("---")
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.info("👇 **PASO 1:** Haz clic en un Cut del mapa.")
        mapa_evento = st.plotly_chart(dibujar_mapa(), use_container_width=True, on_select="rerun")
        pos_seleccionada = None
        if mapa_evento and "selection" in mapa_evento and mapa_evento["selection"]["points"]:
            pos_seleccionada = mapa_evento["selection"]["points"][0]["customdata"]
            
    with col2:
        st.subheader("Configuración de Falla")
        avion = st.selectbox("**PASO 2:** Tipo de Aeronave:", ["Seleccionar...", "Freighter F de Fábrica (Ej: CC-CXA)", "Convertido BCF (Ancra)"])
        
        if avion != "Seleccionar...":
            if not pos_seleccionada:
                st.warning("👈 Por favor, selecciona una posición tocando el mapa de la izquierda.")
            else:
                st.success(f"📍 Analizando la **{pos_seleccionada}**")
                st.write("---")
                
                st.markdown(f"### 🔍 Radiografía de la Paleta")
                st.info("**PASO 3:** Toca los interruptores ubicados alrededor de la paleta para simular la posición física de los seguros inoperativos:")
                
                inoperativos = []
                
                # ==========================================
                # EL NUEVO DISEÑO ESPACIAL (TOP-DOWN VIEW)
                # ==========================================
                c_izq, c_centro, c_der = st.columns([1, 2, 1])
                
                with c_centro:
                    # Seguros FWD (Ubicados físicamente arriba)
                    st.markdown("<div style='text-align:center;'><b>⬆️ FRENTE (FWD) ⬆️</b></div>", unsafe_allow_html=True)
                    f1, f2 = st.columns(2)
                    with f1: 
                        if st.toggle("FWD Inboard"): inoperativos.append("FWD_IN")
                    with f2: 
                        if st.toggle("FWD Outboard"): inoperativos.append("FWD_OUT")
                    
                    # Dibujo de la Paleta Central
                    st.markdown("""
                    <div style='background-color:#d9e2ec; border:3px dashed #627d98; border-radius:10px; height:180px; display:flex; align-items:center; justify-content:center; flex-direction:column; margin: 15px 0; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
                        <h2 style='color:#102a43; margin:0;'>📦 PALETA</h2>
                        <p style='color:#334e68; margin:0;'>Vista Superior</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Seguros AFT (Ubicados físicamente abajo)
                    a1, a2 = st.columns(2)
                    with a1: 
                        if st.toggle("AFT Inboard"): inoperativos.append("AFT_IN")
                    with a2: 
                        if st.toggle("AFT Outboard"): inoperativos.append("AFT_OUT")
                    st.markdown("<div style='text-align:center;'><b>⬇️ ATRÁS (AFT) ⬇️</b></div>", unsafe_allow_html=True)
                    
                with c_izq:
                    # Seguros Laterales (Ubicados físicamente a la izquierda)
                    st.write("<div style='height: 90px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral FWD"): inoperativos.append("SIDE_FWD")
                    st.write("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral AFT"): inoperativos.append("SIDE_AFT")
                
                with c_der:
                    # Espacio visual para mantener el diseño centrado (Rieles derechos)
                    st.write("<div style='height: 90px;'></div>", unsafe_allow_html=True)
                    st.markdown("<span style='color:gray; font-size:12px;'>*Riel lateral externo*</span>", unsafe_allow_html=True)

                # ==========================================
                
                # MOTOR DE CÁLCULO
                st.write("---")
                if len(inoperativos) == 0:
                    st.success("✅ **TODOS LOS SEGUROS OPERATIVOS.** \nPeso máximo normal permitido.")
                else:
                    st.error("🚨 **ALERTA DE RESTRICCIÓN (MEL / W&B)**")
                    if "FWD_IN" in inoperativos and "FWD_OUT" in inoperativos:
                        st.markdown("#### Restricción: 0 KG (NO LOAD)")
                        st.markdown("**Motivo:** Faltan TODOS los seguros frontales (FWD).")
                    elif len(inoperativos) == 1 and "FWD_IN" in inoperativos:
                        st.markdown("#### Restricción: 3,492 KG")
                        st.markdown("**Motivo:** Falla de 1 seguro frontal. Penalización aplicada.")
                    else:
                        st.markdown("#### Restricción: Calculando...")
                        st.markdown(f"Fallas registradas: {', '.join(inoperativos)}")
else:
    st.info("👈 Por favor, inicie sesión en el menú lateral izquierdo para utilizar la herramienta.")
