import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Pescados Medina", page_icon="🐟", layout="centered")

st.title("🐟 Pescados Medina - Control de Caja")

# --- CONEXIÓN DIRECTA A GOOGLE SHEETS ---
# Usamos el conector nativo de Streamlit
try:
    conn = st.connection("gsheets", type="gsheets")
    
    # Leemos las pestañas de tu Google Sheet (asegúrate de que se llaman exactamente así)
    df_compras = conn.read(worksheet="compras", ttl=0)
    df_ventas = conn.read(worksheet="ventas", ttl=0)
    
    # Limpiamos posibles filas vacías que lea Google Sheets
    df_compras = df_compras.dropna(how="all")
    df_ventas = df_ventas.dropna(how="all")
    
    # Aseguramos columnas por si la hoja está vacía al principio
    if df_compras.empty:
        df_compras = pd.DataFrame(columns=["Fecha", "Insumo", "Precio", "Unidades", "Total"])
    if df_ventas.empty:
        df_ventas = pd.DataFrame(columns=["Fecha", "Producto", "Precio", "Unidades", "Total"])

except Exception as e:
    st.error(f"Error al conectar con Google Sheets. Revisa los secretos de Streamlit. Detalle: {e}")
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
            
            # Preparamos la nueva fila
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha_actual,
                "Insumo": insumo,
                "Precio": precio,
                "Unidades": unidades,
                "Total": total_gasto
            }])
            
            # Añadimos la fila al DataFrame existente y actualizamos Google Sheets
            df_actualizado = pd.concat([df_compras, nueva_fila], ignore_index=True)
            conn.update(worksheet="compras", data=df_actualizado)
            
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
            
            # Preparamos la nueva fila
            nueva_fila_v = pd.DataFrame([{
                "Fecha": fecha_actual,
                "Producto": producto,
                "Precio": precio_v,
                "Unidades": unidades_v,
                "Total": total_ingreso
            }])
            
            # Añadimos la fila al DataFrame existente y actualizamos Google Sheets
            df_ventas_actualizado = pd.concat([df_ventas, nueva_fila_v], ignore_index=True)
            conn.update(worksheet="ventas", data=df_ventas_actualizado)
            
            st.success(f"¡Venta de {producto} registrada en tu Google Sheet! Total: {total_ingreso:.2f} €")
            st.rerun()

# --- SECCIÓN 4: VER REGISTROS ---
elif menu == "Ver Registros":
    st.header("📋 Historial de Movimientos")
    
    st.subheader("Compras realizadas")
    st.dataframe(df_compras)
    
    st.subheader("Ventas realizadas")
    st.dataframe(df_ventas)
