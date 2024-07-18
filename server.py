import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import re
import time
import shutil
import threading
from functools import lru_cache
import fitz  # PyMuPDF
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Notas'  # Pasta onde as imagens de notas fiscais serão armazenadas
app.config['UPLOAD_FOLDER_PDF'] = 'Notas_pdf'  # Pasta onde os PDFs temporários serão armazenados

# Configurar o caminho do Tesseract OCR
caminho_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

# Registrar o tempo inicial
inicio = time.time()

# Função para limpar o diretório 'Notas'
def limpar_diretorio_notas():
    diretorio_notas = app.config['UPLOAD_FOLDER']
    if os.path.exists(diretorio_notas):
        shutil.rmtree(diretorio_notas)
    os.makedirs(diretorio_notas)

# Função para limpar o diretório 'Notas_pdf'
def limpar_diretorio_notas_pdf():
    diretorio_notas_pdf = app.config['UPLOAD_FOLDER_PDF']
    if os.path.exists(diretorio_notas_pdf):
        shutil.rmtree(diretorio_notas_pdf)
    os.makedirs(diretorio_notas_pdf)

# Função para converter PDF em imagem PNG usando PyMuPDF
def converter_pdf_para_png(pdf_file):
    document = fitz.open(pdf_file)
    imagens_salvas = []
    
    # Definir DPI alto para imagens
    dpi = 300  # Exemplo de DPI alto, ajuste conforme necessário

    # Converter apenas a primeira página
    page = document.load_page(0)  # Carregar primeira página (índice 0)
    
    # Obter pixmap com DPI especificado
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
    
    # Converter pixmap para imagem PIL
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Nome do arquivo para salvar
    nome_arquivo_png = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.basename(pdf_file).split('.')[0]}_page_1.png")
    
    # Salvar imagem
    img.save(nome_arquivo_png)
    
    # Adicionar caminho do arquivo salvo à lista
    imagens_salvas.append(nome_arquivo_png)
    
    # Fechar documento após o uso
    document.close()
    
    return imagens_salvas

# Função para executar OCR e buscar os padrões no texto extraído
def extrair_dados_da_nf(image):
    # Executar OCR na imagem
    texto = pytesseract.image_to_string(image)

    # Definir os padrões regex
    padrao_numero_nf = r'N[°º]?\s?\d{1,10}(?:\.\d{3})*'
    padrao_data_emissao = r'(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/[0-9]{4}'
    padrao_cnpj_empresa = r'[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}'
    padrao_empenho = r'[2][0][0-9]{2}\s*[NEne]{2}\s*[0-9]{1,6}|[0-9]{3}\/[2][0][0-9]{2}'
    padrao_processo = r'[2][3][0][6][9][., ][0-9]{6}\/[0-9]{4}[-, ][0-9]{2}'

    # Buscar os padrões no texto extraído
    match_numero = re.search(padrao_numero_nf, texto)
    match_data = re.search(padrao_data_emissao, texto)
    match_cnpj = re.search(padrao_cnpj_empresa, texto)
    match_empenho = re.search(padrao_empenho, texto)
    match_processo = re.search(padrao_processo, texto)

    # Retornar os resultados encontrados
    numero = match_numero.group(0) if match_numero else None
    data = match_data.group(0) if match_data else None
    cnpj = match_cnpj.group(0) if match_cnpj else None
    empenho = match_empenho.group(0) if match_empenho else None
    processo = match_processo.group(0) if match_processo else None

    return numero, data, cnpj, empenho, processo

# Função para ajustar o brilho e extrair os dados
def ajustar_brilho_e_extrair_dados(image, brightness):
    # Ajustar o brilho
    adjusted_image = cv2.add(image, brightness)

    # Extrair dados da imagem ajustada
    return extrair_dados_da_nf(adjusted_image)

# Função para processar uma imagem
@lru_cache(maxsize=32)  # Cache com capacidade para 32 resultados
def processar_imagem(nome_arquivo):
    # Carregar a imagem usando OpenCV
    caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
    image = cv2.imread(caminho_imagem)

    # Verificar se a imagem foi carregada corretamente
    if image is None:
        print(f"Erro ao carregar a imagem em '{caminho_imagem}'.")
        return None

    # Ajustar o contraste (aumentar o valor para aumentar o contraste)
    contrast = 1.5
    adjusted_image = cv2.convertScaleAbs(image, alpha=contrast, beta=0)

    # Variáveis para armazenar os resultados
    numero, data, cnpj, empenho, processo = None, None, None, None, None

    # Tentar extrair cada variável com ajustes de brilho otimizados
    ajustes_de_brilho = [0, 50, 80]  # Exemplo de ajustes de brilho
    for brilho in ajustes_de_brilho:
        resultado = ajustar_brilho_e_extrair_dados(adjusted_image, brilho)
        if not numero and resultado[0]:
            numero = resultado[0]
        if not data and resultado[1]:
            data = resultado[1]
        if not cnpj and resultado[2]:
            cnpj = resultado[2]
        if not empenho and resultado[3]:
            empenho = resultado[3]
        if not processo and resultado[4]:
            processo = resultado[4]

    # Retornar os resultados incluindo o nome do arquivo
    return {
        'nome_arquivo': nome_arquivo,
        'numero_nf': numero,
        'data_emissao': data,
        'cnpj_empresa': cnpj,
        'empenho': empenho,
        'processo': processo
    }

# Função para processar todas as imagens na pasta 'Notas' usando threads
def processar_imagens_notas():
    resultados = []
    threads = []

    # Diretório onde estão as imagens de notas fiscais
    diretorio_notas = app.config['UPLOAD_FOLDER']

    # Diretório onde estão os PDFs temporários
    diretorio_notas_pdf = app.config['UPLOAD_FOLDER_PDF']

    # Lista para armazenar os nomes de arquivo de imagem
    image_files = set()  # Usar um conjunto para evitar duplicatas

    # Iterar sobre todos os arquivos na pasta 'Notas_pdf' para converter PDF em PNG
    for nome_arquivo in os.listdir(diretorio_notas_pdf):
        caminho_arquivo_pdf = os.path.join(diretorio_notas_pdf, nome_arquivo)
        if nome_arquivo.lower().endswith('.pdf'):
            imagens_png = converter_pdf_para_png(caminho_arquivo_pdf)
            for png in imagens_png:
                image_files.add(os.path.basename(png))

    # Iterar sobre todos os arquivos na pasta 'Notas'
    for nome_arquivo in os.listdir(diretorio_notas):
        if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_files.add(nome_arquivo)

    # Processar imagens agora que todos os arquivos estão na pasta 'Notas'
    for nome_arquivo in image_files:
        thread = threading.Thread(target=lambda p=nome_arquivo: resultados.append(processar_imagem(p)))
        threads.append(thread)
        thread.start()

    # Aguardar todas as threads terminarem
    for thread in threads:
        thread.join()

    # Calcular o tempo total de execução
    fim = time.time()
    tempo_total = fim - inicio

    return resultados, tempo_total

# Rotas Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def upload_imagens():
    limpar_diretorio_notas()
    limpar_diretorio_notas_pdf()

    if 'imagens' not in request.files:
        return "Nenhum arquivo enviado."

    arquivos = request.files.getlist('imagens')

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    if not os.path.exists(app.config['UPLOAD_FOLDER_PDF']):
        os.makedirs(app.config['UPLOAD_FOLDER_PDF'])

    for arquivo in arquivos:
        if arquivo.filename.lower().endswith('.pdf'):
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER_PDF'], secure_filename(arquivo.filename)))
        else:
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(arquivo.filename)))

    resultados, tempo_total = processar_imagens_notas()

    return render_template('resultado.html', resultados=resultados, tempo_total=tempo_total)

@app.route('/baixar/<nome_arquivo>', methods=['GET'])
def baixar_nota(nome_arquivo):
    caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
    return send_file(caminho_arquivo, as_attachment=True)

@app.route('/visualizar/<nome_arquivo>', methods=['GET'])
def visualizar_nota(nome_arquivo):
    caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
    return send_file(caminho_arquivo)

if __name__ == '__main__':
    app.run(debug=True)