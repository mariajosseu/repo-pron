import os
import pandas as pd
def import_pred_from_folder_with_filter(folder_path, keyword):
    # Obtener la lista de todos los archivos en la carpeta
    archivos_predicciones = [f for f in os.listdir(folder_path) if keyword in f and f.endswith('.csv')]
    
    # Lista para almacenar DataFrames de predicciones
    predicciones_list = []
    
    # Inicializar variables para obtener el rango dinámico de fechas
    fechas_inicio = []
    fechas_fin = []
    
    for file_name in archivos_predicciones:
        # Extraer la fecha de inicio del archivo desde su nombre
        nombre_pred = file_name.replace('.csv', '')
        nombre_pred_fecha = nombre_pred.split('_')[0]
        
        # Convertir la parte de la fecha a datetime
        fecha_inicio = pd.to_datetime(nombre_pred_fecha, format='%Y%m%d')
        fechas_inicio.append(fecha_inicio)
        fechas_fin.append(fecha_inicio + pd.Timedelta(hours=47))  # Cada archivo cubre 48 horas

    # Obtener las fechas mínima y máxima del rango total
    fecha_inicio_global = min(fechas_inicio)
    fecha_fin_global = max(fechas_fin)
    
    # Crear un rango de DATETIME que cubra desde la fecha mínima hasta la fecha máxima
    rango_horas = pd.date_range(start=fecha_inicio_global, end=fecha_fin_global, freq='H')

    # DataFrame base con el rango de DATETIME
    predicciones_combinadas = pd.DataFrame({'DATETIME': rango_horas})
    
    for file_name in archivos_predicciones:
        # Leer el archivo desde la carpeta
        file_path = os.path.join(folder_path, file_name)
        predicciones_df = pd.read_csv(file_path)
        
        # Extraer nuevamente la fecha de inicio del archivo
        nombre_pred = file_name.replace('.csv', '')
        nombre_pred_fecha = nombre_pred.split('_')[0]
        fecha_inicio = pd.to_datetime(nombre_pred_fecha, format='%Y%m%d')
        
        # Crear la columna 'DATETIME' para cubrir 48 horas a partir de 'fecha_inicio'
        predicciones_df['DATETIME'] = fecha_inicio + pd.to_timedelta(predicciones_df.index, unit='h')
        
        # Renombrar 'LOAD [MW]' a 'consumo_pred' + nombre del archivo para diferenciar predicciones
        predicciones_df = predicciones_df.rename(columns={'LOAD [MW]': f'{nombre_pred}'})
        
        # Unir este DataFrame al DataFrame base predicciones_combinadas basado en 'DATETIME'
        predicciones_combinadas = pd.merge(predicciones_combinadas, predicciones_df[['DATETIME', f'{nombre_pred}']],
                                           on='DATETIME', how='left')
    
    return predicciones_combinadas