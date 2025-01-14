import pandas as pd

def to_parquet():
    # Leer el archivo CSV
    csv_file = r'output\ro.csv'
    df = pd.read_csv(csv_file)

    # Guardar el archivo como Parquet
    parquet_file = r'output\ro.parquet'
    df.to_parquet(parquet_file, engine="pyarrow", index=False)

    print(f"Archivo convertido a Parquet y guardado en: {parquet_file}")

def main():
    to_parquet()

if __name__ == "__main__":
    main()