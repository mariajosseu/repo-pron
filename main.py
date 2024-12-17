from tools.load_ro import load_ro, rellenar_load_con_demanda
from tools.weather_params import fetch_and_process_weather_data_for_period, append_new_api_data
from tools.clean_data import limpiar_y_renombrar_columnas
import pandas as pd
from datetime import datetime, timedelta
from preprocesamiento import param_ciclicos, indicador_cambio_hora, add_holidays, get_dummies, procesar_data_diaria

def main():
    merged_data_path = r'output\merged_data.csv'
    #merged_data_path_sing = r'output\merged_data_sing.csv'
    last_weather_df = pd.read_csv(merged_data_path, parse_dates=['momento'], dayfirst=False)
    api_weather_data = fetch_and_process_weather_data_for_period((datetime.now()-timedelta(days=1)),(datetime.now()+timedelta(days=1)))
    weather_data = append_new_api_data(last_weather_df, api_weather_data)
    ro_folder_base_path = r"\\nas-cen1\DPRO\99 Resdiac\Resumenes Diarios"
    month_mapping = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo",
    6: "junio", 7: "julio", 8: "agosto", 9: "septiembre",
    10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    ro = load_ro(merged_data_path, ro_folder_base_path, month_mapping, 'DEMANDA APROX.')
    data = rellenar_load_con_demanda(weather_data, ro, 'DEMANDA APROX.')
    data.to_csv(merged_data_path, index=False)
    ro_data = limpiar_y_renombrar_columnas(data)
    ro_data.to_csv('output/ro_data.csv', index=False)
    print(ro_data)
    print(ro_data.tail(n=40))
    df = param_ciclicos(ro_data, 'DATETIME')
    df1 = indicador_cambio_hora(df)
    df2 = add_holidays(df1)
    data_pre = get_dummies(df2)
    data = procesar_data_diaria(data_pre)
    data.to_csv('output/ro_v2.csv', index=False)
    print(data)

if __name__ == "__main__":
    main()