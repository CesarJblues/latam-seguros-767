import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =============================================================================
# 1. CONFIGURACIÓN INICIAL Y ENTORNO VISUAL
# =============================================================================
st.set_page_config(page_title="LATAM Cargo - Restricciones 767", page_icon="✈️", layout="wide")

# Inyección de CSS exclusivo para el Banner y Tarjetas de Alerta Personalizadas
st.markdown("""
    <style>
        /* Títulos principales */
        h1, h2, h3, h4 {
            font-family: 'Arial Black', sans-serif;
            color: #00205B !important;
        }
        /* Banner superior estilo LATAM */
        .latam-banner {
            background-color: #00205B;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
            border-left: 6px solid #E12D39;
        }
        .latam-banner h2 {
            color: white !important;
            margin: 0;
            font-size: 24px;
        }
        /* Estilo premium para tarjetas de restricción de peso */
        .report-card {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid #00205B;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }
        .report-card b {
            color: #00205B !important;
        }
        .report-card span {
            color: #333333 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Renderizado del Banner Corporativo
st.markdown("""
    <div class="latam-banner">
        <h2>✈️ LATAM Cargo - Calculadora de Restricciones 767 (Main Deck)</h2>
    </div>
""", unsafe_allow_html=True)

RULES_FILE = "BASELocks_and_deferred.xlsx"

# =============================================================================
# 2. CARGA DE DATOS CENTRALIZADA
# =============================================================================
@st.cache_data
def cargar_datos():
    try:
        df_users = pd.read_excel(RULES_FILE, sheet_name="Users")
        df_restricciones = pd.read_excel(RULES_FILE, sheet_name="ULD_Restrictions")
        df_mapa = pd.read_excel(RULES_FILE, sheet_name="Restraint_ULD_Map")
        
        # Limpieza de espacios en blanco en las cabeceras de columnas
        df_users.columns = [c.strip() for c in df_users.columns]
        df_restricciones.columns = [c.strip() for c in df_restricciones.columns]
        df_mapa.columns = [c.strip() for c in df_mapa.columns]
        
        return df_users, df_restricciones, df_mapa
    except Exception as e:
        st.error(f"Error crítico al leer el archivo Excel: {e}")
        return None, None, None

df_users, rules_df, map_df = cargar_datos()

# =============================================================================
# 3. MÓDULO DE LOGIN Y HERRAMIENTAS DE CONTROL
# =============================================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/LATAM_logo.svg/1024px-LATAM_logo.svg.png", width=150)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.header("🔐 Acceso Corporativo")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    correo = st.sidebar.text_input("Correo Institucional:")
    btn_login = st.sidebar.button("Iniciar Sesión")

    if btn_login:
        if df_users is not None:
            usuario_valido = df_users[df_users['User_Email'].str.lower() == correo.lower()]
            if not usuario_valido.empty:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = usuario_valido.iloc[0]['User_Name']
                st.rerun()
            else:
                st.sidebar.error("Acceso denegado. Correo no registrado en el sistema.")
else:
    st.sidebar.success(f"👤 {st.session_state.usuario_actual}")
    
    # Herramienta interactiva para recargar el Excel en caliente
    if st.sidebar.button("🔄 Refrescar Excel (Limpiar Caché)"):
        st.cache_data.clear()
        st.rerun()
        
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.pos_seleccionada = None
        st.rerun()

# =============================================================================
# 4. MAPA DEL AVIÓN (SIN POSICIÓN A1 - ZONA DE CREW REST MANTENIDA)
# =============================================================================
def dibujar_mapa(pos_seleccionada=None):
    # Diccionario maestro de coordenadas (Posición A1 removida por operaciones)
    posiciones = {
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
    
    # 1. Trazo del Fuselaje del Avión
    path_avion = "M 0.4, 1.5 L 0.4, 14.0 Q 1.5, 16.0 2.6, 14.0 L 2.6, 1.5 Q 1.5, -0.5 0.4, 1.5 Z"
    fig.add_shape(
        type="path", path=path_avion,
        line=dict(color="#00205B", width=3),
        fillcolor="#FFFFFF", layer="below"
    )
    
    # 2. Zona de Cabina / Módulo Crew Rest
    fig.add_shape(
        type="path", path="M 0.9, 14.5 Q 1.5, 15.2 2.1, 14.5 L 1.8, 14.2 Q 1.5, 14.7 1.2, 14.2 Z",
        line=dict(color="#00205B", width=1), fillcolor="#00205B", layer="above"
    )
    fig.add_annotation(
        x=1.5, y=14.8, text="CREW<br>REST", showarrow=False,
        font=dict(size=8, color="white", family="Arial Black")
    )
    
    # 3. Indicador de Puerta de Carga Principal (Main Cargo Door)
    fig.add_shape(
        type="rect", x0=0.3, y0=12.5, x1=0.45, y1=13.8,
        line=dict(color="#E12D39", width=2), fillcolor="#E12D39", layer="above"
    )
    fig.add_annotation(
        x=-0.2, y=13.1, text="CARGO<br>DOOR", showarrow=False, 
        font=dict(size=8, color="#E12D39", family="Arial Black")
    )

    # 4. Renderizado dinámico de Paletas Comerciales
    for nombre, datos in posiciones.items():
        if pos_seleccionada == nombre:
            color = "#E12D39"  # Si está seleccionada, cambia a Rojo Coral LATAM
            line_color = "#00205B"
            line_width = 3
        else:
            if "L" in nombre: color = "#00205B"      # Lado Izquierdo: Azul Índigo
            elif "R" in nombre: color = "#5C768D"    # Lado Derecho: Azul Slate
            else: color = "#4A5568"                  # Posición Trasera A17: Gris
            line_color = "white"
            line_width = 1.5

        fig.add_trace(go.Scatter(
            x=datos["x"], y=datos["y"], mode="markers+text",
            marker=dict(size=42, symbol="square", color=color, line=dict(width=line_width, color=line_color)),
            text=[nombre], textposition="middle center",
            textfont=dict(color="white", size=10, family="Arial Black"),
            customdata=[nombre], hoverinfo="none"
        ))

    fig.update_layout(
        xaxis=dict(showgrid=False, range=[-0.6, 3.6], visible=False),
        yaxis=dict(showgrid=False, range=[0, 16.0], visible=False),
        width=380, height=800, plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        margin=dict(l=0, r=0, t=10, b=10), clickmode="event+select", dragmode=False
    )

    return fig

# =============================================================================
# 5. MOTOR INTELIGENTE DE RESTRICCIONES (CRUCE E IMPEDIMENTO DE FILA 1)
# =============================================================================
def calcular_impacto(df_mapa, df_restricciones, avion_tipo, pos_vista, conteo_danos):
    resultados_finales = []
    model = "767-300BCF" if avion_tipo == "BCF" else "767-300F"
    
    # Traducción de contextos para la base de datos
    if avion_tipo == "BCF":
        contexto_buscar = "BCF Side-by-Side" if "L" in pos_vista or "R" in pos_vista else "BCF Centerline"
        pos_mapa = pos_vista 
    else:
        contexto_buscar = "F Side-by-Side" if "L" in pos_vista or "R" in pos_vista else "F Centerline"
        pos_mapa = pos_vista.replace("A", "") 

    col_map = {"FWD": "FWD_kg", "AFT": "AFT_kg", "LEFT": "LEFT_kg", "RIGHT": "RIGHT_kg"}
    lados_rotos = [lado for lado, qty in conteo_danos.items() if qty > 0]

    for lado in lados_rotos:
        # Validación 1: Regla Crítica del manual (2 seguros rotos en el mismo lado)
        if conteo_danos[lado] >= 2:
            resultados_finales.append({
                "tipo": "alerta_critica", "posicion": pos_vista, "lado_perdido": lado, "kg": 0,
                "origen": f"Múltiples seguros dañados en el lado {lado} (Regla de Adyacencia)"
            })
            continue 

        # Validación 2: Impacto Directo de Peso
        candidatos_peso_directo = df_restricciones[
            (df_restricciones["Model"] == model) & 
            ((df_restricciones["Pos"] == pos_vista) | (df_restricciones["Pos"] == pos_vista.replace("A", "")))
        ]
        
        if not candidatos_peso_directo.empty:
            fila_peso = candidatos_peso_directo.iloc[0]
            col_name = col_map.get(lado)
            if col_name and col_name in fila_peso and pd.notna(fila_peso[col_name]):
                resultados_finales.append({
                    "tipo": "alerta", "posicion": pos_vista, "lado_perdido": lado, "kg": float(fila_peso[col_name]),
                    "origen": "Daño directo reportado"
                })

        # Validación 3: Cruce Inverso y Efecto Dominó (Seguros centrales/compartidos)
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
                
                # Bloqueo de seguridad: Evitar arrastrar restricciones a la fila 1 (Crew Rest)
                if pos_afectada_mapa in ["A1", "1"]:
                    continue
                    
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
                            "tipo": "alerta", "posicion": pos_afectada_pantalla, "lado_perdido": lado_afectado_mapa,
                            "kg": float(fila_peso_comp[col_name_comp]), "origen": "Efecto dominó (Seguro central compartido)"
                        })

    # Filtrar posibles duplicados en las consultas
    resultados_unicos = []
    vistos = set()
    for r in resultados_finales:
        clave = (r["posicion"], r["lado_perdido"], r["kg"], r["tipo"])
        if clave not in vistos:
            vistos.add(clave)
            resultados_unicos.append(r)
    return resultados_unicos

# =============================================================================
# 6. INTERFAZ OPERATIVA PRINCIPAL
# =============================================================================
if st.session_state.autenticado:
    col1, col2 = st.columns([1, 1.4])

    if "pos_seleccionada" not in st.session_state:
        st.session_state.pos_seleccionada = None

    with col1:
        st.info("👇 **PASO 1:** Selecciona la posición en el plano del avión.")
        event = st.plotly_chart(dibujar_mapa(st.session_state.pos_seleccionada), use_container_width=True, on_select="rerun")
        
        if event and "selection" in event and event["selection"]["points"]:
            st.session_state.pos_seleccionada = event["selection"]["points"][0]["customdata"]
            st.rerun()

    with col2:
        st.subheader("🛠️ Configuración de Falla en Rampa")
        avion = st.selectbox("**PASO 2:** Modelo de Aeronave:", ["Seleccionar...", "Freighter", "BCF"])

        if avion != "Seleccionar...":
            if not st.session_state.pos_seleccionada:
                st.warning("👈 Selecciona una posición activa del mapa de la izquierda.")
            else:
                st.markdown(f"Análisis Activo: <b style='color:#E12D39; font-size:18px;'>Posición {st.session_state.pos_seleccionada}</b>", unsafe_allow_html=True)
                st.info("**PASO 3:** Selecciona los seguros físicamente inoperativos:")

                danos_por_lado = {"FWD": 0, "AFT": 0, "LEFT": 0, "RIGHT": 0}
                c_izq, c_centro, c_der = st.columns([1, 2, 1])

                with c_centro:
                    st.markdown("<div style='text-align:center;'><b>⬆️ FRENTE (FWD) ⬆️</b></div>", unsafe_allow_html=True)
                    f1, f2 = st.columns(2)
                    if f1.toggle("FWD Inboard"): danos_por_lado["FWD"] += 1
                    if f2.toggle("FWD Outboard"): danos_por_lado["FWD"] += 1
                    
                    st.markdown("""
                    <div style='background-color:#00205B; border:2px solid #E12D39; border-radius:6px; height:110px; display:flex; align-items:center; justify-content:center; margin: 10px 0;'>
                        <h4 style='color:red !important; margin:0;'>PALETA ULD</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    a1, a2 = st.columns(2)
                    if a1.toggle("AFT Inboard"): danos_por_lado["AFT"] += 1
                    if a2.toggle("AFT Outboard"): danos_por_lado["AFT"] += 1
                    st.markdown("<div style='text-align:center;'><b>⬇️ ATRÁS (AFT) ⬇️</b></div>", unsafe_allow_html=True)

                with c_izq:
                    st.write("<div style='height: 65px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral LEFT"): danos_por_lado["LEFT"] += 1
                
                with c_der:
                    st.write("<div style='height: 65px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral RIGHT"): danos_por_lado["RIGHT"] += 1

                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🚨 ANALIZAR IMPACTO OPERATIVO", type="primary", use_container_width=True):
                    total_danos = sum(danos_por_lado.values())
                    
                    if total_danos == 0:
                        st.success("✅ TODOS LOS SEGUROS OPERATIVOS. Posición autorizada para carga normal.")
                    else:
                        alertas = calcular_impacto(map_df, rules_df, avion, st.session_state.pos_seleccionada, danos_por_lado)
                        
                        st.markdown("---")
                        st.subheader("📋 Resumen de Restricciones Estructurales")
                        
                        if not alertas:
                            st.error("⚠️ Alerta: No se encontró la combinación de pesos en la base de datos.")
                        
                        for r in alertas:
                            if r["tipo"] == "alerta_critica":
                                st.markdown(f"""
                                    <div style='background-color:#FFEBEB; border-left:6px solid #E12D39; padding:15px; border-radius:6px; margin-bottom:10px;'>
                                        <b style='color:#E12D39; font-size:16px;'>🚫 NO LOAD (0 kg) en Posición {r['posicion']}</b><br>
                                        <span style='color:#333333;'><b>Motivo:</b> {r['origen']}</span>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div class="report-card">
                                        <b>📍 Restricción Aplicada: Posición {r['posicion']}</b><br>
                                        <span><b>Condición:</b> Pierde seguro del lado {r['lado_perdido']} ({r['origen']})</span><br>
                                        <span style='font-size:18px; color:#E12D39;'><b>Peso Máximo Permitido:</b> <b>{r['kg']:.0f} kg</b></span>
                                    </div>
                                """, unsafe_allow_html=True)
else:
    st.info("👈 Por favor, ingrese con su correo institucional en el panel de la izquierda para habilitar la aplicación.")
