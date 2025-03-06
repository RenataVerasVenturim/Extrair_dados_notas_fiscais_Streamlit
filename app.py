import os
import tempfile
import shutil
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import re
import streamlit as st

# Função para converter PDF em imagem PNG usando PyMuPDF
def converter_pdf_para_png(pdf_file):
    try:
        # Salva o arquivo temporariamente
        temp_dir = tempfile.mkdtemp()
        temp_pdf_path = os.path.join(temp_dir, pdf_file.name)
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        
        document = fitz.open(temp_pdf_path)
        imagens = []
        dpi = 300
        largura_total, altura_total = 0, 0

        # Calcular as dimensões totais
        for page_number in range(len(document)):
            page = document.load_page(page_number)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            imagens.append(pix)
            largura_total = max(largura_total, pix.width)
            altura_total += pix.height

        # Criar uma imagem combinada
        img_combined = Image.new("RGB", (largura_total, altura_total))
        y_offset = 0
        for pix in imagens:
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_combined.paste(img, (0, y_offset))
            y_offset += pix.height
        
        document.close()
        shutil.rmtree(temp_dir)  # Remove o diretório temporário
        return img_combined
    except Exception as e:
        st.error(f"Erro ao converter o PDF: {e}")
        return None

# Função para extrair dados da imagem
def extrair_dados_da_nf(image):
    texto = pytesseract.image_to_string(image)

    # Definir os padrões regex
    padrao_numero_nf = r'N[°º]\s?[.]?\s?\d{1,10}(?:\.\d{3})*|[0-9]{3}\.[0-9]{3}\.[0-9]{3}'
    padrao_data_emissao = r'(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/[0-9]{4}'
    padrao_cnpj_empresa = r'[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2}'
    padrao_empenho = r'\b(?:[2][0][0-9]{2}\s*[NEne]{2}\s*[0-9]{1,6}|[0-9]{3}\/[2][0][0-9]{2}|\d{4}[NEne]\d{2})\b'
    padrao_processo = r'[2][3][0][6][9][., ][0-9]{6}\/[0-9]{4}[-, ][0-9]{2}'

    # Buscar padrões no texto extraído
    numero = re.search(padrao_numero_nf, texto)
    data = re.search(padrao_data_emissao, texto)
    cnpj = re.search(padrao_cnpj_empresa, texto)
    empenho = re.search(padrao_empenho, texto)
    processo = re.search(padrao_processo, texto)

    return {
        "Número NF": numero.group(0) if numero else None,
        "Data Emissão": data.group(0) if data else None,
        "CNPJ": cnpj.group(0) if cnpj else None,
        "Empenho": empenho.group(0) if empenho else None,
        "Processo": processo.group(0) if processo else None,
    }

# Interface do Streamlit
st.title("Extração de Dados de Notas Fiscais")

# Upload de arquivos
uploaded_files = st.file_uploader("Envie os arquivos (PDF ou Imagem)", type=["pdf", "png", "jpg"], accept_multiple_files=True)

if uploaded_files:
    resultados = []
    
    for file in uploaded_files:
        st.write(f"Processando: {file.name}")
        
        # Verifica se é PDF e converte para imagem
        if file.name.endswith(".pdf"):
            imagem = converter_pdf_para_png(file)
        else:
            imagem = Image.open(file)

        if imagem:
            dados_extraidos = extrair_dados_da_nf(imagem)
            resultados.append(dados_extraidos)

    # Exibir os resultados
    if resultados:
        st.table(resultados)
    else:
        st.warning("Nenhum dado foi extraído.")
