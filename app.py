import os
import streamlit as st
import pandas as pd
import fitz
import matplotlib.pyplot as plt
from transformers import pipeline
import openai
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from PIL import Image
import pytesseract
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

models = {
    'Chat-GPT':'Chat-GPT',
    'MoritzLaurer/bge-m3-zeroshot-v2.0': 'MoritzLaurer/bge-m3-zeroshot-v2.0',
}

connect_str = os.getenv("BLOB")
container_name = 'poc-ia'
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def upload_blob_file(filepath, filename):
    container_client = blob_service_client.get_container_client(container=container_name)
    with open(file=os.path.join(filepath, filename), mode="rb") as data:
        blob_client = container_client.upload_blob(name=filename, data=data, overwrite=True)

def get_gpt3_response(prompt, model="gpt-4"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente muito útil"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()

@st.cache_resource
def load_model(model_name):
    return pipeline('zero-shot-classification', model=model_name)

def classify_document(classifier, text, candidate_labels, use_gpt3=False):
    if use_gpt3:
        prompt = f'''Classifique o documento de acordo com as seguintes categorias e retorne apenas 1 palavra dentre as labels que serão informadas.: {', '.join(candidate_labels)}. Documento: {text} 
            Após retornar a palavra caso seja um Documento de identificação, retornar dados pessoais em Json (Ex: RG: 00.000.000-00 ou CPF: 000.000.000-00)
            Após retornar a palavra caso seja um Comprovante de residência, retornar endereço em Json
            Após retornar a palavra caso seja um Certificado de escolaridade, retornar nome da escola e dados pessoais do aluno em Json:
        '''
        return get_gpt3_response(prompt)
    else:
        result = classifier(text, candidate_labels)
        return result['labels'][0]

def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = ''
    for page in doc:
        text += page.get_text()
    return text

def read_jpg(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

def read_document(file_path):
    if file_path.endswith('.pdf'):
        return read_pdf(file_path)
    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        return read_jpg(file_path)
    else:
        raise ValueError(f'Formato de arquivo não suportado: {file_path}')

def index_documents(classifier, files, candidate_labels, use_gpt3=False):
    indexed_data = []
    total_files = len(files)
    progress_bar = st.progress(0)

    for i, file_path in enumerate(files):
        try:
            text = read_document(file_path)
            category = classify_document(classifier, text, candidate_labels, use_gpt3)
            indexed_data.append({'filename': os.path.basename(file_path), 'category': category})
            
            blob_name = os.path.basename(file_path)
            upload_blob_file(os.path.dirname(file_path), blob_name)
        except ValueError as e:
            st.error(e)
        progress_bar.progress((i + 1) / total_files)

    return pd.DataFrame(indexed_data)

def classification():
    st.title('Classificação de documentos para a EMTU')
    #st.write('Iniciando o aplicativo...')

    uploaded_files = st.file_uploader('Envie seus arquivos PDF ou JPG', accept_multiple_files=True, type=['pdf'])
    #st.write('Arquivos enviados:', uploaded_files)

    selected_model = st.selectbox('Selecione o modelo de classificação', list(models.keys()))
    #st.write('Modelo selecionado:', selected_model)

    candidate_labels = st.text_input('Insira os rótulos separados por vírgula', 'Documento de Identificação,Comprovante de residência,Certificado de escolaridade').split(',')
    #st.write('Rótulos:', candidate_labels)

    #use_gpt3 = st.checkbox('Use o Chat-GPT para classificação')
    use_gpt3=True
    if selected_model == 'Chat-GPT':
        use_gpt3=True
    else:
        use_gpt3=False

    if st.button('Classificar'):
        if uploaded_files:
            documents_path = './documents'
            if not os.path.exists(documents_path):
                os.makedirs(documents_path)

            file_paths = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(documents_path, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)
                st.write(f'Arquivo salvo: {file_path}')

            if not use_gpt3:
                classifier = load_model(models[selected_model])
                st.write('Modelo carregado')

            results_df = index_documents(classifier if not use_gpt3 else None, file_paths, candidate_labels, use_gpt3)
            st.write('Documentos indexados')

            if not results_df.empty:
                results_df.to_csv('indexed_documents.csv', index=False)
                st.success('Classificação concluída!')
                st.dataframe(results_df)

                st.subheader('Resultados da Classificação')
                bar_chart_data = results_df['category'].value_counts().reset_index()
                bar_chart_data.columns = ['Category', 'Count']

                plt.figure(figsize=(10, 5))
                plt.bar(bar_chart_data['Category'], bar_chart_data['Count'])
                plt.xlabel('Category')
                plt.ylabel('Count')
                plt.title('Distribuição das categorias')
                st.pyplot(plt)
            else:
                st.warning('Nenhum documento foi classificado.')
        else:
            st.warning('Por favor, envie pelo menos um arquivo PDF ou JPG.')

if __name__ == "__main__":
    classification()
