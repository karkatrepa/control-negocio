import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Control de Negocio", page_icon="🐟", layout="centered")

st.title("🐟 Pescados Medina - Control de Caja")

# Simulación de base de datos local con archivos CSV (o puedes conectarlo a tu Excel)
# Si no existen los archivos, los creamos vacíos
try:
    df_compras = pd.read_csv("compras.csv")
except FileNotFoundError:
    df_compras = pd.DataFrame(columns=["Fecha", "Insumo", "Precio", "Unidades", "Total"])

try:
    df_ventas = pd.read_csv("ventas.csv")
except FileNotFoundError:
    df_ventas = pd.DataFrame(columns=["Fecha", "Producto", "Precio", "Unidades", "Total"])

# Menú lateral para navegar entre secciones
menu = st.sidebar.selectbox("Menú", ["Resumen", "Registrar Compra", "Registrar Venta", "Ver Registros"])

# --- SECCIÓN 1: RESUMEN GLOBAL ---
if menu == "Resumen":
    st.header("📊 Resumen del Negocio")
    
    total_compras = df_compras["Total"].sum() if not df_compras.empty else 0.0
    total_ventas = df_ventas["Total"].sum() if not df_ventas.empty else 0.0
    beneficio_neto = total_ventas - total_compras
    
    # Mostramos métricas visuales limpias
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Totales", f"{total_ventas:.2f} €")
    col2.metric("Gastos Compras", f"{total_compras:.2f} €")
    col3.metric("Beneficio Neto", f"{beneficio_neto:.2f} €", delta=f"{beneficio_neto:.2f} €")

# --- SECCIÓN 2: REGISTRAR COMPRA ---
elif menu == "Registrar Compra":
    st.header("📥 Registrar Nueva Compra")
    
    with st.form("form_compra"):
        insumo = st.text_input("Nombre del Insumo / Producto (ej. Caja Boquerón)")
        precio = st.number_input("Precio por unidad (€)", min_value=0.0, step=0.5)
        unidades = st.number_input("Unidades / Cantidad", min_value=1, step=1)
        
        submitted = st.form_submit_button("Guardar Compra")
        
        if submitted and insumo:
            total_gasto = precio * unidades
            nueva_fila = pd.DataFrame({
                "Fecha": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                "Insumo": [insumo],
                "Precio": [precio],
                "Unidades": [unidades],
                "Total": [total_gasto]
            })
            df_compras = pd.concat([df_compras, nueva_fila], ignore_index=True)
            df_compras.to_csv("compras.csv", index=False)
            st.success(f"¡Compra de {insumo} guardada correctamente! Total: {total_gasto:.2f} €")

# --- SECCIÓN 3: REGISTRAR VENTA ---
elif menu == "Registrar Venta":
    st.header("📤 Registrar Nueva Venta")
    
    with st.form("form_venta"):
        producto = st.text_input("Producto vendido (ej. Tarrina Boquerón)")
        precio_v = st.number_input("Precio de venta (€)", min_value=0.0, step=0.5)
        unidades_v = st.number_input("Cantidad vendida", min_value=1, step=1)
        
        submitted_v = st.form_submit_button("Guardar Venta")
        
        if submitted_v and producto:
            total_ingreso = precio_v * unidades_v
            nueva_fila_v = pd.DataFrame({
                "Fecha": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                "Producto": [producto],
                "Precio": [precio_v],
                "Unidades": [unidades_v],
                "Total": [total_ingreso]
            })
            df_ventas = pd.concat([df_ventas, nueva_fila_v], ignore_index=True)
            df_ventas.to_csv("ventas.csv", index=False)
            st.success(f"¡Venta de {producto} registrada! Total: {total_ingreso:.2f} €")

# --- SECCIÓN 4: VER REGISTROS ---
elif menu == "Ver Registros":
    st.header("📋 Historial de Movimientos")
    
    st.subheader("Compras realizadas")
    st.dataframe(df_compras)
    
    st.subheader("Ventas realizadas")
    st.dataframe(df_ventas)