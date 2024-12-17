import pandas as pd
import numpy as np
import holidays
import matplotlib.dates as mdates
import seaborn as sns
import matplotlib.ticker as ticker
from datetime import datetime
import scipy.stats as stats
import boto3
from io import StringIO

def param_ciclicos(df, datetime_column):
    df[datetime_column] = pd.to_datetime(df[datetime_column])
    # Extrae el dia de semana (0=Monday, 1=Tuesday, ..., 6=Sunday)
    df['day_of_week'] = df[datetime_column].dt.dayofweek
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # Mapeo de "day_of_week" a day_names
    df['DAY'] = df['day_of_week'].apply(lambda x: day_names[x])
    # Creación de parámetros cíclicos para day of the week
    df['DAY_SIN'] = np.sin(2 * np.pi * df['day_of_week'] /7)
    df['DAY_COS'] = np.cos(2 * np.pi * df['day_of_week'] /7)
    df.drop('day_of_week', axis=1, inplace=True)
    # Creación de parámetros cíclicos para las horas del día
    df['HOUR'] = df[datetime_column].apply(lambda x: x.hour + x.minute / 60)
    df['time_angle']=(2 * np.pi * df['HOUR'] /24)
    df['TIME_SIN'] = np.sin (2 * np.pi * df['HOUR'] /24)
    df['TIME_COS'] = np.cos (2 * np.pi * df['HOUR'] /24)
    df.drop('time_angle', axis=1, inplace=True)
    df.drop('HOUR', axis=1, inplace=True)
    #Creación de parámetros cíclicos para los meses del año
    df['MONTH'] = df[datetime_column].dt.month
    df['MONTH_SIN'] = np.sin(2 * np.pi * df['MONTH'] / 12)
    df['MONTH_COS'] = np.cos(2 * np.pi * df['MONTH'] / 12)
    df.drop('MONTH', axis=1, inplace=True)
    pd.set_option('display.float_format', '{:.3f}'.format)
    df['Fecha'] = df['DATETIME'].dt.date
    df['Hora'] = df['DATETIME'].dt.hour
    return df


# Función para verificar si una fecha es un día festivo o un domingo
def is_holiday(date_value, holiday_list):
    return date_value in holiday_list or date_value.dayofweek == 6  # 6 significa domingo

# Función que agrega una columna de festivo al DataFrame
def add_holidays(df):
    # Asegura que la columna 'DATETIME' esté en formato datetime
    df['DATETIME'] = pd.to_datetime(df['DATETIME'])
    # Crea una lista de festivos en Chile para un rango de años
    chile_holidays = holidays.Chile(years=list(range(df['DATETIME'].dt.year.min(), df['DATETIME'].dt.year.max() + 1)))
    # Aplica la función is_holiday para cada fecha en la columna 'DATETIME'
    df['HOLIDAY'] = df['DATETIME'].apply(lambda date: date in chile_holidays or date.dayofweek == 6)
    return df

# Función para determinar si hubo cambio de hora
def cambio_de_hora(row):
    fechas_adelanto = {pd.Timestamp("2018-08-12 00:00:00"),
                       pd.Timestamp("2019-09-08 00:00:00"),
                       pd.Timestamp("2020-09-06 00:00:00"),
                       pd.Timestamp("2021-09-05 00:00:00"),
                       pd.Timestamp("2022-09-11 00:00:00"),
                       pd.Timestamp("2023-09-03 00:00:00"),
                       pd.Timestamp("2024-09-07 00:00:00")}
    return (row['DATETIME'] in fechas_adelanto) or (row['Hora'] == 25)

#Función que entrega columna booleana para cambio de hora
def indicador_cambio_hora(df):
    df['DATETIME'] = pd.to_datetime(df['DATETIME'])
    df['TIME_CHANGE'] = df.apply(cambio_de_hora, axis=1)
    return df

def get_dummies(df):
    dummies_df = pd.get_dummies(data=df, columns=['HOLIDAY', 'TIME_CHANGE'], drop_first=True, dtype=int)
    dummies_df.rename(columns={'HOLIDAY_True': 'HOLIDAY',
                               'TIME_CHANGE_True': 'TIME_CHANGE'}, inplace=True)
    return dummies_df

def procesar_data_diaria(data):
    data_filtrada = data.copy()
    # Obtener la fecha actual a la medianoche
    hoy = pd.Timestamp.today().normalize()
    # Filtrar las filas donde 'DATETIME' sea menor a hoy
    data_filtrada = data_filtrada[data_filtrada['DATETIME'] < hoy]
    # Interpolar los valores de 'consumo' y 'temperature'
    data_filtrada['consumo'] = data_filtrada['consumo'].interpolate(method='linear', limit_direction='forward')
    data_filtrada['temperature'] = data_filtrada['temperature'].interpolate(method='linear', limit_direction='forward')
    return data_filtrada


def main():
    df = param_ciclicos(df, 'DATETIME')
    df1 = indicador_cambio_hora(df)
    df2 = add_holidays(df1)
    data_pre = get_dummies(df2)
    data = procesar_data_diaria(data_pre)
    print(data)

if __name__ == "__main__":
    main()