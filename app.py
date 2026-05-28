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
        # Cargamos las 3 pestañas clave
        df_users = pd.read_excel(RULES_FILE, sheet_name="Users")
        df_restricciones = pd.read_excel(RULES_FILE, sheet_name="ULD_Restrictions")
        df_mapa = pd.read_excel(RULES_FILE, sheet_name="Restraint_ULD_Map")
        
        # Limpieza básica de nombres de columnas
        df_users.columns = [c.strip() for c in df_users.columns]
        df_restricciones.columns = [c.strip() for c in df_restricciones.columns]
        df_mapa.columns = [c.strip() for c in df_mapa.columns]
        
        return df_users, df_restricciones, df_mapa
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        return None, None, None

df_users, rules_df, map_df = cargar_datos()

# =============================================================================
# 3. LOGIN Y BARRA LATERAL
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
    
    # Botón útil para cuando actualices el Excel sin tener que apagar la terminal
    if st.sidebar.button("🔄 Refrescar Excel (Limpiar Caché)"):
        st.cache_data.clear()
        st.rerun()
        
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

# =============================================================================
# 4. MAPA VISUAL CREATIVO (MAIN DECK 767 - 24 POSICIONES)
# =============================================================================
def dibujar_mapa(pos_seleccionada=None):
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
    
    # 1. FORMA DEL FUSELAJE (Nariz curva y cola)
    path_avion = "M 0.4, 1.5 L 0.4, 14.5 Q 1.5, 16.5 2.6, 14.5 L 2.6, 1.5 Q 1.5, -0.5 0.4, 1.5 Z"
    fig.add_shape(
        type="path", path=path_avion,
        line=dict(color="#9fb3c8", width=3),
        fillcolor="#f0f4f8", layer="below"
    )
    
    # 2. CABINA DE PILOTOS (Cockpit Windows)
    fig.add_shape(
        type="path", path="M 0.9, 14.9 Q 1.5, 15.6 2.1, 14.9 L 1.8, 14.6 Q 1.5, 15.1 1.2, 14.6 Z",
        line=dict(color="#334e68", width=1),
        fillcolor="#486581", layer="above"
    )
    
    # 3. PUERTA DE CARGA PRINCIPAL (Main Deck Cargo Door)
    fig.add_shape(
        type="rect", x0=0.3, y0=13.2, x1=0.45, y1=14.4,
        line=dict(color="#e12d39", width=2),
        fillcolor="white", layer="above"
    )
    fig.add_annotation(
        x=-0.1, y=13.8, text="CARGO<br>DOOR", showarrow=False, 
        font=dict(size=9, color="#e12d39", family="Arial Black")
    )

    # 4. POSICIONES DE LAS PALETAS
    for nombre, datos in posiciones.items():
        # Lógica de color interactiva: Destacar si la posición está seleccionada
        if pos_seleccionada == nombre:
            color = "#e12d39" # Rojo corporativo si está clickeada
            line_color = "black"
            line_width = 3
        else:
            if "L" in nombre: color = "#102a43"
            elif "R" in nombre: color = "#829ab1"
            else: color = "#003b70"
            line_color = "white"
            line_width = 1.5

        fig.add_trace(go.Scatter(
            x=datos["x"], y=datos["y"], mode="markers+text",
            marker=dict(
                size=42, symbol="square", color=color, 
                line=dict(width=line_width, color=line_color), opacity=0.95
            ),
            text=[nombre], textposition="middle center",
            textfont=dict(color="white", size=10, family="Arial Black"),
            customdata=[nombre], hoverinfo="none"
        ))

    fig.update_layout(
        title=dict(text="✈️ Plano Interactivo 767", font=dict(size=18, color="#102a43"), x=0.5),
        xaxis=dict(showgrid=False, range=[-0.5, 3.5], visible=False),
        yaxis=dict(showgrid=False, range=[0, 16.5], visible=False),
        width=400, height=850, plot_bgcolor="white", showlegend=False,
        margin=dict(l=0, r=0, t=50, b=10), clickmode="event+select",
        dragmode=False # Evita paneos por error en tablets
    )

    return fig

# =============================================================================
# 5. MOTOR COMPLETAMENTE BLINDADO DE RESTRICCIONES (EFECTO DOMINÓ)
# =============================================================================
def calcular_impacto(df_mapa, df_restricciones, avion_tipo, pos_vista, conteo_danos):
    resultados_finales = []
    
    model = "767-300BCF" if avion_tipo == "BCF" else "767-300F"
    
    if avion_tipo == "BCF":
        contexto_buscar = "BCF Side-by-Side" if "L" in pos_vista or "R" in pos_vista else "BCF Centerline"
        pos_mapa = pos_vista 
    else:
        contexto_buscar = "F Side-by-Side" if "L" in pos_vista or "R" in pos_vista else "F Centerline"
        pos_mapa = pos_vista.replace("A", "") 

    col_map = {"FWD": "FWD_kg", "AFT": "AFT_kg", "LEFT": "LEFT_kg", "RIGHT": "RIGHT_kg"}
    lados_rotos = [lado for lado, qty in conteo_danos.items() if qty > 0]

    for lado in lados_rotos:
        # 1. REGLA CRÍTICA: Múltiples seguros en el mismo lado (Adyacentes) -> 0 KG
        if conteo_danos[lado] >= 2:
            resultados_finales.append({
                "tipo": "alerta_critica",
                "posicion": pos_vista,
                "lado_perdido": lado,
                "kg": 0,
                "origen": f"Múltiples seguros dañados en el lado {lado} (Regla de Adyacencia)"
            })
            continue 

        # 2. IMPACTO DIRECTO (Buscar en tabla de pesos general)
        candidatos_peso_directo = df_restricciones[
            (df_restricciones["Model"] == model) & 
            ((df_restricciones["Pos"] == pos_vista) | (df_restricciones["Pos"] == pos_vista.replace("A", "")))
        ]
        
        if not candidatos_peso_directo.empty:
            fila_peso = candidatos_peso_directo.iloc[0]
            col_name = col_map.get(lado)
            
            if col_name and col_name in fila_peso and pd.notna(fila_peso[col_name]):
                resultados_finales.append({
                    "tipo": "alerta",
                    "posicion": pos_vista,
                    "lado_perdido": lado,
                    "kg": float(fila_peso[col_name]),
                    "origen": "Daño directo reportado"
                })

        # 3. IMPACTO COMPARTIDO (EFECTO DOMINÓ - Buscar en mapa de seguros)
        seguro_buscado = df_mapa[
            (df_mapa["ULD_Pos_ID"] == pos_mapa) & 
            (df_mapa["Side_Affected"] == lado) &
            (df_mapa["Config_Context"].str.contains(contexto_buscar, na=False))
        ]
        
        if not seguro_buscado.empty:
            seguro_fisico_id = seguro_buscado.iloc[0]["Restraint_Fisico_ID"]
            
            afectados = df_mapa[
                (df_mapa["Restraint_Fisico_ID"] == seguro_fisico_id) &
                (df_mapa["Config_Context"].str.contains(contexto_buscar, na=False)) &
                (df_mapa["ULD_Pos_ID"] != pos_mapa) 
            ]
            
            for index, fila in afectados.iterrows():
                pos_afectada_mapa = fila["ULD_Pos_ID"]
                lado_afectado_mapa = fila["Side_Affected"]
                
                pos_afectada_pantalla = pos_afectada_mapa if pos_afectada_mapa.startswith("A") else f"A{pos_afectada_mapa}"
                if pos_afectada_pantalla == "A17": pos_afectada_pantalla = "A17"
                
                candidatos_peso_compartido = df_restricciones[
                    (df_restricciones["Model"] == model) & 
                    ((df_restricciones["Pos"] == pos_afectada_mapa) | (df_restricciones["Pos"] == pos_afectada_pantalla))
                ]
                
                if not candidatos_peso_compartido.empty:
                    fila_peso_comp = candidatos_peso_compartido.iloc[0]
                    col_name_comp = col_map.get(lado_afectado_mapa)
                    
                    if col_name_comp and col_name_comp in fila_peso_comp and pd.notna(fila_peso_comp[col_name_comp]):
                        resultados_finales.append({
                            "tipo": "alerta",
                            "posicion": pos_afectada_pantalla,
                            "lado_perdido": lado_afectado_mapa,
                            "kg": float(fila_peso_comp[col_name_comp]),
                            "origen": f"Efecto dominó (Seguro central compartido)"
                        })

    # Eliminar posibles alertas duplicadas visualmente
    resultados_unicos = []
    vistos = set()
    for r in resultados_finales:
        clave = (r["posicion"], r["lado_perdido"], r["kg"], r["tipo"])
        if clave not in vistos:
            vistos.add(clave)
            resultados_unicos.append(r)

    return resultados_unicos

# =============================================================================
# 6. INTERFAZ PRINCIPAL DE LA APP
# =============================================================================
if st.session_state.autenticado:
    st.write("---")
    col1, col2 = st.columns([1, 1.5])

    # Variable de sesión para guardar la posición clickeada visualmente
    if "pos_seleccionada" not in st.session_state:
        st.session_state.pos_seleccionada = None

    with col1:
        st.info("👇 **PASO 1:** Haz clic en una posición del mapa.")
        # Dibujamos el mapa mandando la posición clickeada (para el color rojo)
        event = st.plotly_chart(dibujar_mapa(st.session_state.pos_seleccionada), use_container_width=True, on_select="rerun")
        
        if event and "selection" in event and event["selection"]["points"]:
            st.session_state.pos_seleccionada = event["selection"]["points"][0]["customdata"]
            st.rerun() # Recargamos suavemente para que se pinte el botón

    with col2:
        st.subheader("Configuración de Falla")
        avion = st.selectbox("**PASO 2:** Tipo de Aeronave:", ["Seleccionar...", "Freighter", "BCF"])

        if avion != "Seleccionar...":
            if not st.session_state.pos_seleccionada:
                st.warning("👈 Selecciona una posición del mapa de la izquierda.")
            else:
                st.success(f"📍 Posición seleccionada: **{st.session_state.pos_seleccionada}**")

                st.markdown("### 🔍 Radiografía de la Paleta")
                st.info("**PASO 3:** Selecciona los seguros que ves inoperativos:")

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
                        alertas = calcular_impacto(map_df, rules_df, avion, st.session_state.pos_seleccionada, danos_por_lado)
                        
                        st.markdown("---")
                        st.subheader("📋 Resumen de Restricciones Generadas")
                        
                        if not alertas:
                            st.error("⚠️ Error: No se encontró la combinación en la base de datos (pestaña ULD_Restrictions).")
                        
                        for alerta in alertas:
                            if alerta["tipo"] == "alerta_critica":
                                st.error(f"🚫 **NO LOAD (0 kg) en Posición {alerta['posicion']}**")
                                st.markdown(f"> **Motivo:** {alerta['origen']}")
                            elif alerta["tipo"] == "alerta":
                                st.warning(f"📍 **Restricción en Posición {alerta['posicion']}**")
                                st.markdown(f"> **Condición:** Pierde seguro del lado **{alerta['lado_perdido']}** ({alerta['origen']}).")
                                st.markdown(f"> **Peso Máximo Permitido:** `{alerta['kg']:.0f} kg`")
