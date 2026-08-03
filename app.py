import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# Configuración de la página
st.set_page_config(page_title="Pescados Medina", page_icon="🐟", layout="centered")

st.title("🐟 Pescados Medina - Control Total")

# --- CONEXIÓN A BASE DE DATOS LOCAL ---
def init_db():
    conn = sqlite3.connect('negocio.db', check_same_thread=False)
    c = conn.cursor()
    # Tablas de caja (no se borran gracias al IF NOT EXISTS)
    c.execute('''CREATE TABLE IF NOT EXISTS compras (fecha TEXT, insumo TEXT, precio REAL, unidades INTEGER, total REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (fecha TEXT, producto TEXT, precio REAL, unidades INTEGER, total REAL)''')
    # NUEVA: Tabla de temperaturas diarias
    c.execute('''CREATE TABLE IF NOT EXISTS temperaturas (fecha TEXT, equipo TEXT, grados REAL)''')
    conn.commit()
    return conn

conn = init_db()

# Cargar datos en DataFrames
df_compras = pd.read_sql("SELECT * FROM compras", conn)
df_ventas = pd.read_sql("SELECT * FROM ventas", conn)
df_temp = pd.read_sql("SELECT * FROM temperaturas", conn)

# Menú lateral ampliado
menu = st.sidebar.selectbox("Menú", ["Resumen", "Registrar Compra", "Registrar Venta", "Control de Temperaturas", "Ver Registros"])

# --- SECCIÓN 1: RESUMEN GLOBAL ---
if menu == "Resumen":
    st.header("📊 Resumen del Negocio")
    
    total_compras = df_compras["total"].sum() if not df_compras.empty else 0.0
    total_ventas = df_ventas["total"].sum() if not df_ventas.empty else 0.0
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
        submitted = st.form_submit_button("Guardar Compra")
        
        if submitted and insumo:
            total_gasto = precio * unidades
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            c = conn.cursor()
            c.execute("INSERT INTO compras VALUES (?, ?, ?, ?, ?)", (fecha_actual, insumo, precio, unidades, total_gasto))
            conn.commit()
            st.success(f"¡Compra de {insumo} guardada! Total: {total_gasto:.2f} €")
            st.rerun()

# --- SECCIÓN 3: REGISTRAR VENTA ---
elif menu == "Registrar Venta":
    st.header("📤 Registrar Nueva Venta")
    with st.form("form_venta"):
        producto = st.text_input("Producto vendido")
        precio_v = st.number_input("Precio de venta (€)", min_value=0.0, step=0.5)
        unidades_v = st.number_input("Cantidad vendida", min_value=1, step=1)
        submitted_v = st.form_submit_button("Guardar Venta")
        
        if submitted_v and producto:
            total_ingreso = precio_v * unidades_v
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            c = conn.cursor()
            c.execute("INSERT INTO ventas VALUES (?, ?, ?, ?, ?)", (fecha_actual, producto, precio_v, unidades_v, total_ingreso))
            conn.commit()
            st.success(f"¡Venta de {producto} registrada! Total: {total_ingreso:.2f} €")
            st.rerun()

# --- SECCIÓN 4: CONTROL DE TEMPERATURAS ---
elif menu == "Control de Temperaturas":
    st.header("❄️ Registro Diario de Cámaras")
    
    with st.form("form_temp"):
        equipo = st.selectbox("Selecciona la cámara", ["Nevera", "Congelador", "Mostrador"])
        grados = st.number_input("Temperatura actual (ºC)", value=2.0, step=0.5)
        submitted_t = st.form_submit_button("Guardar Temperatura")
        
        if submitted_t:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            c = conn.cursor()
            c.execute("INSERT INTO temperaturas VALUES (?, ?, ?)", (fecha_actual, equipo, grados))
            conn.commit()
            st.success(f"¡Registro guardado! {equipo} está a {grados}ºC")
            st.rerun()
            
    st.subheader("Últimos registros de temperatura")
    st.dataframe(df_temp)

# --- SECCIÓN 5: VER REGISTROS Y DESCARGA ---
elif menu == "Ver Registros":
    st.header("📋 Historial de Movimientos y Copia de Seguridad")
    
    st.subheader("Compras realizadas")
    st.dataframe(df_compras)
    
    st.subheader("Ventas realizadas")
    st.dataframe(df_ventas)
    
    st.markdown("---")
    st.subheader("🛠️ Corregir o Reiniciar Registros")
    
    if not df_ventas.empty:
        if st.button("🗑️ Borrar última venta registrada"):
            c = conn.cursor()
            c.execute("DELETE FROM ventas WHERE rowid = (SELECT MAX(rowid) FROM ventas)")
            conn.commit()
            st.warning("Se ha borrado la última venta registrada.")
            st.rerun()

    if not df_compras.empty:
        if st.button("🗑️ Borrar última compra registrada"):
            c = conn.cursor()
            c.execute("DELETE FROM compras WHERE rowid = (SELECT MAX(rowid) FROM compras)")
            conn.commit()
            st.warning("Se ha borrado la última compra registrada.")
            st.rerun()
            
    if not df_temp.empty:
        if st.button("🗑️ Borrar última temperatura registrada"):
            c = conn.cursor()
            c.execute("DELETE FROM temperaturas WHERE rowid = (SELECT MAX(rowid) FROM temperaturas)")
            conn.commit()
            st.warning("Se ha borrado el último registro de temperatura.")
            st.rerun()

    st.markdown("---")
    if st.checkbox("⚠️ Activar opción de borrado total"):
        if st.button("🔴 Borrar absolutamente todo y empezar de cero"):
            c = conn.cursor()
            c.execute("DELETE FROM compras")
            c.execute("DELETE FROM ventas")
            c.execute("DELETE FROM temperaturas")
            conn.commit()
            st.success("Se han borrado todos los registros. La base de datos está limpia.")
            st.rerun()

    st.markdown("---")
    st.subheader("💾 Copias de Seguridad")
    
    col1, col2, col3 = st.columns(3)
    
    if not df_compras.empty:
        csv_compras = df_compras.to_csv(index=False).encode('utf-8')
        col1.download_button("📥 Compras (CSV)", csv_compras, "compras.csv", "text/csv")
        
    if not df_ventas.empty:
        csv_ventas = df_ventas.to_csv(index=False).encode('utf-8')
        col2.download_button("📤 Ventas (CSV)", csv_ventas, "ventas.csv", "text/csv")
        
    if not df_temp.empty:
        csv_temp = df_temp.to_csv(index=False).encode('utf-8')
        col3.download_button("❄️ Temperaturas (CSV)", csv_temp, "temperaturas.csv", "text/csv")
