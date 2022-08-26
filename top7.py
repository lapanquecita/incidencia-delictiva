"""
Abreviaciones:

https://www.ieec.org.mx/transparencia/doctos/art74/i/reglamentos/Reglamento_de_elecciones/anexo_7.pdf


Ambas funciones en este programa hacen lo mismo, la única diferencia
es:

main() : Genera la gráfica de mayor incidencia delictiva
main2() : Genera la gráfica de menor incidencia delictiva

"""

import pandas as pd
import plotly.graph_objects as go


ENTIDADES = {
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
    32: "Zacatecas"
}


ABREVIACIONES = {
    "Aguascalientes": "AGS",
    "Baja California": "BC",
    "Baja California Sur": "BCS",
    "Campeche": "CAMP",
    "Coahuila": "COAH",
    "Colima": "COL",
    "Chiapas": "CHIS",
    "Chihuahua": "CHIH",
    "Ciudad de México": "CDMX",
    "Durango": "DGO",
    "Guanajuato": "GTO",
    "Guerrero": "GRO",
    "Hidalgo": "HGO",
    "Jalisco": "JAL",
    "Estado de México": "MEX",
    "Michoacán": "MICH",
    "Morelos": "MOR",
    "Nayarit": "NAY",
    "Nuevo León": "NL",
    "Oaxaca": "OAX",
    "Puebla": "PUE",
    "Querétaro": "QRO",
    "Quintana Roo": "QROO",
    "San Luis Potosí": "SLP",
    "Sinaloa": "SIN",
    "Sonora": "SON",
    "Tabasco": "TAB",
    "Tamaulipas": "TAMPS",
    "Tlaxcala": "TLAX",
    "Veracruz": "VER",
    "Yucatán": "YUC",
    "Zacatecas": "ZAC",
}


COLORES = {
    "Aguascalientes": "#f44336",
    "Baja California": "#d50000",
    "Baja California Sur": "#455a64",
    "Campeche": "#e91e63",
    "Coahuila": "#c51162",
    "Colima": "#880e4f",
    "Chiapas": "#9c27b0",
    "Chihuahua": "#4a148c",
    "Ciudad de México": "#aa00ff",
    "Durango": "#d500f9",
    "Guanajuato": "#673ab7",
    "Guerrero": "#6200ea",
    "Hidalgo": "#311b92",
    "Jalisco": "#3f51b5",
    "Estado de México": "#304ffe",
    "Michoacán": "#1a237e",
    "Morelos": "#0d47a1",
    "Nayarit": "#1976d2",
    "Nuevo León": "#00838f",
    "Oaxaca": "#00796b",
    "Puebla": "#004d40",
    "Querétaro": "#616161",
    "Quintana Roo": "#d32f2f",
    "San Luis Potosí": "#4e342e",
    "Sinaloa": "#795548",
    "Sonora": "#ff3d00",
    "Tabasco": "#ef6c00",
    "Tamaulipas": "#827717",
    "Tlaxcala": "#689f38",
    "Veracruz": "#33691e",
    "Yucatán": "#388e3c",
    "Zacatecas": "#1b5e20",
}


MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


DELITOS = ["Falsificación", "Fraude",
           "Amenazas", "Lesiones", "Violencia familiar",
           "Narcomenudeo", "Trata de personas",
           "Acoso sexual", "Abuso sexual", "Violación simple",
           "Allanamiento de morada", "Robo",
           "Extorsión", "Secuestro",  "Feminicidio", "Homicidio"]


def main():

    # Cargamos la población del 2020 y la agrupamos por entidad
    pop = pd.read_csv("./poblacion2020.csv")
    pop = pop.groupby("entidad").sum()["poblacion"]

    # Cargamos el dataset de incidencia delictiva y lo filtramos para el año 2021
    df = pd.read_csv("./delitos.csv", encoding="latin-1")
    df = df[df["Año"] == 2021]

    fig = go.Figure()

    # iteramos sobre los delitos que nos interesan
    for index, item in enumerate(DELITOS):

        # Creamos un DataFrame con el delito
        temp_df = df[df["Tipo de delito"] == item]

        # Agrupamos el DataFrame por entidad y solo ons quedamos con la columna del total por año
        temp_df = temp_df[MESES + ["Clave_Ent"]].groupby("Clave_Ent").sum()
        temp_df = temp_df.sum(axis=1).to_frame("total")

        # Este es el total nacional
        total = temp_df["total"].sum()

        # Convertimos nuestro indice de números palabras, esto es para que sea más fácil
        # saber a que entidad nos referimos
        temp_df.index = temp_df.index.map(ENTIDADES)

        # Agregamos la población de cada entidad
        temp_df["pop"] = pop

        # Calculamos la incidencia por cada 100k habitantes y el resultado se converitrá en
        # nuestro DataFrame (ya no neceistamos lo demás)
        temp_df = temp_df["total"] / temp_df["pop"] * 100000

        # Redondeamos los valores con un punto decimal
        temp_df = temp_df.round(decimals=1)

        # Esta linea es la más importante de todas, ya que ordena los valores calculados
        #  y solo toma los que necesitamos (top 7)
        temp_df = temp_df.sort_values(ascending=False)[:7].to_frame("perc")

        # Reseteamos el indice, ya que necesitamos valores del 0 al 6
        temp_df.reset_index(inplace=True)

        # Aquí creamos el texto para los círculos usando el diccionario de abreviaciones
        temp_df["text"] = temp_df.apply(
            lambda x: "{:,}<br>{}".format(x["perc"], ABREVIACIONES[x["Clave_Ent"]]), axis=1)

        # Aquí definimos el color de cada círculo usando el diccionario de colores
        temp_df["color"] = temp_df["Clave_Ent"].map(COLORES)

        # Estas lineas son para arreglar las etiquetas del eje vertical
        # si el nombre del delito es muy largo lo partimos en cachos
        item = item.replace("Violencia familiar", "Violencia<br>familiar")
        item = item.replace("Violación simple", "Violación<br>simple")
        item = item.replace("Trata de personas", "Trata de<br>personas")
        item = item.replace("Allanamiento de morada",
                            "Allanamiento<br>de morada")

        # El eje vertical va a ser el nombre del delito 7 veces.
        # Esto es como un hack para que nuestra visualización funcoine.
        y = [f"{item}<br>({total:,.0f})" for _ in range(7)]

        fig.add_trace(
            go.Scatter(
                x=temp_df.index,
                y=y,
                mode="markers+text",
                text=temp_df["text"],
                marker_color=temp_df["color"],
                textfont_size=22,
                marker_size=90,
            )
        )

    fig.update_xaxes(
        title="",
        range=[-0.75, 6.75],
        showticklabels=False,
        ticklen=10,
        zeroline=False,
        title_standoff=20,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        mirror=True,
        showgrid=False,
        nticks=0
    )

    fig.update_yaxes(
        title="Incidencia por cada 100k habitantes (total nacional en paréntesis)",
        range=[-0.75, 15.75],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        title_standoff=12,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        mirror=True,
        showgrid=False,
        nticks=0
    )

    fig.update_layout(
        showlegend=False,
        width=1080,
        height=1920,
        font_family="Quicksand",
        font_color="white",
        font_size=18,
        title_text="Principales entidades con <b>mayor</b> incidencia delictiva durante el 2021 en México",
        title_x=0.5,
        title_y=0.98,
        margin_t=80,
        margin_l=220,
        margin_r=40,
        margin_b=60,
        title_font_size=26,
        plot_bgcolor="#100F0F",
        paper_bgcolor="#0F3D3E",
        annotations=[
            dict(
                x=0.01,
                xanchor="left",
                xref="paper",
                y=-0.045,
                yanchor="bottom",
                yref="paper",
                text="Fuente: SESNSP (2021)"
            ),
            dict(
                x=1.01,
                xanchor="right",
                xref="paper",
                y=-0.045,
                yanchor="bottom",
                yref="paper",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image("./0.png")


def main2():

    # Cargamos la población del 2020 y la agrupamos por entidad
    pop = pd.read_csv("./poblacion2020.csv")
    pop = pop.groupby("entidad").sum()["poblacion"]

    # Cargamos el dataset de incidencia delictiva y lo filtramos para el año 2021
    df = pd.read_csv("./delitos.csv", encoding="latin-1")
    df = df[df["Año"] == 2021]

    fig = go.Figure()

    # iteramos sobre los delitos que nos interesan
    for index, item in enumerate(DELITOS):

        # Creamos un DataFrame con el delito
        temp_df = df[df["Tipo de delito"] == item]

        # Agrupamos el DataFrame por entidad y solo ons quedamos con la columna del total por año
        temp_df = temp_df[MESES + ["Clave_Ent"]].groupby("Clave_Ent").sum()
        temp_df = temp_df.sum(axis=1).to_frame("total")

        # Este es el total nacional
        total = temp_df["total"].sum()

        # Convertimos nuestro indice de números palabras, esto es para que sea más fácil
        # saber a que entidad nos referimos
        temp_df.index = temp_df.index.map(ENTIDADES)

        # Agregamos la población de cada entidad
        temp_df["pop"] = pop

        # Calculamos la incidencia por cada 100k habitantes y el resultado se converitrá en
        # nuestro DataFrame (ya no neceistamos lo demás)
        temp_df = temp_df["total"] / temp_df["pop"] * 100000

        # Redondeamos los valores con un punto decimal
        temp_df = temp_df.round(decimals=1)

        # Esta linea es la más importante de todas, ya que ordena los valores calculados
        #  y solo toma los que necesitamos (top 7)
        temp_df = temp_df.sort_values(ascending=True)[:7].to_frame("perc")

        # Reseteamos el indice, ya que necesitamos valores del 0 al 6
        temp_df.reset_index(inplace=True)

        # Aquí creamos el texto para los círculos usando el diccionario de abreviaciones
        temp_df["text"] = temp_df.apply(
            lambda x: "{:,}<br>{}".format(x["perc"], ABREVIACIONES[x["Clave_Ent"]]), axis=1)

        # Aquí definimos el color de cada círculo usando el diccionario de colores
        temp_df["color"] = temp_df["Clave_Ent"].map(COLORES)

        # Estas lineas son para arreglar las etiquetas del eje vertical
        # si el nombre del delito es muy largo lo partimos en cachos
        item = item.replace("Violencia familiar", "Violencia<br>familiar")
        item = item.replace("Violación simple", "Violación<br>simple")
        item = item.replace("Trata de personas", "Trata de<br>personas")
        item = item.replace("Allanamiento de morada",
                            "Allanamiento<br>de morada")

        # El eje vertical va a ser el nombre del delito 7 veces.
        # Esto es como un hack para que nuestra visualización funcoine.
        y = [f"{item}<br>({total:,.0f})" for _ in range(7)]

        fig.add_trace(
            go.Scatter(
                x=temp_df.index,
                y=y,
                mode="markers+text",
                text=temp_df["text"],
                marker_color=temp_df["color"],
                textfont_size=22,
                marker_size=90,
            )
        )

    fig.update_xaxes(
        title="",
        range=[-0.75, 6.75],
        showticklabels=False,
        ticklen=10,
        zeroline=False,
        title_standoff=20,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        mirror=True,
        showgrid=False,
        nticks=0
    )

    fig.update_yaxes(
        title="Incidencia por cada 100k habitantes (total nacional en paréntesis)",
        range=[-0.75, 15.75],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        title_standoff=12,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        mirror=True,
        showgrid=False,
        nticks=0
    )

    fig.update_layout(
        showlegend=False,
        width=1080,
        height=1920,
        font_family="Quicksand",
        font_color="white",
        font_size=18,
        title_text="Principales entidades con <b>menor</b> incidencia delictiva durante el 2021 en México",
        title_x=0.5,
        title_y=0.98,
        margin_t=80,
        margin_l=220,
        margin_r=40,
        margin_b=60,
        title_font_size=26,
        plot_bgcolor="#100F0F",
        paper_bgcolor="#0F3D3E",
        annotations=[
            dict(
                x=0.01,
                xanchor="left",
                xref="paper",
                y=-0.045,
                yanchor="bottom",
                yref="paper",
                text="Fuente: SESNSP (2021)"
            ),
            dict(
                x=1.01,
                xanchor="right",
                xref="paper",
                y=-0.045,
                yanchor="bottom",
                yref="paper",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image("./1.png")


if __name__ == "__main__":

    main()
    main2()
