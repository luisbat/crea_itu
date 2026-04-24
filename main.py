import pandas as pd
import numpy as np
import configparser
import re
from datetime import date
from cabecera import crea_cabecera


def time_to_seconds_rel(time_series):
    """
    Convierte una serie de strings 'hh:mm:ss' a segundos relativos al primer valor.
    """
    # Convertir a timedelta (si ya es datetime, usar .dt)
    t = pd.to_timedelta(time_series)
    seg_abs = t.dt.total_seconds()
    seg_rel = seg_abs - seg_abs.iloc[0]
    return seg_rel.values

def calcula_rms(y):
    media=np.sum(y)/len(y)
    suma2=np.sum(y**2)
    nm2=(media**2)*len(y)
    r=(suma2-nm2)/len(y)
    rms=np.sqrt(r)
    return media,rms

def calcula_residuos(c,x,y):
    residuos=np.array([])
    yfit=np.polyval(c,x)
    residuos=y-yfit
    return residuos

def calcula_datos(medidas_x, medidas_y):
        while True:
            coef=np.polyfit(medidas_x,medidas_y,2)
            res=calcula_residuos(coef,medidas_x,medidas_y)
            media,drms=calcula_rms(res)
            tope=drms*5.0
            borrados=0
            for i in range(len(medidas_x)):
                if (abs(res[i] - media) > tope):
                    medidas_x=np.delete(medidas_x,i)
                    medidas_y=np.delete(medidas_y,i)
                    borrados=1
                    break
            if (borrados==0):
                break;

        valor=np.polyval(coef,59.5)
        smp=len(medidas_x)
#        return valor,drms*1e9,len(medidas_x)
        return valor,drms,len(medidas_x)
    
def filas_slot(df, hora, slot_num):
    slot_start = slot_num * 180 + hora * 3600
    inicio_valido = slot_start + 60
    fin_valido = slot_start + 180   # límite superior exclusivo
    filtro = (df.iloc[:, 2] >= inicio_valido) & (df.iloc[:, 2] < fin_valido)
    comienzo_medidas = f"{hora:02d}{slot_num*3+1:02d}00"
    return df.loc[filtro],comienzo_medidas

def tiempo_a_segundos(t_str):
    h, m, s = map(int, t_str.split(':'))
    return h * 3600 + m * 60 + s

def busca_slot(slot_num):
    minuto_comienzo = slot_num * 3
    patron = re.compile(r'^Lab [A-Z0-9]{1,6}$')
    for seccion in config.sections():
        if patron.match(seccion):
            if int(config[seccion]['minuto']) == minuto_comienzo:
                minuto = int(config[seccion]['minuto'])
                return seccion
    return None

def busca_local():
    patron = re.compile(r'^Lab [A-Z0-9]{1,6}$')
    for seccion in config.sections():
        if patron.match(seccion):
            if config[seccion].getboolean('local') == True:
                return seccion
    return None

def fecha_a_mjd(fecha_str: str) -> int:
    try:
        año, mes, dia = map(int, fecha_str.split('/'))
        fecha = date(año, mes, dia)
        epoch = date(1858, 11, 17)
        mjd = (fecha - epoch).days
        return mjd
    except (ValueError, TypeError):
        raise ValueError("Formato de fecha inválido. Use 'aaaa/mm/dd'.")

def abre_ambientales(fecha_str):
    meses = {'01': 'ene',
             '02': 'feb',
             '03': 'mar',
             '04': 'abr',
             '05': 'may',
             '06': 'jun',
             '07': 'jul',
             '08': 'ago',
             '09': 'sep',
             '10': 'oct',
             '11': 'nov',
             '12': 'dic'
             }

    campos=fecha_str.split('/')
    if len(campos) != 3:
        return None
    archivo = f"./datos/{campos[2]}{meses[campos[1]]}{campos[0][2:]}.ema"
    df = pd.read_csv(archivo, sep=' ', header=None)
    return df

def recupera_ambientales(df_amb, minuto):
#    print(f"Recuperando datos ambientales del minuto {minuto}")
    anteriores = df_amb[df_amb.iloc[:, 0] <= minuto]
    if anteriores.empty:
        print("No se encontraron datos ambientales anteriores al minuto solicitado.")
        return None, None, None
    fila = anteriores.iloc[-1]      # obtenemos la última fila válida
    temperatura = round(float(fila[1]))
    humedad = int(fila[2])
    presion = round(float(fila[7]))

    return temperatura, humedad, presion


def calcula_atl(df: pd.DataFrame) -> float:
    """
    Calcula la diferencia en segundos entre el último y el primer tiempo
    de la segunda columna de un DataFrame. Los tiempos están en formato 'hh:mm:ss'.

    Parámetros:
    df (pd.DataFrame): DataFrame cuya segunda columna (índice 1) contiene
                       cadenas con formato 'hh:mm:ss'.

    Retorna:
    float: Diferencia en segundos (último - primero). Si el DataFrame está vacío,
           retorna 0.0.
    """
    if df.empty:
        return 0.0

    # Extraer la segunda columna (columna en índice 1)
    time_col = df.iloc[:, 1]

    # Convertir las cadenas a timedelta (formato hh:mm:ss)
    time_series = pd.to_timedelta(time_col)

    # Primer y último valor
    first = time_series.iloc[0]
    last = time_series.iloc[-1]

    # Diferencia en segundos
    diff_seconds = (last - first).total_seconds()
    return diff_seconds

config = configparser.ConfigParser()
config.read('twstft.ini')


with open("./datos/raw.20260411", "r") as f:
    filas = []
    for linea in f:
        if ">" in linea:
            partes = linea.split(">", 1)
            if partes[0].strip() == "%Rx1":
                parte_derecha = partes[1]
                valores = parte_derecha.strip().split(";")

                if len(valores) > 12:
                    segundos = tiempo_a_segundos(valores[1])
                    nueva_fila = [valores[0], valores[1], segundos] + valores[2:]
                    filas.append(nueva_fila)
df = pd.DataFrame(filas)
df_amb=abre_ambientales(df.iloc[0, 0])
djm = fecha_a_mjd(df.iloc[0, 0])  # fecha en la primera columna
nombre_archivo_itu = f"twroa{djm//1000}.{djm%1000}"
crea_cabecera(config,nombre_archivo_itu)
pd.set_option('display.max_rows', None)
for hora in range(0,24,2):
    for slot in range(20):
        valores_slot, comienzo = filas_slot(df, hora, slot)
        if valores_slot.empty:
#            print(f"Slot {slot}: No se encontraron datos válidos.")
            continue
        datos_slot = busca_slot(slot)
        if datos_slot is None:
            print(f"Slot {slot}: No se encontró sección correspondiente en el archivo .ini.")
            continue
#        guardar_como_texto_legible(valores_slot, f"valores_slot_{slot}.txt")

#    df_120 = valores_slot.head(120).copy()
        df_120 = valores_slot.copy()

    # 2. Extraer y convertir la columna de tiempo (columna 2, índice 1)
        tiempo_str = df_120.iloc[:, 1]   # segunda columna
        x_segundos = time_to_seconds_rel(tiempo_str)

        y_str = df_120.iloc[:, 13]       # columna 14
        y_float = pd.to_numeric(y_str, errors='coerce')  # convierte errores a NaN

    # Eliminar filas con NaN en Y (si las hay)
        mask_valid = ~np.isnan(y_float)
        x_segundos = x_segundos[mask_valid]
        y_float = y_float[mask_valid].values

        v,y_std, n_puntos = calcula_datos(x_segundos, y_float)
#        djm = fecha_a_mjd(df_120.iloc[0, 0])  # fecha en la primera columna
# 5. Resultados
# Divido la linea de salida por comodidad, para que sea más fácil de leer y modificar en el futuro
        atl=calcula_atl(df_120)
        lab_local=busca_local()
        if float(config[datos_slot]['calr']) > 999999990:
            calr=str(999999999)
        else:
            calr=f"{float(config[datos_slot]['calr']):>9.3f}"
        if float(config[datos_slot]['esdvar']) > 999999990:
            esdvar=str(999999999)
        else:
            esdvar=f"{float(config[datos_slot]['esdvar']):>9.3f}"
        if config[lab_local]['esig'] == "99999":
            esig=str(99999)
        else:
            esig=f"{float(config[lab_local]['esig']):>5.3f}"

        temperatura, humedad, presion = recupera_ambientales(df_amb,int(comienzo[0:2])*60 + int(comienzo[2:4]))

        linea_salida = f"{config[lab_local]['nombre']:>6} {config[datos_slot]['nombre']:>6} {int(config[datos_slot]['link']):2d} {djm} {comienzo} "
        linea_salida += f"{int(config['itu']['ntl']):3d} {v/1e9:+.12f} {y_std:.3f} {n_puntos:03d} {int(atl):03d} "
        linea_salida += f"{float(config[lab_local]['refdelay']):+.12f} {float(config[lab_local]['rsig']):.3f} "
        linea_salida += f"{int(config[datos_slot]['ci']):3d} {int(config[datos_slot]['sw']):1d} {calr} {esdvar} {esig}"
        linea_salida += f" {int(temperatura):3d} {int(humedad):3d} {int(presion):2d}"

        print(linea_salida)


