import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose

# Cargar archivo de accidentes
def load_file_accidentes(file_path):
    print(f"\nRecibimos la ruta: {file_path}")
    df_accidentes = pd.read_csv(file_path)

    # Convertir la columna de fecha en tipo datetime si existe
    if 'Fecha del Accidente' in df_accidentes.columns:
        df_accidentes['Fecha del Accidente'] = pd.to_datetime(df_accidentes['Fecha del Accidente'], errors='coerce')
    return df_accidentes

# Análisis exploratorio
def analisis_exploratorio(df_accidentes):
    print("\nAnálisis exploratorio")
    
    # Primeras líneas del archivo
    print("\nPrimeras líneas del archivo\n")
    print(df_accidentes.head(), "\n")
    
    # Información general
    print("\nInformación general del archivo\n")
    print(df_accidentes.info(), "\n")
    
    # Estadística descriptiva
    print("\nEstadística descriptiva del archivo\n")
    print(df_accidentes.describe(), "\n")
    
    # Valores nulos por columna
    print("\nValores nulos por columnas del archivo\n")
    print(df_accidentes.isnull().sum(), "\n")  

    # Valores únicos por columna
    print("Valores únicos por columna:\n")
    for column in df_accidentes.columns:
        unique_values = df_accidentes[column].nunique()
        print(f"{column}: {unique_values} valores únicos")

# Limpieza y ajuste de datos, incluyendo unificación de valores
def ajustar_datos(df_accidentes):
    # Eliminación de columnas innecesarias
    df_depurado = df_accidentes.drop(['Informes Policiales de Accidentes de Tránsito (IPAT) ', 
                                       'Dirección', 'Barrio', 'Comuna', 'Corregimiento', 'Hipótesis',
                                       'Hipótesis 2', 'Motocicleta', 'Mes'], axis=1)

    # Unificación de valores en la columna Clase_accidente
    df_depurado['Clase de Accidente'] = df_depurado['Clase de Accidente'].replace({
        'CAIDA OCUPANTE': 'CAIDA OCUPANTE',
        'CAÍDA': 'CAIDA OCUPANTE',
        'INCENDIO': 'INCENDIO',
        'INCENERADO': 'INCENDIO',
        'OTRO': 'OTROS',
        'OTROS': 'OTROS'
    })

    # Unificación de valores en la columna Gravedad
    df_depurado['Gravedad'] = df_depurado['Gravedad'].replace({
        'CON MUERTO': 'MUERTOS',
        'MUERTO': 'MUERTOS',
        'HERIDO': 'HERIDOS',
        'HERIDOS': 'HERIDOS'
    })

    # Ajuste del formato de fecha de accidente
    df_depurado['Fecha del Accidente'] = df_depurado['Fecha del Accidente'].dt.strftime('%Y/%m/%d')

    # Ajuste del formato de Hora
    if 'Hora' in df_depurado.columns:
        df_depurado['Hora'] = pd.to_datetime(df_depurado['Hora'], errors='coerce')
        df_depurado['Hora'] = df_depurado['Hora'].dt.strftime('%H:%M')

    # Renombre de columnas del df
    df_depurado = df_depurado.rename(columns={
        'Fecha del Accidente': 'Fecha_accidente', 
        'Género': 'Genero',
        'Clase de Accidente': 'Clase_accidente',
        'Choque Con': 'Choque_con',
        'Clase de Vehículo 1': 'Clase_vehiculo_1',
        'Servicio': 'Servicio_vehiculo_1',
        'Gravedad Conductor': 'Gravedad_Conductor_vehiculo_1',
        'Embriaguez': 'Embriaguez_vehiculo_1',
        'Grado': 'Grado_vehiculo_1',
        'Clase de Vehículo 2': 'Clase_vehiculo_2',
        'Servicio 2': 'Servicio_vehiculo_2',
        'Gravedad Conductor 2': 'Gravedad_conductor_vehiculo_2',
        'Embriaguez 2': 'Embriaguez_vehiculo_2',
        'Grado 2': 'Grado_vehiculo_2'})

    return df_depurado

# Análisis de series temporales con descomposición
def analisis_series_temporales(df_depurado):
    if 'Fecha_accidente' in df_depurado.columns:
        print("\nRealizando análisis de series temporales con descomposición")
        
        # Crear nuevas columnas para el año y el mes
        df_depurado['año'] = pd.to_datetime(df_depurado['Fecha_accidente']).dt.year
        df_depurado['mes'] = pd.to_datetime(df_depurado['Fecha_accidente']).dt.month

        # Agrupar por año y mes y contar los accidentes
        accidentes_por_mes = df_depurado.groupby(['año', 'mes']).size().reset_index(name='conteo_accidentes')

        # Crear una columna de fecha con formato YYYY-MM para el análisis de series temporales
        accidentes_por_mes['fecha'] = pd.to_datetime(accidentes_por_mes['año'].astype(str) + '-' + accidentes_por_mes['mes'].astype(str), format='%Y-%m')

        # Establecer la columna fecha como el índice
        accidentes_por_mes.set_index('fecha', inplace=True)

        # Realizar la descomposición de la serie temporal
        descomposicion = seasonal_decompose(accidentes_por_mes['conteo_accidentes'], model='additive', period=12)
        
        # Graficar los componentes de la descomposición
        descomposicion.plot()
        plt.suptitle('Descomposición de la serie temporal - Accidentes', fontsize=16)
        plt.tight_layout()

        # Mostrar el gráfico
        plt.show()
    else:
        print("No se encontró una columna de 'Fecha_accidente' para realizar el análisis temporal.")



# Ajustes adicionales y gráficas consolidadas
def ajustar_y_graficar(df_depurado):
    # Primeras líneas del df depurado
    print("\nPrimeras líneas del df depurado\n")
    print(df_depurado.head(), "\n")

    # Conteo de accidentes por mes
    df_depurado['conteo_accidentes'] = 0
    df_depurado.loc[df_depurado['año'] < 2024, 'conteo_accidentes'] = 1
    df_depurado = df_depurado.loc[df_depurado['año'] < 2024]

    # Agrupación mes/año de cada accidente
    df_mensual = df_depurado.groupby(['año', 'mes']).agg({'conteo_accidentes': 'sum'}).reset_index()

    # Gráfica consolidada por año
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.lineplot(df_mensual, x='mes', y='conteo_accidentes', hue='año', palette='bright')

    # Ajuste de etiquetas de datos
    plt.title('Accidentalidad consolidada 2019 - 2023', fontsize=16)
    plt.xlabel('Mes', fontsize=12)
    plt.ylabel('Accidentalidad', fontsize=12)
    plt.xticks(range(1, 13), ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
    plt.legend(title='Año')

    plt.show()

# Función para generar gráfico de barras agrupadas (Clase_accidente vs Gravedad)
def graficar_barras_agrupadas(df_depurado):
    print("\nGenerando gráfico de barras agrupadas para Clase_accidente y Gravedad")

    # Crear nuevas columnas para el año
    df_depurado['año'] = pd.to_datetime(df_depurado['Fecha_accidente']).dt.year
    df_depurado = df_depurado[df_depurado['año']<2024]
    df_depurado = df_depurado[df_depurado['conteo_accidentes']>0]

    # Verificar que las columnas existan
    if 'Clase_accidente' in df_depurado.columns and 'Gravedad' in df_depurado.columns:
        # Crear tabla de contingencia para contar ocurrencias de accidentes según Clase y Gravedad
        tabla_clase_gravedad = pd.crosstab(df_depurado['Clase_accidente'], df_depurado['Gravedad'])
       

        # Reiniciar el índice para poder usarlo en seaborn
        tabla_clase_gravedad = tabla_clase_gravedad.reset_index()

        # Usar seaborn para generar un gráfico de barras agrupadas
        tabla_melt = tabla_clase_gravedad.melt(id_vars='Clase_accidente', var_name='Gravedad', value_name='conteo_accidentes')
        tabla_melt = tabla_melt[tabla_melt['conteo_accidentes']>0]

        # Configurar el gráfico
        plt.figure(figsize=(12, 8))
        sns.barplot(data=tabla_melt, x='Clase_accidente', y='conteo_accidentes', hue='Gravedad', palette='tab10')

        # Ajustar título y etiquetas
        plt.title('Distribución de Accidentes por Clase y Gravedad (2019 al 2023)', fontsize=16)
        plt.xlabel('Clase de Accidente', fontsize=12)
        plt.ylabel('Número de Accidentes', fontsize=12)

        # Mostrar la leyenda fuera del gráfico
        plt.legend(title='Gravedad', bbox_to_anchor=(1.05, 1), loc='upper left')

        # Rotar las etiquetas del eje x para que se lean bien
        plt.xticks(rotation=45, ha='right')

        # Mostrar las etiquetas de los valores en cada barra
        for p in plt.gca().patches:
            plt.gca().annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                               ha='center', va='baseline', fontsize=10, color='black', xytext=(0, 5),
                               textcoords='offset points')

        # Ajustar el diseño para evitar que se corte la leyenda
        plt.tight_layout()

        # Mostrar el gráfico
        plt.show()

    else:
        print("No se encontraron las columnas 'Clase_accidente' o 'Gravedad' en el DataFrame.")


# Programa principal
if __name__ == "__main__":
    print("Bienvenidos al sistema de Análisis de Accidentes de Tránsito")

    # Ruta del archivo CSV
    path_file_csv = '.\\data\\accidentes_transito.csv'

    # Cargar archivo
    df_accidentes = load_file_accidentes(path_file_csv)
    
    # Realizar análisis exploratorio
    analisis_exploratorio(df_accidentes)
    
    # Limpiar y ajustar datos
    df_depurado = ajustar_datos(df_accidentes)
    
    # Realizar análisis de series temporales
    analisis_series_temporales(df_depurado)
    
    # Ajustar datos y crear gráficos
    ajustar_y_graficar(df_depurado)
    
    # Generar gráfico de barras apiladas para Clase_accidente y Gravedad
    graficar_barras_agrupadas(df_depurado)

#primera version