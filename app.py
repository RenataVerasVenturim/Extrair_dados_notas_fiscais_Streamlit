import cv2
import pytesseract
import re

# Configurar o caminho do Tesseract OCR
caminho_tesseract = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

# Função para executar OCR e buscar o padrão no texto extraído
def extrair_numeros_da_nf(image):
    # Executar OCR na imagem ajustada
    texto = pytesseract.image_to_string(image)

    # Definir o padrão regex para o número da NF-e
    pattern = r'N[°º]?\s?\d{1,10}(?:\.\d{3})*'

    # Buscar o padrão no texto extraído
    matches = re.findall(pattern, texto)
    return matches

# Carregar a imagem usando OpenCV
image = cv2.imread("imagem6.png")

# Ajustar o brilho (aumentar o valor para aumentar o brilho)
brightness = 50
adjusted_image = cv2.add(image, brightness)

# Ajustar o contraste (aumentar o valor para aumentar o contraste)
contrast = 1.5
adjusted_image = cv2.convertScaleAbs(adjusted_image, alpha=contrast, beta=0)

# Salvar a imagem ajustada (opcional, para ver como ficou a imagem)
cv2.imwrite('imagem_ajustada.png', adjusted_image)

# Primeiro, tente extrair números da imagem ajustada
matches = extrair_numeros_da_nf(adjusted_image)

# Se nenhum número for encontrado, tente com brilho original (brightness = 0)
if not matches:
    print("Nenhum número encontrado com brilho ajustado. Tentando com brilho original...")
    adjusted_image = cv2.add(image, 0)  # Ajustar o brilho para 0 (sem alteração)
    matches = extrair_numeros_da_nf(adjusted_image)

# Exibir os resultados encontrados
print("Números da NF-e encontrados:")
if matches:
    for match in matches:
        print(match)
else:
    print("Nenhum número da NF-e encontrado.")
