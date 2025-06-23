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
from statsmodels.tsa.seasonal import STL


# Todas las gráficas de este script
# van a compartir el mismo esquema de colores.
PLOT_COLOR = "#171010"
PAPER_COLOR = "#2B2B2B"

# La fecha en la que los datos fueron recopilados.
FECHA_FUENTE = "junio 2025"


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


# Este diccionario es utilizado por todas las funciones
# para poder referenciar cada entidad con su clave numérica.
ENTIDADES = {
    0: "México",
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "Estado de México",
    16: "Michoacán",
    17: "Morelos",
    18: "Nayarit",
    19: "Nuevo León",
    20: "Oaxaca",
    21: "Puebla",
    22: "Querétaro",
    23: "Quintana Roo",
    24: "San Luis Potosí",
    25: "Sinaloa",
    26: "Sonora",
    27: "Tabasco",
    28: "Tamaulipas",
    29: "Tlaxcala",
    30: "Veracruz",
    31: "Yucatán",
    32: "Zacatecas",
}


def tendencia_anual(delito, entidad_id, xanchor="left"):
    """
    GEnera una gráfica mostrando la evolución
    de la tasa anual del delito y entidad especificados.

    Parameters
    ----------
    delito : str
        El nombre del delito que se desea graficar.

    entidad_id : int
        La clave numérica de la entidad. 0 para datos a nivel nacional.

    xanchor : str
        Es la ubicación de la leyenda dentro del gráfico.
        Los posibles valores pueden ser "left" o "right".

    """

    # Cargamos el dataset de la población estimada según el CONAPO.
    pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str})

    # Sumamos el total de población por entidad.
    pop["CVE"] = pop["CVE"].str[:2]
    pop = pop.groupby("CVE").sum(numeric_only=True)

    # Si el valor de entidad_id es 0, sumamos la población de todas las entidades.
    if entidad_id == 0:
        pop = pop.sum(axis=0)
    else:
        pop = pop.loc[f"{entidad_id:02}"]

    # Convertimos el índice a int.
    pop.index = pop.index.astype(int)

    # Cargamos el dataset de víctimas (serie de tiempo).
    df = pd.read_csv(
        "./data/timeseries_victimas.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Filtramos por entidad. Si entidad_es 0, no hacemos filtro.
    if entidad_id != 0:
        df = df[df["ENTIDAD"] == ENTIDADES[entidad_id]]

    # Filtramos por el delito que nos interesa.
    df = df[df["DELITO"] == delito]

    # Calculamos el total de víctimas por año.
    df = df.resample("YS").sum(numeric_only=True)

    # Solo necesitamos el año para emparejar los DataFrames.
    df.index = df.index.year

    # Agregamos la población total para cada año.
    df["poblacion"] = pop

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["TOTAL"] / df["poblacion"] * 100000

    # Preparamos el texto para cada observación dentro de la gráfica.
    df["texto"] = df.apply(
        lambda x: f"<b>{x['tasa']:,.2f}</b><br>({x['TOTAL']:,.0f})", axis=1
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["tasa"],
            text=df["texto"],
            marker_color=df["tasa"],
            marker_colorscale="redor",
            name=f"<b>Total acumulado</b><br>{df['TOTAL'].sum():,.0f} víctimas",
            textposition="outside",
            marker_line_width=0,
            textfont_size=40,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=12,
    )

    fig.update_yaxes(
        title="Tasa bruta por cada 100,000 habitantes",
        range=[0, df["tasa"].max() * 1.13],
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        showlegend=True,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01 if xanchor == "left" else 0.99,
        legend_y=0.98,
        legend_xanchor=xanchor,
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la tasa de <b>{delito.lower()}</b> en <b>{ENTIDADES[entidad_id]}</b> ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.97,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=130,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro del delito",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Guardamos el archiov usando la clave de la entidad.
    fig.write_image(f"./tendencia_anual_{entidad_id}.png")


def tendencia_mensual(delito, entidad_id, xanchor="left"):
    """
    GEnera una gráfica mostrando la evolución
    de la incidencia mensual del delito y entidad especificados.

    Parameters
    ----------
    delito : str
        El nombre del delito que se desea graficar.

    entidad_id : int
        La clave numérica de la entidad. 0 para datos a nivel nacional.

    xanchor : str
        Es la ubicación de la leyenda dentro del gráfico.
        Los posibles valores pueden ser "left" o "right".

    """

    # Cargamos el dataset de víctimas (serie de tiempo).
    df = pd.read_csv(
        "./data/timeseries_victimas.csv", parse_dates=["PERIODO"], index_col=0
    )

    # Filtramos por entidad. Si entidad_es 0, no hacemos filtro.
    if entidad_id != 0:
        df = df[df["ENTIDAD"] == ENTIDADES[entidad_id]]

    # Filtramos por el delito que nos interesa.
    df = df[df["DELITO"] == delito]

    # Calculamos el total de víctimas por mes.
    df = df.resample("MS").sum(numeric_only=True)

    # Calculamos la tendencia usando STL.
    df["tendencia"] = STL(df["TOTAL"]).fit().trend

    # Solo vamos a mostrar los últimos 120 meses (10 años).
    # Con esto es suficiente para mostrar una tendencia a mediano plazo.
    df = df.tail(120)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["TOTAL"],
            marker_color="#00897b",
            name="Serie original",
            marker_line_width=0,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["tendencia"],
            mode="lines",
            line_color="#ffd54f",
            name="Tendencia (12 periodos)",
            line_width=6,
        )
    )

    fig.update_xaxes(
        tickformat="%m<br>%Y",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Víctimas mensuales",
        tickformat="s",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        showlegend=True,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01 if xanchor == "left" else 0.99,
        legend_y=0.98,
        legend_xanchor=xanchor,
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la incidencia mensual de <b>{delito.lower()}</b> en <b>{ENTIDADES[entidad_id]}</b> ({df.index.year.min()}-{df.index.year.max()})",
        title_x=0.5,
        title_y=0.97,
        margin_t=80,
        margin_r=40,
        margin_b=160,
        margin_l=130,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro del delito",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Guardamos el archiov usando la clave de la entidad.
    fig.write_image(f"./tendencia_mensual_{entidad_id}.png")


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
    df = pd.read_csv("./data/timeseries_victimas.csv", parse_dates=["PERIODO"])

    # Filtramos por el delito que nos interesa.
    df = df[df["DELITO"] == delito]

    # Transformamos el DataFrame para tener los conteos por entidad y por año.
    df = df.pivot_table(
        index="CVE_ENT",
        columns=df["PERIODO"].dt.year,
        values="TOTAL",
        aggfunc="sum",
        fill_value=0,
    )

    # Asignamos el nombre común para cada entidad.
    df.index = df.index.map(ENTIDADES)

    # Creamos la fila para el total naiconal.
    df.loc["<b>Nacional</b>"] = df.sum(axis=0)

    # Calculamos el cambio porcentual.
    df["cambio"] = (df[segundo_año] - df[primer_año]) / df[primer_año] * 100

    # Quitamos las filas con cambios inválidos.
    df = df.dropna(axis=0)

    # Preparamos el texto para cada observación.
    df["texto"] = df.apply(
        lambda x: f" {x['cambio']:,.1f}% ({x[primer_año]:,.0f} → {x[segundo_año]:,.0f}) ",
        axis=1,
    )

    # Ordenamos de mayor a menor usando el cambio porcentual.
    df.sort_values("cambio", ascending=False, inplace=True)

    # Calculamos el valor máximo para ajustar el rango del eje horizontal.
    valor_max = df["cambio"].abs().max()
    valor_max = ((valor_max // 5) + 1) * 5

    # Determinamos la posición de los textos para cada barra.
    df["ratio"] = df["cambio"].abs() / valor_max
    df["texto_pos"] = df["ratio"].apply(lambda x: "inside" if x >= 0.7 else "outside")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df.index,
            x=df["cambio"],
            text=df["texto"],
            textposition=df["texto_pos"],
            textfont_color="#FFFFFF",
            orientation="h",
            marker_color=df["cambio"],
            marker_colorscale="geyser",
            marker_cmid=0,
            marker_line_width=0,
            textfont_size=30,
            textfont_family="Oswald",
        )
    )

    fig.update_xaxes(
        range=[valor_max * -1, valor_max],
        ticksuffix="%",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        gridwidth=0.5,
        mirror=True,
        nticks=20,
    )

    fig.update_yaxes(
        autorange="reversed",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1920,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Comparación del total de víctimas de <b>{delito.lower()}</b> registradas en México ({primer_año} vs. {segundo_año})",
        title_x=0.5,
        title_y=0.98,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=280,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.58,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Cambio porcentual (cambio absoluto)",
            ),
            dict(
                x=1.01,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Guardamos el nombre del archivo usando los parámetros de la función.
    fig.write_image(f"./comparacion_entidad_{primer_año}_{segundo_año}.png")


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

    # Cargamos el dataset de la población estimada según el CONAPO.
    pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str})

    # Sumamos el total de población por entidad.
    pop["CVE"] = pop["CVE"].str[:2]
    pop = pop.groupby("CVE").sum(numeric_only=True)

    # Convertimos el índice a int para poderlo emparejar
    # con las cifras de delitos.
    pop.index = pop.index.astype(int)

    # Seleccionamos la población del año especificado.
    pop = pop[str(año)]

    # Cargamos el dataset de víctimas (serie de tiempo).
    df = pd.read_csv("./data/timeseries_victimas.csv", parse_dates=["PERIODO"])

    # Filtramos por el delito que nos interesa.
    df = df[df["DELITO"] == delito]

    # Seleccionamos los registros del año especificado.
    df = df[df["PERIODO"].dt.year == año]

    # Transformamos el DataFrame para tener los conteos por entidad y por año.
    df = df.pivot_table(
        index="CVE_ENT",
        columns="SEXO",
        values="TOTAL",
        aggfunc="sum",
        fill_value=0,
    )

    # Calculamos el total por entidad.
    df["total"] = df.sum(axis=1)

    # Agregamos la población para cada entidad.
    df["pop"] = pop

    # Calculamos la tasa por cada 100,000 habitantes.
    df["tasa"] = df["total"] / df["pop"] * 100000

    # Ordenamos la tasa de manera descendente.
    df.sort_values("tasa", ascending=False, inplace=True)

    # Calculamos los totales nacionales.
    total_nacional = df["total"].sum()
    poblacion_nacional = pop.sum()

    # Preparamos los valores para nuestro subtítulo.
    subtitulo = f"Tasa nacional: <b>{total_nacional / poblacion_nacional * 100000:,.1f}</b> (con <b>{total_nacional:,.0f}</b> víctimas)"

    # Quitamos los valores NaN para que no interfieran con los siguientes pasos.
    df = df.dropna(axis=0)

    # Determinamos los valores mínimos y máximos para nuestra escala.
    # Para el valor máximo usamos el 95 percentil para mitigar los
    # efectos de valores atípicos.
    valor_min = df["tasa"].min()
    valor_max = df["tasa"].quantile(0.95)

    # Vamos a crear nuestra escala con 13 intervalos.
    marcas = np.linspace(valor_min, valor_max, 13)
    etiquetas = list()

    for item in marcas:
        if item >= 10:
            etiquetas.append(f"{item:,.0f}")
        else:
            etiquetas.append(f"{item:,.1f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{etiquetas[-1]}"

    # Cargamos el GeoJSON de México.
    geojson = json.load(open("./assets/mexico.json", "r", encoding="utf-8"))

    fig = go.Figure()

    # PAra hacer funcionar el mapa debemos emparejar los valores
    # de la propiedad CVEGEO con nuestro DataFrame.
    # En este caso en particular, solo se requiere convertirlos
    # a string y agregar un cero cuando sea menor de 10.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index.astype(str).str.zfill(2),
            z=df["tasa"],
            featureidkey="properties.CVEGEO",
            colorscale="portland",
            zmin=valor_min,
            zmax=valor_max,
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
            ),
        )
    )

    # El propósito de este segundo mapa es dibujar la división política.
    # En casos donde un estado no tiene registros, normalmente no se vería esto.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=pop.index.astype(str).str.zfill(2),
            z=[1 for _ in range(len(pop))],
            featureidkey="properties.CVEGEO",
            colorscale=["hsla(0,0,0,0)", "hsla(0,0,0,0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=1.5,
            zmin=0,
            zmax=1,
            showscale=False,
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
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=80,
        margin_r=40,
        margin_b=60,
        margin_l=40,
        width=1920,
        height=1080,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.025,
                xanchor="center",
                yanchor="top",
                text=f"Incidencia de víctimas de <b>{delito.lower()}</b> en México durante el {año}",
                font_size=42,
            ),
            dict(
                x=0.0275,
                y=0.46,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Tasa bruta por cada 100,000 habitantes",
            ),
            dict(
                x=0.01,
                y=-0.056,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.056,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=-0.056,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Guardamos el mapa con un nombre temporal.
    fig.write_image("./1.png")

    # Ahora crearemos las tablas con el desglose por entidad.

    # Agregamos el nombre a cada entidad.
    df["nombre"] = df.index.map(lambda x: ENTIDADES[x])

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
                fill_color=["#00897b", "#00897b", "#00897b", "#00897b", "#FF1E56"],
                align="center",
                height=43,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df["nombre"][:16],
                    df["Hombre"][:16],
                    df["Mujer"][:16],
                    df["total"][:16],
                    df["tasa"][:16],
                ],
                fill_color=PLOT_COLOR,
                height=43,
                format=["", ",", ",", ",", ",.1f"],
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
                fill_color=["#00897b", "#00897b", "#00897b", "#00897b", "#FF1E56"],
                align="center",
                height=43,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df["nombre"][16:],
                    df["Hombre"][16:],
                    df["Mujer"][16:],
                    df["total"][16:],
                    df["tasa"][16:],
                ],
                fill_color=PLOT_COLOR,
                height=43,
                format=["", ",", ",", ",", ",.1f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=2,
        row=1,
    )

    fig.update_layout(
        width=1920,
        height=840,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=25,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=0.03,
                xanchor="center",
                yanchor="top",
                text="*El total está conformado por hombres, mujeres y víctimas con sexo no identificado.",
            ),
        ],
    )

    # Guardamos la tabla con un nombre temporal.
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
    resultado.save(f"./mapa_estatal_{año}.png")

    os.remove("./1.png")
    os.remove("./2.png")


def comparacion_sexo(año, delito):
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

    # Estos son los colores para cada categoría de sexo.
    colores = {"Hombre": "#00695c", "Mujer": "#e65100", "No identificado": "#7b1fa2"}

    # Cargamos el dataset de víctimas.
    df = pd.read_csv("./data/timeseries_victimas.csv", parse_dates=["PERIODO"])

    # Filtramos por el delito que nos interesa.
    df = df[df["DELITO"] == delito]

    # Seleccionamos los registros del año de nuestro interés.
    df = df[df["PERIODO"].dt.year == año]

    # Transformamos el DataFrame para que
    # el índice sean las entidades y el sexo las columnas.
    df = df.pivot_table(
        index="CVE_ENT",
        columns="SEXO",
        values="TOTAL",
        aggfunc="sum",
        fill_value=0,
    )

    # Asignamos el nombre común para cada entidad.
    df.index = df.index.map(ENTIDADES)

    # Calculamos de nuevo el total, esto será usado
    # para calcular los porcentajes.
    df["Total"] = df.sum(axis=1)

    # Agregamos la fila para los datos a nivel nacional.
    df.loc["<b>Nacional</b>"] = df.sum(axis=0)

    sexos_disponibles = df.columns[:-1]

    # De forma dinámica, calcularemos el porcentaje y texto
    # pcara cada sexo.
    for sexo in sexos_disponibles:
        # Calculamos los porcentajes para cada sexo.
        df[f"perc_{sexo}"] = df[sexo] / df["Total"] * 100

        # Creamos los textos para cada entidad.
        df[f"text_{sexo}"] = df.apply(
            lambda x: f"{x[f'perc_{sexo}']:,.1f}% ({x[sexo]:,.0f}) ".replace(
                ".0%", "%"
            ),
            axis=1,
        )

    # Ordenamos de mayor a menor proporción de hombres violentados.
    df.sort_values(["perc_Hombre", "perc_Mujer"], ascending=False, inplace=True)

    # Para crear una gráfica de barras normalizada solo
    # necesitamos que los valores sumen 100.
    # En este caso son 3 gráficas de barrs horizontales apiladas.
    fig = go.Figure()

    # Ahora creamos una gráfica para cada sexo.
    for sexo in sexos_disponibles:
        fig.add_trace(
            go.Bar(
                y=df.index,
                x=df[f"perc_{sexo}"],
                text=df[f"text_{sexo}"],
                name=sexo,
                textposition="inside",
                orientation="h",
                marker_color=colores[sexo],
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
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True,
        nticks=15,
    )

    fig.update_yaxes(
        autorange="reversed",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
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
        legend_y=1.035,
        legend_yanchor="top",
        barmode="stack",
        width=1920,
        height=1920,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Víctimas de <b>{delito.lower()}</b> en México durante el {año} según sexo y entidad de registro",
        title_x=0.5,
        title_y=0.98,
        margin_t=140,
        margin_r=40,
        margin_b=120,
        margin_l=280,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.57,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Proporción dentro de cada categoría (absolutos)",
            ),
            dict(
                x=1.01,
                y=-0.06,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./comparacion_sexo_{año}.png")


if __name__ == "__main__":
    tendencia_anual("Extorsión", 0)
    tendencia_mensual("Extorsión", 0)
    crear_mapa(2024, "Extorsión")
    comparacion_entidad(2023, 2024, "Extorsión")
    comparacion_sexo(2024, "Extorsión")
