import logging

# filename= arquivo onde grava os logs
# encoding= codificação do arquivo
# format= formatação da mensagem
# level= nível mínimo pra registrar
logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(message)s",
    filename="mensagens.log",
    encoding="utf-8",
    level=logging.DEBUG,
)

# incluindo variáveis formatadas no texto
logging.debug(
    "mensagem pro log apenas de verificação %s - %i", logging.__name__, logging.DEBUG
)
logging.info("mensagem pro log informando atividade")
logging.warning("mensagem pro log possível problema")
logging.error("mensagem pro log erro no programa")
