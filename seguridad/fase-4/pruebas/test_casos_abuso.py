"""Pruebas escritas desde los casos de abuso (fase 4).

Reglas:
* Cada prueba lleva @pytest.mark.caso_abuso(N), donde N es el número del issue
  del caso de abuso del que sale.
* La prueba afirma el comportamiento seguro, el «Entonces» del requerimiento.
  Por eso falla mientras la app siga vulnerable: rojo esperado en la fase 4.
* Cuando el equipo corrige la debilidad (fase 5), la prueba suma
  @pytest.mark.corregida y el gate del release exige que pase.

Ejecución local, con la app levantada (bash lab/app.sh levantar):
    pytest seguridad/fase-4/pruebas -v
"""

import pytest


@pytest.mark.caso_abuso(0)  # TODO: número del issue del caso de abuso
def test_plantilla(app_url, sesion):
    """Dado ... Cuando ... Entonces ..."""
    pytest.skip("Plantilla: reemplácela por una prueba escrita desde un caso de abuso")
