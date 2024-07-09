"""

Este script convierte los datasets del SESNSP a series de tiempo.
Lo cual los hace más fáciles de utilizar.

Fuente:
https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva

"""

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
    "Diciembre": 12,
}


def convert_to_timeseries(file):
    # Iniciamos nuestra lista con la cabecera.
    data_list = [["isodate", "entidad", "delito", "total"]]

    # Cargamos el dataset con codificación latin-1.
    df = pd.read_csv(f"./data/{file}.csv", encoding="latin-1", thousands=",")

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
                temp_df = df[(df["Año"] == year) & (df["Entidad"] == entidad)]

            # Agrupamos el DataFrame por subtipo de delito.
            temp_df = temp_df.groupby("Subtipo de delito").sum(numeric_only=True)

            # Iteramos sobre cada subtipo de delito.
            for delito in delitos:
                # iteramos sobre cada mes.
                for k, v in MESES.items():
                    # Finalmente armamos el registro con todos los valores
                    # que estamos iterando.
                    data_list.append(
                        [date(year, v, 1), entidad, delito, int(temp_df.loc[delito, k])]
                    )

    # Guardamos el archivo final con un prefijo.
    with open(
        f"./data/timeseries_{file}.csv", "w", encoding="utf-8", newline=""
    ) as csv_file:
        csv.writer(csv_file).writerows(data_list)


def municipios_to_timeseries():
    """
    Genera series de tiempo para cada municipio y subtipo de delito.
    En lugar de ser mensual, es anual.

    Esta función es similar a la anterior, pero las diferencias ameritan
    tener su propia función.
    """

    # Cargamos el dataset de municipios con codificación latin-1.
    df = pd.read_csv("./data/municipal.csv", encoding="latin-1", thousands=",")

    # Arreglamos la clave del municipio.
    df["Cve. Municipio"] = df["Cve. Municipio"].astype(str).str.zfill(5)

    # Esta lista de meses será usada para calcular el total anual.
    meses = [item for item in MESES.keys()]

    # Calculamos los totales anuales de cada delito.
    df["total"] = df[meses].sum(axis=1)

    # Agrupamos las columnas.
    df = df.groupby(["Año", "Cve. Municipio", "Subtipo de delito"]).sum(
        numeric_only=True
    )

    # Reseteamos el índice y renombramos las columnas.
    df.reset_index(names=["año", "cve_municipio", "delito", "total"], inplace=True)

    # Reordenamos las columnas
    df = df[["año", "cve_municipio", "delito", "total"]]

    # Convertimos el total a int.
    df["total"] = df["total"].astype(int)

    # Guardamos el nuevo archivo .csv
    df.to_csv(
        "./data/timeseries_municipal.csv",
        index=False,
        encoding="utf-8",
        chunksize=200000,
    )


def robos_to_timeseries():
    """
    Genera series de tiempo para cada tipo de robo por entidad.
    """

    # Iniciamos nuestra lista con la cabecera.
    data_list = [["isodate", "entidad", "delito", "modalidad", "total"]]

    # Cargamos el dataset con codificación latin-1.
    df = pd.read_csv("./data/estatal.csv", encoding="latin-1", thousands=",")

    # Seleccionamos solo los delitos clasificados como robo.
    df = df[df["Tipo de delito"] == "Robo"]

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
                temp_df = df[(df["Año"] == year) & (df["Entidad"] == entidad)]

            # Agrupamos el DataFrame por subtipo de delito y modalidad.
            temp_df = temp_df.groupby(["Subtipo de delito", "Modalidad"]).sum(
                numeric_only=True
            )

            # Iteramos sobre cada subtipo de delito.
            for delito, modalidad in temp_df.index:
                # iteramos sobre cada mes.
                for k, v in MESES.items():
                    # Finalmente armamos el registro con todos los valores
                    # que estamos iterando.
                    data_list.append(
                        [
                            date(year, v, 1),
                            entidad,
                            delito,
                            modalidad,
                            int(temp_df.loc[delito, modalidad][k]),
                        ]
                    )

    # Guardamos el archivo final con un prefijo.
    with open(
        "./data/timeseries_robos.csv", "w", encoding="utf-8", newline=""
    ) as csv_file:
        csv.writer(csv_file).writerows(data_list)


if __name__ == "__main__":
    convert_to_timeseries("victimas")
    convert_to_timeseries("estatal")
    municipios_to_timeseries()
    robos_to_timeseries()
