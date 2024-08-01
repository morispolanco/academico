import streamlit as st
import requests
import json
import time

API_URL = "https://api.together.xyz/v1/chat/completions"

# Usa st.secrets para acceder a la API key
API_KEY = st.secrets["TOGETHER_API_KEY"]

def generate_latin_story():
    prompt = """Escribe una historia corta en latín.
    Asegúrate de que la historia tenga coherencia y esté bien estructurada."""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": [""],
        "stream": True
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        story = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8').split("data: ", 1)[1])
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        content = chunk['choices'][0]['delta'].get('content', '')
                        story += content
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Problematic line: {line}")
                    continue
        return story
    except requests.exceptions.RequestException as e:
        return f"Error en la solicitud a la API: {str(e)}"

def analyze_grammar(text):
    prompt = f"""Proporciona un análisis gramatical detallado del siguiente texto en latín:
    {text}"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": [""],
        "stream": True
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        analysis = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8').split("data: ", 1)[1])
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        content = chunk['choices'][0]['delta'].get('content', '')
                        analysis += content
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Problematic line: {line}")
                    continue
        return analysis
    except requests.exceptions.RequestException as e:
        return f"Error en la solicitud a la API: {str(e)}"

def main():
    st.title("Generador de Historias en Latín con Análisis Gramatical")
    
    if st.button("Generar Historia y Análisis"):
        story_placeholder = st.empty()
        analysis_placeholder = st.empty()
        
        st.write("Generando historia en latín...")
        progress_bar = st.progress(0)
        
        try:
            # Generar la historia en latín
            latin_story = generate_latin_story()
            story_placeholder.markdown(f"**Historia en Latín:**\n\n{latin_story}")
            
            # Actualizar la barra de progreso
            progress_bar.progress(0.5)
            
            # Analizar la gramática de la historia generada
            st.write("Analizando gramática...")
            grammar_analysis = analyze_grammar(latin_story)
            analysis_placeholder.markdown(f"**Análisis Gramatical:**\n\n{grammar_analysis}")
            
            # Completar la barra de progreso
            progress_bar.progress(1.0)
            
            st.success("¡Historia y análisis generados con éxito!")
        except Exception as e:
            st.error(f"Ocurrió un error durante la generación: {str(e)}")

if __name__ == "__main__":
    main()
