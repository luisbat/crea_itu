import configparser

def crea_cabecera(config,nombre_archivo:str):
    cabecera_str=""
    cabecera_str += f"* {nombre_archivo.upper()}\n"
    cabecera_str += f"* FORMAT    {config['itu']['format']}\n"
    cabecera_str += f"* LAB       {config['itu']['lab']}\n"
    cabecera_str += f"* REV DATE  {config['itu']['rev_date']}\n"

    

    cabecera_str += f"* \n"
    cabecera_str += "* EARTH-STAT  LI  MJD  STTIME NTL        TW        DRMS SMP ATL     REFDELAY     RSIG  CI S    CALR     ESDVAR   ESIG TMP HUM PRES\n"
    cabecera_str += "* LOC    REM           hhmmss  s         s          ns       s         s          ns            ns        ns      ns degC  %  mbar"
    print(cabecera_str)
