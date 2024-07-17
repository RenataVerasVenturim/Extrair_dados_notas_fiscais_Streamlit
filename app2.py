import os
import cv2

# Diretório onde estão as imagens de notas fiscais
diretorio_notas = "Notas"
diretorio_notas_ajustadas = "Notas_ajustadas"  # Pasta para salvar as imagens ajustadas

# Verificar se a pasta Notas_ajustadas existe, senão criar
if not os.path.exists(diretorio_notas_ajustadas):
    os.makedirs(diretorio_notas_ajustadas)
else:
    # Limpar a pasta Notas_ajustadas
    for arquivo in os.listdir(diretorio_notas_ajustadas):
        caminho_arquivo = os.path.join(diretorio_notas_ajustadas, arquivo)
        os.remove(caminho_arquivo)
    print(f"Pasta {diretorio_notas_ajustadas} limpa com sucesso.")

# Iterar sobre todos os arquivos na pasta de notas
for nome_arquivo in os.listdir(diretorio_notas):
    # Verificar se é um arquivo de imagem
    if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Caminho completo da imagem original
        caminho_imagem_original = os.path.join(diretorio_notas, nome_arquivo)
        
        try:
            # Carregar a imagem usando OpenCV
            image = cv2.imread(caminho_imagem_original)

            if image is None:
                raise Exception(f"Erro ao ler a imagem em '{caminho_imagem_original}'.")

            # Converter para escala de cinza
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar binarização (usando o método de Otsu)
            _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Gerar o nome do arquivo ajustado
            nome_arquivo_ajustado = f"imagem_ajustada_{nome_arquivo}"
            
            # Salvar a imagem binarizada ajustada na pasta Notas_ajustadas
            caminho_imagem_ajustada = os.path.join(diretorio_notas_ajustadas, nome_arquivo_ajustado)
            cv2.imwrite(caminho_imagem_ajustada, binary_image)
            
            print(f"Imagem binarizada e salva como {nome_arquivo_ajustado} para o arquivo {nome_arquivo}")
        
        except Exception as e:
            print(f"Erro ao processar a imagem '{nome_arquivo}': {str(e)}")
