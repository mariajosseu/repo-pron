import streamlit as st
from tools.evaluate import *
from tools.import_preds import *
import pandas as pd
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    layout="wide",  # Activa "Wide Mode"
    page_title="Reporte Pronóstico de Demanda",  # Título de la pestaña del navegador
    page_icon="📊"  # Icono de la pestaña del navegador
)

# Mostrar el logo en la parte superior
st.image(r'coordinador-informa-e.jpg')
# Streamlit
st.title("Reporte Pronóstico de Demanda")

# Importar datos
pred_df = import_pred_from_folder_with_filter('output/preds', 'conv')
real = pd.read_csv('output/preds/demanda_real.csv')
dpron_ems = pd.read_csv('output/preds/DPRON_EMS.csv')

# Crear las pestañas
tab0, tab1 = st.tabs(["Gráficos", "Estadísticas"])

with tab0:
    # Diseño de dos columnas: Filtros a la izquierda y gráficos a la derecha
    col1, col2 = st.columns([1, 3])  # La primera columna es más pequeña que la segunda

    # Filtros en la columna izquierda
    with col1:
        print(real['DATETIME'])
        # Asegúrate de que las columnas DATETIME estén en formato datetime
        real['DATETIME'] = pd.to_datetime(real['DATETIME'])
        #print(real['DATETIME'])
        pred_df['DATETIME'] = pd.to_datetime(pred_df['DATETIME'])

        # Definir el rango de fechas predeterminado
        hoy = datetime.now()
        default_fecha_inicio = hoy - timedelta(days=7)
        default_fecha_fin = hoy + timedelta(days=2)

        # Validar los límites del rango con los datos reales
        min_date = real['DATETIME'].min()
        max_date = real['DATETIME'].max()

        # Asegurarse de que las fechas por defecto estén dentro del rango de los datos
        default_fecha_inicio = max(default_fecha_inicio, min_date)
        default_fecha_fin = min(default_fecha_fin, max_date)

        # Controles de rango de fechas
        fecha_inicio = st.date_input("Fecha de inicio", default_fecha_inicio)
        fecha_fin = st.date_input("Fecha de fin", default_fecha_fin)

        # Selección de columnas
        columnas_seleccionadas = st.multiselect(
            "Selecciona predicciones para incluir",
            sorted([col for col in pred_df.columns if col.startswith('2024')], reverse=True),
            default=[]
        )

        # Validar rango de fechas
        if fecha_inicio > fecha_fin:
            st.error("La fecha de inicio no puede ser mayor a la fecha de fin")

    # Gráficos en la columna derecha
    with col2:
        # Graficar Consumo Real vs Predicciones
        fig1 = graficar_con_seleccion(real, pred_df, dpron_ems, pd.to_datetime(fecha_inicio), pd.to_datetime(fecha_fin), columnas_seleccionadas)
        st.plotly_chart(fig1, use_container_width=True)

        # Graficar MAPE
        fig2 = plot_mape_over_time(real, pred_df, dpron_ems, pd.to_datetime(fecha_inicio), pd.to_datetime(fecha_fin), columnas_seleccionadas)
        st.plotly_chart(fig2, use_container_width=True)

        # Graficar RMSE
        fig3 = plot_rmse_over_time(real, pred_df, dpron_ems, pd.to_datetime(fecha_inicio), pd.to_datetime(fecha_fin), columnas_seleccionadas)
        st.plotly_chart(fig3, use_container_width=True)

with tab1:
    # Contenido específico para estadísticas
    st.header("Desempeño de Predicciones")
    col1, col2 = st.columns([3, 3])
    with col1:
        # Espaciador para empujar la tabla hacia abajo
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        tabla0 = calculate_daily_mape_rmse(real, pred_df, dpron_ems)
        st.dataframe(tabla0)
    with col2:
        # Botón de selección de métrica
        metric_to_plot = st.radio("Selecciona la métrica a graficar:", ["MAPE", "RMSE"], horizontal=True)

        # Fecha de inicio y fin por defecto
        today = datetime.now().date()
        default_start_date = today - timedelta(days=7)
        default_end_date = today
        # Barra deslizadora para rango de fechas
        date_range = st.slider(
            "Selecciona el rango de fechas:",
            min_value=datetime(2024, 11, 4).date(),  # Rango mínimo (puedes ajustar)
            max_value=today,  # Hasta hoy
            value=(default_start_date, default_end_date),  # Valores predeterminados
            format="YYYY-MM-DD"  # Formato de las fechas
        )

        # Separar las fechas seleccionadas
        start_date, end_date = date_range

        # Validar rango de fechas
        if start_date > end_date:
            st.error("La fecha de inicio no puede ser mayor a la fecha de fin.")

        # Crear y mostrar el gráfico en Streamlit
        comparison_chart = create_comparison_bar_chart(
            resultados_df=tabla0,
            metric=metric_to_plot,
            start_date=start_date,
            end_date=end_date
        )
        st.plotly_chart(comparison_chart, use_container_width=True)
    st.image(r'MAPE.png', width=300)
    st.image(r'RMSE.png', width=300)