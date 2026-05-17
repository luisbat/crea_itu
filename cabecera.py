import configparser

def crea_cabecera(config,nombre_archivo:str):
    cabecera_str=""
    cabecera_str += f"* {nombre_archivo.upper()}"
    cabecera_str += config.get("cabecera", "texto")
    

    cabecera_str += "\n"
    cabecera_str += "* EARTH-STAT  LI  MJD  STTIME NTL        TW        DRMS SMP ATL     REFDELAY     RSIG  CI S    CALR     ESDVAR   ESIG TMP HUM PRES\n"
    cabecera_str += "* LOC    REM           hhmmss  s         s          ns       s         s          ns            ns        ns      ns degC  %  mbar\n"
    return(cabecera_str)
