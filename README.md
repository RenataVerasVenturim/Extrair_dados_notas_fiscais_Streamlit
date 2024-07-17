# Extrair_dados_notas_fiscais
Extrair dados de notas fiscais com Tesseract OCR e expressões regulares


REGEX utilizado para extrair dados:

    padrao_numero_nf = r'N[°º]?\s?\d{1,10}(?:\.\d{3})*'
    padrao_data_emissao = r'(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/[0-9]{4}'
    padrao_cnpj_empresa = r'[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}'
    padrao_empenho = r'[2][0][0-9]{2}\s*[NEne]{2}\s*[0-9]{1,6}|[0-9]{3}\/[2][0][0-9]{2}'
    padrao_processo = r'[2][3][0][6][9][., ][0-9]{6}\/[0-9]{4}[-, ][0-9]{2}'

Site utilizado: https://regex101.com/

![image](https://github.com/RenataVerasVenturim/Extrair_dados_notas_fiscais/assets/129551549/44d2b002-7692-4716-89d5-1a9c0a0fba60)


Resultado:
![image](https://github.com/user-attachments/assets/e7683202-43ba-41f1-bb55-929367e0b64b)

