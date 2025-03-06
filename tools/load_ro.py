from datetime import datetime, timedelta
import pandas as pd
import os

def get_latest_momento(file):
    if os.path.exists(file):
        #merged_data_df = pd.read_parquet(parquet_file)
        merged_data_df = pd.read_csv(file, parse_dates=['momento'])
        merged_data_df['momento'] = pd.to_datetime(merged_data_df['momento'], dayfirst=True)
        latest_momento = merged_data_df['momento'].max()
        return latest_momento
    else:
        raise FileNotFoundError(f"{file} not found.")

def read_ro_load_data(ro_folder_path, start_date, end_date, month_mapping):
    all_ro_load_data = []

    # Loop through years and months
    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 13):
            if year == start_date.year and month < start_date.month:
                continue
            if year == end_date.year and month > end_date.month:
                break

            month_name = month_mapping[month]
            ro_folder_month_path = os.path.join(ro_folder_path, f"{year}", f"{month_name} {year}")

            for day in range(1, 32):
                try:
                    ro_file_name = f"RO{year % 100:02d}{month:02d}{day:02d}.xls"
                    ro_file_path = os.path.join(ro_folder_month_path, ro_file_name)

                    if os.path.exists(ro_file_path):
                        # Read RO Excel file
                        df_ro = pd.read_excel(ro_file_path, header=None)

                        # Find the "DEMANDA APROX." row
                        demanda_rows = df_ro.apply(lambda row: row.str.contains("DEMANDA APROX.", na=False).any(), axis=1)
                        if demanda_rows.any():
                            demanda_row_idx = demanda_rows.idxmax()

                            # Extract the relevant row and convert it into a DataFrame
                            extracted_row = df_ro.iloc[demanda_row_idx].transpose().iloc[1:25].reset_index(drop=True)
                            extracted_df = pd.DataFrame({'DEMANDA APROX.': extracted_row})

                            # Add 'Date' and 'Hour' columns and create 'Datetime'
                            date_from_path = pd.to_datetime(f"{year}-{month:02d}-{day:02d}")
                            extracted_df['Date'] = date_from_path
                            extracted_df['Hour'] = range(24)
                            extracted_df['momento'] = pd.to_datetime(extracted_df['Date']) + pd.to_timedelta(extracted_df['Hour'], unit='h')

                            # Store extracted data in a list
                            all_ro_load_data.append(extracted_df[['DEMANDA APROX.', 'momento']])
                        else:
                            print(f"'DEMANDA APROX.' not found in {ro_file_path}")

                except Exception as e:
                    print(f"Error processing file {ro_file_path}: {e}")

    # Concatenate all the data at the end
    if all_ro_load_data:
        all_ro_load_data_df = pd.concat(all_ro_load_data, ignore_index=True)
    else:
        all_ro_load_data_df = pd.DataFrame(columns=['DEMANDA APROX.', 'momento'])

    return all_ro_load_data_df

def rellenar_load_con_demanda(weather_data, ro):
    # Convertir las columnas 'momento' a formato datetime
    weather_data['momento'] = pd.to_datetime(weather_data['momento'])
    ro['momento'] = pd.to_datetime(ro['momento'])
    
    # Unir ambos DataFrames en función de la columna 'momento'
    combined_data = pd.merge(weather_data, ro[['momento', 'DEMANDA APROX.']], on='momento', how='left')
    
    # Rellenar los NaN en 'load' con los valores de 'DEMANDA APROX.'
    combined_data['load'] = combined_data['load'].fillna(combined_data['DEMANDA APROX.'])
    
    # Eliminar la columna 'DEMANDA APROX.' si no es necesaria
    combined_data = combined_data.drop(columns=['DEMANDA APROX.'])
    return combined_data


def read_ro_load_data(ro_folder_path, start_date, end_date, month_mapping, demanda_column_name):
    all_ro_load_data = []

    # Loop through years and months
    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 13):
            if year == start_date.year and month < start_date.month:
                continue
            if year == end_date.year and month > end_date.month:
                break

            month_name = month_mapping[month]
            ro_folder_month_path = os.path.join(ro_folder_path, f"{year}", f"{month_name} {year}")

            for day in range(1, 32):
                try:
                    ro_file_name = f"RO{year % 100:02d}{month:02d}{day:02d}.xls"
                    ro_file_path = os.path.join(ro_folder_month_path, ro_file_name)

                    if os.path.exists(ro_file_path):
                        # Read RO Excel file
                        df_ro = pd.read_excel(ro_file_path, header=None)

                        # Find the specified demand row
                        demanda_rows = df_ro.apply(lambda row: row.str.contains(demanda_column_name, na=False).any(), axis=1)
                        if demanda_rows.any():
                            demanda_row_idx = demanda_rows.idxmax()

                            # Extract the relevant row and convert it into a DataFrame
                            extracted_row = df_ro.iloc[demanda_row_idx].transpose().iloc[1:25].reset_index(drop=True)
                            extracted_df = pd.DataFrame({demanda_column_name: extracted_row})

                            # Add 'Date' and 'Hour' columns and create 'Datetime'
                            date_from_path = pd.to_datetime(f"{year}-{month:02d}-{day:02d}")
                            extracted_df['Date'] = date_from_path
                            extracted_df['Hour'] = range(24)
                            extracted_df['momento'] = pd.to_datetime(extracted_df['Date']) + pd.to_timedelta(extracted_df['Hour'], unit='h')

                            # Store extracted data in a list
                            all_ro_load_data.append(extracted_df[[demanda_column_name, 'momento']])
                        else:
                            print(f"{demanda_column_name} not found in {ro_file_path}")

                except Exception as e:
                    print(f"Error processing file {ro_file_path}: {e}")

    # Concatenate all the data at the end
    if all_ro_load_data:
        all_ro_load_data_df = pd.concat(all_ro_load_data, ignore_index=True)
    else:
        all_ro_load_data_df = pd.DataFrame(columns=[demanda_column_name, 'momento'])

    return all_ro_load_data_df

def rellenar_load_con_demanda(weather_data, ro, demanda_column_name):
    # Convertir las columnas 'momento' a formato datetime
    weather_data['momento'] = pd.to_datetime(weather_data['momento'])
    ro['momento'] = pd.to_datetime(ro['momento'])
    
    # Unir ambos DataFrames en función de la columna 'momento'
    combined_data = pd.merge(weather_data, ro[['momento', demanda_column_name]], on='momento', how='left')
    
    # Rellenar los NaN en 'load' con los valores de la columna de demanda
    combined_data['load'] = combined_data['load'].fillna(combined_data[demanda_column_name])
    
    # Eliminar la columna de demanda si no es necesaria
    combined_data = combined_data.drop(columns=[demanda_column_name])
    return combined_data

def load_ro(parquet_file, ro_folder_base_path, month_mapping, demanda_column_name):
    # Step 1: Get the latest 'momento' from merged_data.csv and set the date range
    latest_momento = get_latest_momento(parquet_file)
    start_date = latest_momento - timedelta(days=5)
    end_date = datetime.now() - timedelta(days=3)  # Current date minus 3 days

    print(f"Fetching RO load data from {start_date.date()} to {latest_momento.date()}")
    new_ro_data = read_ro_load_data(ro_folder_base_path, start_date, end_date, month_mapping, demanda_column_name)
    return new_ro_data