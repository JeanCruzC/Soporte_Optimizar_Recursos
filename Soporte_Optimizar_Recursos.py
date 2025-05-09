import streamlit as st
import pandas as pd
import numpy as np
import math
import re
from io import BytesIO

st.set_page_config(page_title="Detalle Programación", layout="wide")
st.title("📋 Detalle de Programación: Jornada y Break")

# === Parámetros y carga de archivo ===
st.sidebar.header("Carga de archivo")
uploader = st.sidebar.file_uploader("Sube Detalle_Programacion.xlsx", type=["xlsx"])
if not uploader:
    st.info("Por favor, sube el archivo de programación.")
    st.stop()

# === Turnos coverage (pega aquí tu diccionario) ===
# 2. DEFINICIÓN DE TURNOS ---------------------------------------
shifts_coverage = {
    # ----------------------------------------------------------
    # TURNOS FULL‑TIME 8H
    # ----------------------------------------------------------
    "FT_00:00_1":[1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_00:00_2":[1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_00:00_3":[1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_01:00_1":[0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_01:00_2":[0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_01:00_3":[0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_02:00_1":[0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_02:00_2":[0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_02:00_3":[0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_03:00_1":[0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_03:00_2":[0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_03:00_3":[0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    "FT_04:00_1":[0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
    "FT_04:00_2":[0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
    "FT_04:00_3":[0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
    "FT_05:00_1":[0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
    "FT_05:00_2":[0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
    "FT_05:00_3":[0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0],
    "FT_06:00_1":[0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
    "FT_06:00_2":[0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0],
    "FT_06:00_3":[0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0],
    "FT_07:00_1":[0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0],
    "FT_07:00_2":[0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0],
    "FT_07:00_3":[0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0],
    "FT_08:00_1":[0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0],
    "FT_08:00_2":[0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0],
    "FT_08:00_3":[0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0],
    "FT_09:00_1":[0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0],
    "FT_09:00_2":[0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0],
    "FT_09:00_3":[0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0],
    "FT_10:00_1":[0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0],
    "FT_10:00_2":[0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0],
    "FT_10:00_3":[0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,0],
    "FT_11:00_1":[0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0,0],
    "FT_11:00_2":[0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0],
    "FT_11:00_3":[0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0],
    "FT_12:00_1":[0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0,0],
    "FT_12:00_2":[0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0],
    "FT_12:00_3":[0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0,0],
    "FT_13:00_1":[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0,0],
    "FT_13:00_2":[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0],
    "FT_13:00_3":[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0,0],
    "FT_14:00_1":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,0],
    "FT_14:00_2":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,0],
    "FT_14:00_3":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0],
    "FT_15:00_1":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1],
    "FT_15:00_2":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1],
    "FT_15:00_3":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1],
    "FT_16:00_1":[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1],
    "FT_16:00_2":[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1],
    "FT_16:00_3":[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1],
    "FT_17:00_1":[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1],
    "FT_17:00_2":[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1],
    "FT_17:00_3":[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1],
    "FT_18:00_1":[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1],
    "FT_18:00_2":[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1],
    "FT_18:00_3":[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1],
    "FT_19:00_1":[1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1],
    "FT_19:00_2":[1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1],
    "FT_19:00_3":[0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1],
    "FT_20:00_1":[1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
    "FT_20:00_2":[0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
    "FT_20:00_3":[1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
    "FT_21:00_1":[0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    "FT_21:00_2":[1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    "FT_21:00_3":[1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    "FT_22:00_1":[1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
    "FT_22:00_2":[1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
    "FT_22:00_3":[1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
    "FT_23:00_1":[1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    "FT_23:00_2":[1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    "FT_23:00_3":[1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],

    # ----------------------------------------------------------
    # TURNOS PART‑TIME 4H
    # ----------------------------------------------------------
    "00_4":[1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "01_4":[0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "02_4":[0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "03_4":[0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "04_4":[0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "05_4":[0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "06_4":[0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "07_4":[0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "08_4":[0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
    "09_4":[0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
    "10_4":[0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
    "11_4":[0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0],
    "12_4":[0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0],
    "13_4":[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0],
    "14_4":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],
    "15_4":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0],
    "16_4":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0],
    "17_4":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0],
    "18_4":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0],
    "19_4":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0],
    "20_4":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
    "21_4":[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    "22_4":[1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
    "23_4":[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
}

dias_semana = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']

# === Función de detalle de shift ===
def get_shift_details(shift_name):
    cov = shifts_coverage.get(shift_name, [0]*24)
    total_ones = sum(cov)
    if total_ones == 0:
        return '-', '-'
    ext = cov + cov
    best = None
    for start in range(24):
        ones = 0
        for end in range(start, start + 24):
            if ext[end] == 1:
                ones += 1
            if ones == total_ones:
                length = end - start + 1
                if best is None or length < best[0]:
                    best = (length, start)
                break
    length, start_idx = best
    start_hour = start_idx % 24
    end_hour = (start_idx + length) % 24
    jornada = f"{start_hour:02d}:00-{end_hour:02d}:00"
    # detectar break
    break_time = '-'
    for i in range(start_idx, start_idx + length - 2):
        if ext[i] == 1 and ext[i+1] == 0 and ext[i+2] == 1:
            gap = (i + 1) % 24
            break_time = f"{gap:02d}:00-{(gap+1)%24:02d}:00"
            break
    return jornada, break_time

# === Procesamiento de datos ===
try:
    df = pd.read_excel(uploader)
except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
    st.stop()

# Normalizar part-time
df['Horario'] = df['Horario'].str.replace(r"(.*?_4)_\d+$", r"\1", regex=True)

# Validar columnas
required_cols = {'Nombre','Día','Horario','Refrig'}
if not required_cols.issubset(df.columns):
    st.error(f"Columnas faltantes: {required_cols - set(df.columns)}")
    st.stop()

# Calcular Jornada y Break
detalles = df['Horario'].apply(lambda s: pd.Series(get_shift_details(s), index=['Jornada','Break']))
result = pd.concat([df, detalles], axis=1)

# Reemplazar 24:00
result['Jornada'] = result['Jornada'].str.replace('24:00','00:00')

# Mostrar tabla
st.dataframe(result)

# Descargar Excel
buf = BytesIO()
with pd.ExcelWriter(buf, engine='openpyxl') as writer:
    result.to_excel(writer, index=False)
buf.seek(0)
st.download_button(
    label="📥 Descargar Detalle_Programacion_Final.xlsx",
    data=buf,
    file_name="Detalle_Programacion_Final.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
