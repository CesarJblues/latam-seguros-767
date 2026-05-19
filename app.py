import streamlit as st
import plotly.graph_objects as go

# --- BASE DE DATOS REAL (AQUÍ RELLENAS CON TUS PDFS) ---
# Estructura: [Avion][Posicion][Seguro_Danado] = Peso_Restringido_KG
BASE_DE_DATOS_REAL = {
    "Freighter (F)": {
        "2L": {"FWD_IN": 3492, "FWD_OUT": 3492, "AFT_IN": 3000, "SIDE_FWD": 2100},
        "10R": {"FWD_IN": 6032, "AFT_IN": 5500}
    },
    "Convertido BCF": {
        "2L": {"AFT_IN": 1747, "FWD_IN": 2800}, # Valor real que mencionaste
        "14": {"FWD_IN": 4000, "AFT_IN": 3800}
    }
}

# --- LÓGICA DE CÁLCULO ---
def consultar_peso(avion, pos, inoperativos):
    try:
        # Simplificación: si fallan varios, tomamos el valor más restrictivo de la tabla
        reglas = BASE_DE_DATOS_REAL.get(avion, {}).get(pos, {})
        valores = [reglas[f] for f in inoperativos if f in reglas]
        if not valores: return "3855 KG (Sin restricciones específicas registradas)"
        return f"{min(valores)} KG", "Valor extraído de tabla de ingeniería."
    except:
        return "N/A", "Posición no configurada en base de datos."

# 1. Configuración
st.set_page_config(page_title="LATAM - Seguros 767", page_icon="✈️", layout="wide")
st.title("✈️ Calculadora de Restricciones 767")

# ... (MANTÉN AQUÍ TU CÓDIGO DE LOGIN Y DIBUJAR MAPA QUE YA FUNCIONA) ...
# [Nota: Para ahorrar espacio aquí, mantén tu código anterior de Login y Dibujar_mapa]

# 4. LA APLICACIÓN PRINCIPAL (MOTOR REAL)
if st.session_state.get('autenticado'):
    # ... (CÓDIGO DE COLUMNAS Y MAPA CLICKEABLE ANTERIOR) ...
    # ...
    # Sustituye la parte final de tu código por esta lógica de consulta real:
    
    # Después de capturar inoperativos en el bloque anterior:
    if len(inoperativos) > 0:
        peso, motivo = consultar_peso(avion, pos_seleccionada, inoperativos)
        st.error("🚨 **ALERTA DE RESTRICCIÓN (MANUAL)**")
        st.markdown(f"#### Peso máximo: **{peso}**")
        st.caption(f"Referencia: {motivo}")
