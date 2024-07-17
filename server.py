from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import cv2
import pytesseract
import re
import time
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Notas'  # Pasta onde as imagens serão armazenadas

# Configurar o caminho do Tesseract OCR
caminho_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

# Função para limpar o diretório 'Notas'
def limpar_diretorio_notas():
    diretorio_notas = app.config['UPLOAD_FOLDER']
    if os.path.exists(diretorio_notas):
        shutil.rmtree(diretorio_notas)
    os.makedirs(diretorio_notas)

# Função para executar OCR e buscar os padrões no texto extraído
def extrair_dados_da_nf(image):
    # Executar OCR na imagem
    texto = pytesseract.image_to_string(image)

    # Definir os padrões regex
    padrao_numero_nf = r'N[°º]?\s?\d{1,10}(?:\.\d{3})*'
    padrao_data_emissao = r'(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/[0-9]{4}'
    padrao_cnpj_empresa = r'[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}'
    padrao_valor_total_nota = r'[0-9]{0,3},[0-9]{2}|[0-9]{0,3}\.[0-9]{0,3},[0-9]{2}|[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3},[0-9]{2}'
    padrao_informacoes_complementares = r'(?i)COMPLEMENTARES\n([\s\S]*)'
    padrao_empenho = r'[2][0][0-9]{2}\s*[NEne]{2}\s*[0-9]{1,6}|[0-9]{3}\/[2][0][0-9]{2}'
    padrao_processo = r'[2][3][0][6][9][., ][0-9]{6}\/[0-9]{4}[-, ][0-9]{2}'

    # Buscar os padrões no texto extraído
    match_numero = re.search(padrao_numero_nf, texto)
    match_data = re.search(padrao_data_emissao, texto)
    match_cnpj = re.search(padrao_cnpj_empresa, texto)
    match_valor_total = re.search(padrao_valor_total_nota, texto)
    match_informacoes_complementares = re.search(padrao_informacoes_complementares, texto)
    match_empenho = re.search(padrao_empenho, texto)
    match_processo = re.search(padrao_processo, texto)

    # Retornar os resultados encontrados
    numero = match_numero.group(0) if match_numero else None
    data = match_data.group(0) if match_data else None
    cnpj = match_cnpj.group(0) if match_cnpj else None
    valor_total = match_valor_total.group(0) if match_valor_total else None
    informacoes_complementares = match_informacoes_complementares.group(1) if match_informacoes_complementares else None
    empenho = match_empenho.group(0) if match_empenho else None
    processo = match_processo.group(0) if match_processo else None

    return numero, data, cnpj, valor_total, informacoes_complementares, empenho, processo

# Função para ajustar o brilho e extrair os dados
def ajustar_brilho_e_extrair_dados(image, brightness):
    # Ajustar o brilho
    adjusted_image = cv2.add(image, brightness)

    # Extrair dados da imagem ajustada
    return extrair_dados_da_nf(adjusted_image)

# Função para processar todas as imagens na pasta 'Notas'
def processar_imagens_notas():
    resultados = []

    # Diretório onde estão as imagens de notas fiscais ajustadas
    diretorio_notas = app.config['UPLOAD_FOLDER']

    # Ajustar o contraste (aumentar o valor para aumentar o contraste)
    contrast = 1.5

    # Registrar o tempo inicial
    inicio = time.time()

    # Iterar sobre todos os arquivos na pasta de notas ajustadas
    for nome_arquivo in os.listdir(diretorio_notas):
        # Verificar se é um arquivo de imagem
        if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Carregar a imagem usando OpenCV
            caminho_imagem = os.path.join(diretorio_notas, nome_arquivo)
            image = cv2.imread(caminho_imagem)

            # Verificar se a imagem foi carregada corretamente
            if image is None:
                print(f"Erro ao carregar a imagem em '{caminho_imagem}'.")
                continue

            # Ajustar o contraste da imagem
            adjusted_image = cv2.convertScaleAbs(image, alpha=contrast, beta=0)

            # Variáveis para armazenar os resultados
            numero, data, cnpj, valor_total, informacoes_complementares, empenho, processo = None, None, None, None, None, None, None

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
                if not valor_total and resultado[3]:
                    valor_total = resultado[3]
                if not informacoes_complementares and resultado[4]:
                    informacoes_complementares = resultado[4]
                if not empenho and resultado[5]:
                    empenho = resultado[5]
                if not processo and resultado[6]:
                    processo = resultado[6]

            # Armazenar os resultados encontrados para o arquivo atual
            resultados.append({
                'nome_arquivo': nome_arquivo,
                'numero_nf': numero,
                'data_emissao': data,
                'cnpj_empresa': cnpj,
                'empenho': empenho,
                'processo': processo
            })

    # Calcular o tempo total de execução
    fim = time.time()
    tempo_total = fim - inicio

    return resultados, tempo_total

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def upload_imagens():
    
    limpar_diretorio_notas()
    # Verificar se o formulário contém arquivos de imagem
    if 'imagens' not in request.files:
        return "Nenhum arquivo de imagem enviado."

    # Obter lista de arquivos de imagem enviados pelo usuário
    imagens = request.files.getlist('imagens')

    # Criar diretório de uploads se não existir
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Salvar cada imagem no diretório de uploads
    caminhos_imagens = []
    for imagem in imagens:
        if imagem.filename == '':
            continue
        nome_arquivo = secure_filename(imagem.filename)
        caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        imagem.save(caminho_arquivo)
        caminhos_imagens.append(caminho_arquivo)

    # Processar as imagens salvas
    resultados, tempo_total = processar_imagens_notas()

    # Renderizar o template com os resultados
    return render_template('resultado.html', resultados=resultados, tempo_total=tempo_total)

if __name__ == '__main__':
    app.run(debug=True)
