import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =============================================================================
# 1. CONFIGURACIÓN
# =============================================================================
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")
st.title("✈️ Calculadora de Restricciones 767")

# Nombre del archivo actualizado
RULES_FILE = "Locks_and_deferred.xlsx"
RULES_SHEET = "ULD_Restrictions"

# =============================================================================
# 2. CARGA DE REGLAS
# =============================================================================
@st.cache_data
def cargar_reglas():
    # Leemos directamente de tu nuevo archivo
    df = pd.read_excel(RULES_FILE, sheet_name=RULES_SHEET)
    # Limpiamos nombres de columnas por si acaso
    df.columns = [c.strip() for c in df.columns]
    return df

rules_df = cargar_reglas()

# =============================================================================
# 3. LOGIN SIMPLE
# =============================================================================
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/LATAM_logo.svg/1024px-LATAM_logo.svg.png",
    width=150
)
st.sidebar.header("🔐 Acceso Corporativo")

correo = st.sidebar.text_input("Correo Institucional:")
password = st.sidebar.text_input("Contraseña:", type="password")
btn_login = st.sidebar.button("Iniciar Sesión")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if btn_login:
    if correo.endswith("@latam.com") and password != "":
        st.session_state.autenticado = True
        st.sidebar.success("Acceso autorizado.")
    elif correo and not correo.endswith("@latam.com"):
        st.sidebar.error("Acceso denegado. Debe usar correo de LATAM.")

# =============================================================================
# 4. MAPA (NO MODIFICADO)
# =============================================================================
def dibujar_mapa():
    posiciones = {
        "A1": {"x": [1.5], "y": [10]},
        "A2L": {"x": [1], "y": [9]},
        "A2R": {"x": [2], "y": [9]},
        "A3L": {"x": [1], "y": [8]},
        "A3R": {"x": [2], "y": [8]},
        "A10L": {"x": [1], "y": [4]},
        "A10R": {"x": [2], "y": [4]},
        "A14": {"x": [1.5], "y": [2]},
    }

    fig = go.Figure()
    for nombre, datos in posiciones.items():
        color = "royalblue" if "L" in nombre else ("orange" if "R" in nombre else "green")
        fig.add_trace(go.Scatter(
            x=datos["x"],
            y=datos["y"],
            mode="markers+text",
            marker=dict(size=45, symbol="square", color=color, line=dict(width=2, color="white")),
            text=[nombre],
            textposition="middle center",
            textfont=dict(color="white", size=12),
            name=f"Posición {nombre}",
            customdata=[nombre],
            hoverinfo="text"
        ))

    fig.update_layout(
        title="Plano Main Deck",
        xaxis=dict(showgrid=False, range=[0, 3], visible=False),
        yaxis=dict(showgrid=False, range=[0, 11], visible=False),
        width=300,
        height=500,
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
        clickmode="event+select",
    )
    return fig

# =============================================================================
# 5. MOTOR DE REGLAS (AJUSTADO A NUEVO EXCEL)
# =============================================================================
def resolver_restriccion(df, model, position, missing_sides):
    # Regla: Si hay más de un seguro dañado, no se puede cargar
    if len(missing_sides) > 1:
        return {
            "status": "NO_LOAD", 
            "kg": 0, 
            "text": "Más de un restraint dañado: la posición no puede cargarse."
        }
    
    if len(missing_sides) == 0:
        return {"status": "NORMAL", "kg": None, "text": "Operación normal."}

    # Filtrar por Modelo y Posición
    candidatos = df[(df["Model"] == model) & (df["Pos"] == position)]

    if candidatos.empty:
        return {
            "status": "REVIEW", 
            "kg": None, 
            "text": f"No se encontró la posición {position} para el modelo {model}."
        }

    fila = candidatos.iloc[0]
    side = missing_sides[0] # FWD, AFT, LEFT, RIGHT

    # Mapeo de lados a columnas del Excel (FWD_kg, AFT_kg, etc.)
    col_map = {"FWD": "FWD_kg", "AFT": "AFT_kg", "LEFT": "LEFT_kg", "RIGHT": "RIGHT_kg"}
    col_name = col_map.get(side)

    if col_name and col_name in fila and pd.notna(fila[col_name]):
        return {
            "status": "OK", 
            "kg": float(fila[col_name]), 
            "text": f"Restricción encontrada: {fila[col_name]} kg."
        }
    
    return {"status": "REVIEW", "kg": None, "text": "No hay restricción definida para ese lado específico."}

# =============================================================================
# 6. APP
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

        avion = st.selectbox(
            "**PASO 2:** Tipo de Aeronave:",
            ["Seleccionar...", "Freighter F (Ej: CC-CXA)", "Convertido BCF"]
        )

        if avion != "Seleccionar...":
            if not pos_seleccionada:
                st.warning("👈 Selecciona una posición del mapa de la izquierda.")
            else:
                # Determinación del Modelo para el filtro
                model = "767-300F" if avion.startswith("Freighter") else "767-300BCF"

                st.success(f"📍 Analizando la **{pos_seleccionada}** en {model}")

                st.markdown("### 🔍 Radiografía de la Paleta")
                st.info("**PASO 3:** Selecciona los seguros inoperativos:")

                inoperativos = []
                c_izq, c_centro, c_der = st.columns([1, 2, 1])

                with c_centro:
                    st.markdown("<div style='text-align:center;'><b>⬆️ FRENTE (FWD) ⬆️</b></div>", unsafe_allow_html=True)
                    f1, f2 = st.columns(2)
                    if f1.toggle("FWD Inboard"): inoperativos.append("FWD")
                    if f2.toggle("FWD Outboard"): inoperativos.append("FWD")
                    
                    st.markdown("""
                    <div style='background-color:#d9e2ec; border:3px dashed #627d98; border-radius:10px; height:180px; display:flex; align-items:center; justify-content:center; flex-direction:column; margin: 15px 0;'>
                        <h2 style='color:#102a43; margin:0;'>📦 PALETA</h2>
                    </div>
                    """, unsafe_allow_html=True)

                    a1, a2 = st.columns(2)
                    if a1.toggle("AFT Inboard"): inoperativos.append("AFT")
                    if a2.toggle("AFT Outboard"): inoperativos.append("AFT")
                    st.markdown("<div style='text-align:center;'><b>⬇️ ATRÁS (AFT) ⬇️</b></div>", unsafe_allow_html=True)

                with c_izq:
                    st.write("<div style='height: 90px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral LEFT"): inoperativos.append("LEFT")
                    st.write("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral RIGHT"): inoperativos.append("RIGHT")

                # Cálculo
                resultado = resolver_restriccion(
                    rules_df,
                    model=model,
                    position=pos_seleccionada,
                    missing_sides=list(set(inoperativos)) # set para evitar duplicados
                )

                if resultado["status"] == "NORMAL":
                    st.success("✅ TODOS LOS SEGUROS OPERATIVOS.")
                elif resultado["status"] == "OK":
                    st.error("🚨 ALERTA DE RESTRICCIÓN")
                    st.markdown(f"#### Restricción Aplicada: **{resultado['kg']:.0f} kg**")
                    st.markdown(f"**Motivo:** {resultado['text']}")
                elif resultado["status"] == "NO_LOAD":
                    st.error("🚨 NO LOAD")
                    st.markdown(f"**Motivo:** {resultado['text']}")
                else:
                    st.warning(resultado["text"])

else:
    st.info("👈 Inicie sesión en el menú lateral para utilizar la herramienta.")
