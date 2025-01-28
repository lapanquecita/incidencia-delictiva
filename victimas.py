"""
Este script analiza las cifras de incidencia delictiva en México.

Se hace uso de los datasets de víctimas, los cuales son diferentes
a las cifras estatales o municipales.

Las cifrás de víctimas son mayores a la de casos, ya que en el de
casos se suelen juntar varias víctimas en uno solo.

"""

import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots


# Todas las gráficas de este script
# van a compartir el mismo esquema de colores.
PLOT_BGCOLOR = "#171010"
PAPER_BGCOLOR = "#2B2B2B"

# La fecha en la que los datos fueron recopilados.
FECHA_FUENTE = "marzo 2024"


MESES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


def tendencia(delito):
    """
    Crea una gráfica con la tendencia de la tasa anual
    de homicidios dolosos a nivel nacional.

    Parameters
    ----------
    delito : str
        El nombre del delito que se desea graficar.

    """

    # Cargamos el dataset de la polación total estimada según el CONAPO.
    pop = pd.read_csv("./assets/poblacion.csv")

    # Seleccionamos las columnas ed años.
    pop = pop.iloc[:, 3:]

    # Calculamos la población nacional anual.
    pop = pop.sum(axis=0)

    # Convertimos el índice a int.
    pop.index = pop.index.astype(int)

    # Cargamos el dataset de víctimas (serie de tiempo).
    df = pd.read_csv(
        "./data/timeseries_victimas.csv", parse_dates=["isodate"], index_col=0
    )

    # Seleccionamos los registros a nivel nacional.
    df = df[df["entidad"] == "Nacional"]

    # Filtramos por el delito que nos interesa.
    df = df[df["delito"] == delito]

    # Calculamos el total de víctimas por año.
    df = df.resample("YE").sum(numeric_only=True)

    # Solo necesitamos el año para emparejar los DataFrames.
    df.index = df.index.year

    # Agregamos la población total para cada año.
    df["poblacion"] = pop

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Preparamos el texto para cada observación dentro de la gráfica.
    df["texto"] = df.apply(
        lambda x: f"<b>{x['tasa']:,.2f}</b><br>({x['total']:,.0f})", axis=1
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["tasa"],
            text=df["texto"],
            marker_color=df["tasa"],
            marker_colorscale="portland",
            marker_cmid=0,
            name=f"Total acumulado: <b>{df['total'].sum():,.0f}</b>",
            textposition="outside",
            marker_line_width=0,
            textfont_size=20,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=12,
    )

    fig.update_yaxes(
        title="Tasa bruta por cada 100,000 habitantes",
        range=[0, df["tasa"].max() * 1.12],
        ticks="outside",
        separatethousands=True,
        title_font_size=18,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.35,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=True,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        legend_font_size=16,
        width=1280,
        height=720,
        font_family="Montserrat",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Evolución de la tasa de <b>{delito.lower()}</b> en México (2015-2024)",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_r=40,
        margin_b=85,
        margin_l=100,
        title_font_size=22,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro del delito",
            ),
            dict(
                x=1.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./tendencia.png")


def comparacion_entidad(primer_año, segundo_año, delito):
    """
    Crea una gráfica de barras donde se comparan
    los totales de dos años.

    Parameters
    ----------
    primer_año : int
        El primer año que deseamos comparar.

    segundo_año : int
        El segundo año que deseamos comparar.

    delito : str
        El nombre del delito que se desea graficar.

    """

    # Cargamos el dataset de víctimas (serie de tiempo).
    df = pd.read_csv(
        "./data/timeseries_victimas.csv", parse_dates=["isodate"], index_col=0
    )

    # Filtramos por el delito que nos interesa.
    df = df[df["delito"] == delito]

    # Seleccionamos los dos años que queremos comparar.
    df = df[(df.index.year == primer_año) | (df.index.year == segundo_año)]

    # Transformamos el DataFrame para tener los conteos por entidad y por año.
    df = df.pivot_table(index="entidad", columns=df.index.year, aggfunc="sum")["total"]

    # Calculamos el cambio porcentual.
    df["cambio"] = (df[segundo_año] - df[primer_año]) / df[primer_año] * 100

    # Preparamos el texto para cada observación.
    df["text"] = df.apply(
        lambda x: f" {x['cambio']:,.2f}% ({x[primer_año]:,.0f} → {x[segundo_año]:,.0f}) ",
        axis=1,
    )

    # Ordenamos de mayor a menor usando el cambio porcentual.
    df.sort_values("cambio", ascending=False, inplace=True)

    # Renombramos algunos estados a sus nombres comunes.
    df = df.rename(
        index={
            "Nacional": "<b>Nacional</b>",
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Calculamos el valor máximo para ajustar el rango del eje horizontal.
    valor_max = df["cambio"].abs().max()
    valor_max = ((valor_max // 5) + 1) * 5

    # Determinamos la posición de los textos para cada barra.
    text_position = list()

    for valor in df["cambio"]:
        ratio = abs(valor) / valor_max

        # Si el valor está cercano al máximo, la etiqueta irá adentro de la barra.
        if ratio >= 0.7:
            text_position.append("inside")
        else:
            text_position.append("outside")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["cambio"],
            text=df["text"],
            textposition=text_position,
            textfont_color="#FFFFFF",
            orientation="h",
            marker_color=df["cambio"],
            marker_colorscale="portland",
            marker_cmid=0,
            marker_line_width=0,
            textfont_size=16,
        )
    )

    fig.update_xaxes(
        range=[valor_max * -1, valor_max],
        ticksuffix="%",
        tickfont_size=14,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.35,
        mirror=True,
        nticks=20,
    )

    fig.update_yaxes(
        autorange="reversed",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.35,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        barmode="overlay",
        width=1280,
        height=1280,
        font_family="Montserrat",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Comparación del total de víctimas de <b>{delito.lower()}</b> registradas en México por entidad ({primer_año} vs. {segundo_año})",
        title_x=0.5,
        title_y=0.98,
        margin_t=60,
        margin_r=40,
        margin_b=80,
        margin_l=200,
        title_font_size=22,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.065,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.58,
                y=-0.065,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Cambio porcentual",
            ),
            dict(
                x=1.01,
                y=-0.065,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./comparacion_entidad.png")


def crear_mapa(año, delito):
    """
    Crea un mapa Choropleth y una tabla con las tasas y total
    de víctimas en México por entidad de registro del
    año especificado.

    Parameters
    ----------
    año : int
        El año de nuestro interés

    delito : str
        El nombre del delito que se desea graficar.

    """

    # Cargamos el dataset de la polación total estimada según el CONAPO.
    pop = pd.read_csv("./assets/poblacion.csv")

    # Calculamos la población total por entidad.
    pop = pop.groupby("Entidad").sum(numeric_only=True)

    # Seleccionamos la población del año de nuestro interés.
    pop = pop[str(año)]

    # Cargamos el dataset de víctimas.
    df = pd.read_csv("./data/victimas.csv", encoding="latin-1")

    # Filtramos por el delito que nos interesa.
    df = df[df["Subtipo de delito"] == delito]

    # Seleccionamos los registros del año de nuestro interés.
    df = df[df["Año"] == año]

    # Calculamos el total anual al sumar todos los meses.
    df["Total"] = df[MESES].sum(axis=1)

    # Transformamos el DataFrame para que las columnas sean el sexo de la víctima.
    df = df.pivot_table(
        index="Entidad", columns="Sexo", values="Total", fill_value=0, aggfunc="sum"
    )

    # Calculamos el total de víctimas por entidad.
    df["Todos"] = df.sum(axis=1)

    # Agregamos la población para cada entidad.
    df["poblacion"] = pop

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["Todos"] / df["poblacion"] * 100000

    # Ordenamos por mayor a menor la tasa.
    df.sort_values("tasa", ascending=False, inplace=True)

    # Renombramos algunos estados a sus nombres comunes.
    df = df.rename(
        index={
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Calculamos los valores a nivel nacional para configurar el subtítulo.
    total_nacional = df["Todos"].sum()
    total_poblacion = df["poblacion"].sum()
    tasa_nacional = total_nacional / total_poblacion * 100000
    subtitulo = f"Nacional: {tasa_nacional:,.2f} ({total_nacional:,.0f} registros)"

    # Determinamos los valores mínimos y máximos para nuestra escala.
    # Para el valor máximo usamos el 97.5 percentil para mitigar los
    # efectos de valores atípicos.
    min_value = df["tasa"].min()
    max_value = df["tasa"].quantile(0.975)

    # Vamos a crear nuestra escala con 11 intervalos.
    marcas = np.linspace(min_value, max_value, 11)
    etiquetas = list()

    for marca in marcas:
        etiquetas.append(f"{marca:,.1f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{etiquetas[-1]}"

    # Cargamos el GeoJSON de México.
    geojson = json.load(open("./assets/mexico.json", "r", encoding="utf-8"))

    # Estas listas serán usadas para configurar el mapa Choropleth.    ubicaciones = list()
    valores = list()
    ubicaciones = list()

    # Iteramos sobre las entidades dentro del GeoJSON.
    for item in geojson["features"]:
        # Extraemos el nombre de la entidad.
        geo = item["properties"]["NOMGEO"]

        # Agregamos el objeto de la entidad y su valor a las listas correspondientes.
        ubicaciones.append(geo)
        valores.append(df.loc[geo, "tasa"])

    fig = go.Figure()

    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=ubicaciones,
            z=valores,
            featureidkey="properties.NOMGEO",
            colorscale="portland",
            colorbar=dict(
                x=0.03,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=2,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=3,
                tickcolor="#FFFFFF",
                ticklen=10,
                tickfont_size=20,
            ),
            marker_line_color="#FFFFFF",
            marker_line_width=1.0,
            zmin=min_value,
            zmax=max_value,
        )
    )

    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor="#082032",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        showlegend=False,
        font_family="Montserrat",
        font_color="#FFFFFF",
        margin_t=50,
        margin_r=40,
        margin_b=30,
        margin_l=40,
        width=1280,
        height=720,
        paper_bgcolor=PAPER_BGCOLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.0,
                xanchor="center",
                yanchor="top",
                text=f"Víctimas de <b>{delito.lower()}</b> registradas en México durante el {año} por entidad de registro",
                font_size=26,
            ),
            dict(
                x=0.0275,
                y=0.45,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Tasa bruta por cada 100,000 habitantes",
                font_size=16,
            ),
            dict(
                x=0.58,
                y=-0.04,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
                font_size=22,
            ),
            dict(
                x=0.01,
                y=-0.04,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
                font_size=22,
            ),
            dict(
                x=1.01,
                y=-0.04,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
                font_size=22,
            ),
        ],
    )

    fig.write_image("./1.png")

    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.03,
        specs=[[{"type": "table"}, {"type": "table"}]],
    )

    fig.add_trace(
        go.Table(
            columnwidth=[150, 80],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Hombres</b>",
                    "<b>Mujeres</b>",
                    "<b>Total*</b>",
                    "<b>Tasa ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color="#FF1E56",
                align="center",
                height=27,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[:16],
                    df["Hombre"][:16],
                    df["Mujer"][:16],
                    df["Todos"][:16],
                    df["tasa"][:16],
                ],
                fill_color=PLOT_BGCOLOR,
                height=27,
                format=["", ",", ",", ",", ",.2f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=1,
        row=1,
    )

    fig.add_trace(
        go.Table(
            columnwidth=[150, 80],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Hombres</b>",
                    "<b>Mujeres</b>",
                    "<b>Total*</b>",
                    "<b>Tasa ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color="#FF1E56",
                align="center",
                height=27,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[16:],
                    df["Hombre"][16:],
                    df["Mujer"][16:],
                    df["Todos"][16:],
                    df["tasa"][16:],
                ],
                fill_color=PLOT_BGCOLOR,
                height=27,
                format=["", ",", ",", ",", ",.2f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=2,
        row=1,
    )

    fig.update_layout(
        width=1280,
        height=560,
        font_family="Montserrat",
        font_color="#FFFFFF",
        font_size=17,
        margin_t=20,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        paper_bgcolor=PAPER_BGCOLOR,
        annotations=[
            dict(
                x=0.5,
                y=0.025,
                xanchor="center",
                yanchor="top",
                text="*El total está conformado por víctimas hombres, mujeres y de sexo no identificado.",
            ),
        ],
    )

    fig.write_image("./2.png")

    # Vamos a usar la librería Pillow para unir ambas imágenes.
    # Primero cargamos las dos imágenes recién creadas.
    imagen1 = Image.open("./1.png")
    imagen2 = Image.open("./2.png")

    # Calculamos el ancho y alto final de nuestra imagen.
    resultado_ancho = imagen1.width
    resultado_alto = imagen1.height + imagen2.height

    # Copiamos los pixeles de ambas imágenes.
    resultado = Image.new("RGB", (resultado_ancho, resultado_alto))
    resultado.paste(im=imagen1, box=(0, 0))
    resultado.paste(im=imagen2, box=(0, imagen1.height))

    # Exportamos la nueva imagen unida y borramos las originales.
    resultado.save(f"./estatal_{año}.png")

    os.remove("./1.png")
    os.remove("./2.png")


def plot_sexo(año, delito):
    """
    Crea una gráfica de barras normalizada con la
    distribución del delito por sexo de la víctima.

    Parameters
    ----------
    año : int
        El año de nuestro interés

    delito : str
        El nombre del delito que se desea graficar.

    """

    # Cargamos el dataset de víctimas.
    df = pd.read_csv("./data/victimas.csv", encoding="latin-1")

    # Filtramos por el delito que nos interesa.
    df = df[df["Subtipo de delito"] == delito]

    # Seleccionamos los registros del año de nuestro interés.
    df = df[df["Año"] == año]

    # CAlculamos el total anual.
    df["Total"] = df[MESES].sum(axis=1)

    # Transformamos el DataFrame para que
    # el índice sean las entidades y el sexo las columnas.
    df = df.pivot_table(
        index="Entidad",
        columns="Sexo",
        values="Total",
        aggfunc="sum",
        fill_value=0,
    )

    # Renombramos algunos estados a sus nombres comunes.
    df = df.rename(
        index={
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Calculamos de nuevo el total, esto será usado
    # para calcular los porcentajes.
    df["Total"] = df.sum(axis=1)

    # Agregamos la fila para los datos a nivel nacional.
    df.loc["<b>Nacional</b>"] = df.sum(axis=0)

    # Calculamos los porcentajes para cada sexo.
    df["perc_hombre"] = df["Hombre"] / df["Total"] * 100
    df["perc_mujer"] = df["Mujer"] / df["Total"] * 100
    df["perc_no_identificado"] = df["No identificado"] / df["Total"] * 100

    # Creamos los textos para cada entidad.
    df["text_hombre"] = df.apply(
        lambda x: format_text(x["perc_hombre"], x["Hombre"]),
        axis=1,
    )

    df["text_mujer"] = df.apply(
        lambda x: format_text(x["perc_mujer"], x["Mujer"]),
        axis=1,
    )

    df["text_no_identificado"] = df.apply(
        lambda x: format_text(x["perc_no_identificado"], x["No identificado"]),
        axis=1,
    )

    # Ordenamos de mayor a menor proporción de hombres violentados.
    df.sort_values(["perc_hombre", "perc_mujer"], ascending=False, inplace=True)

    # Para crear una gráfica de barras normalizada solo
    # necesitamos que los valores sumen 100.
    # En este caso son 3 gráficas de barrs horizontales apiladas.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["perc_hombre"],
            text=df["text_hombre"],
            name="Hombre",
            textposition="inside",
            orientation="h",
            marker_color="#3366CC",
            marker_line_width=0,
            textfont_family="Oswald",
            textfont_size=40,
        )
    )

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["perc_mujer"],
            text=df["text_mujer"],
            name="Mujer",
            textposition="inside",
            orientation="h",
            marker_color="#d81b60",
            marker_line_width=0,
            textfont_family="Oswald",
            textfont_size=40,
        )
    )

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["perc_no_identificado"],
            text=df["text_no_identificado"],
            name="No identificado",
            textposition="inside",
            orientation="h",
            marker_color="#7b1fa2",
            marker_line_width=0,
            textfont_family="Oswald",
            textfont_size=40,
        )
    )

    # Nos aseguramos que el rango sea de 0 a 100.
    fig.update_xaxes(
        range=[0, 100],
        ticksuffix="%",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        zeroline=False,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        autorange="reversed",
        tickfont_size=14,
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=False,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=True,
        legend_orientation="h",
        legend_traceorder="normal",
        legend_x=0.5,
        legend_xanchor="center",
        legend_y=1.042,
        legend_yanchor="top",
        barmode="stack",
        width=1280,
        height=1280,
        font_family="Montserrat",
        font_color="#FFFFFF",
        font_size=16,
        title_text=f"Distribución de víctimas de <b>{delito.lower()}</b> en México durante el {año} por entidad y sexo de la víctima",
        title_x=0.5,
        title_y=0.98,
        margin_t=100,
        margin_r=40,
        margin_b=90,
        margin_l=150,
        title_font_size=22,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.07,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.57,
                y=-0.07,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Proporción dentro de cada categoría (absolutos)",
            ),
            dict(
                x=1.01,
                y=-0.07,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./comparacion_sexo_{año}.png")


def format_text(perc, total):
    """
    Da formato a los textos de cada barra en
    la gráfiac de barras normalizada.
    """

    # Si el porcentaje es 100, no redondeamos.
    if perc == 100:
        return f" {perc:,.0f}% ({total:,.0f}) "
    else:
        return f" {perc:,.1f}% ({total:,.0f}) "


if __name__ == "__main__":
    tendencia("Extorsión")
    comparacion_entidad(2022, 2023, "Extorsión")
    crear_mapa(2023, "Extorsión")
    plot_sexo(2023, "Extorsión")
