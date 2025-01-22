import pandas as pd
import requests
from datetime import timedelta

def fetch_and_process_weather_data_for_period(start_date, end_date):
    # Your credentials
    usuario = 'tomas.searle@coordinador.cl'
    token = '2fab7d3ae3c3175abf8aa5e7'
    codigo_nacional = '330020'

    # Create an empty DataFrame to store all the weather data
    all_weather_data = pd.DataFrame()

    # Loop over the period month-by-month
    current_date = start_date
    print(f'current date: {current_date}')
    while current_date <= end_date:
        year = current_date.strftime('%Y')  # Get the current year
        month = current_date.strftime('%m')  # Get the current month

        # API endpoint
        url = f'https://climatologia.meteochile.gob.cl/application/servicios/getDatosRecientesEma/{codigo_nacional}/{year}/{month}'
        print(url)
        # Parameters for the API request
        params = {
            'usuario': usuario,
            'token': token
        }

        # Make the request with SSL verification disabled
        response = requests.get(url, params=params, verify=False)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if 'datosEstaciones' in data and 'datos' in data['datosEstaciones']:
                weather_records = data['datosEstaciones']['datos']

                # Create a DataFrame from the weather records
                api_weather_df = pd.DataFrame(weather_records)

                # Convert 'momento' to a datetime object
                api_weather_df['momento'] = pd.to_datetime(api_weather_df['momento'])

                # Set the 'momento' column to UTC timezone (since the weather data is in UTC)
                api_weather_df['momento'] = api_weather_df['momento'].dt.tz_localize('UTC')

                # Convert the 'momento' column from UTC to Chilean local time
                api_weather_df['momento'] = api_weather_df['momento'].dt.tz_convert('America/Santiago')

                # Remove timezone information and keep only the datetime
                api_weather_df['momento'] = api_weather_df['momento'].dt.tz_localize(None)

                # Clean up and convert API fields to match historical DataFrame fields
                api_weather_df['Temperatura'] = api_weather_df['temperatura'].str.replace(' °C', '').astype(float)
                #api_weather_df['PuntoRocio'] = api_weather_df['puntoDeRocio'].str.replace(' °C', '').astype(float)
                #api_weather_df['Humedad'] = api_weather_df['humedadRelativa'].str.replace(' %', '').astype(float)
                #api_weather_df['IndiceUVB'] = api_weather_df['radiacionGlobalInst'].str.replace(' Watt/m2', '').astype(float) * 0.005  # Adjust conversion factor for UV Index
                #api_weather_df['dd_Valor'] = api_weather_df['direccionDelViento'].str.replace(' °', '').astype(float)
                #api_weather_df['ff_Valor'] = api_weather_df['fuerzaDelViento'].str.replace(' kt', '').astype(float)
                #api_weather_df['RRR6_Valor'] = api_weather_df['aguaCaida6Horas'].str.replace(' mm', '').astype(float)

                # Select relevant columns for further processing
                #relevant_columns = ['momento', 'Temperatura', 'PuntoRocio', 'Humedad', 'IndiceUVB', 'dd_Valor', 'ff_Valor', 'RRR6_Valor']
                relevant_columns = ['momento', 'Temperatura']
                api_weather_df = api_weather_df[relevant_columns]

                # Set 'momento' as the index
                api_weather_df.set_index('momento', inplace=True)

                # Resample the data to hourly frequency (taking mean for continuous data)
                hourly_api_weather_df = api_weather_df.resample('H').mean()

                # Forward-fill the data over 6-hour intervals for Agua6Horas
                hourly_api_weather_df['RRR6_Valor'] = hourly_api_weather_df['RRR6_Valor'].resample('H').ffill()

                # Append to all_weather_data
                all_weather_data = pd.concat([all_weather_data, hourly_api_weather_df])

            else:
                print(f"Unexpected response structure: {data}")
        else:
            print(f"Failed to fetch data from API. Status code: {response.status_code}")

        # Move to the next month
        current_date += timedelta(days=32)
        current_date = current_date.replace(day=1)  # Reset to the first day of the next month

    return all_weather_data  # Return all the weather data for the period


def append_new_api_data(merged_df, api_weather_df):
    if api_weather_df.empty:
        print("No new weather data to append.")
        return merged_df

    # Merge the new weather data with the existing merged data on 'momento'
    merged_df = pd.merge(merged_df, api_weather_df, on='momento', how='outer', suffixes=('', '_new'))

    # Now, for each weather-related column, update missing values in the original with the new data
    #weather_columns = ['Temperatura', 'PuntoRocio', 'Humedad', 'IndiceUVB', 'dd_Valor', 'ff_Valor', 'RRR6_Valor']
    weather_columns = ['Temperatura']
    for col in weather_columns:
        if f"{col}_new" in merged_df.columns:
            # Use combine_first to fill NaN values from new data
            merged_df[col] = merged_df[col].combine_first(merged_df[f"{col}_new"])
            # Drop the newly appended column
            merged_df.drop(columns=[f"{col}_new"], inplace=True)

    # Sort the dataframe by 'momento' to ensure chronological order
    merged_df = merged_df.sort_values('momento').reset_index(drop=True)

    return merged_df
