"""
Esta programa cuenta con dos funciones muy similares, la diferencia es la siguiente:

main() : Coloca en una tabla la comparación anual de los tipos de delito
main2() : Coloca en una tabla la comparación anual de los subtipos de delito

main2() genera una tabla mucho más grande verticalmente
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# El primer año que se desea comparar
AÑO1 = 2021

# El segundo año que se desea comparar
AÑO2 = 2022

# El mes que se desea comparar (la primera letra debe ir en mayúscula)
MES = "Octubre"

# La entidad que se desea comparar (México para comparar todo el país)
ENTIDAD = "México"


def main():

    df = pd.read_csv("./delitos.csv", encoding="latin-1")

    # Si la entidad es México entonces se calcula a nivel nacional
    # de lo contrario se calcula a nivel estatal
    if ENTIDAD != "México":
        df = df[df["Entidad"] == ENTIDAD]

    # Creamos un DataFrame para el primer año
    df1 = df[df["Año"] == AÑO1].groupby("Tipo de delito").sum()
    df1 = df1[MES].to_frame(AÑO1)

    # Creamos un DataFrame para el segundo año
    df2 = df[df["Año"] == AÑO2].groupby("Tipo de delito").sum()
    df2 = df2[MES].to_frame(AÑO2)

    # Combinamos los DataFrames
    final = pd.concat([df1, df2], axis=1)

    # Agregamos una fila con el conteeo total
    final.loc["Todos los delitos"] = final.sum(axis=0)

    # Ordenamos el DataFrame con los valores del segundo año
    final = final.sort_values(AÑO2, ascending=False)

    # Calculamos la diferencia y el cambio porcentual entre AÑO1 y AÑO2
    final["diff"] = final[AÑO2] - final[AÑO1]
    final["change"] = (final[AÑO2] - final[AÑO1]) / final[AÑO1] * 100

    # Preparamos las celdas para su presentación
    # Nota: la parte de <sup> es un hack para alinear el texto verticalmente
    final["nombre"] = final.index.map(lambda x: "{}<sup></sup>".format(x))
    final["texto"] = final.apply(format_text, axis=1)
    final[AÑO1] = final[AÑO1].apply(lambda x: "{:,.0f}<sup></sup>".format(x))
    final[AÑO2] = final[AÑO2].apply(lambda x: "{:,.0f}<sup></sup>".format(x))
    final["color"] = final["diff"].apply(set_color)

    fig = go.Figure()

    fig.add_trace(
        go.Table(
            columnwidth=[250, 50, 50, 60],
            header=dict(
                values=[
                    "<b>Tipo de delito</b>",
                    f"<b>{AÑO1}</b>",
                    f"<b>{AÑO2} ↓</b>",
                    "<b>Cambio</b>"
                ],
                font_color="#FFFFFF",
                line_width=0.75,
                fill_color="#827717",
                align="center",
                height=28
            ),
            cells=dict(
                values=[
                    final["nombre"],
                    final[AÑO1],
                    final[AÑO2],
                    final["texto"]
                ],
                line_width=0.75,
                fill_color=["#041C32", "#041C32", "#041C32", final["color"]],
                height=28,
                align=["left", "center", "center"]
            )
        )
    )

    fig.update_layout(
        showlegend=False,
        legend_borderwidth=1.5,
        xaxis_rangeslider_visible=False,
        width=920,
        height=1705,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=16,
        margin_t=50,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.988,
        title_font_size=20,
        title_text=f"Comparación de delitos reportados en {ENTIDAD} durante {MES.lower()} de los años {AÑO1} y {AÑO2}",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.015,
                y=0.005,
                xanchor="left",
                yanchor="top",
                text="Fuente: SESNSP"
            ),
            dict(
                x=1.015,
                y=0.005,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image("./2.png")


def main2():

    df = pd.read_csv("./delitos.csv", encoding="latin-1")

    # Si la entidad es México entonces se calcula a nivel nacional
    # de lo contrario se calcula a nivel estatal
    if ENTIDAD != "México":
        df = df[df["Entidad"] == ENTIDAD]

    # Creamos un DataFrame para el primer año
    df1 = df[df["Año"] == AÑO1].groupby("Subtipo de delito").sum()
    df1 = df1[MES].to_frame(AÑO1)

    # Creamos un DataFrame para el segundo año
    df2 = df[df["Año"] == AÑO2].groupby("Subtipo de delito").sum()
    df2 = df2[MES].to_frame(AÑO2)

    # Combinamos los DataFrames
    final = pd.concat([df1, df2], axis=1)

    # Agregamos una fila con el conteeo total
    final.loc["Todos los delitos"] = final.sum(axis=0)

    # Ordenamos el DataFrame con los valores del segundo año
    final = final.sort_values(AÑO2, ascending=False)

    # Calculamos la diferencia y el cambio porcentual entre AÑO1 y AÑO2
    final["diff"] = final[AÑO2] - final[AÑO1]
    final["change"] = (final[AÑO2] - final[AÑO1]) / final[AÑO1] * 100

    # Preparamos las celdas para su presentación
    # Nota: la parte de <sup> es un hack para alinear el texto verticalmente
    final["nombre"] = final.index.map(lambda x: "{}<sup></sup>".format(x))
    final["texto"] = final.apply(format_text, axis=1)
    final[AÑO1] = final[AÑO1].apply(lambda x: "{:,.0f}<sup></sup>".format(x))
    final[AÑO2] = final[AÑO2].apply(lambda x: "{:,.0f}<sup></sup>".format(x))
    final["color"] = final["diff"].apply(set_color)

    fig = go.Figure()

    fig.add_trace(
        go.Table(
            columnwidth=[250, 50, 50, 60],
            header=dict(
                values=[
                    "<b>Subtipo de delito</b>",
                    f"<b>{AÑO1}</b>",
                    f"<b>{AÑO2} ↓</b>",
                    "<b>Cambio</b>"
                ],
                font_color="#FFFFFF",
                line_width=0.75,
                fill_color="#ad1457",
                align="center",
                height=28
            ),
            cells=dict(
                values=[
                    final["nombre"],
                    final[AÑO1],
                    final[AÑO2],
                    final["texto"]
                ],
                line_width=0.75,
                fill_color=["#041C32", "#041C32", "#041C32", final["color"]],
                height=28,
                align=["left", "center", "center"]
            )
        )
    )

    fig.update_layout(
        width=920,
        height=2265,
        font_family="Quicksand",
        font_color="#FFFFFF",
        font_size=16,
        margin_t=50,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.992,
        title_font_size=20,
        title_text=f"Comparación de delitos reportados en {ENTIDAD} durante {MES.lower()} de los años {AÑO1} y {AÑO2}",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.015,
                y=0.002,
                xanchor="left",
                yanchor="top",
                text="Fuente: SESNSP"
            ),
            dict(
                x=1.015,
                y=0.002,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image("./3.png")


def format_text(x):
    """
    El cambio porcentual puede venir en diferentes formas
    Aquí las detectamos y formateamos el texto de acorde
    """

    # En caso de que el cambio porcentual sea infinito
    if x["change"] == np.inf:
        return "+{:,.0f} <sup>---</sup>".format(x["diff"])

    # En caso de que el cambio porcentual se nulo
    if pd.isna(x["change"]):
        if x["diff"] == 0.0:
            return "{:,.0f} <sup>---</sup>".format(x["diff"])
        else:
            return "+{:,.0f} <sup>---</sup>".format(x["diff"])

    if x["diff"] > 0:
        return "+{:,.0f} <sup>+{:,.2f}%</sup>".format(x["diff"], x["change"])
    else:
        return "{:,.0f} <sup>{:,.2f}%</sup>".format(x["diff"], x["change"])


def set_color(x):
    """
    Con esta función definimos que color de fondo tendrá la celda del cambio porcentual
    """

    # Verde para los delitos que se redujeron
    if x > 0:
        return "#b71c1c"
    # rojo para los delitos que aumentaron
    elif x < 0:
        return "#2e7d32"
    # Azul para los que se mantuvieron igual
    else:
        return "#1976d2"


if __name__ == "__main__":

    main()
    main2()
