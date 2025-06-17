"""

Este script convierte los datasets del SESNSP a series de tiempo.
Lo cual los hace más fáciles de utilizar.

Fuente:
https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva

"""

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


def victimas_to_timeseries():
    """
    Transforma el dataset a series de tiempo.
    """

    # Iniciamos la lista que almacenará los DataFrames por cada mes.
    dfs = []

    # Cargamos el dataset con codificación latin-1.
    df = pd.read_csv("./data/victimas.csv", encoding="latin-1", thousands=",")

    # Iteramos por cada mes.
    for k, v in MESES.items():
        temp_df = df[
            [
                "Año",
                "Clave_Ent",
                "Entidad",
                "Subtipo de delito",
                "Modalidad",
                "Sexo",
                "Rango de edad",
                k,
            ]
        ].copy()

        # Calculamos la fecha.
        temp_df["PERIODO"] = pd.to_datetime(
            {"year": temp_df["Año"], "month": v, "day": 1}
        )

        # Renombramos la columna del mes y agregamos el DataFrame a la lista.
        temp_df.rename(columns={k: "TOTAL"}, inplace=True)
        dfs.append(temp_df)

    # Unimos todos los DataFrames.
    final = pd.concat(dfs)

    # Renombramos algunas columnas.
    final.rename(
        columns={
            "Clave_Ent": "Cve_ent",
            "Subtipo de delito": "delito",
            "Rango de edad": "edad",
        },
        inplace=True,
    )

    # Convertimos nuestras columnas a mayúsculas.
    final.columns = [col.upper() for col in final.columns]

    # Convertimos los totales a int.
    final["TOTAL"] = final["TOTAL"].fillna(0).astype(int)

    # Quitamos valores en cero para reducir el tamaño del archivo.
    final = final[final["TOTAL"] != 0]

    # Ordenamos las columnas.
    final = final[
        [
            "PERIODO",
            "CVE_ENT",
            "ENTIDAD",
            "DELITO",
            "MODALIDAD",
            "SEXO",
            "EDAD",
            "TOTAL",
        ]
    ]

    # Ordenamos el DataFrame.
    final.sort_values(list(final.columns), inplace=True)

    # Guardamos al archivo final.
    final.to_csv("./data/timeseries_victimas.csv", index=False, encoding="utf-8")


def estatal_to_timeseries():
    """
    Transforma el dataset a series de tiempo.
    """

    # Iniciamos la lista que almacenará los DataFrames por cada mes.
    dfs = []

    # Cargamos el dataset con codificación latin-1.
    df = pd.read_csv("./data/estatal.csv", encoding="latin-1", thousands=",")

    # Iteramos por cada mes.
    for k, v in MESES.items():
        temp_df = df[
            [
                "Año",
                "Clave_Ent",
                "Entidad",
                "Subtipo de delito",
                k,
            ]
        ].copy()

        # Calculamos la fecha.
        temp_df["PERIODO"] = pd.to_datetime(
            {"year": temp_df["Año"], "month": v, "day": 1}
        )

        # Renombramos la columna del mes y agregamos el DataFrame a la lista.
        temp_df.rename(columns={k: "TOTAL"}, inplace=True)
        dfs.append(temp_df)

    # Unimos todos los DataFrames.
    final = pd.concat(dfs)

    # Renombramos algunas columnas.
    final.rename(
        columns={"Clave_Ent": "Cve_ent", "Subtipo de delito": "delito"}, inplace=True
    )

    # Convertimos nuestras columnas a mayúsculas.
    final.columns = [col.upper() for col in final.columns]

    # Convertimos los totales a int.
    final["TOTAL"] = final["TOTAL"].fillna(0).astype(int)

    # Ordenamos las columnas.
    final = final[["PERIODO", "CVE_ENT", "ENTIDAD", "DELITO", "TOTAL"]]

    # Ordenamos el DataFrame.
    final.sort_values(list(final.columns), inplace=True)

    # Guardamos al archivo final.
    final.to_csv("./data/timeseries_estatal.csv", index=False, encoding="utf-8")


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
    df["TOTAL"] = df[meses].sum(axis=1)

    # Agrupamos las columnas.
    df = df.groupby(["Año", "Cve. Municipio", "Subtipo de delito"]).sum(
        numeric_only=True
    )

    # Reseteamos el índice y renombramos las columnas.
    df.reset_index(names=["AÑO", "CVE_MUN", "DELITO", "TOTAL"], inplace=True)

    # Reordenamos las columnas
    df = df[["AÑO", "CVE_MUN", "DELITO", "TOTAL"]]

    # Convertimos el total a int.
    df["TOTAL"] = df["TOTAL"].astype(int)

    # Quitamos valores en cero para reducir el tamaño del archivo.
    df = df[df["TOTAL"] != 0]

    # Ordenamos el DataFrame.
    df.sort_values(list(df.columns), inplace=True)

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

    # Iniciamos la lista que almacenará los DataFrames por cada mes.
    dfs = []

    # Cargamos el dataset con codificación latin-1.
    df = pd.read_csv("./data/estatal.csv", encoding="latin-1", thousands=",")

    # Seleccionamos solo los delitos clasificados como robo.
    df = df[df["Tipo de delito"] == "Robo"]

    # Iteramos por cada mes.
    for k, v in MESES.items():
        temp_df = df[
            [
                "Año",
                "Clave_Ent",
                "Entidad",
                "Subtipo de delito",
                "Modalidad",
                k,
            ]
        ].copy()

        # Calculamos la fecha.
        temp_df["PERIODO"] = pd.to_datetime(
            {"year": temp_df["Año"], "month": v, "day": 1}
        )

        # Renombramos la columna del mes y agregamos el DataFrame a la lista.
        temp_df.rename(columns={k: "TOTAL"}, inplace=True)
        dfs.append(temp_df)

    # Unimos todos los DataFrames.
    final = pd.concat(dfs)

    # Renombramos algunas columnas.
    final.rename(
        columns={
            "Clave_Ent": "Cve_ent",
            "Subtipo de delito": "delito",
        },
        inplace=True,
    )

    # Convertimos nuestras columnas a mayúsculas.
    final.columns = [col.upper() for col in final.columns]

    # Convertimos los totales a int.
    final["TOTAL"] = final["TOTAL"].fillna(0).astype(int)

    # Ordenamos las columnas.
    final = final[["PERIODO", "CVE_ENT", "ENTIDAD", "DELITO", "MODALIDAD", "TOTAL"]]

    # Arreglamos los delitos con submodalidad.
    final["DELITO"] = final.apply(
        lambda x: x["MODALIDAD"][:-14] if len(x["MODALIDAD"]) > 13 else x["DELITO"],
        axis=1,
    )

    final["MODALIDAD"] = final["MODALIDAD"].apply(
        lambda x: x[-13:] if len(x) > 13 else x
    )

    # Ordenamos el DataFrame.
    final.sort_values(list(final.columns), inplace=True)

    # Guardamos el archivo final.
    final.to_csv("./data/timeseries_robos.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    victimas_to_timeseries()
    estatal_to_timeseries()
    municipios_to_timeseries()
    robos_to_timeseries()
