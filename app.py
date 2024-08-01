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
        "max_tokens": 2512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": True
    }

    response = requests.post(API_URL, headers=headers, json=data, stream=True)
    
    if response.status_code == 200:
        article = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8').split("data: ")[1])
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    content = chunk['choices'][0]['delta'].get('content', '')
                    article += content
                    yield content
    else:
        yield f"Error: {response.status_code} - {response.text}"

def main():
    st.title("Generador de Artículos Académicos")
    
    title = st.text_input("Ingrese el título del artículo:")
    
    if st.button("Generar Artículo"):
        if title:
            article_placeholder = st.empty()
            full_article = ""
            
            st.write("Generando artículo...")
            progress_bar = st.progress(0)
            
            for chunk in generate_article(title):
                full_article += chunk
                article_placeholder.markdown(full_article)
                
                # Actualizar la barra de progreso (asumiendo que 3000 palabras son aproximadamente 18000 caracteres)
                progress = min(len(full_article) / 18000, 1.0)
                progress_bar.progress(progress)
                
                time.sleep(0.05)  # Para evitar sobrecarga de la interfaz
            
            st.success("¡Artículo generado con éxito!")
        else:
            st.warning("Por favor, ingrese un título para el artículo.")

if __name__ == "__main__":
    main()
