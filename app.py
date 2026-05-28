# =============================================================================
# 4. MAPA VISUAL COMPLETO (MAIN DECK 767 - BASADO EN MANUALES BOEING/ANCRA)
# =============================================================================
def dibujar_mapa():
    # Posiciones basadas en el WBM D043T532-LAN1 y el Suplemento Ancra 9924
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
        "A17": {"x": [1.5], "y": [2]}, # El manual salta a la A17 en la cola
    }

    fig = go.Figure()
    for nombre, datos in posiciones.items():
        if "L" in nombre:
            color = "#1f77b4" # Azul para Left
        elif "R" in nombre:
            color = "#ff7f0e" # Naranja para Right
        else:
            color = "#2ca02c" # Verde para posiciones centrales (A1 y A17)

        fig.add_trace(go.Scatter(
            x=datos["x"], y=datos["y"],
            mode="markers+text",
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
    
    # Contorno simulando el fuselaje
    fig.add_shape(
        type="rect", x0=0.5, y0=1.2, x1=2.5, y1=14.8,
        line=dict(color="#bcccdc", width=4, shape="spline"),
        fillcolor="rgba(0,0,0,0)", layer="below"
    )

    return fig
