"""Con `seleccion: multianual`, fase_congelar exige las 4 ventanas juntas y no escribe nada si faltan.

Uso: python -m tests.test_seleccion_multianual (con la configuración por defecto, que es la v4)
"""
from src.comun import leer_config
from src.entrenar import fase_congelar


def test_falla_con_ventanas_incompletas():
    assert leer_config().get("seleccion") == "multianual"
    antes = leer_config()
    try:
        fase_congelar({"2": None, "3": None})
    except ValueError as e:
        assert "necesita las ventanas" in str(e)
    else:
        raise AssertionError("fase_congelar eligió con ventanas incompletas sin avisar")
    assert leer_config() == antes


if __name__ == "__main__":
    test_falla_con_ventanas_incompletas()
    print("ok: la selección multianual exige las 4 ventanas")
