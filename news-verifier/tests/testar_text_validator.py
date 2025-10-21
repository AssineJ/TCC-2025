import pathlib
import sys

import pytest

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.text_validator import validar_qualidade_texto


@pytest.mark.parametrize(
    "texto, mensagem_esperada",
    [
        (
            "fake " * 12,
            "Palavra",
        ),
        (
            "O governo anunciou corte de gastos " * 3,
            "Sequência repetida",
        ),
    ],
)
def test_detecta_textos_com_palavras_ou_frases_repetidas(texto, mensagem_esperada):
    resultado = validar_qualidade_texto(texto)

    assert resultado["valido"] is False
    assert "dados fornecidos insuficientes"in resultado["motivo"].lower()
    assert any(mensagem_esperada in problema for problema in resultado["problemas"])


def test_detecta_texto_sem_contexto_repleto_de_palavras_curtas():
    texto = "de " * 40

    resultado = validar_qualidade_texto(texto)

    assert resultado["valido"] is False
    assert "dados fornecidos insuficientes"in resultado["motivo"].lower()
    assert any(
        "fora de contexto"in problema.lower() or "muitas palavras soltas"in problema.lower()
        for problema in resultado["problemas"]
    )
