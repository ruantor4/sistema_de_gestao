from django.contrib import messages

def validar_produto(request, nome: str, localizacao: str, quantidade: int | None = None) -> bool:
    """
        Função responsável por validar os campos de um produto antes de salvar ou atualizar no banco de dados.

        A validação verifica se o nome está preenchido, se a quantidade foi informada
        e se o valor é não negativo. Caso ocorra erro, mensagens são exibidas ao usuário.

        Args:
            request (django.http.HttpRequest): Objeto da requisição HTTP, utilizado para exibir mensagens de erro.
            nome (str): Nome do produto a ser validado.
            localizacao (str): Localização física ou setor do produto no estoque.
            quantidade (int | None, opcional): Quantidade atual do produto. Pode ser None para validação inicial.

        Returns:
            bool: Retorna True se todos os campos forem válidos; False caso contrário.
    """
    if not nome.strip():
        messages.error(request, "O campo 'Nome' é obrigatório.")
        return False

    if quantidade is None:
        messages.error(request, "O campo 'Quantidade' é obrigatório.")
        return False

    if quantidade < 0:
        messages.error(request, "A quantidade não pode ser negativa.")
        return False

    return True
