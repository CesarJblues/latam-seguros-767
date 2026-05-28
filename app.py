import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =============================================================================
# 1. CONFIGURACIÓN INICIAL
# =============================================================================
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")
st.title("✈️ Calculadora Inteligente de Restricciones 767")

RULES_FILE = "Locks_and_deferred.xlsx"

# =============================================================================
# 2. CARGA DE DATOS LOCALES
# =============================================================================
@st.cache_data
def cargar_datos():
    try:
        # Cargamos las pestañas clave de tu archivo
        df_users = pd.read_excel(RULES_FILE, sheet_name="Users")
        df_restricciones = pd.read_excel(RULES_FILE, sheet_name="ULD_Restrictions")
        df_mapa = pd.read_excel(RULES_FILE, sheet_name="Restraint_ULD_Map")
        
        # Limpieza básica
        df_users.columns = [c.strip() for c in df_users.columns]
        df_restricciones.columns = [c.strip() for c in df_restricciones.columns]
        df_mapa.columns = [c.strip() for c in df_mapa.columns]
        
        return df_users, df_restricciones, df_mapa
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        return None, None, None

df_users, rules_df, map_df = cargar_datos()

# =============================================================================
# 3. LOGIN VALIDADO CON LA BASE DE DATOS
# =============================================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/LATAM_logo.svg/1024px-LATAM_logo.svg.png", width=150)
st.sidebar.header("🔐 Acceso Corporativo")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    correo = st.sidebar.text_input("Correo Institucional (Ej: nombre@latam.com):")
    btn_login = st.sidebar.button("Iniciar Sesión")

    if btn_login:
        if df_users is not None:
            usuario_valido = df_users[df_users['User_Email'].str.lower() == correo.lower()]
            if not usuario_valido.empty:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = usuario_valido.iloc[0]['User_Name']
                st.rerun()
            else:
                st.sidebar.error("Acceso denegado. Correo no registrado.")
else:
    st.sidebar.success(f"Hola, {st.session_state.usuario_actual}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

# =============================================================================
# 4. MAPA VISUAL COMPLETO (MAIN DECK 767 - 24 POSICIONES)
# =============================================================================
def dibujar_mapa():
    posiciones = {
        "A1":  {"x": [1.5], "y": [14]},
        "A2L": {"x": [1], "y": [13]},  "A2R": {"x": [2], "y": [13]},
        "A3L": {"x": [1], "y": [12]},  "A3R": {"x": [2], "y": [12]},
        "A4L": {"x": [1], "y": [11]},  "A4R": {"x": [2], "y": [11]},
        "A5L": {"x": [1], "y": [10]},  "A5R": {"x": [2], "y": [10]},
        "A6L": {"x": [1], "y": [9]},   "A6R": {"x": [2], "y": [9]},
        "A7L": {"x": [1], "y": [8]},   "A7R": {"x": [2], "y": [8]},
        "A8L": {"x": [1], "y": [7]},   "A8R": {"x": [2], "y": [7]},
        "A9L": {"x": [1], "y": [6]},   "A9R": {"x": [2], "y": [6]},
        "A10L":{"x": [1], "y": [5]},   "A10R":{"x": [2], "y": [5]},
        "A11L":{"x": [1], "y": [4]},   "A11R":{"x": [2], "y": [4]},
        "A12L":{"x": [1], "y": [3]},   "A12R":{"x": [2], "y": [3]},
        "A17": {"x": [1.5], "y": [2]},
    }

    fig = go.Figure()
    for nombre, datos in posiciones.items():
        if "L" in nombre: color = "#1f77b4"
        elif "R" in nombre: color = "#ff7f0e"
        else: color = "#2ca02c"

        fig.add_trace(go.Scatter(
            x=datos["x"], y=datos["y"], mode="markers+text",
            marker=dict(size=40, symbol="square", color=color, line=dict(width=2, color="white")),
            text=[nombre], textposition="middle center",
            textfont=dict(color="white", size=10, family="Arial Black"),
            customdata=[nombre], hoverinfo="none"
        ))

    fig.update_layout(
        title=dict(text="📍 Plano Main Deck 767-300", font=dict(size=18, color="#102a43"), x=0.5),
        xaxis=dict(showgrid=False, range=[0, 3], visible=False),
        yaxis=dict(showgrid=False, range=[1, 15], visible=False),
        width=350, height=800, plot_bgcolor="#f0f4f8", showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10), clickmode="event+select",
    )
    
    fig.add_shape(type="rect", x0=0.5, y0=1.2, x1=2.5, y1=14.8,
                  line=dict(color="#bcccdc", width=4), fillcolor="rgba(0,0,0,0)", layer="below")

    return fig

# =============================================================================
# 5. MOTOR INTELIGENTE DE RESTRICCIONES (BÚSQUEDA INVERSA)
# =============================================================================
def calcular_impacto(df_mapa, df_restricciones, avion_tipo, pos_vista, conteo_danos):
    resultados_finales = []
    
    # Contexto BCF o Freighter
    if avion_tipo == "BCF":
        model = "767-300BCF"
        contexto_buscar = "BCF Side-by-Side" if "L" in pos_vista or "R" in pos_vista else "BCF Centerline"
        pos_real = pos_vista 
    else:
        model = "767-300F"
        contexto_buscar = "F Side-by-Side" if "L" in pos_vista or "R" in pos_vista else "F Centerline"
        pos_real = pos_vista.replace("A", "") 

    lados_rotos = [lado for lado, qty in conteo_danos.items() if qty > 0]

    for lado in lados_rotos:
        # REGLA DEL MANUAL: Si hay 2 o más seguros dañados en el MISMO LADO (Adyacentes) -> 0 KG
        if conteo_danos[lado] >= 2:
            resultados_finales.append({
                "tipo": "alerta_critica",
                "posicion": pos_real,
                "lado_perdido": lado,
                "kg": 0,
                "origen": f"Múltiples seguros dañados en el lado {lado} (Regla de Adyacencia WBM)"
            })
            continue # Como ya dio 0, saltamos a la siguiente regla
            
        # Si es solo 1 seguro roto por lado, hacemos BÚSQUEDA INVERSA en tu mapa
        seguro_buscado = df_mapa[
            (df_mapa["ULD_Pos_ID"] == pos_real) & 
            (df_mapa["Side_Affected"] == lado) &
            (df_mapa["Config_Context"].str.contains(contexto_buscar, na=False))
        ]
        
        if seguro_buscado.empty:
            continue

        seguro_fisico_id = seguro_buscado.iloc[0]["Restraint_Fisico_ID"]
        
        # EFECTO DOMINÓ: Posiciones que comparten este seguro
        afectados = df_mapa[
            (df_mapa["Restraint_Fisico_ID"] == seguro_fisico_id) &
            (df_mapa["Config_Context"].str.contains(contexto_buscar, na=False))
        ]
        
        for index, fila in afectados.iterrows():
            pos_afectada = fila["ULD_Pos_ID"]
            lado_afectado = fila["Side_Affected"]
            
            candidatos_peso = df_restricciones[(df_restricciones["Model"] == model) & (df_restricciones["Pos"] == pos_afectada)]
            
            if not candidatos_peso.empty:
                fila_peso = candidatos_peso.iloc[0]
                col_map = {"FWD": "FWD_kg", "AFT": "AFT_kg", "LEFT": "LEFT_kg", "RIGHT": "RIGHT_kg"}
                col_name = col_map.get(lado_afectado)
                
                if col_name and pd.notna(fila_peso[col_name]):
                    resultados_finales.append({
                        "tipo": "alerta",
                        "posicion": pos_afectada,
                        "lado_perdido": lado_afectado,
                        "kg": float(fila_peso[col_name]),
                        "origen": f"Daño reportado en {pos_real} ({lado})"
                    })

    return resultados_finales

# =============================================================================
# 6. INTERFAZ PRINCIPAL DE LA APP
# =============================================================================
if st.session_state.autenticado:
    st.write("---")
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.info("👇 **PASO 1:** Haz clic en una posición del mapa.")
        event = st.plotly_chart(dibujar_mapa(), use_container_width=True, on_select="rerun")
        pos_seleccionada = None

        if event and "selection" in event and event["selection"]["points"]:
            pos_seleccionada = event["selection"]["points"][0]["customdata"]

    with col2:
        st.subheader("Configuración de Falla")
        avion = st.selectbox("**PASO 2:** Tipo de Aeronave:", ["Seleccionar...", "Freighter", "BCF"])

        if avion != "Seleccionar...":
            if not pos_seleccionada:
                st.warning("👈 Selecciona una posición del mapa de la izquierda.")
            else:
                st.success(f"📍 Posición seleccionada: **{pos_seleccionada}**")

                st.markdown("### 🔍 Radiografía de la Paleta")
                st.info("**PASO 3:** Selecciona los seguros que ves inoperativos:")

                # Diccionario para contar cuántos seguros se dañan por lado (Para la regla 0 KG)
                danos_por_lado = {"FWD": 0, "AFT": 0, "LEFT": 0, "RIGHT": 0}
                
                c_izq, c_centro, c_der = st.columns([1, 2, 1])

                with c_centro:
                    st.markdown("<div style='text-align:center;'><b>⬆️ FRENTE (FWD) ⬆️</b></div>", unsafe_allow_html=True)
                    f1, f2 = st.columns(2)
                    if f1.toggle("FWD Inboard"): danos_por_lado["FWD"] += 1
                    if f2.toggle("FWD Outboard"): danos_por_lado["FWD"] += 1
                    
                    st.markdown("""
                    <div style='background-color:#d9e2ec; border:3px dashed #627d98; border-radius:10px; height:120px; display:flex; align-items:center; justify-content:center; flex-direction:column; margin: 10px 0;'>
                        <h3 style='color:#102a43; margin:0;'>📦 PALETA</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    a1, a2 = st.columns(2)
                    if a1.toggle("AFT Inboard"): danos_por_lado["AFT"] += 1
                    if a2.toggle("AFT Outboard"): danos_por_lado["AFT"] += 1
                    st.markdown("<div style='text-align:center;'><b>⬇️ ATRÁS (AFT) ⬇️</b></div>", unsafe_allow_html=True)

                with c_izq:
                    st.write("<div style='height: 70px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral LEFT"): danos_por_lado["LEFT"] += 1
                
                with c_der:
                    st.write("<div style='height: 70px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral RIGHT"): danos_por_lado["RIGHT"] += 1

                # =================================================================
                # BOTÓN DE ANÁLISIS
                # =================================================================
                if st.button("🚨 Analizar Impacto de Daños", type="primary"):
                    total_danos = sum(danos_por_lado.values())
                    
                    if total_danos == 0:
                        st.success("✅ No hay seguros inoperativos. Posición OK para cargar.")
                    else:
                        alertas = calcular_impacto(map_df, rules_df, avion, pos_seleccionada, danos_por_lado)
                        
                        st.markdown("---")
                        st.subheader("📋 Resumen de Restricciones (Efecto Dominó)")
                        
                        if not alertas:
                            st.warning("⚠️ No se encontró restricción para esta configuración en la base de datos.")
                        
                        for alerta in alertas:
                            if alerta["tipo"] == "alerta_critica":
                                st.error(f"🚫 **NO LOAD (0 KG) en Posición {alerta['posicion']}**")
                                st.markdown(f"> **Motivo:** {alerta['origen']}")
                            elif alerta["tipo"] == "alerta":
                                st.warning(f"📍 **Penalización en Posición {alerta['posicion']}**")
                                st.markdown(f"> Pierde seguro **{alerta['lado_perdido']}** por {alerta['origen']}.")
                                st.markdown(f"> **Peso Máximo Permitido:** `{alerta['kg']} kg`")
