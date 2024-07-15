# Extrair_dados_notas_fiscais
Extrair dados de notas fiscais com Tesseract OCR e expressões regulares


REGEX utilizado para extrair número da nota fiscal = r'N[°º]?\s?\d{1,10}(?:\.\d{3})*'
    padrao_data_emissao = r'(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/[0-9]{4}'
    padrao_cnpj_empresa = r'[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}'  

Site utilizado: https://regex101.com/

![image](https://github.com/RenataVerasVenturim/Extrair_dados_notas_fiscais/assets/129551549/44d2b002-7692-4716-89d5-1a9c0a0fba60)


Resultado:
![image](https://github.com/RenataVerasVenturim/Extrair_dados_notas_fiscais/assets/129551549/eec39e96-fc5e-473f-ab0c-fd3920612105)
