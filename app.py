import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide", page_title="Engagement Dashboard")
st.title("📊 Engagement Dashboard – @ppoohkt & @pavelphoom")
st.markdown("Subí los archivos CSV para visualizar el *engagement*, hashtags e interacciones entre las cuentas.")

# Sidebar
st.sidebar.header("📁 Subí tus CSVs aquí")
archivo1 = st.sidebar.file_uploader("CSV de @ppoohkt", type="csv")
archivo2 = st.sidebar.file_uploader("CSV de @pavelphoom", type="csv")

if st.sidebar.button("🔄 Resetear"):
    st.experimental_rerun()

def validar_archivo(df, nombre_archivo):
    columnas_esperadas = ['Fecha', 'Engagement (%)', 'Likes', 'Retweets', 'Replies', 'Hashtags', 'Texto']
    if not all(col in df.columns for col in columnas_esperadas):
        st.error(f"⚠️ El archivo '{nombre_archivo}' no contiene todas las columnas necesarias: {columnas_esperadas}")
        return False
    return True

def preparar_dataframe(df):
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Engagement (%)'] = pd.to_numeric(df['Engagement (%)'], errors='coerce')
    return df

def filtro_fecha_global(df1, df2):
    min_date = min(df1['Fecha'].min(), df2['Fecha'].min())
    max_date = max(df1['Fecha'].max(), df2['Fecha'].max())
    rango = st.sidebar.date_input("🗓 Rango de fechas", [min_date, max_date], min_value=min_date, max_value=max_date)
    if len(rango) == 2:
        df1 = df1[(df1['Fecha'] >= pd.to_datetime(rango[0])) & (df1['Fecha'] <= pd.to_datetime(rango[1]))]
        df2 = df2[(df2['Fecha'] >= pd.to_datetime(rango[0])) & (df2['Fecha'] <= pd.to_datetime(rango[1]))]
    return df1, df2

def graficar_engagement(df, nombre):
    st.subheader(f"📈 Engagement por fecha – @{nombre}")
    fig = px.line(df, x='Fecha', y='Engagement (%)', markers=True, title=f"Engagement diario – @{nombre}")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"📊 Interacciones por tweet – @{nombre}")
    df_long = df[['Likes', 'Retweets', 'Replies']].reset_index().melt(id_vars='index')
    fig2 = px.bar(df_long, x='index', y='value', color='variable', barmode='group', labels={"index": "Tweet Nº"})
    st.plotly_chart(fig2, use_container_width=True)

def graficar_hashtags(df, nombre):
    st.subheader(f"🏷️ Top hashtags – @{nombre}")
    cantidad_top = st.slider("Selecciona la cantidad de hashtags a mostrar", 5, 20, 10, key=f"{nombre}_hashtags_slider")
    
    hashtags = df['Hashtags'].dropna().str.split(', ')
    all_tags = [tag for sublist in hashtags for tag in sublist]
    top_tags = pd.Series(all_tags).value_counts().head(cantidad_top).reset_index()
    top_tags.columns = ['Hashtag', 'Frecuencia']
    
    fig = px.bar(top_tags, x='Frecuencia', y='Hashtag', orientation='h', color='Frecuencia')
    st.plotly_chart(fig, use_container_width=True)

def comparar_engagement(df1, df2):
    st.subheader("⚔️ Comparación de Engagement entre cuentas")
    df1['Cuenta'] = 'ppoohkt'
    df2['Cuenta'] = 'pavelphoom'
    comb = pd.concat([df1, df2])
    fig = px.line(comb, x='Fecha', y='Engagement (%)', color='Cuenta', markers=True)
    st.plotly_chart(fig, use_container_width=True)

def analizar_menciones(df, nombre_objetivo):
    st.subheader(f"💬 Menciones a @{nombre_objetivo}")
    df['Menciona a otro'] = df['Texto'].str.contains(f"@{nombre_objetivo}", case=False, na=False)
    menciones = df[df['Menciona a otro'] == True]
    st.write(f"{len(menciones)} tweets mencionan a @{nombre_objetivo}")
    st.dataframe(menciones[['Fecha', 'Texto']])

def mostrar_estadisticas(df, nombre):
    st.subheader(f"📋 Estadísticas generales – @{nombre}")
    stats = {
        "Total de tweets": len(df),
        "Engagement promedio (%)": df['Engagement (%)'].mean(),
        "Likes totales": df['Likes'].sum(),
        "Retweets totales": df['Retweets'].sum(),
        "Respuestas totales": df['Replies'].sum()
    }
    st.table(pd.DataFrame(stats.items(), columns=["Métrica", "Valor"]))

def exportar_datos(df, nombre_archivo):
    csv = df.to_csv(index=False)
    st.download_button(
        label=f"⬇️ Descargar datos procesados para @{nombre_archivo}",
        data=csv,
        file_name=f"{nombre_archivo}_procesado.csv",
        mime="text/csv"
    )

# Proceso principal
if archivo1 and archivo2:
    try:
        df1 = pd.read_csv(archivo1)
        df2 = pd.read_csv(archivo2)
    except Exception as e:
        st.error(f"❌ Error al leer los archivos CSV: {e}")
        st.stop()

    if not (validar_archivo(df1, "ppoohkt.csv") and validar_archivo(df2, "pavelphoom.csv")):
        st.stop()

    df1 = preparar_dataframe(df1)
    df2 = preparar_dataframe(df2)

    df1, df2 = filtro_fecha_global(df1, df2)

    st.markdown("## 📊 Visualización individual")
    col1, col2 = st.columns(2)

    with col1:
        graficar_engagement(df1, "ppoohkt")
        graficar_hashtags(df1, "ppoohkt")
        analizar_menciones(df1, "pavelphoom")
        mostrar_estadisticas(df1, "ppoohkt")
        exportar_datos(df1, "ppoohkt")

    with col2:
        graficar_engagement(df2, "pavelphoom")
        graficar_hashtags(df2, "pavelphoom")
        analizar_menciones(df2, "ppoohkt")
        mostrar_estadisticas(df2, "pavelphoom")
        exportar_datos(df2, "pavelphoom")

    st.markdown("## 🤜🤛 Comparación directa")
    comparar_engagement(df1, df2)

elif archivo1 or archivo2:
    st.warning("⚠️ Subí **ambos archivos CSV** para activar el análisis completo.")
else:
    st.info("⬅️ Empezá subiendo los CSV de engagement desde la barra lateral.")
