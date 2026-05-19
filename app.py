import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =============================================================================
# 1. CONFIGURACIÓN
# =============================================================================
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")
st.title("✈️ Calculadora de Restricciones 767")

RULES_FILE = "Restricciones_767_template.xlsx"   # o .csv si prefieres
RULES_SHEET = "ULD_Restrictions"

# =============================================================================
# 2. CARGA DE REGLAS
# =============================================================================
@st.cache_data
def cargar_reglas():
    df = pd.read_excel(RULES_FILE, sheet_name=RULES_SHEET)
    df.columns = [c.strip().lower() for c in df.columns]

    # Normalización básica
    if "active" in df.columns:
        df["active"] = df["active"].astype(str).str.upper().isin(["TRUE", "YES", "1", "SI", "SÍ"])

    for col in ["aircraft_family", "config_group", "position", "missing_side", "rule_type", "restriction_text", "vacate_position"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

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
# 4. MAPA
# =============================================================================
def dibujar_mapa():
    posiciones = {
        "1": {"x": [1.5], "y": [10]},
        "2L": {"x": [1], "y": [9]},
        "2R": {"x": [2], "y": [9]},
        "3L": {"x": [1], "y": [8]},
        "3R": {"x": [2], "y": [8]},
        "10L": {"x": [1], "y": [4]},
        "10R": {"x": [2], "y": [4]},
        "14": {"x": [1.5], "y": [2]},
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
# 5. MOTOR DE REGLAS
# =============================================================================
def resolver_restriccion(df, aircraft_family, config_group, position, missing_sides):
    """
    missing_sides: lista de lados/seguro dañado, por ejemplo ["FWD", "AFT"] o ["LEFT"]
    """

    # Regla del manual: más de un restraint missing/inoperative por ULD => no load
    if len(missing_sides) > 1:
        return {
            "status": "NO_LOAD",
            "kg": 0,
            "text": "Más de un restraint missing/inoperative en la misma ULD: la posición no puede cargarse."
        }

    if len(missing_sides) == 0:
        return {
            "status": "NORMAL",
            "kg": None,
            "text": "Operación normal."
        }

    missing_side = missing_sides[0]

    candidatos = df[
        (df["active"] == True) &
        (df["aircraft_family"].str.upper() == aircraft_family.upper()) &
        (df["config_group"].str.upper() == config_group.upper()) &
        (df["position"].str.upper() == position.upper()) &
        (df["missing_side"].str.upper() == missing_side.upper()) &
        (df["inop_count_min"] <= 1) &
        (df["inop_count_max"] >= 1)
    ].copy()

    if candidatos.empty:
        return {
            "status": "REVIEW",
            "kg": None,
            "text": "No se encontró una regla exacta en la tabla de restricciones."
        }

    # Gana la regla de mayor prioridad (menor número = más prioritaria)
    candidatos = candidatos.sort_values(by=["priority"], ascending=[True])
    fila = candidatos.iloc[0]

    vacate = str(fila.get("vacate_position", "")).strip().upper() in ["YES", "TRUE", "1", "SI", "SÍ"]

    if vacate:
        return {
            "status": "VACANT",
            "kg": 0,
            "text": fila["restriction_text"] if pd.notna(fila["restriction_text"]) else "Position vacant."
        }

    return {
        "status": "OK",
        "kg": float(fila["allowed_weight_kg"]),
        "text": fila["restriction_text"] if pd.notna(fila["restriction_text"]) else "Restricción encontrada."
    }

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
            [
                "Seleccionar...",
                "Freighter F de Fábrica (Ej: CC-CXA)",
                "Convertido BCF (Ancra)"
            ]
        )

        if avion != "Seleccionar...":
            if not pos_seleccionada:
                st.warning("👈 Selecciona una posición del mapa de la izquierda.")
            else:
                # Mapeo del avión a familia/configuración
                if avion.startswith("Freighter F"):
                    aircraft_family = "FREIGHTER"
                    config_group = "FREIGHTER_F"
                else:
                    aircraft_family = "BCF"
                    config_group = "BCF_A_M_R"  # o BCF_B si seleccionas Size Code B

                st.success(f"📍 Analizando la **{pos_seleccionada}**")

                st.markdown("### 🔍 Radiografía de la Paleta")
                st.info("**PASO 3:** Selecciona los seguros inoperativos:")

                inoperativos = []

                c_izq, c_centro, c_der = st.columns([1, 2, 1])

                with c_centro:
                    st.markdown("<div style='text-align:center;'><b>⬆️ FRENTE (FWD) ⬆️</b></div>", unsafe_allow_html=True)

                    f1, f2 = st.columns(2)
                    with f1:
                        if st.toggle("FWD Inboard"):
                            inoperativos.append("FWD")
                    with f2:
                        if st.toggle("FWD Outboard"):
                            inoperativos.append("FWD")

                    st.markdown("""
                    <div style='background-color:#d9e2ec; border:3px dashed #627d98; border-radius:10px; height:180px; display:flex; align-items:center; justify-content:center; flex-direction:column; margin: 15px 0; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
                        <h2 style='color:#102a43; margin:0;'>📦 PALETA</h2>
                        <p style='color:#334e68; margin:0;'>Vista Superior</p>
                    </div>
                    """, unsafe_allow_html=True)

                    a1, a2 = st.columns(2)
                    with a1:
                        if st.toggle("AFT Inboard"):
                            inoperativos.append("AFT")
                    with a2:
                        if st.toggle("AFT Outboard"):
                            inoperativos.append("AFT")

                    st.markdown("<div style='text-align:center;'><b>⬇️ ATRÁS (AFT) ⬇️</b></div>", unsafe_allow_html=True)

                with c_izq:
                    st.write("<div style='height: 90px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral LEFT"):
                        inoperativos.append("LEFT")
                    st.write("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if st.toggle("Lateral RIGHT"):
                        inoperativos.append("RIGHT")

                with c_der:
                    st.write("<div style='height: 90px;'></div>", unsafe_allow_html=True)
                    st.markdown("<span style='color:gray; font-size:12px;'>*Riel lateral externo*</span>", unsafe_allow_html=True)

                st.write("---")

                resultado = resolver_restriccion(
                    rules_df,
                    aircraft_family=aircraft_family,
                    config_group=config_group,
                    position=pos_seleccionada,
                    missing_sides=inoperativos
                )

                if resultado["status"] == "NORMAL":
                    st.success("✅ TODOS LOS SEGUROS OPERATIVOS.")
                elif resultado["status"] == "OK":
                    st.error("🚨 ALERTA DE RESTRICCIÓN")
                    st.markdown(f"#### Restricción Aplicada: **{resultado['kg']:.0f} kg**")
                    st.markdown(f"**Motivo según manual:** {resultado['text']}")
                elif resultado["status"] == "VACANT":
                    st.error("🚨 POSICIÓN VACANTE")
                    st.markdown(f"**Motivo según manual:** {resultado['text']}")
                elif resultado["status"] == "NO_LOAD":
                    st.error("🚨 NO LOAD")
                    st.markdown(f"**Motivo según manual:** {resultado['text']}")
                else:
                    st.warning(resultado["text"])

else:
    st.info("👈 Inicie sesión en el menú lateral para utilizar la herramienta.")
