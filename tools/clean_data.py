def limpiar_y_renombrar_columnas(df):
    # Eliminar las columnas que comienzan con 'Unnamed'
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Renombrar las columnas 'momento', 'load' y 'Temperatura'
    df = df.rename(columns={'momento': 'DATETIME', 'load': 'consumo', 'Temperatura': 'temperature'})
    # Eliminar las filas donde la columna 'DATETIME' sea NaT
    df = df.dropna(subset=['DATETIME'])
    
    return df