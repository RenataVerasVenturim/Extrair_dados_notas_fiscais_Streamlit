import os
import cv2
import pytesseract
import re
import time

# Configurar o caminho do Tesseract OCR
caminho_tesseract = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

# Função para executar OCR e buscar os padrões no texto extraído
def extrair_dados_da_nf(image):
    # Executar OCR na imagem
    texto = pytesseract.image_to_string(image)

    # Definir os padrões regex
    padrao_numero_nf = r'N[°º]?\s?\d{1,10}(?:\.\d{3})*'
    padrao_data_emissao = r'(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/[0-9]{4}'
    padrao_cnpj_empresa = r'[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}'  
    padrao_valor_total_nota = r'^[1-9]\d{0,2}(\.\d{3})*,\d{2}$'#'VALOR TOTAL DA NOTA:\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{1,2})?)'      
    padrao_informacoes_complementares = r'(?i)COMPLEMENTARES\n([\s\S]*)'

    # Buscar os padrões no texto extraído
    match_numero = re.search(padrao_numero_nf, texto)
    match_data = re.search(padrao_data_emissao, texto)
    match_cnpj = re.search(padrao_cnpj_empresa, texto)
    match_valor_total = re.search(padrao_valor_total_nota, texto)
    match_padrao_informacoes_complementares=re.search(padrao_informacoes_complementares, texto)

    # Retornar os resultados encontrados
    numero = match_numero.group(0) if match_numero else None
    data = match_data.group(0) if match_data else None    
    cnpj = match_cnpj.group(0) if match_cnpj else None
    valor_total = match_valor_total.group(1) if match_valor_total else None    
    padrao_informacoes_complementares =  match_padrao_informacoes_complementares.group(1) if  match_padrao_informacoes_complementares else None

    return numero, data, cnpj, valor_total, padrao_informacoes_complementares

# Função para ajustar o brilho e extrair os dados
def ajustar_brilho_e_extrair_dados(image, brightness):
    # Ajustar o brilho
    adjusted_image = cv2.add(image, brightness)
    
    # Extrair dados da imagem ajustada
    return extrair_dados_da_nf(adjusted_image)

# Diretório onde estão as imagens de notas fiscais
diretorio_notas = "Notas"

# Ajustar o contraste (aumentar o valor para aumentar o contraste)
contrast = 1.5

# Definir o limite máximo de brilho
limite_brilho = 100

# Registrar o tempo inicial
inicio = time.time()

# Iterar sobre todos os arquivos na pasta de notas
# Variáveis para ajuste de brilho otimizado
ajustes_de_brilho = [0, 50,80]

# Iterar sobre todos os arquivos na pasta de notas
for nome_arquivo in os.listdir(diretorio_notas):
    # Verificar se é um arquivo de imagem
    if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Carregar a imagem usando OpenCV
        caminho_imagem = os.path.join(diretorio_notas, nome_arquivo)
        image = cv2.imread(caminho_imagem)

        # Ajustar o contraste da imagem
        adjusted_image = cv2.convertScaleAbs(image, alpha=contrast, beta=0)

        # Variáveis para armazenar os resultados
        numero, data, cnpj, valor_total,padrao_informacoes_complementares = None, None, None, None,None

        # Tentar extrair cada variável com ajustes de brilho otimizados
        for brilho in ajustes_de_brilho:
            resultado = ajustar_brilho_e_extrair_dados(adjusted_image, brilho)
            if not numero and resultado[0]:
                numero = resultado[0]
            if not data and resultado[1]:
                data = resultado[1]
            if not cnpj and resultado[2]:
                cnpj = resultado[2]
            if not valor_total and resultado[3]:
                valor_total = resultado[3]
            if not padrao_informacoes_complementares and resultado[4]:
                padrao_informacoes_complementares=resultado[4]

        # Exibir os resultados encontrados para o arquivo atual
        print(f"\nDados da NF-e encontrados para o arquivo {nome_arquivo}:")
        if numero:
            print("Número da NF-e:", numero)
        else:
            print("Número da NF-e não encontrado.")

        if data:
            print("Data de emissão:", data)
        else:
            print("Data de emissão não encontrada.")
            
        if cnpj:
            print("CNPJ empresa:", cnpj)
        else:
            print("CNPJ da empresa não encontrado.")

        if valor_total:
            print("Valor total da nota:", valor_total)
        else:
            print("Valor total da nota não encontrado.")
        if padrao_informacoes_complementares:
            print("Informações complementares:", padrao_informacoes_complementares)
        else:
            print("Informações complementares não encontradas.")


# Calcular o tempo total de execução
fim = time.time()
tempo_total = fim - inicio

print(f"\nTempo total de execução: {tempo_total:.2f} segundos")
