"""
Este script crea una serie de gráficas tipo sparkline con los delitos
de mayor interés.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Estos son los delitos que nos interesan.
DELITOS = [
    "Homicidio doloso",
    "Feminicidio",
    "Secuestro",
    "Extorsión",
    "Lesiones dolosas",
    "Abuso sexual",
    "Violencia familiar",
    "Narcomenudeo",
    "Robo a negocio",
    "Robo a casa habitación",
    "Robo de vehículo automotor",
    "Robo en transporte público colectivo",
]

# esta constante es usada para definir el último mes.
MES_ACTUAL = "2024-01-01"

# El mes que se mostrará en el título.
MES = "enero"

# El mes que se mostrará en la anotación de la fuente.
MES_FUENTE = "febrero"


def main():
    # Estas abreviaciones serán usadas para el eje horizontal.
    abreviaciones = {
        1: "Ene",
        2: "Feb",
        3: "Mar",
        4: "Abr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dic",
    }

    # Cargamos el dataset de series de tiempo estatal y definimos la columna índice.
    df = pd.read_csv(
        "./data/timeseries_estatal.csv", parse_dates=["isodate"], index_col="isodate"
    )

    # Filtramos el DataFrame hasta el mes actual y a nivel nacional.
    df = df[df.index <= MES_ACTUAL]
    df = df[df["entidad"] == "Nacional"]

    totales = list()
    colores = list()

    # Preparamos el título para cada gráfica.
    subtitulos = [f"<b>{item}</b>" for item in DELITOS]

    # Vamos a necesitar una cuadrícula de 3 columnas por 4 filas.
    fig = make_subplots(
        rows=4,
        cols=3,
        horizontal_spacing=0.08,
        vertical_spacing=0.09,
        subplot_titles=subtitulos,
    )

    # Esta variable la usaremos para saber que delito tomar de nuestra lista.
    index = 0

    # iniciamos la iteración sobre las filas y columnas.
    for fila in range(4):
        for columna in range(3):
            # Filtramos el dataset con el delito seleccionado.
            temp_df = df[df["delito"] == DELITOS[index]].copy()

            # Creamos el promedio móvil.
            temp_df["movil"] = temp_df["total"].rolling(12).mean()

            # Escogemos los últimos 13 meses del delito seleccionado.
            temp_df = temp_df[-13:]

            # Creamos la columna de fecha usando la abreviación y el año en formato corto.
            temp_df["fecha"] = temp_df.index.map(
                lambda x: f"{abreviaciones[x.month]}<br>'{x.year-2000}"
            )

            # Para nuestra gráfica sparkline solo el primer y el último punto
            # tendrán una marca. Aquí definimos eso.
            tamaño_marca = [0 for _ in range(len(temp_df))]
            tamaño_marca[0] = 16
            tamaño_marca[-1] = 16

            # El siguiente grupo de variables van a ser usadas para
            # definir la posición de los textos, así como los colores.
            primer_valor = temp_df["total"].iloc[0]
            segundo_valor = temp_df["total"].iloc[1]
            penultimo_valor = temp_df["total"].iloc[-2]
            ultimo_valor = temp_df["total"].iloc[-1]

            valor_maximo = temp_df["total"].max()
            valor_minimo = temp_df["total"].min()

            # Definimos el texto predeterminado para todas las etiquetas.
            textos = ["" for _ in range(len(temp_df))]

            # Definimos la posición predeterminada para todas las etiquetas.
            text_pos = ["top center" for _ in range(len(temp_df))]

            # Si el primer valor es mayor a 10,000, lo acortamos.
            if primer_valor >= 10000:
                textos[0] = f"<b>{primer_valor / 1000:,.1f}k</b>"
            else:
                textos[0] = f"<b>{primer_valor:,}</b>"

            # Ajustamos la posición de la primera etiqueta.
            if primer_valor >= segundo_valor:
                text_pos[0] = "top center"
            else:
                text_pos[0] = "bottom center"

            if primer_valor == valor_maximo or primer_valor == valor_minimo:
                text_pos[0] = "middle right"

            # Ajustamos la posición de la última etiqueta.
            if ultimo_valor >= 10000:
                textos[-1] = f"<b>{ultimo_valor / 1000:,.1f}k</b>"
            else:
                textos[-1] = f"<b>{ultimo_valor:,}</b>"

            if ultimo_valor >= penultimo_valor:
                text_pos[-1] = "top center"
            else:
                text_pos[-1] = "bottom center"

            if ultimo_valor == valor_maximo or ultimo_valor == valor_minimo:
                text_pos[-1] = "middle left"

            # Definimos el color del sparkline.
            # Amarillo si hubo un aumento o azul si hubo una reducción.
            if ultimo_valor < primer_valor:
                color = "#18ffff"
            else:
                color = "#ffd740"

            colores.append(color)

            # Estas variables serán usadas para la anotación de cada sparkline.
            diferencia = ultimo_valor - primer_valor
            cambio_porcentual = (ultimo_valor - primer_valor) / primer_valor * 100

            if diferencia > 0:
                totales.append(f"<b>+{diferencia:,}</b><br>+{cambio_porcentual:,.2f}%")
            else:
                totales.append(f"<b>{diferencia:,}</b><br>{cambio_porcentual:,.2f}%")

            # Creamos nuestro sparkline.
            fig.add_trace(
                go.Scatter(
                    x=temp_df["fecha"],
                    y=temp_df["total"],
                    text=textos,
                    mode="markers+lines+text",
                    textposition=text_pos,
                    textfont_size=16,
                    marker_color=color,
                    marker_opacity=1.0,
                    marker_size=tamaño_marca,
                    marker_line_width=0,
                    line_width=3.5,
                    line_shape="spline",
                    line_smoothing=1.0,
                ),
                row=fila + 1,
                col=columna + 1,
            )

            # Agregamos el promedio móvil.
            fig.add_trace(
                go.Scatter(
                    x=temp_df["fecha"],
                    y=temp_df["movil"],
                    mode="lines",
                    line_width=3.5,
                    line_color="hsla(255, 100, 100, 0.8)",
                ),
                row=fila + 1,
                col=columna + 1,
            )

            index += 1

    fig.update_xaxes(
        tickfont_size=12,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        gridwidth=0.35,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        title_text="Delitos registrados mensualmente",
        separatethousands=True,
        tickfont_size=14,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=10,
    )

    fig.update_layout(
        font_family="Lato",
        showlegend=False,
        width=1600,
        height=1600,
        font_color="#FFFFFF",
        font_size=14,
        margin_t=160,
        margin_l=110,
        margin_r=40,
        margin_b=120,
        title_text=f"Reporte de incidencia delictiva en México correspondiente al mes de {MES} del año 2024",
        title_x=0.5,
        title_y=0.98,
        title_font_size=28,
        plot_bgcolor="#1A1A2E",
        paper_bgcolor="#16213E",
    )

    # Estas listas guardaran las coordenadas X y Y de nuestras anotaciones.
    anotaciones_x = list()
    anotaciones_y = list()

    # Esta lista representa la posición de las anotaciones dentro de cada gráfica.
    posiciones = [
        "up",
        "bottom",
        "top",
        "top",
        "top",
        "top",
        "top",
        "bottom",
        "bottom",
        "bottom",
        "bottom",
        "bottom",
    ]

    # Lo que haremos se puede considerar como un hack.
    # Cuando se agregan títulos a las gráficas, estos se consideran como anotaciones.
    # Lo que haremos es modificar estos títulos y extraer sus coordenadas
    # para usarlas en nuestras propias anotaciones.
    for annotation in fig["layout"]["annotations"]:
        # Ajustamos un poco la posición Y de los títulos y le cambiamos el tamaño de texto.
        annotation["y"] += 0.005
        annotation["font"]["size"] = 24

        # Extraemos las coordenadas X y Y.
        anotaciones_x.append(annotation["x"])
        anotaciones_y.append(annotation["y"])

    # Ahora que ya tenemos todo lo necesario para nuestras anotaciones, las creamos.
    for x, y, t, c, p in zip(
        anotaciones_x, anotaciones_y, totales, colores, posiciones
    ):
        # Esto pondrá la anotación en la parte izquierda de cada gráfica.
        x -= 0.125

        # Si la posición es 'top', la anotación ira arriba, de lo contraroi irá abajo.
        if p == "top":
            y -= 0.038
        else:
            y -= 0.158

        # Creamos nuestra anotación con el color, texto y coordenadas.
        fig.add_annotation(
            x=x,
            xanchor="left",
            xref="paper",
            y=y,
            yanchor="top",
            yref="paper",
            text=t,
            font_color=c,
            font_size=18,
            bordercolor=c,
            borderpad=5,
            borderwidth=1.5,
            bgcolor="#1A1A2E",
        )

    fig.add_annotation(
        x=0.01,
        xanchor="left",
        xref="paper",
        y=-0.095,
        yanchor="bottom",
        yref="paper",
        text=f"Fuente: SESNSP ({MES_FUENTE} 2024)",
        font_size=20,
    )

    fig.add_annotation(
        x=0.5,
        xanchor="center",
        xref="paper",
        y=1.05,
        yanchor="top",
        yref="paper",
        font_size=22,
        text="(Un registro de delito puede tener más de una víctima. Se incluye el promedio móvil de los últimos 12 meses.)",
    )

    fig.add_annotation(
        x=0.5,
        xanchor="center",
        xref="paper",
        y=-0.095,
        yanchor="bottom",
        yref="paper",
        text="Se compara el mismo mes respecto al año anterior",
        font_size=20,
    )

    fig.add_annotation(
        x=1.01,
        xanchor="right",
        xref="paper",
        y=-0.095,
        yanchor="bottom",
        yref="paper",
        text="🧁 @lapankecita",
        font_size=20,
    )

    fig.write_image("./alto_impacto.png")


if __name__ == "__main__":
    main()
