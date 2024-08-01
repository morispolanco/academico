import streamlit as st
import requests
import json
import time
import re

API_URL = "https://api.together.xyz/v1/chat/completions"
API_KEY = st.secrets["TOGETHER_API_KEY"]

def generate_index(title):
    prompt = f"""Crea un índice detallado para un artículo académico de más de 3000 palabras sobre el tema: "{title}".
    El índice debe incluir:
    1. Introducción
    2. Al menos 3 secciones principales con 2-3 subsecciones cada una
    3. Conclusión
    4. Referencias
    
    Formato el índice usando Markdown, con enlaces internos a cada sección. Por ejemplo:

    # Índice
    1. [Introducción](#introduccion)
    2. [Sección Principal 1](#seccion-1)
        2.1 [Subsección 1.1](#subseccion-1-1)
        2.2 [Subsección 1.2](#subseccion-1-2)
    3. [Sección Principal 2](#seccion-2)
        ...
    4. [Conclusión](#conclusion)
    5. [Referencias](#referencias)
    """

    return call_api(prompt)

def generate_section(title, section):
    prompt = f"""Genera el contenido para la sección "{section}" del artículo académico sobre "{title}".
    Asegúrate de que el contenido sea detallado, bien estructurado y académicamente riguroso.
    Si es una subsección, relaciona el contenido con la sección principal.
    Usa un estilo académico y formal. Incluye citas si es apropiado.
    """

    return call_api(prompt)

def call_api(prompt):
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

    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        full_content = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8').split("data: ", 1)[1])
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        content = chunk['choices'][0]['delta'].get('content', '')
                        full_content += content
                        yield content
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Problematic line: {line}")
                    continue
        
        if not full_content:
            yield "Error: No se generó contenido."
    except requests.exceptions.RequestException as e:
        yield f"Error en la solicitud a la API: {str(e)}"

def parse_index(index_content):
    lines = index_content.split('\n')
    sections = []
    for line in lines:
        if line.startswith('#'):
            continue
        match = re.match(r'\d+\.?\d*\s*\[(.+)\]\(#(.+)\)', line.strip())
        if match:
            sections.append((match.group(1), match.group(2)))
    return sections

def main():
    st.title("Generador de Artículos Académicos")
    
    title = st.text_input("Ingrese el título del artículo:")
    
    if st.button("Generar Artículo"):
        if title:
            st.write("Generando índice...")
            index_content = "".join(list(generate_index(title)))
            st.markdown(index_content)
            
            sections = parse_index(index_content)
            
            full_article = index_content + "\n\n"
            
            for section_title, section_id in sections:
                st.write(f"Generando sección: {section_title}")
                section_content = "".join(list(generate_section(title, section_title)))
                full_article += f"\n\n## {section_title}\n\n{section_content}"
                st.markdown(full_article)
            
            st.success("¡Artículo generado con éxito!")
        else:
            st.warning("Por favor, ingrese un título para el artículo.")

if __name__ == "__main__":
    main()
