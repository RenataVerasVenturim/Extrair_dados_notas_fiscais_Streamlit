# Extrair_dados_notas_fiscais
Extrair dados de notas fiscais com Tesseract OCR e expressões regulares

![InShot_20240724_162829677-ezgif com-video-to-gif-converter (2)](https://github.com/user-attachments/assets/3736fe43-9d0f-45a6-adf6-6efe63a0429d)

<b>Necessário ter instalado:</b>
<ol>1. VS CODE (IDE)</ol>
<ol>2. Python</ol>
<ol>3. Tesseract</ol>

<b>Clonar projeto</b>

    git clone  https://github.com/RenataVerasVenturim/Extrair_dados_notas_fiscais --config http.proxy=

<b>Acessar pasta do projeto (verifique o seu)</b>

    cd C:\Users\PROPPI_01\Desktop\ocr_github_projeto\Extrair_dados_notas_fiscais
    
<b>Comando no terminal - baixar bibliotecas</b>
    
    pip install -r requirements.txt

<b>Executar projeto</b>
    
    python server.py

REGEX utilizado para extrair dados:

    padrao_numero_nf = r'N[°º]\s?[.]?\s?\d{1,10}(?:\.\d{3})*|[0-9]{3}\.[0-9]{3}\.[0-9]{3}'
    padrao_data_emissao = r'(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/[0-9]{4}'
    padrao_cnpj_empresa = r'[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}'
    padrao_empenho = r'\b(?:[2][0][0-9]{2}\s*[NEne]{2}\s*[0-9]{1,6}|[0-9]{3}\/[2][0][0-9]{2}|\d{4}[NEne]\d{2})\b'
    padrao_processo = r'[2][3][0][6][9][., ][0-9]{6}\/[0-9]{4}[-, ][0-9]{2}'
    
Site utilizado: https://regex101.com/

![image](https://github.com/RenataVerasVenturim/Extrair_dados_notas_fiscais/assets/129551549/44d2b002-7692-4716-89d5-1a9c0a0fba60)


Resultado:
![image](https://github.com/user-attachments/assets/ef5233a6-7f03-4411-bacb-30c5f00e5cf2)

![image](https://github.com/user-attachments/assets/3d62a963-8fa0-4cec-9f12-35b87788771e)



