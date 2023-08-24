"""
Este script convierte los datasets del SESNSP a series de tiempo.
Lo cual los hace más fáciles de utilizar.
"""

import numpy as np
import csv
from datetime import date

import pandas as pd


# Este diccionario será usado para crear las fechas.
MESES = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12
}


def convert_to_timeseries(file):

    # Iniciamos nuestra lista con la cabecera.
    data_list = [["isodate", "entidad", "delito", "total"]]

    # Cargamos el dataset con codificación latin-1.
    df = pd.read_csv(f"./{file}.csv", encoding="latin-1")

    # Obtenemos una lista de todos los subtipos de delitos.
    delitos = df["Subtipo de delito"].unique().tolist()

    # Obtenemos una lista de todas las entidades federativas de México.
    entidades = df["Entidad"].unique().tolist()

    # Insertamos una entidad para el nivel nacional.
    entidades.insert(0, "Nacional")

    # iteramos sobre cada año en nuestro dataset.
    for year in df["Año"].unique():

        # Iteramos sobre cada entidad.
        for entidad in entidades:

            # Si la entidad es 'Nacional' hacemos otro tipo de filtrado.
            if entidad == "Nacional":
                temp_df = df[df["Año"] == year]
            else:
                temp_df = df[(df["Año"] == year) & (
                    df["Entidad"] == entidad)]

            # Agrupamos el DataFrame por subtipo de delito.
            temp_df = temp_df.groupby(
                "Subtipo de delito").sum(numeric_only=True)

            # Iteramos sobre cada subtipo de delito.
            for delito in delitos:

                # iteramos sobre cada mes.
                for k, v in MESES.items():

                    # Finalmente armamos el registro con todos los valores
                    # que estamos iterando.
                    data_list.append(
                        [
                            date(year, v, 1),
                            entidad,
                            delito,
                            int(temp_df.loc[delito, k])
                        ]
                    )

    # Guardamos el archivo final con un prefijo.
    with open(f"./timeseries_{file}.csv", "w", encoding="utf-8", newline="") as csv_file:
        csv.writer(csv_file).writerows(data_list)


if __name__ == "__main__":

    convert_to_timeseries("victimas")
    convert_to_timeseries("estatal")
