"""
Este script crea una serie de gráficas tipo sparkline con los delitos
de mayor interés.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import STL


# Estos son los delitos que nos interesan.
# A partir de la nueva metodología (2026)
# algunos subtipos de delitos fueron desagregados
# y por lo tanto se debe especificar la nueva modalidad.
DELITOS = {
    "Homicidio doloso": ["Homicidio doloso"],
    "Feminicidio": ["Feminicidio"],
    "Secuestro": [
        "Secuestro",
        "Secuestro extorsivo",
        "Secuestro con calidad de rehén",
        "Secuestro para causar daño",
        "Secuestro exprés",
    ],
    "Extorsión": [
        "Extorsión",
        "Extorsión presencial",
        "Extorsión por otros medios",
    ],
    "Lesiones dolosas": ["Lesiones dolosas"],
    "Abuso sexual": ["Abuso sexual"],
    "Violencia familiar": ["Violencia familiar"],
    "Narcomenudeo": [
        "Narcomenudeo",
        "Narcomenudeo posesión simple",
        "Narcomenudeo con fines de venta",
    ],
    "Robo a negocio": ["Robo a negocio"],
    "Robo a casa habitación": ["Robo a casa habitación"],
    "Robo de vehículo automotor": [
        "Robo de vehículo automotor",
        "Robo de vehículo automotor - Coche de 4 ruedas",
        "Robo de vehículo automotor - Motocicleta",
        "Robo de vehículo automotor - Embarcaciones",
    ],
    "Robo en transporte público colectivo": ["Robo en transporte público colectivo"],
}

# Esta constante es usada para definir que mes será comparado.
MES_REFERENCIA = "2026-02-01"

# El mes que se mostrará en el título.
MES = "febrero"

# El mes que se mostrará en la anotación de la fuente.
MES_FUENTE = "marzo"


# Estas abreviaciones serán usadas para el eje horizontal.
ABREVIACIONES = {
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


def main():
    """
    Genera una cuadrícula de gráficas linea mostrando
    la tendencia de los delitos especificados.
    """

    # Cargamos el dataset de series de tiempo estatal y definimos la columna índice.
    df = pd.read_csv(
        "./data/timeseries_estatal.csv", parse_dates=["PERIODO"], index_col="PERIODO"
    )

    # Filtramos el DataFrame hasta el mes actual.
    df = df[df.index <= MES_REFERENCIA]

    totales = list()
    colores = list()

    # Preparamos el título para cada gráfica.
    subtitulos = [f"<b>{item}</b>" for item in DELITOS.keys()]

    # Estos serán los grupos de subdelitos que se analizarán.
    subtipos_delito = [item for item in DELITOS.values()]

    # Esta lista representa la posición de las anotaciones dentro de cada gráfica.
    posiciones = list()

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
            # Filtramos el dataset con el delito seleccionado y agruapoms por mes.
            temp_df = (
                df[df["DELITO"].isin(subtipos_delito[index])]
                .resample("MS")
                .sum(numeric_only=True)
            )

            # Escogemos los últimos 13 meses del delito seleccionado.
            temp_df = temp_df[-13:]

            # Calculamos la tendencia usando STL.
            temp_df["tendencia"] = STL(temp_df["TOTAL"]).fit().trend

            # Creamos la columna de fecha usando la abreviación y el año en formato corto.
            temp_df["fecha"] = temp_df.index.map(
                lambda x: f"{ABREVIACIONES[x.month]}<br>'{x.year - 2000}"
            )

            # Para nuestra gráfica sparkline solo el primer y el último punto
            # tendrán una marca. Aquí definimos eso.
            tamaño_marca = [0 for _ in range(len(temp_df))]
            tamaño_marca[0] = 16
            tamaño_marca[-1] = 16

            # El siguiente grupo de variables van a ser usadas para
            # definir la posición de los textos, así como los colores.
            primer_valor = temp_df["TOTAL"].iloc[0]
            segundo_valor = temp_df["TOTAL"].iloc[1]
            penultimo_valor = temp_df["TOTAL"].iloc[-2]
            ultimo_valor = temp_df["TOTAL"].iloc[-1]

            valor_maximo = temp_df["TOTAL"].max()
            valor_minimo = temp_df["TOTAL"].min()

            punto_medio = (valor_maximo + valor_minimo) / 2

            if primer_valor >= punto_medio:
                posiciones.append("bottom")
            else:
                posiciones.append("top")

            # Definimos el texto predeterminado para todas las etiquetas.
            textos = ["" for _ in range(len(temp_df))]

            # Definimos la posición predeterminada para todas las etiquetas.
            text_pos = ["top center" for _ in range(len(temp_df))]

            # Si el primer o último valor es mayor a 10,000, lo acortamos.
            if primer_valor >= 10000:
                textos[0] = f"<b>{primer_valor / 1000:,.1f}k</b>"
            else:
                textos[0] = f"<b>{primer_valor:,}</b>"

            if ultimo_valor >= 10000:
                textos[-1] = f"<b>{ultimo_valor / 1000:,.1f}k</b>"
            else:
                textos[-1] = f"<b>{ultimo_valor:,}</b>"

            # Estos ratios nos ayudan a acomodar nuestras etiquetas con más precisión.
            primer_valor_ratio = segundo_valor / primer_valor
            ultimo_valor_ratio = penultimo_valor / ultimo_valor

            # Ajustamos la posición de la primera etiqueta.
            if primer_valor == valor_maximo:
                if primer_valor_ratio <= 0.70:
                    text_pos[0] = "bottom center"
                else:
                    text_pos[0] = "middle right"
            elif primer_valor == valor_minimo:
                if primer_valor_ratio <= 0.95:
                    text_pos[0] = "middle right"
                else:
                    text_pos[0] = "top center"
            else:
                if primer_valor_ratio <= 1.0:
                    text_pos[0] = "top center"
                else:
                    text_pos[0] = "bottom center"

            # Ajustamos la posición de la última etiqueta.
            if ultimo_valor == valor_maximo:
                if ultimo_valor_ratio <= 1.0:
                    text_pos[-1] = "middle left"
                else:
                    text_pos[-1] = "top center"
            elif ultimo_valor == valor_minimo:
                if ultimo_valor_ratio <= 1.02:
                    text_pos[-1] = "top center"
                else:
                    text_pos[-1] = "middle left"
            else:
                if ultimo_valor_ratio <= 1.0:
                    text_pos[-1] = "top center"
                else:
                    text_pos[-1] = "bottom center"

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
                    y=temp_df["TOTAL"],
                    text=textos,
                    mode="markers+lines+text",
                    textposition=text_pos,
                    textfont_size=20,
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
                    y=temp_df["tendencia"],
                    mode="lines",
                    line_width=3.5,
                    line_color="hsla(255, 100, 100, 0.8)",
                ),
                row=fila + 1,
                col=columna + 1,
            )

            index += 1

    fig.update_xaxes(
        tickfont_size=17,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        title_text="Incidencia mensual",
        tickformat=".2s",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=10,
    )

    fig.update_layout(
        font_family="Inter",
        showlegend=False,
        width=2000,
        height=2000,
        font_color="#FFFFFF",
        font_size=18,
        margin_t=200,
        margin_l=110,
        margin_r=40,
        margin_b=150,
        title_text=f"Reporte de incidencia delictiva en México correspondiente al mes de {MES} del año {MES_REFERENCIA[:4]}",
        title_x=0.5,
        title_y=0.98,
        title_font_size=40,
        plot_bgcolor="#1A1A2E",
        paper_bgcolor="#16213E",
    )

    # Estas listas guardaran las coordenadas X y Y de nuestras anotaciones.
    anotaciones_x = list()
    anotaciones_y = list()

    # Lo que haremos se puede considerar como un hack.
    # Cuando se agregan títulos a las gráficas, estos se consideran como anotaciones.
    # Lo que haremos es modificar estos títulos y extraer sus coordenadas
    # para usarlas en nuestras propias anotaciones.
    for annotation in fig["layout"]["annotations"]:
        # Ajustamos un poco la posición Y de los títulos y le cambiamos el tamaño de texto.
        annotation["y"] += 0.005
        annotation["font"]["size"] = 28

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
            y -= 0.036
        else:
            y -= 0.154

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
            font_size=22,
            bordercolor=c,
            borderpad=5,
            borderwidth=2,
            bgcolor="#1A1A2E",
        )

    fig.add_annotation(
        x=0.01,
        xanchor="left",
        xref="paper",
        y=-0.095,
        yanchor="bottom",
        yref="paper",
        text=f"Fuente: SESNSP ({MES_FUENTE} 2026)",
        font_size=24,
    )

    fig.add_annotation(
        x=0.5,
        xanchor="center",
        xref="paper",
        y=1.05,
        yanchor="top",
        yref="paper",
        font_size=30,
        text="(Un registro de delito puede tener más de una víctima. Se incluye la tendencia de los últimos 12 periodos.)",
    )

    fig.add_annotation(
        x=0.5,
        xanchor="center",
        xref="paper",
        y=-0.095,
        yanchor="bottom",
        yref="paper",
        text="Se compara el mismo mes respecto al año anterior",
        font_size=24,
    )

    fig.add_annotation(
        x=1.01,
        xanchor="right",
        xref="paper",
        y=-0.095,
        yanchor="bottom",
        yref="paper",
        text="🧁 @lapanquecita",
        font_size=24,
    )

    fig.write_image("./alto_impacto.png")


if __name__ == "__main__":
    main()
