# Extrair_dados_notas_fiscais
Extrair dados de notas fiscais com Tesseract OCR e expressões regulares


REGEX utilizado para extrair número da nota fiscal = N[°º]?\s?\d{1,10}(?:\.\d{3})*

número do empenho (em desenvolvimento...)= /(?i)20[0-9]{2}\s?ne\s?[0-9]{1,6}|[0-9]{3}/gm


Site utilizado: https://regex101.com/

![image](https://github.com/RenataVerasVenturim/Extrair_dados_notas_fiscais/assets/129551549/44d2b002-7692-4716-89d5-1a9c0a0fba60)


Resultado:
![image](https://github.com/RenataVerasVenturim/Extrair_dados_notas_fiscais/assets/129551549/eec39e96-fc5e-473f-ab0c-fd3920612105)
