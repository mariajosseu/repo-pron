import pandas as pd

def get_forecast(target_date):

    data = pd.read_csv('output/preds/pred_guia.csv')
    # Asegurarse de que 'DATETIME' sea tipo datetime
    data['DATETIME'] = pd.to_datetime(data['DATETIME'])
    
    # Filtrar el pronóstico hecho a las 00:00 del día objetivo
    data['DATETIME'] = pd.to_datetime(data['DATETIME'])
    
    # Convertir la fecha objetivo en datetime con hora 00:00
    target_datetime = pd.to_datetime(target_date)
    forecast_row = data.loc[data['DATETIME'] == target_datetime]
    
    if forecast_row.empty:
        raise ValueError(f"No se encontró un pronóstico para {target_datetime}")
    
    # Obtener el vector horizontal
    vector_horizontal = forecast_row.iloc[0, 1:].values  # Ignorar la columna DATETIME

    # Crear el vector vertical simulando pronósticos hora a hora
    vector_vertical = data.loc[(data['DATETIME'].dt.date >= target_datetime.date()) & 
                                (data['DATETIME'].dt.date <= target_datetime.date() + pd.Timedelta(days=1))
                                ].iloc[:, 1].values
    
    # Crear fechas comunes para ambos vectores
    dates = [target_datetime + pd.Timedelta(hours=i) for i in range(len(vector_horizontal))]

    # Crear DataFrame para el vector horizontal
    horizontal_df = pd.DataFrame({
        'YEAR': [date.year for date in dates],
        'MONTH': [date.month for date in dates],
        'DAY': [date.day for date in dates],
        'PERIOD': [date.hour for date in dates],
        'LOAD [MW]': vector_horizontal
    })

    # Crear DataFrame para el vector vertical (mismas fechas)
    vertical_df = pd.DataFrame({
        'YEAR': [date.year for date in dates],
        'MONTH': [date.month for date in dates],
        'DAY': [date.day for date in dates],
        'PERIOD': [date.hour for date in dates],
        'LOAD [MW]': vector_vertical
    })

    # Convertir target_date al formato YYYYMMDD
    formatted_date = target_datetime.strftime('%Y%m%d')

    horizontal_df.to_csv(f'output/preds/{formatted_date}_conv.csv')
    vertical_df.to_csv(f'output/preds/{formatted_date}_conv_.csv')
    return horizontal_df, vertical_df

def main():
    horizontal_df, vertical_df = get_forecast('2024-12-11')
    print(horizontal_df)
    print(vertical_df)

if __name__ == "__main__":
    main()