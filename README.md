# Objetivo
Criar um sistema em que o usuário pudesse enviar arquivos e uma IA pudesse classificá-los quanto a categoria que pertecem. 
Isso foi inpirado no sistema da EMTU que geralmente fica pedindo para o usuário reenviar documentos, pois enviaram algo errado. 
Nesse caso o próprio sistema poderia dizer que os arquivos não condizem com a categoria. 

# Participantes e Contribuições
Jéssica - Criação da tela, envio de arquivos, treinamento de modelos, envio de PDF <br>
Pedro Torini - Integração com Chat-GPT, envio de JPG

# Ferramentas Utilizadas
- Python
- OpenAI
- Tesseract 

# Instruções de Uso

1. Instalar o python na máquina, caso não possua, é possivel baixa-lo na Microsoft Store
2. Entrar no site ```
        https://digi.bib.uni-mannheim.de/tesseract/
    ```
Instalar a versão ```
        tesseract-ocr-w64-setup-5.4.0.20240606.exe
    ```
3. ```
    git clone https://github.com/PTorini1/poc-ia.git
    ```
4. ```
    cd poc-ia
    ```
5. ```
    	pip install pandas streamlit fitz matplotlib streamlit-option-menu transformers tensorflow tf-keras streamlit-pdf-viewer PyMuPDF openai==0.28 pytesseract tesseract azure-storage-blob asyncio python-dotenv
    ```
6. ```
    python -m venv venv
    ```
7. ```
    venv\scripts\activate
    ```
8. Criar arquivo .env na raíz do projeto e coloque suas chaves 
    ```
        OPENAI_API_KEY = <SUA CHAVE> 
        BLOB = <SUA CHAVE>
    ```
9. ```
    streamlit run app.py
    ```

Obs: Na hora de rodar a aplicação, pode acontecer de a biblioteca não se comportar bem no localhost e será necessário usar o outro link pelo IP que é fornecido no terminal
Também desabilitamos o envio de JPG para teste, pois seria necessário um passo extra para download