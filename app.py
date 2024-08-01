import streamlit as st
import requests
import json
import time

API_URL = "https://api.together.xyz/v1/chat/completions"

# Usa st.secrets para acceder a la API key
API_KEY = st.secrets["TOGETHER_API_KEY"]

def generate_article(title):
    prompt = f"""Genera un artículo académico de más de 3000 palabras sobre el tema: "{title}".
    El artículo debe incluir:
    1. Introducción
    2. Desarrollo del tema (con subtemas)
    3. Conclusión
    4. Referencias (cita al menos 5 fuentes académicas)
    
    Usa un estilo académico y formal. Asegúrate de que el artículo tenga coherencia y esté bien estructurado."""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": [""],
        "stream": True
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8').split("data: ", 1)[1])
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        content = chunk['choices'][0]['delta'].get('content', '')
                        yield content
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Problematic line: {line}")
                    continue  # Skip this line and continue with the next one
    except requests.exceptions.RequestException as e:
        yield f"Error en la solicitud a la API: {str(e)}"

def main():
    st.title("Generador de Artículos Académicos")
    
    title = st.text_input("Ingrese el título del artículo:")
    
    if st.button("Generar Artículo"):
        if title:
            article_placeholder = st.empty()
            full_article = ""
            
            st.write("Generando artículo...")
            progress_bar = st.progress(0)
            
            try:
                for chunk in generate_article(title):
                    full_article += chunk
                    article_placeholder.markdown(full_article)
                    
                    # Actualizar la barra de progreso (asumiendo que 3000 palabras son aproximadamente 18000 caracteres)
                    progress = min(len(full_article) / 18000, 1.0)
                    progress_bar.progress(progress)
                    
                    time.sleep(0.05)  # Para evitar sobrecarga de la interfaz
                
                if full_article:
                    st.success("¡Artículo generado con éxito!")
                else:
                    st.warning("No se pudo generar el artículo. Por favor, intente de nuevo.")
            except Exception as e:
                st.error(f"Ocurrió un error durante la generación del artículo: {str(e)}")
        else:
            st.warning("Por favor, ingrese un título para el artículo.")

if __name__ == "__main__":
    main()
