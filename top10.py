"""
Fuente de abreviaciones:

https://www.ieec.org.mx/transparencia/doctos/art74/i/reglamentos/Reglamento_de_elecciones/anexo_7.pdf

"""

import pandas as pd
import plotly.graph_objects as go
from textwrap import wrap


# La fecha en la que los datos fueron recopilados.
FECHA_FUENTE = "febrero 2024"

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
    32: "Zacatecas",
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

DELITOS = [
    ["Homicidio doloso", "Feminicidio"],
    ["Secuestro"],
    ["Extorsión"],
    ["Lesiones dolosas"],
    ["Amenazas"],
    ["Fraude"],
    ["Abuso sexual"],
    ["Violencia familiar"],
    ["Narcomenudeo"],
    ["Robo a negocio"],
    ["Robo a casa habitación"],
    ["Robo de vehículo automotor"],
    ["Robo en transporte público colectivo"],
]


def main(tipo, año):
    """
    Crea una gráfica con el top 10 o bottom 10 de incidencia deliactiva por entidad.

    Parameters
    ----------
    tipo : str
        El tipo de orden, pueden ser 'top' o 'bottom'.

    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de población total por entidad.
    pop = pd.read_csv("./assets/poblacion_anual.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    pop = pop[str(año)]

    # Renombramos algunos estados a sus nombres más comunes.
    pop = pop.rename(
        {
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Cargamos el dataset de incidencia delictiva estatal.
    df = pd.read_csv("./data/estatal.csv", encoding="latin-1")

    # Filtramos los registros para el año de nuestro interés.
    df = df[df["Año"] == año]

    # Calculamos los totales anuales de cada delito.
    df["total"] = df[MESES].sum(axis=1)

    # El título depende del tipo de orden.
    if tipo == "top":
        titulo = "mayor"
    elif tipo == "bottom":
        titulo = "menor"

    fig = go.Figure()

    # Iteramos sobre los delitos que nos interesan
    for item in DELITOS:
        # Creamos un DataFrame con el delito o delitos.
        temp_df = df[df["Subtipo de delito"].isin(item)]

        # Agrupamos el DataFrame por entidad y solo nos quedamos con la columna del total por año.
        temp_df = (
            temp_df[["Clave_Ent", "total"]].groupby("Clave_Ent").sum(numeric_only=True)
        )

        # Este es el total nacional, el cual será usado para las etiquetas.
        total = temp_df["total"].sum()

        # Renombramos los valores del índice para poder emparejarlos con la población.
        temp_df.index = temp_df.index.map(ENTIDADES)

        # Agregamos la población de cada entidad.
        temp_df["pop"] = pop

        # Calculamos la incidencia por cada 100k habitantes.
        temp_df["tasa"] = temp_df["total"] / temp_df["pop"] * 100000

        # Esta linea es la más importante de todas, ya que ordena los valores calculados
        #  y solo toma los que necesitamos (top 10)
        if tipo == "top":
            temp_df = temp_df.sort_values("tasa", ascending=False).head(10)
        elif tipo == "bottom":
            temp_df = temp_df.sort_values("tasa", ascending=True).head(10)

        # Reseteamos el indice, ya que necesitamos valores del 0 al 6
        temp_df.reset_index(inplace=True)

        # Aquí creamos los textos para cada entidad y tasa.
        temp_df["text"] = temp_df.apply(formatear_texto, axis=1)

        # Definimos el color de cada círculo usando el diccionario de colores.
        temp_df["color"] = temp_df["Clave_Ent"].map(COLORES)

        # Unimos los nombres de delitos y los partimos en dos en caso de ser muy largos.
        item = " y ".join(item)
        item = "<br>".join(wrap(item, 20))

        # El eje vertical va a ser el nombre del delito 10 veces.
        # Esto es como un hack para que nuestra visualización funcione.
        y = [f"<b>{item}</b><br>({total:,.0f} registros)" for _ in range(len(temp_df))]

        fig.add_trace(
            go.Scatter(
                x=temp_df.index,
                y=y,
                mode="markers+text",
                text=temp_df["text"],
                marker_color=temp_df["color"],
                textfont_family="Oswald",
                textfont_size=24,
                marker_size=86,
            )
        )

    fig.update_xaxes(
        range=[-0.75, 9.75],
        showticklabels=False,
        ticklen=10,
        zeroline=False,
        title_standoff=20,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        mirror=True,
        showgrid=False,
        nticks=0,
    )

    fig.update_yaxes(
        range=[12.75, -0.75],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        title_standoff=12,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        mirror=True,
        showgrid=False,
        nticks=0,
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=1600,
        font_family="Montserrat",
        font_color="white",
        font_size=18,
        title_text=f"Las 10 entidades de México con <b>{titulo}</b> incidencia delictiva por tipo de delito durante el {año}<br>(un registro puede tener más de una víctima)",
        title_x=0.5,
        title_y=0.975,
        margin_t=100,
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
                y=-0.05,
                yanchor="bottom",
                yref="paper",
                text=f"Fuente: SESNSP ({FECHA_FUENTE})",
            ),
            dict(
                x=0.55,
                xanchor="center",
                xref="paper",
                y=-0.05,
                yanchor="bottom",
                yref="paper",
                text="Incidencia delictiva ajustada por cada 100k habitantes",
            ),
            dict(
                x=1.01,
                xanchor="right",
                xref="paper",
                y=-0.05,
                yanchor="bottom",
                yref="paper",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # El nombre del archivo depende del tipo de orden.
    fig.write_image(f"./{tipo}_10.png")


def formatear_texto(x):
    """
    Las tasas pueden variar desde 0 a más de 100.
    Para mantener la estétitica, nos aseguramos de
    que siempre tengan 3 dígitos.
    """

    abreviacion = ABREVIACIONES[x["Clave_Ent"]]

    if x["tasa"] < 10:
        return f"{x['tasa']:,.2f}<br>{abreviacion}"
    elif x["tasa"] >= 100:
        return f"{x['tasa']:,.0f}<br>{abreviacion}"
    else:
        return f"{x['tasa']:,.1f}<br>{abreviacion}"


if __name__ == "__main__":
    main("top", 2023)
    main("bottom", 2023)
