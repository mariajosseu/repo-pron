import pandas as pd
import matplotlib.pyplot as plt
def demanda_total():
    # Leer los archivos CSV
    ro_data_sic = pd.read_csv('output/ro_data.csv')
    ro_data_sing = pd.read_csv('output/ro_data_sing.csv')
    
    # Convertir 'consumo' a numérico en ambos DataFrames
    ro_data_sic['consumo'] = pd.to_numeric(ro_data_sic['consumo'], errors='coerce').fillna(0)
    ro_data_sing['consumo'] = pd.to_numeric(ro_data_sing['consumo'], errors='coerce').fillna(0)
    
    # Agregar una columna para identificar el origen de los datos
    ro_data_sic['source'] = 'sic'
    ro_data_sing['source'] = 'sing'
    
    # Concatenar los DataFrames y calcular el total
    ro_data = pd.concat([ro_data_sic, ro_data_sing])
    
    # Agrupar por 'DATETIME' y sumar 'consumo' para obtener el total
    ro_data_total = ro_data.groupby(['DATETIME'], as_index=False).agg({
        'consumo': 'sum', 
        'temperature': 'first',
        'PuntoRocio': 'first',
        'Humedad': 'first',
        'IndiceUVB': 'first',
        'dd_Valor': 'first',
        'ff_Valor': 'first',
        'RRR6_Valor': 'first'
    })
    
    # Guardar el archivo combinado
    ro_data_total.to_csv('output/ro_data_sen.csv', index=False)
    
    # Convertir 'DATETIME' a formato de fecha para los gráficos
    ro_data_sic['DATETIME'] = pd.to_datetime(ro_data_sic['DATETIME'])
    ro_data_sing['DATETIME'] = pd.to_datetime(ro_data_sing['DATETIME'])
    ro_data_total['DATETIME'] = pd.to_datetime(ro_data_total['DATETIME'])
    # Filtrar solo los últimos 30 dias para cada DataFrame
    ro_data_sic = ro_data_sic.tail(30*24)
    ro_data_sing = ro_data_sing.tail(30*24)
    ro_data_total = ro_data_total.tail(30*24)

    
    # Graficar las curvas
    plt.figure(figsize=(14, 7))
    
    # SIC curve
    plt.plot(ro_data_sic['DATETIME'], ro_data_sic['consumo'], label='SIC Consumo', color='blue', alpha=0.7)
    
    # SING curve
    plt.plot(ro_data_sing['DATETIME'], ro_data_sing['consumo'], label='SING Consumo', color='green', alpha=0.7)
    
    # Total (RO) curve
    plt.plot(ro_data_total['DATETIME'], ro_data_total['consumo'], label='Total (RO) Consumo', color='red', alpha=0.7)
    
    # Configurar detalles del gráfico
    plt.xlabel('Fecha')
    plt.ylabel('Consumo')
    plt.title('Consumo Over Time para SIC, SING y Total (RO)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Mostrar el gráfico
    plt.show()

def estudio(ro_path):
    ro_data = pd.read_csv(ro_path)
    # Filtrar datos para el año 2024 y eliminar filas con valores nulos en 'consumo'
    ro_data['DATETIME'] = pd.to_datetime(ro_data['DATETIME'])
    df_2024 = ro_data[(ro_data['DATETIME'].dt.year == 2024) & (ro_data['DATETIME'].dt.month <= 10) & (ro_data['consumo'].notna())].copy()
    
    # Crear una columna 'Fecha' con solo la fecha (sin la hora) para agrupar por día
    df_2024.loc[:, 'Fecha'] = df_2024['DATETIME'].dt.date
    
    # Agrupar por día y calcular el consumo diario
    daily_consumo = df_2024.groupby(['Fecha']).agg({'consumo': 'sum'}).reset_index()
    daily_consumo['consumo'] /= 1000
    daily_consumo['Mes'] = pd.to_datetime(daily_consumo['Fecha']).dt.month
    daily_consumo['Dia'] = pd.to_datetime(daily_consumo['Fecha']).dt.day
    resultados = {}

    # Crear la figura con 10 subplots (5 filas x 2 columnas, dejando el último vacío)
    fig, axs = plt.subplots(5, 2, figsize=(15, 10))
    fig.suptitle('Demanda diaria 2024', fontsize=16)
    
    # Iterar sobre cada mes de enero a octubre
    for mes in range(1, 11):
        # Filtrar por mes
        consumo_mes = daily_consumo[daily_consumo['Mes'] == mes].copy()
        
        if not consumo_mes.empty:
            # Seleccionar el subplot correspondiente
            ax = axs[(mes-1) // 2, (mes-1) % 2]
            
            # Calcular la media
            mean_consumo = consumo_mes['consumo'].mean()
            consumo_mes['desviacion'] = consumo_mes['consumo'] - mean_consumo

            # Filtrar solo los días con desviación positiva
            consumo_mes_positiva = consumo_mes[consumo_mes['desviacion'] > 0]

            # Encontrar el día de mayor desviación positiva
            if not consumo_mes_positiva.empty:
                dia_mayor_desviacion = consumo_mes_positiva.loc[consumo_mes_positiva['desviacion'].idxmax()]
                fecha_mayor_desviacion = dia_mayor_desviacion['Fecha']
                consumo_mayor_desviacion = dia_mayor_desviacion['consumo']

                # Encontrar el día más cercano a la media
                dia_mas_cercano_media = consumo_mes.loc[consumo_mes['desviacion'].abs().idxmin()]
                fecha_mas_cercana_media = dia_mas_cercano_media['Fecha']
                consumo_cercano_media = dia_mas_cercano_media['consumo']

                # Graficar el consumo diario
                ax.plot(consumo_mes['Dia'], consumo_mes['consumo'], label='Consumo Diario')
                ax.scatter([dia_mayor_desviacion['Dia']], [consumo_mayor_desviacion], color='red', label='dia de mayor desviación')
                ax.set_title(f'Mes {mes}')
                ax.set_xlabel('Día')
                ax.set_ylabel('Demanda [GW]')
                # Calcular la diferencia porcentual del día de mayor desviación
                diferencia_porcentual = ((consumo_mayor_desviacion - mean_consumo) / mean_consumo) * 100

                # Guardar los resultados en un diccionario con el formato de fecha solicitado
                resultados[mes] = {
                    'dia_mayor_desviacion': fecha_mayor_desviacion.strftime('%d-%m-%Y'),
                    'consumo_mayor_desviacion (GW)': round(consumo_mayor_desviacion, 2),
                    'dia_mas_cercano_media': fecha_mas_cercana_media.strftime('%d-%m-%Y'),
                    'diferencia_porcentual': round(diferencia_porcentual, 2),
                    'consumo_dia_mas_cercano_media (GW)': round(consumo_cercano_media, 2)
                    
                }
                
            # Ajustar el formato del eje x para mostrar solo los días del mes
            ax.set_xticks(range(1, 32))
            ax.set_xlim(1, 31)

    # Añadir la leyenda fuera de los subplots
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')
    
    # Ajustar el diseño de la figura
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
    return resultados

def mostrar_resultados_en_tabla(resultados):
    # Convertir el diccionario en un DataFrame para mejor visualización
    df_resultados = pd.DataFrame.from_dict(resultados, orient='index')
    df_resultados.index.name = 'Mes'
    df_resultados.columns = ['Día mayor desviacion', 'Consumo día mayor desviación', 'Día normal','consumo día normal', 'Diferencia porcentual (%)']
    
    # Mostrar la tabla
    print(df_resultados.to_string(index=True))
    
    return df_resultados


def main():
    demanda_total()
    #resultados = estudio('output/ro_data_sen.csv')
    #mostrar_resultados_en_tabla(resultados)
if __name__ == "__main__":
    main()