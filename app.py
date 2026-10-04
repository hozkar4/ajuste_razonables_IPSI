import os
import streamlit as st
from google import genai
import io
from docx import Document

st.set_page_config(
    page_title="Banco de Ajustes Razonables - I.PS.I.",
    page_icon="🧠",
    layout="wide",
)

# Escudo del IPSI
if os.path.exists("logo_ipsi.jpg"):
    st.sidebar.image("logo_ipsi.jpg", use_container_width=True)

st.sidebar.markdown("### 🏫 Instituto Psicopedagógico Integral")
st.sidebar.markdown("**Banco Dinámico de Ajustes Razonables (IA)**")
st.sidebar.markdown("---")
st.sidebar.caption("Powered by Hózkar")

# Input para la API key en el panel lateral
api_key = st.sidebar.text_input("🔑 Tu clave API de Gemini:", type="password", help="Pega aquí tu clave API. Puedes obtenerla en Google AI Studio.")
st.sidebar.markdown("[Obtener clave API gratuita aquí](https://aistudio.google.com/app/apikey)")
st.sidebar.markdown("---")

@st.cache_data
def cargar_opciones_base():
    import pandas as pd
    try:
        file_diag = "listado_de_trastornos_y_deficits_escolares_con_definicion_IPSI_2026.xlsx"
        file_asig = "listado_asignaturas_2026_IPSI.xlsx"
        df_diag_raw = pd.read_excel(file_diag, header=None)
        df_asig_raw = pd.read_excel(file_asig, header=None)
        return df_diag_raw, df_asig_raw
    except Exception as e:
        return None, None

df_diag_raw, df_asig_raw = cargar_opciones_base()

st.title("🧩 Banco Dinámico de Ajustes Razonables y Actividades Sugeridas - I.PS.I.")
st.write("Esta herramienta interactúa en tiempo real con inteligencia artificial para generar planes de apoyo psicopedagógico únicos y contextualizados.")

if df_diag_raw is None or df_asig_raw is None:
    st.error("⚠️ No se encontraron los archivos de Excel.")
else:
    cursos = ["TR"] + [f"{i}°" for i in range(1, 12)]
    edades = list(range(4, 20))
    generos = ["Masculino", "Femenino"]
    lista_asignaturas = df_asig_raw.iloc[:, 0].dropna().tolist()

    dict_diagnosticos = dict(zip(df_diag_raw.iloc[:, 0].dropna(), df_diag_raw.iloc[:, 1].fillna("Sin descripción disponible.")))
    
    # Agregar la opción de "Sin diagnóstico"
    opciones_diagnostico = ["Ninguno (Sin diagnóstico)"] + list(dict_diagnosticos.keys())
    dict_diagnosticos["Ninguno (Sin diagnóstico)"] = "Estudiante sin un diagnóstico clínico específico."

    with st.form("form_dinamico_ipsi"):
        st.subheader("📋 Parámetros del Caso")
        col1, col2 = st.columns(2)
        with col1:
            curso_sel = st.selectbox("1. CURSO * (Obligatorio)", cursos)
            edad_sel = st.selectbox("2. EDAD * (Obligatorio)", edades)
            genero_sel = st.selectbox("3. GÉNERO * (Obligatorio)", generos)
        with col2:
            asignatura_sel = st.selectbox("4. ASIGNATURA * (Obligatorio)", lista_asignaturas)
            # Usar un contenedor con altura fija para no ocupar toda la pantalla
            st.markdown("**5. DIAGNÓSTICO(S) * (Obligatorio)**")
            st.caption("💡 *Pase el cursor sobre los nombres para visualizar su definición.*")
            
            diagnosticos_sel = []
            
            with st.container(height=250):
                for diag in opciones_diagnostico:
                    definicion = dict_diagnosticos[diag]
                    if st.checkbox(diag, help=f"Definición: {definicion}"):
                        diagnosticos_sel.append(diag)
            
            st.markdown("---")
            tema_sel = st.text_input("6. TEMA (Opcional - Escriba el tema específico de la clase)")
        
        submitted = st.form_submit_button("✨ Generar Propuesta Inteligente con Gemini")

    if submitted:
        if not api_key:
            st.error("❌ ERROR: Para poder generar la propuesta, debes pegar tu **Clave API de Gemini** en el panel lateral izquierdo.")
        elif not diagnosticos_sel:
            st.warning("⚠️ Por favor, seleccione al menos un diagnóstico (puede elegir 'Ninguno').")
        else:
            with st.spinner("🤖 La IA está analizando el caso y estructurando los ajustes razonables para el I.PS.I..."):
                prompt_sistema = f"""
Eres un asesor experto en psicopedagogía e inclusión escolar del Instituto Psicopedagógico Integral (I.PS.I.) de Bogotá.
Tu tarea es generar un plan de apoyo pedagógico detallado, claro y aterrizado al aula de clase para un estudiante con los siguientes parámetros:
- Curso: {curso_sel}
- Edad: {edad_sel} años
- Género: {genero_sel}
- Asignatura: {asignatura_sel}
- Diagnóstico(s): {', '.join(diagnosticos_sel)}
- Tema específico de la clase: {tema_sel if tema_sel else 'No especificado (desarrollar de forma general para la asignatura)'}

Por favor, estructura tu respuesta en las siguientes secciones con lenguaje profesional pero accesible para los docentes:
1. 🛠️ **Sugerencias de Ajustes Razonables** (metodología, apoyos visuales, adaptaciones en tiempos y entorno de aula).
2. 💡 **Actividades Prácticas Sugeridas** (ejercicios concretos y aplicables en la clase de {asignatura_sel}).
3. 📌 **Recomendaciones Clave** (pautas para el docente y articulación con la familia).

Al final de tu respuesta, cierra obligatoriamente con el siguiente crédito exacto:
"BANCO DE AJUSTES RAZONABLES — I.PS.I. | Powered by Hózkar"
"""
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt_sistema,
                    )
                    
                    st.success("¡Plan generado exitosamente por la IA!")
                    
                    # Mostrar el resultado dentro de un contenedor visualmente atractivo
                    st.info("💡 **A continuación se muestra el plan. Puedes copiar el texto directamente o descargarlo usando los botones de abajo.**")
                    st.markdown(response.text)
                    
                    st.markdown("---")
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        st.download_button(
                            label="📥 Descargar como Archivo de Texto (.txt)",
                            data=response.text,
                            file_name=f"Ajustes_{curso_sel}_{asignatura_sel}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                    with col_btn2:
                        doc = Document()
                        doc.add_heading("Banco de Ajustes Razonables - I.PS.I.", 0)
                        doc.add_paragraph(f"Curso: {curso_sel} | Edad: {edad_sel} | Asignatura: {asignatura_sel}")
                        doc.add_paragraph(f"Diagnósticos: {', '.join(diagnosticos_sel)}")
                        doc.add_paragraph(response.text)
                        
                        bio = io.BytesIO()
                        doc.save(bio)
                        st.download_button(
                            label="📄 Descargar como Documento de Word (.docx)",
                            data=bio.getvalue(),
                            file_name=f"Ajustes_{curso_sel}_{asignatura_sel}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"Ocurrió un error al conectar con el servicio de Gemini: {e}")
