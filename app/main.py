import requests
import pandas as pd
import re
import sys
from io import BytesIO
from loguru import logger

sys.path.append('/app')

from utils.credentials import get_auth_path

BUCKET_NAME = "im-projects-gcp"
RAW_LAYER = "raw"
TRUSTED_LAYER = "trusted"
ORIGEM = "agrofit"
BASE = "produto_formulado"

credentials = get_auth_path()


def pegar_texto_sem_parenteses(string):
    """
    Pega todo o texto exceto o que estiver entre parenteses.

    Args:
    string: A string a ser analisada.

    Returns:
    Uma string contendo o texto encontrado.
    """
    regex = r"(?<!\()[^()]+(?!\))"
    match = re.findall(regex, string)
    return "".join(match)


if __name__ == "__main__":

    logger.info("Iniciando")

    # Obtem os dados
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0"}
    url = "https://dados.agricultura.gov.br/dataset/6c913699-e82e-4da3-a0a1-fb6c431e367f/resource/d30b30d7-e256-484e-9ab8-cd40974e1238/download/agrofitprodutosformulados.csv"

    logger.info(f"Request para {url}")

    response = requests.get(url, headers=headers)

    df = pd.read_csv(BytesIO(response.content), encoding="utf-8", delimiter=";")

    # Salva na RAW
    logger.info("Preparando para salvar na RAW")
    raw_filename = f"{RAW_LAYER}/{ORIGEM}/{BASE}/{BASE}.csv"
    logger.info(f"Salvando na {raw_filename}")
    df.to_csv('gs://' + BUCKET_NAME + '/' + raw_filename,
                        storage_options={"token": credentials}, index=False, sep=";")
    logger.info(f"Salvo na RAW {raw_filename} com sucesso")

    logger.info("Tratando os dados")
    logger.info("Transformando para string")
    df = df.astype(str)
    
    # Salva na Trusted
    trusted_filename = f"/{TRUSTED_LAYER}/{ORIGEM}/{BASE}/{BASE}.parquet"
    logger.info(f"Salvando na {trusted_filename}")
    df.to_parquet('gs://' + BUCKET_NAME + trusted_filename,
                        storage_options={"token": credentials}, engine="fastparquet", index=False)
    logger.info(f"Salvo na TRUSTED {trusted_filename} com sucesso")

    logger.info("Finalizado") 