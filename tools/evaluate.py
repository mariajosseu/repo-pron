import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, mean_absolute_error
import matplotlib.pyplot as plt
import pandas as pd
import pandas as pd
import glob
import matplotlib.dates as mdates
import seaborn as sns
import hashlib
import plotly.graph_objects as go
import plotly.express as px

def get_color(name):
    """Genera un color único basado en el nombre"""
    # Colores fijos para EMS y DPron
    fixed_colors = {
        "EMS": "#64B5F6",# Softer blue
        "DPron": "#E57373",  # Softer red
        "Demanda real": "purple",
    }
    
    # Si el nombre tiene un color fijo, devolverlo
    if name in fixed_colors:
        return fixed_colors[name]
    
    # Generar color dinámico para otros nombres
    color_palette = px.colors.qualitative.Plotly  # Paleta de colores de Plotly
    hash_val = int(hashlib.sha256(name.encode()).hexdigest(), 16)  # Hash del nombre
    return color_palette[hash_val % len(color_palette)]  # Seleccionar color de la paleta

def graficar_con_seleccion(df_real, df_pred_combinadas, df_dpron_ems, fecha_inicio, fecha_fin, columnas_seleccionadas):
    df_combinado = combinar_real_preds(df_real, df_pred_combinadas, df_dpron_ems)
    df_filtrado = df_combinado[(df_combinado['DATETIME'] >= fecha_inicio) & (df_combinado['DATETIME'] <= fecha_fin)]
    
    # Crear una figura de Plotly
    fig = go.Figure()

    # Agregar datos reales
    fig.add_trace(go.Scatter(
        x=df_filtrado['DATETIME'], 
        y=df_filtrado['consumo'], 
        mode='lines', 
        name="Consumo Real", 
        line=dict(color=get_color("Demanda real"))
    ))

    # Agregar columnas EMS y DPron con colores fijos
    for col in ["EMS", "DPron"]:
        if col in df_filtrado.columns:
            fig.add_trace(go.Scatter(
                x=df_filtrado['DATETIME'], 
                y=df_filtrado[col], 
                mode='lines', 
                name=f"Pronóstico {col}", 
                line=dict(color=get_color(col))
            ))

    # Agregar predicciones seleccionadas con colores dinámicos
    for col in columnas_seleccionadas:
        fig.add_trace(go.Scatter(
            x=df_filtrado['DATETIME'], 
            y=df_filtrado[col], 
            mode='lines', 
            name=f"Pronóstico {col}", 
            line=dict(color=get_color(col), dash='dash')  # Líneas punteadas para predicciones
        ))

    # Configuración de diseño
    fig.update_layout(
        title="Consumo Real vs Predicciones",
        xaxis_title="Fecha y Hora",
        yaxis_title="Consumo [MW]",
        legend=dict(
            x=1,  # Posición derecha
            y=1,  # Posición superior
            xanchor="left",  # Anclaje izquierdo
            orientation="v",  # Leyenda vertical
        ),
        xaxis=dict(
            tickformat="%Y-%m-%d %H:%M",  # Formato del tick
            tickangle=270,  # Rotación de los ticks
        ),
        template="plotly_white",
    )
    return fig

def combinar_real_preds(df_real, df_pred_combinadas, df_dpron_ems):
    # Asegurarnos de que la columna 'DATETIME' de todos los DataFrames esté en formato datetime64[ns]
    df_pred_combinadas['DATETIME'] = pd.to_datetime(df_pred_combinadas['DATETIME'])
    df_dpron_ems['DATETIME'] = pd.to_datetime(df_dpron_ems['DATETIME'])
    df_real['DATETIME'] = pd.to_datetime(df_real['DATETIME'])
    # Combinar los valores reales con las predicciones por 'DATETIME'
    df_combinado = pd.merge(df_real, df_pred_combinadas, on='DATETIME', how='outer')
    # Combinar los valores reales con las predicciones por 'DATETIME'
    df_combinado = pd.merge(df_combinado, df_dpron_ems, on='DATETIME', how='outer')
    # Ordenar por 'DATETIME' para evitar cualquier desorden en los datos
    df_combinado = df_combinado.sort_values(by='DATETIME')
    
    # Limitar la gráfica a las fechas donde haya predicciones (asumiendo que predicciones son la referencia)
    fecha_min = df_pred_combinadas['DATETIME'].min()
    fecha_max = df_pred_combinadas['DATETIME'].max()
    
    # Filtrar el DataFrame combinado para esas fechas
    df_combinado = df_combinado[(df_combinado['DATETIME'] >= fecha_min) & (df_combinado['DATETIME'] <= fecha_max)]
    
    return df_combinado
    
def plot_mape_over_time(df_real, df_pred_combinadas, df_dpron_ems, fecha_inicio, fecha_fin, columnas_seleccionadas):
    df_combinado = combinar_real_preds(df_real, df_pred_combinadas, df_dpron_ems)
    df_combinado = df_combinado[(df_combinado['DATETIME'] >= fecha_inicio) & (df_combinado['DATETIME'] <= fecha_fin)]
    df_combinado.set_index("DATETIME", inplace=True)

    # Calcular MAPE
    mape_time_series = pd.DataFrame(index=df_combinado.index)
    for col in columnas_seleccionadas:
        valid_mask = (df_combinado['consumo'] != 0) & (~df_combinado['consumo'].isna()) & (~df_combinado[col].isna())
        mape_time_series[col] = np.where(valid_mask, abs(df_combinado['consumo'] - df_combinado[col]) / df_combinado['consumo'] * 100, np.nan)
    for col in ["EMS", "DPron"]:
        valid_mask = (df_combinado['Demanda real'] != 0) & (~df_combinado['Demanda real'].isna()) & (~df_combinado[col].isna())
        mape_time_series[col] = np.where(valid_mask, abs(df_combinado['Demanda real'] - df_combinado[col]) / df_combinado['Demanda real'] * 100, np.nan)

    # Crear figura
    fig = go.Figure()
    for col in mape_time_series.columns:
        fig.add_trace(go.Scatter(
            x=mape_time_series.index, 
            y=mape_time_series[col], 
            mode='lines', 
            name=f"MAPE for {col}", 
            line=dict(color=get_color(col))
        ))

    # Configuración de diseño
    fig.update_layout(
        title="MAPE Over Time",
        xaxis_title="Fecha y Hora",
        yaxis_title="MAPE [%]",
        legend=dict(
            x=1.05,  # Posición ligeramente a la derecha
            y=1,  # Posición superior
            xanchor="left",  # Anclaje izquierdo
            orientation="v",  # Leyenda vertical
        ),
        xaxis=dict(
            tickformat="%Y-%m-%d %H:%M",  # Formato del tick
            tickangle=270,  # Rotación de los ticks a 270 grados
        ),
        template="plotly_white",
    )
    return fig

def plot_rmse_over_time(df_real, df_pred_combinadas, df_dpron_ems, fecha_inicio, fecha_fin, columnas_seleccionadas):
    df_combinado = combinar_real_preds(df_real, df_pred_combinadas, df_dpron_ems)
    df_combinado = df_combinado[(df_combinado['DATETIME'] >= fecha_inicio) & (df_combinado['DATETIME'] <= fecha_fin)]
    df_combinado.set_index("DATETIME", inplace=True)

    # Calcular RMSE
    rmse_time_series = pd.DataFrame(index=df_combinado.index)
    for col in columnas_seleccionadas:
        valid_mask = (~df_combinado['consumo'].isna()) & (~df_combinado[col].isna())
        squared_errors = (df_combinado['consumo'] - df_combinado[col]) ** 2
        rmse_time_series[col] = np.where(valid_mask, np.sqrt(squared_errors), np.nan)
    for col in ["EMS", "DPron"]:
        valid_mask = (~df_combinado['Demanda real'].isna()) & (~df_combinado[col].isna())
        squared_errors = (df_combinado['Demanda real'] - df_combinado[col]) ** 2
        rmse_time_series[col] = np.where(valid_mask, np.sqrt(squared_errors), np.nan)

    # Crear figura
    fig = go.Figure()
    for col in rmse_time_series.columns:
        fig.add_trace(go.Scatter(
            x=rmse_time_series.index, 
            y=rmse_time_series[col], 
            mode='lines', 
            name=f"RMSE for {col}", 
            line=dict(color=get_color(col))
        ))
    
    # Línea de referencia
    fig.add_trace(go.Scatter(
        x=rmse_time_series.index, 
        y=[300] * len(rmse_time_series), 
        mode='lines', 
        name="300 MW Setpoint", 
        line=dict(color="red", dash="dash")
    ))

    # Configuración de diseño
    fig.update_layout(
        title="RMSE Over Time",
        xaxis_title="Fecha y Hora",
        yaxis_title="RMSE [MW]",
        legend=dict(
            x=1.05,  # Posición ligeramente a la derecha
            y=1,  # Posición superior
            xanchor="left",  # Anclaje izquierdo
            orientation="v",  # Leyenda vertical
        ),
        xaxis=dict(
            tickformat="%Y-%m-%d %H:%M",  # Formato del tick
            tickangle=270,  # Rotación de los ticks a 270 grados
        ),
        template="plotly_white",
    )
    return fig

def calculate_mape_rmse_summary(df_real, df_pred_combinadas):
    # Combine real and predicted values into a single DataFrame
    df_combinado = combinar_real_preds(df_real, df_pred_combinadas)
    
    # Ensure 'DATETIME' is the index for easier alignment if not already
    if 'DATETIME' in df_combinado.columns:
        df_combinado.set_index('DATETIME', inplace=True)

    # List of prediction columns (assuming they start with '2024' based on your format)
    pred_columns = sorted([col for col in df_combinado.columns if col.startswith('2024')])

    # Initialize lists to store results
    mape_values = []
    rmse_values = []

    # Calculate MAPE and RMSE for each prediction column
    for col in pred_columns:
        # Valid mask to avoid NaN or division by zero errors
        valid_mask = (df_combinado['consumo'] != 0) & (~df_combinado['consumo'].isna()) & (~df_combinado[col].isna())

        # Calculate MAPE and RMSE for the current prediction column
        mape = (abs(df_combinado['consumo'] - df_combinado[col]) / df_combinado['consumo'])[valid_mask].mean() * 100
        rmse = np.sqrt(((df_combinado['consumo'] - df_combinado[col]) ** 2)[valid_mask].mean())
        
        # Append results to the lists
        mape_values.append(mape)
        rmse_values.append(rmse)
    
    # Create a DataFrame with the results
    summary_df = pd.DataFrame({
        'Prediction': pred_columns,
        'Average MAPE (%)': mape_values,
        'Average RMSE (MW)': rmse_values
    })

    # Print the table to the console
    print("MAPE and RMSE Summary Table")
    print(summary_df)

    return summary_df

def calculate_daily_mape_rmse(df_real, df_pred_combinadas, df_dpron_ems):
    # Combinar datos reales, predicciones y columnas EMS y DPron
    df_combinado = combinar_real_preds(df_real, df_pred_combinadas, df_dpron_ems)
    
    # Crear columna de fecha para agrupar por día
    df_combinado['Fecha'] = df_combinado['DATETIME'].dt.date

    # Inicializar resultados
    resultados = {"Periodo": [], "DPron MAPE": [], "DPron RMSE": [], "EMS MAPE": [], "EMS RMSE": [], "Conv1D MAPE": [], "Conv1D RMSE": []}

    # Agrupar por fecha para procesar cada día
    for fecha, grupo in df_combinado.groupby("Fecha"):
        resultados["Periodo"].append(fecha)

        # Calcular métricas para DPron
        valid_mask_dpron = (grupo['Demanda real'] != 0) & (~grupo['Demanda real'].isna()) & (~grupo['DPron'].isna())
        if valid_mask_dpron.any():
            dpron_mape = (abs(grupo['Demanda real'] - grupo['DPron']) / grupo['Demanda real'])[valid_mask_dpron].mean() * 100
            dpron_rmse = np.sqrt(((grupo['Demanda real'] - grupo['DPron']) ** 2)[valid_mask_dpron].mean())
        else:
            dpron_mape, dpron_rmse = None, None
        resultados["DPron MAPE"].append(round(dpron_mape, 2) if dpron_mape is not None else None)
        resultados["DPron RMSE"].append(round(dpron_rmse, 2) if dpron_rmse is not None else None)

        # Calcular métricas para EMS
        valid_mask_ems = (grupo['Demanda real'] != 0) & (~grupo['Demanda real'].isna()) & (~grupo['EMS'].isna())
        if valid_mask_ems.any():
            ems_mape = (abs(grupo['Demanda real'] - grupo['EMS']) / grupo['Demanda real'])[valid_mask_ems].mean() * 100
            ems_rmse = np.sqrt(((grupo['Demanda real'] - grupo['EMS']) ** 2)[valid_mask_ems].mean())
        else:
            ems_mape, ems_rmse = None, None
        resultados["EMS MAPE"].append(round(ems_mape, 2) if ems_mape is not None else None)
        resultados["EMS RMSE"].append(round(ems_rmse, 2) if ems_rmse is not None else None)

        # Calcular métricas para Conv1D (primeras 24 horas del día)
        conv_mape, conv_rmse = None, None
        # Identificar columnas relevantes para esta fecha
        conv_columns = [col for col in df_pred_combinadas.columns if col.startswith(f"{fecha.strftime('%Y%m%d')}_")]
        # Priorizar columnas con guion bajo (_)
        if conv_columns:
            conv_column = next((col for col in conv_columns if col.endswith("_")), conv_columns[0])
            grupo_conv = grupo.iloc[:24]  # Tomar solo las primeras 24 horas
            valid_mask_conv = (grupo_conv['consumo'] != 0) & (~grupo_conv['consumo'].isna()) & (~grupo_conv[conv_column].isna())
            if valid_mask_conv.any():
                conv_mape = (abs(grupo_conv['consumo'] - grupo_conv[conv_column]) / grupo_conv['consumo'])[valid_mask_conv].mean() * 100
                conv_rmse = np.sqrt(((grupo_conv['consumo'] - grupo_conv[conv_column]) ** 2)[valid_mask_conv].mean())
        resultados["Conv1D MAPE"].append(round(conv_mape, 2) if conv_mape is not None else None)
        resultados["Conv1D RMSE"].append(round(conv_rmse, 2) if conv_rmse is not None else None)

    # Crear DataFrame con el formato final
    resultados_df = pd.DataFrame(resultados)

    # Reorganizar columnas con MultiIndex
    multiindex_columns = pd.MultiIndex.from_tuples([
        ("", "Periodo"),
        ("DPron", "MAPE [%]"),
        ("DPron", "RMSE [MW]"),
        ("EMS", "MAPE [%]"),
        ("EMS", "RMSE [MW]"),
        ("Conv1D", "MAPE [%]"),
        ("Conv1D", "RMSE [MW]")
    ])
    resultados_df.columns = multiindex_columns
    return resultados_df

def create_comparison_bar_chart(resultados_df, metric="MAPE", start_date=None, end_date=None):
    # Filtrar por rango de fechas
    if start_date and end_date:
        resultados_df = resultados_df[(resultados_df[("", "Periodo")] >= start_date) & 
                                      (resultados_df[("", "Periodo")] <= end_date)]

    # Extraer los datos para cada modelo
    days = resultados_df[("", "Periodo")].tolist()
    dpron_values = resultados_df["DPron", f"{metric} [%]" if metric == "MAPE" else f"{metric} [MW]"].tolist()
    ems_values = resultados_df["EMS", f"{metric} [%]" if metric == "MAPE" else f"{metric} [MW]"].tolist()
    conv1d_values = resultados_df["Conv1D", f"{metric} [%]" if metric == "MAPE" else f"{metric} [MW]"].tolist()
    
    # Crear el gráfico
    fig = go.Figure()

    # Añadir barras para DPron
    fig.add_trace(go.Bar(
        x=days,
        y=dpron_values,
        name="DPron",
        marker_color="#E57373"
    ))

    # Añadir barras para EMS
    fig.add_trace(go.Bar(
        x=days,
        y=ems_values,
        name="EMS",
        marker_color="orange"
    ))

    # Añadir barras para Conv1D
    fig.add_trace(go.Bar(
        x=days,
        y=conv1d_values,
        name="Conv1D",
        marker_color="slateblue"
    ))

    # Configurar diseño
    fig.update_layout(
        title=f"Comparación {metric} por modelo",
        xaxis_title="Días",
        yaxis_title=f"{metric} [%]" if metric == "MAPE" else f"{metric} [MW]",
        barmode="group",  # Agrupar barras una al lado de la otra
        template="plotly_white"
    )

    return fig
