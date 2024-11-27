import streamlit as st
import pandas as pd
import requests
import plotly.express as px

def obtener_datos_terremotos(fecha_inicio, fecha_fin, magnitud_min):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": fecha_inicio,
        "endtime": fecha_fin,
        "minmagnitude": magnitud_min
    }
    respuesta = requests.get(url, params=params)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        eventos = datos["features"]
        lista = []
        for evento in eventos:
            propiedades = evento["properties"]
            geometria = evento["geometry"]
            lista.append({
                "Fecha": pd.to_datetime(propiedades["time"], unit="ms"),
                "Magnitud": propiedades["mag"],
                "Lugar": propiedades["place"],
                "Latitud": geometria["coordinates"][1],
                "Longitud": geometria["coordinates"][0],
                "Profundidad (km)": geometria["coordinates"][2]
            })
        return pd.DataFrame(lista)
    return None

st.set_page_config(page_title="Actividad Sismica Global", layout="wide")

st.title("🌍 Visualizacion de Actividad Sismica Global")

st.sidebar.header("Filtros")
fecha_inicio = st.sidebar.date_input("Fecha de inicio")
fecha_fin = st.sidebar.date_input("Fecha de fin")
magnitud_min = st.sidebar.slider("Magnitud minima", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

st.sidebar.write("Selecciona los parametros y haz clic en 'Cargar datos'")
if st.sidebar.button("Cargar datos"):
    datos = obtener_datos_terremotos(str(fecha_inicio), str(fecha_fin), magnitud_min)
    if datos is not None:
        st.success(f"Se encontraron {len(datos)} registros.")
        
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Mapa de actividad sismica")
            mapa = px.scatter_geo(
                datos,
                lat="Latitud",
                lon="Longitud",
                color="Magnitud",
                hover_name="Lugar",
                size="Magnitud",
                title="Mapa Global",
                projection="natural earth"
            )
            st.plotly_chart(mapa, use_container_width=True)

        with col2:
            st.subheader("Distribucion de magnitudes")
            grafico = px.histogram(
                datos,
                x="Magnitud",
                nbins=20,
                title="Histograma de Magnitudes",
                labels={"x": "Magnitud", "y": "Frecuencia"}
            )
            st.plotly_chart(grafico, use_container_width=True)

        st.subheader("Datos detallados")
        st.dataframe(datos)

        st.download_button(
            label="Descargar datos en CSV",
            data=datos.to_csv(index=False),
            file_name="datos_sismicos.csv",
            mime="text/csv"
        )
    else:
        st.error("No se encontraron datos para los parametros seleccionados.")
