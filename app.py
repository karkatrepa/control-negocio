import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de la página
st.set_page_config(page_title="Pescados Medina", page_icon="🐟", layout="centered")

st.title("🐟 Pescados Medina - Control de Caja")

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_google_sheets():
    # Usaremos los secretos seguros de Streamlit para las credenciales
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Esto leerá las credenciales de los secretos de Streamlit Cloud
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Nombre de tu archivo de Google Sheets
    spreadsheet = client.open("ControlNegocioPescados") # Asegúrate de que tu hoja se llama así o cambia el nombre aquí
    return spreadsheet

try:
    sh = conectar_google_sheets()
    # Conectamos con las pestañas "compras" y "ventas" de tu Google Sheet
    sheet_compras = sh.worksheet("compras")
    sheet_ventas = sh.worksheet("ventas")
    
    # Leemos los datos en formato DataFrame
    data_compras = sheet_compras.get_all_records()
    data_ventas = sheet_ventas.get_all_records()
    
    df_compras = pd.DataFrame(data_compras)
    df_ventas = pd.DataFrame(data_ventas)
    
    # Por si las hojas están vacías al principio, aseguramos las columnas
    if df_compras.empty:
        df_compras = pd.DataFrame(columns=["Fecha", "Insumo", "Precio", "Unidades", "Total"])
    if df_ventas.empty:
        df_ventas = pd.DataFrame(columns=["Fecha", "Producto", "Precio", "Unidades", "Total"])

except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# Menú lateral
menu = st.sidebar.selectbox("Menú", ["Resumen", "Registrar Compra", "Registrar Venta", "Ver Registros"])

# --- SECCIÓN 1: RESUMEN GLOBAL ---
if menu == "Resumen":
    st.header("📊 Resumen del Negocio")
    
    total_compras = pd.to_numeric(df_compras["Total"]).sum() if not df_compras.empty and "Total" in df_compras else 0.0
    total_ventas = pd.to_numeric(df_ventas["Total"]).sum() if not df_ventas.empty and "Total" in df_ventas else 0.0
    beneficio_neto = total_ventas - total_compras
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Totales", f"{total_ventas:.2f} €")
    col2.metric("Gastos Compras", f"{total_compras:.2f} €")
    col3.metric("Beneficio Neto", f"{beneficio_neto:.2f} €", delta=f"{beneficio_neto:.2f} €")

# --- SECCIÓN 2: REGISTRAR COMPRA ---
elif menu == "Registrar Compra":
    st.header("📥 Registrar Nueva Compra")
    
    with st.form("form_compra"):
        insumo = st.text_input("Nombre del Insumo / Producto")
        precio = st.number_input("Precio por unidad (€)", min_value=0.0, step=0.5)
        unidades = st.number_input("Unidades / Cantidad", min_value=1, step=1)
        
        submitted = st.form_submit_button("Guardar Compra en Google Sheets")
        
        if submitted and insumo:
            total_gasto = precio * unidades
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Añadimos la fila directamente a la hoja de Google Sheets
            sheet_compras.append_row([fecha_actual, insumo, precio, unidades, total_gasto])
            st.success(f"¡Compra de {insumo} guardada en tu Google Sheet! Total: {total_gasto:.2f} €")
            st.rerun()

# --- SECCIÓN 3: REGISTRAR VENTA ---
elif menu == "Registrar Venta":
    st.header("📤 Registrar Nueva Venta")
    
    with st.form("form_venta"):
        producto = st.text_input("Producto vendido")
        precio_v = st.number_input("Precio de venta (€)", min_value=0.0, step=0.5)
        unidades_v = st.number_input("Cantidad vendida", min_value=1, step=1)
        
        submitted_v = st.form_submit_button("Guardar Venta en Google Sheets")
        
        if submitted_v and producto:
            total_ingreso = precio_v * unidades_v
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Añadimos la fila directamente a la hoja de Google Sheets
            sheet_ventas.append_row([fecha_actual, producto, precio_v, unidades_v, total_ingreso])
            st.success(f"¡Venta de {producto} registrada en tu Google Sheet! Total: {total_ingreso:.2f} €")
            st.rerun()

# --- SECCIÓN 4: VER REGISTROS ---
elif menu == "Ver Registros":
    st.header("📋 Historial de Movimientos")
    
    st.subheader("Compras realizadas")
    st.dataframe(df_compras)
    
    st.subheader("Ventas realizadas")
    st.dataframe(df_ventas)
