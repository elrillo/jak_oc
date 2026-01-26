
# 🏛️ Observatorio Congreso: Radiografía Legislativa JAK

> **Versión Beta 0.9** - Plataforma de Análisis de Datos Políticos para Revisión Interna

## 📋 Descripción del Proyecto
Este observatorio es una herramienta interactiva de **Inteligencia de Datos** diseñada para auditar y visualizar la actividad parlamentaria del ex-diputado **José Antonio Kast**. 

Hemos digitalizado, procesado y analizado el 100% de su producción legislativa documentada:
*   **Total de Proyectos**: 255 Mociones Parlamentarias.
*   **Periodo Analizado**: 2002 - 2018 (Periodos legislativos completos).
*   **Tecnología**: Motor de análisis NLP local y visualización en Streamlit.

## 🧠 Inteligencia Artificial Aplicada
Más allá de los datos duros, hemos implementado una capa de **Procesamiento de Lenguaje Natural (NLP)** sobre los testiomonios originales (PDFs) de cada ley para generar:

1.  **Resúmenes Ejecutivos Automáticos**: Síntesis de 2 oraciones que capturan la "Idea Matriz" de cada proyecto, facilitando la lectura rápida.
2.  **Clasificación Temática**: Detección automática de tópicos clave (Seguridad, Familia, Constitución, etc.).
3.  **Análisis de Sentimiento**: Evaluación del tono (Punitivo vs. Propositivo) del lenguaje jurídico utilizado.

## 📊 Principales Hallazgos (Spoiler)
El análisis automatizado de los 255 proyectos revela un perfil legislativo distintivo:

*   **Enfoque 100% Nacional**: El análisis territorial muestra que el **0%** de sus proyectos tuvo un foco exclusivamente distrital (La Reina/Peñalolén). Toda su producción legislativa apuntó a reformas de carácter nacional o general.
*   **Obsesión Temática**: Sus ejes prioritarios fueron **Constitucional**, **Familia y Valores** y **Seguridad**, relegando temas administrativos a un segundo plano.
*   **Red de Alianzas**: La plataforma revela gráficamente su círculo de hierro político y la transversalidad (o falta de ella) en sus coautorías.

## 🚀 Cómo Ejecutar el Observatorio
Esta aplicación corre en local utilizando Python y Streamlit.

1.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Ejecutar la App**:
    ```bash
    streamlit run app.py
    ```

## 🛠️ Stack Tecnológico
*   **Frontend**: Streamlit (Python)
*   **Backend/Data**: SQLite & Pandas
*   **NLP**: Algoritmos de extracción de reglas y análisis léxico customizado.
*   **Visualización**: Plotly Express

---
*Desarrollado por el Equipo de Data Science del Observatorio Congreso.*
