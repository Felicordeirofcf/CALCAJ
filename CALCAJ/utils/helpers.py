def gerar_callback_exclusao(id_, janela_principal):
    def callback():
        janela_principal.excluir_cliente(id_)
    return callback
