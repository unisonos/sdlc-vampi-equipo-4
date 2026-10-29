"""Fixtures comunes de las pruebas de abuso.

La URL de la app sale de la variable APP_URL. Si no existe, se arma con el
puerto de lab/app.env, el mismo que usa bash lab/app.sh.
"""

import os
import re
from pathlib import Path

import pytest
import requests

RAIZ = Path(__file__).resolve().parents[3]


def _puerto():
    texto = (RAIZ / "lab" / "app.env").read_text(encoding="utf-8")
    return re.search(r"^APP_PUERTO=(\d+)", texto, re.M).group(1)


@pytest.fixture(scope="session")
def app_url():
    url = os.environ.get("APP_URL") or f"http://localhost:{_puerto()}"
    return url.rstrip("/")


@pytest.fixture
def sesion():
    with requests.Session() as s:
        s.headers["User-Agent"] = "lab-sdlc-pruebas-de-abuso"
        yield s
