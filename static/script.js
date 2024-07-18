function verificarArquivos() {
    // Selecionar o elemento de input de arquivo
    var input = document.getElementById('imagens');

    // Verificar se há arquivos selecionados
    if (input.files.length === 0) {
        alert("Por favor, selecione pelo menos um arquivo.");
        return;
    }

    // Validar os tipos de arquivo permitidos
    for (var i = 0; i < input.files.length; i++) {
        var file = input.files[i];
        var allowedTypes = ['image/png', 'image/jpeg', 'image/jpg','application/pdf'];

        if (allowedTypes.indexOf(file.type) === -1) {
            alert("Formato de arquivo não suportado. Insira apenas arquivos .pdf, .png ou .jpeg");
            return;
        }
    }

    // Se todos os arquivos forem válidos, submeter o formulário
    document.getElementById('upload-form').submit();
}
