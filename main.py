import streamlit as st
import pandas as pd

# Configuración de la página para móvil
st.set_page_config(page_title="Prediseño de Vigas", layout="centered")

st.title("🏗️ Predimensionamiento de Vigas HA")
st.write("Herramienta educativa para el cálculo de vigas de hormigón armado.")

# --- PASO 1: DATOS GEOMÉTRICOS ---
st.header("Paso 1: Datos Geométricos")
L = st.number_input("Longitud de la viga L (m)", min_value=1.0, value=5.0, step=0.1)
b = st.number_input("Ancho de la viga b (m)", min_value=0.2, value=0.3, step=0.05)
if st.button ("ℹ️ ¿Que ancho de viga consideramos?"):
    st.markdown("""Se suele elegir un ancho de viga igual a la dimensión del pilar al que entrega. """)
    
f_lim = (L * 100) / 500
st.info(f"Flecha máxima permitida ($f < L/500$): **{f_lim:.2f} cm**")

if st.button("ℹ️ ¿Por qué limitamos la flecha?"):
    st.markdown("""**ELU vs ELS**: El dimensionado por flecha es un Estado Límite de Servicio (ELS). 
    Estado límite último ELU se enfoca en al seguridad y la prevención del colapso o rotura bajo cargas extremas. 
    Estado límite de servicio ELS asegura que la estructura sea funcional durante su uso normal, limitando aspectos como vibraciones, flecha o fisuración
    ELS por flecha: Protege la funcionalidad y la estética. Una viga que se comba en exceso puede agrietar tabiques o causar inseguridad visual.""")

# --- PASO 2: TIPO DE APOYO ---
st.divider()
st.header("Paso 2: Tipo de Apoyo")

if st.button("ℹ️ ¿Qué tipo de apoyo consideramos?"):
    st.markdown("""**Apoyo vs Empotramiento**
    La distinción entre apoyo y empotramiento en un pórtico de hormigón depende de la rigidez relativa entre ambos: 
    se considera un empotramiento cuando la sección del pilar es lo suficientemente grande frente al canto de la viga para impedir el giro del nudo, 
    permitiendo que el pilar "absorba" los momentos flectores de la viga. 
    Por el contrario, si el canto de la viga es muy grande en relación con una sección de pilar reducida, el pilar no tiene capacidad para restringir la rotación de la viga y el nudo se comporta como un apoyo, ya que el pilar simplemente girará junto con el extremo de la viga sin oponer resistencia significativa. 
    En la práctica, esto se traduce en que un pilar robusto "sujeta" la viga (empotramiento), mientras que un pilar esbelto solo la "sostiene" (apoyo).
    Para una viga biapoyada se suele predimensionar un canto L/14 y para una viga biempotrada L/22.""")
    
h_max = L / 14
h_min = L / 22
st.write(f"Rango de canto estimado: **{h_min:.2f} m** (rígido) a **{h_max:.2f} m** (flexible)")

tipo_viga = st.selectbox("Selecciona el modelo estático:", 
    ["Biapoyada", "Biempotrada", "Apoyo-Empotramiento", "Voladizo", "Continua"])

# Diccionario de coeficientes para Momento e Inercia (simplificado para el ejemplo)
coefs = {
    "Biapoyada": {"km": 1/8, "kf": 5/384},
    "Biempotrada": {"km": 1/12, "kf": 1/384},
    "Apoyo-Empotramiento": {"km": 1/8, "kf": 1/185},
    "Voladizo": {"km": 1/2, "kf": 1/8},
    "Continua": {"km": 0.7 * (1/8), "kf": 1/200} # Ejemplo simplificado
}

# --- PASO 3: CARGAS ---
st.divider()
st.header("Paso 3: Definición de Cargas")
g_forjado = st.number_input("Peso forjado (kN/m²)", value=4.0)
g_solado = 1.0
g_tabique = 1.0
ancho_trib = st.number_input("Ancho tributario A (m)", value=4.0)

uso_val = st.selectbox("Sobrecarga de uso (kN/m²):", [2.0, 3.0, 4.0, 5.0], help="Residencial=2, Oficinas=3, Pública=5")

qd = ((g_forjado + g_solado + g_tabique) * 1.35 + uso_val * 1.50) * ancho_trib
st.success(f"Carga lineal de diseño ($q_d$): **{qd:.2f} kN/ml**")

# --- PASO 4: MATERIALES ---
st.divider()
st.header("Paso 4: Materiales")
fck = st.selectbox("Hormigón (fck)", [25, 30, 35])
fyk = st.selectbox("Acero (fyk)", [400, 500])

fcd = fck / 1.5
fyd = fyk / 1.15

# --- PASO 5: RESULTADOS Y ARMADO ---
st.divider()
st.header("Paso 5: Resultados")

h_final = st.slider("Ajusta el canto final de la viga h (m)", min_value=0.2, max_value=1.0, value=float(round(h_max,2)), step=0.05)
ambiente = st.radio("Ambiente:", ["Desconocido (d=0.9h)", "XC1 (Interiores)", "XC3 (Exteriores)"])

if ambiente == "Desconocido (d=0.9h)":
    d = 0.9 * h_final
else:
    r = 0.03 # 3cm por defecto para el ejemplo
    d = h_final - (2 * r)

z = 0.9 * d
Md = coefs[tipo_viga]["km"] * qd * (L**2)
T = Md / z
As = (T / (fyd / 10)) # Conversión a cm2 aproximada

st.metric("Sección de Acero necesaria (As)", f"{As:.2f} cm²")

st.write("🔎 **Consulta la tabla de armaduras para elegir tus barras:**")
# Aquí se mostraría la imagen 'armadura.png'
st.info("Ejemplo: Si As = 6.03 cm², podrías usar 3 barras del Ø16.")
import numpy as np
import pandas as pd

def recomendar_armado(as_necesario, ancho_viga_m):
    # 1. Definimos los diámetros comerciales (mm)
    diametros = [8, 10, 12, 16, 20, 25] # Editado para simplificar, puedes añadir todos
    ancho_viga_mm = ancho_viga_m * 1000
    recubrimiento_lateral = 30 # mm
    espacio_libre_min = 25 # mm
    
    recomendaciones = []

    for phi in diametros:
        area_una_barra = (np.pi * (phi/10)**2) / 4 # cm2
        
        # Calculamos cuántas barras necesitamos para cubrir el área
        n_barras = int(np.ceil(as_necesario / area_una_barra))
        
        # Filtro 1: Mínimo 2 barras para formar la jaula
        if n_barras < 2: n_barras = 2
        
        as_provisto = n_barras * area_una_barra
        
        # Filtro 2: ¿Caben en una sola fila? 
        # Ancho ocupado = (n * phi) + (n-1)*espacio_libre + 2*recubrimiento
        ancho_necesario = (n_barras * phi) + (n_barras - 1) * espacio_libre_min + (2 * recubrimiento_lateral)
        
        if ancho_necesario <= ancho_viga_mm:
            recomendaciones.append({
                "Combinación": f"{n_barras} Ø {phi}",
                "As Provisto (cm²)": round(as_provisto, 2),
                "Exceso (%)": round(((as_provisto/as_necesario)-1)*100, 1),
                "Estatus": "✅ Cabe en 1 fila"
            })
        else:
            recomendaciones.append({
                "Combinación": f"{n_barras} Ø {phi}",
                "As Provisto (cm²)": round(as_provisto, 2),
                "Exceso (%)": round(((as_provisto/as_necesario)-1)*100, 1),
                "Estatus": "⚠️ Requiere 2 filas"
            })

    # Convertimos a DataFrame y ordenamos por la que tenga menos exceso de acero (economía)
    df_res = pd.DataFrame(recomendaciones)
    return df_res.sort_values(by="As Provisto (cm²)")

# Ejemplo de uso:
# Si necesitamos 5.2 cm2 en una viga de 30cm (0.3m)
# print(recomendar_armado(5.2, 0.3))
