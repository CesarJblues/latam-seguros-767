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

# 3. FUNCIÓN DEL MAPA (AVIÓN COMPLETO)
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
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.plotly_chart(dibujar_mapa(), use_container_width=True)
        
    with col2:
        st.subheader("Configuración de la Posición")
        avion = st.selectbox("1. Tipo de Aeronave:", ["Seleccionar...", "Freighter F de Fábrica (Ej: CC-CXA)", "Convertido BCF (Ancra)"])
        
        if avion != "Seleccionar...":
            pos = st.selectbox("2. Posición (Cut):", ["Seleccionar...", "Posición 2L", "Posición 10R"])
            
            if pos != "Seleccionar...":
                st.write("---")
                st.markdown(f"### 🔍 Esquema de Seguros en {pos}")
                st.info("Marca en el diagrama los seguros que se encuentran **INOPERATIVOS / DAÑADOS**:")
                
                # --- AQUÍ EMPIEZA LA MAGIA VISUAL (SIMULANDO EL MANUAL) ---
                inoperativos = []
                
                # Simulamos la vista desde arriba de la paleta
                st.markdown("#### ⬆️ Lado Frontal (FWD)")
                c1, c2 = st.columns(2)
                with c1:
                    if st.checkbox("❌ Seguro FWD Inboard"): inoperativos.append("FWD_IN")
                with c2:
                    if st.checkbox("❌ Seguro FWD Outboard"): inoperativos.append("FWD_OUT")
                
                st.write("") # Espacio
                st.markdown("#### ↔️ Laterales (SIDE)")
                c3, c4 = st.columns(2)
                with c3:
                    if st.checkbox("❌ Lateral FWD"): inoperativos.append("SIDE_FWD")
                with c4:
                    if st.checkbox("❌ Lateral AFT"): inoperativos.append("SIDE_AFT")
                    
                st.write("") # Espacio
                st.markdown("#### ⬇️ Lado Trasero (AFT)")
                c5, c6 = st.columns(2)
                with c5:
                    if st.checkbox("❌ Seguro AFT Inboard"): inoperativos.append("AFT_IN")
                with c6:
                    if st.checkbox("❌ Seguro AFT Outboard"): inoperativos.append("AFT_OUT")
                    
                # --- MOTOR DE CÁLCULO DE RESTRICCIONES ---
                st.write("---")
                if len(inoperativos) == 0:
                    st.success("✅ **TODOS LOS SEGUROS OPERATIVOS.** \n\nPeso máximo normal permitido para esta posición según manual.")
                else:
                    st.error("🚨 **ALERTA DE RESTRICCIÓN (MEL / W&B)**")
                    
                    # Lógica basada en combinaciones (Ejemplo)
                    if "FWD_IN" in inoperativos and "FWD_OUT" in inoperativos:
                        st.markdown("#### Restricción: 0 KG (NO LOAD)")
                        st.markdown("**Motivo:** Faltan TODOS los seguros frontales (FWD).")
                        
                    elif len(inoperativos) == 1 and "FWD_IN" in inoperativos:
                        st.markdown("#### Restricción: 3,492 KG")
                        st.markdown("**Motivo:** Falla de 1 seguro frontal. Penalización aplicada.")
                        
                    elif "SIDE_FWD" in inoperativos or "SIDE_AFT" in inoperativos:
                        st.markdown("#### Restricción: 2,100 KG")
                        st.markdown("⚠️ **Atención:** Verifique que la posición adyacente no tenga fallas laterales también.")
                        
                    else:
                        st.markdown("#### Restricción: Calculando configuración especial...")
                        st.markdown(f"Fallas detectadas: {', '.join(inoperativos)}")
else:
    st.info("👈 Por favor, inicie sesión en el menú lateral izquierdo para utilizar la herramienta.")
