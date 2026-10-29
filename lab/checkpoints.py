#!/usr/bin/env python3
"""Checkpoints automáticos del Laboratorio SDLC Seguro (IC-8071).

Evalúa las condiciones de cada fase leyendo el repositorio del equipo por la
API de GitHub. El mismo script corre en dos lugares:

* En el repositorio del equipo (workflow «Checkpoints»): da retroalimentación,
  sincroniza etiquetas y desbloquea el issue de la fase siguiente.
* En el verificador central (repositorio sdlc-guia): calcula la nota de
  checkpoints sin depender de archivos que el equipo pueda modificar.

Solo usa la biblioteca estándar de Python 3.9 o superior.

Ejemplos:
  python3 lab/checkpoints.py --repo org/sdlc-vampi-equipo-1 --salida estado.json
  python3 lab/checkpoints.py --repo org/sdlc-vampi-equipo-1 --desbloquear --sitio _site
  python3 lab/checkpoints.py --lote equipos.json --salida tablero/estado.json
"""

import argparse
import base64
import datetime
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")

# Umbrales de cada checkpoint. Ajustables entre semestres.
MIN_MIEMBROS = 4
MIN_CASOS = 6
MIN_CATEGORIAS = 5
MIN_REQUERIMIENTOS = 6
MIN_RIESGOS = 6
MIN_PRUEBAS = 3
MIN_HALLAZGOS = 4
MIN_HERRAMIENTAS = 3
MIN_CORREGIDAS = 3

FASES = [
    (0, "Arranque"),
    (1, "Casos de abuso y requerimientos"),
    (2, "Análisis de riesgo arquitectónico"),
    (3, "Análisis estático y cadena de suministro"),
    (4, "Análisis dinámico y pruebas de abuso"),
    (5, "Release firmado y gate"),
]

CATEGORIAS = {
    "S": "stride:S",
    "T": "stride:T",
    "R": "stride:R",
    "I": "stride:I",
    "D": "stride:D",
    "E": "stride:E",
    "Cadena de suministro": "cadena-suministro",
    "Configuración": "configuracion",
}

HERRAMIENTAS = {
    "Semgrep": "herramienta:semgrep",
    "Gitleaks": "herramienta:gitleaks",
    "Dependabot o Dependency Review": "herramienta:sca",
    "ZAP": "herramienta:zap",
    "Trivy": "herramienta:trivy",
    "Prueba pytest": "herramienta:pytest",
    "Revisión manual": "herramienta:manual",
    "Equipo rojo": "herramienta:equipo-rojo",
}

ETIQUETAS = {
    "caso-de-abuso": ("b60205", "Caso de abuso (fase 1)"),
    "requerimiento": ("0e8a16", "Requerimiento de seguridad ASVS (fase 1)"),
    "hallazgo": ("d93f0b", "Hallazgo de una herramienta o revisión"),
    "corregir": ("5319e7", "Hallazgo trazado que el equipo corrige"),
    "stride:S": ("f9d0c4", "Suplantación"),
    "stride:T": ("f9d0c4", "Manipulación"),
    "stride:R": ("f9d0c4", "Repudio"),
    "stride:I": ("f9d0c4", "Divulgación de información"),
    "stride:D": ("f9d0c4", "Denegación de servicio"),
    "stride:E": ("f9d0c4", "Elevación de privilegios"),
    "cadena-suministro": ("f9d0c4", "Cadena de suministro"),
    "configuracion": ("f9d0c4", "Configuración"),
}
for _n in range(1, 18):
    ETIQUETAS[f"asvs:V{_n}"] = ("c2e0c6", f"Capítulo V{_n} de ASVS 5.0")
for _n, _ in FASES:
    ETIQUETAS[f"fase-{_n}"] = ("1d76db", f"Issue de la fase {_n}")
for _h in HERRAMIENTAS.values():
    ETIQUETAS[_h] = ("fbca04", "Herramienta que produjo el hallazgo")

RE_SHA = re.compile(r"@[0-9a-f]{40}\b")
RE_REF = re.compile(r"#(\d+)")


class GitHub:
    def __init__(self, repo, token):
        self.repo = repo
        self.token = token
        self.cache = {}

    def _pedir(self, metodo, url, datos=None):
        if not url.startswith("http"):
            url = API + url
        cuerpo = json.dumps(datos).encode() if datos is not None else None
        req = urllib.request.Request(url, data=cuerpo, method=metodo)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("User-Agent", "lab-sdlc-checkpoints")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        if cuerpo is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                texto = r.read().decode()
                return r.status, (json.loads(texto) if texto else None), r.headers
        except urllib.error.HTTPError as e:
            return e.code, None, e.headers

    def get(self, ruta, **params):
        url = f"/repos/{self.repo}{ruta}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        if url not in self.cache:
            estado, datos, _ = self._pedir("GET", url)
            self.cache[url] = datos if estado == 200 else None
        return self.cache[url]

    def paginar(self, ruta, limite=10, **params):
        params.setdefault("per_page", 100)
        url = f"/repos/{self.repo}{ruta}?" + urllib.parse.urlencode(params)
        todo = []
        for _ in range(limite):
            estado, datos, cab = self._pedir("GET", url)
            if estado != 200 or not datos:
                break
            todo.extend(datos)
            sig = re.search(r'<([^>]+)>;\s*rel="next"', cab.get("Link", "") or "")
            if not sig:
                break
            url = sig.group(1)
        return todo

    def post(self, ruta, datos):
        return self._pedir("POST", f"/repos/{self.repo}{ruta}", datos)[:2]

    def patch(self, ruta, datos):
        return self._pedir("PATCH", f"/repos/{self.repo}{ruta}", datos)[:2]

    def archivo(self, ruta):
        datos = self.get(f"/contents/{urllib.parse.quote(ruta)}")
        if not isinstance(datos, dict) or datos.get("type") != "file":
            return None
        if datos.get("encoding") == "base64" and datos.get("content"):
            return base64.b64decode(datos["content"]).decode("utf-8", "replace")
        if datos.get("download_url"):
            try:
                with urllib.request.urlopen(datos["download_url"], timeout=30) as r:
                    return r.read().decode("utf-8", "replace")
            except urllib.error.URLError:
                return None
        return ""

    def listar(self, ruta):
        datos = self.get(f"/contents/{urllib.parse.quote(ruta)}")
        return [d["name"] for d in datos] if isinstance(datos, list) else []

    def corridas_exitosas(self, archivo, **filtro):
        datos = self.get(f"/actions/workflows/{archivo}/runs", status="success", per_page=1, **filtro)
        return (datos or {}).get("total_count", 0)

    def commits_de(self, ruta):
        return self.paginar("/commits", limite=2, path=ruta)


def secciones(cuerpo):
    """Convierte el cuerpo de un issue creado con formulario en un diccionario."""
    partes = re.split(r"^###\s+(.+?)\s*$", cuerpo or "", flags=re.M)
    campos = {}
    for titulo, valor in zip(partes[1::2], partes[2::2]):
        valor = valor.strip()
        campos[titulo.strip().lower()] = "" if valor == "_No response_" else valor
    return campos


def campo(campos, prefijo):
    for clave, valor in campos.items():
        if clave.startswith(prefijo):
            return valor
    return ""


def con_gherkin(texto):
    """Cada palabra clave abre una línea con al menos dos palabras propias."""
    return all(re.search(rf"^\s*{k}\b[ \t]+\S+[ \t]+\S+", texto or "", re.I | re.M)
               for k in ("dado", "cuando", "entonces"))


def sin_comentarios(texto):
    return "\n".join(re.sub(r"(^|\s)#.*$", "", l) for l in (texto or "").splitlines())


def referencias(texto):
    return {int(n) for n in RE_REF.findall(texto or "")}


def tabla_markdown(texto):
    """Devuelve las filas de la primera tabla Markdown como diccionarios."""
    lineas = [l.strip() for l in (texto or "").splitlines() if l.strip().startswith("|")]
    if len(lineas) < 2:
        return []
    celdas = lambda l: [c.strip() for c in l.strip("|").split("|")]
    encabezado = [c.lower() for c in celdas(lineas[0])]
    filas = []
    for linea in lineas[2:]:
        valores = celdas(linea)
        filas.append(dict(zip(encabezado, valores)))
    return filas


def columna(fila, prefijo):
    for clave, valor in fila.items():
        if clave.startswith(prefijo):
            return valor
    return ""


def entero(texto):
    m = re.search(r"\d+", texto or "")
    return int(m.group()) if m else None


class Evaluacion:
    def __init__(self, gh):
        self.gh = gh
        self.checks = {n: [] for n, _ in FASES}
        repo = gh.get("") or {}
        self.rama = repo.get("default_branch", "main")
        self.repo_info = repo
        issues = [i for i in gh.paginar("/issues", state="all") if "pull_request" not in i]
        self.issues = {i["number"]: i for i in issues}
        self.por_etiqueta = {}
        for i in issues:
            for e in i.get("labels", []):
                self.por_etiqueta.setdefault(e["name"], []).append(i)

    def check(self, fase, ident, descripcion, ok, detalle=""):
        self.checks[fase].append(
            {"id": ident, "descripcion": descripcion, "ok": bool(ok), "detalle": detalle}
        )

    def de_tipo(self, etiqueta):
        return self.por_etiqueta.get(etiqueta, [])

    # Fase 0 ---------------------------------------------------------------
    def fase0(self):
        filas = tabla_markdown(self.gh.archivo("EQUIPO.md"))
        miembros = [
            f for f in filas
            if re.fullmatch(r"@?[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", columna(f, "usuario"))
            and columna(f, "usuario").lstrip("@").lower() not in {"usuario", "tu-usuario"}
        ]
        self.check(0, "f0.equipo", f"EQUIPO.md lista al menos {MIN_MIEMBROS} integrantes con usuario de GitHub",
                   len(miembros) >= MIN_MIEMBROS, f"{len(miembros)} integrantes")
        n = self.gh.corridas_exitosas("fase0-ci.yml", branch=self.rama)
        self.check(0, "f0.ci", "El workflow «Fase 0 · CI» terminó en verde en la rama principal",
                   n > 0, f"{n} corridas exitosas")
        self.check(0, "f0.pages", "GitHub Pages está activado (fuente: GitHub Actions)",
                   self.repo_info.get("has_pages"), "")

    # Fase 1 ---------------------------------------------------------------
    def fase1(self):
        casos = self.de_tipo("caso-de-abuso")
        reqs = self.de_tipo("requerimiento")
        numeros_req = {r["number"] for r in reqs}
        self.check(1, "f1.casos", f"Al menos {MIN_CASOS} casos de abuso",
                   len(casos) >= MIN_CASOS, f"{len(casos)} casos")
        categorias = {campo(secciones(c["body"]), "categoría") for c in casos} - {""}
        self.check(1, "f1.categorias", f"Los casos cubren al menos {MIN_CATEGORIAS} categorías distintas",
                   len(categorias) >= MIN_CATEGORIAS, ", ".join(sorted(categorias)) or "ninguna")
        sin_gherkin = [c["number"] for c in casos if not con_gherkin(campo(secciones(c["body"]), "escenario"))]
        self.check(1, "f1.gherkin", "Cada caso de abuso tiene escenario Dado, Cuando, Entonces",
                   casos and not sin_gherkin, f"faltan: {sin_gherkin}" if sin_gherkin else "")
        con_carta = [c for c in casos if campo(secciones(c["body"]), "carta")]
        self.check(1, "f1.cornucopia", "Cada caso de abuso cita su carta de Cornucopia",
                   casos and len(con_carta) == len(casos), f"{len(con_carta)} de {len(casos)}")
        validos = [r for r in reqs
                   if re.search(r"(?<![\d.])V?\d{1,2}\.\d{1,2}\.\d{1,2}(?![\d.])", campo(secciones(r["body"]), "identificador"), re.I)]
        self.check(1, "f1.requerimientos", f"Al menos {MIN_REQUERIMIENTOS} requerimientos con identificador ASVS 5.0",
                   len(validos) >= MIN_REQUERIMIENTOS, f"{len(validos)} válidos de {len(reqs)}")
        sin_enlace = [c["number"] for c in casos
                      if not referencias(campo(secciones(c["body"]), "requerimiento")) & numeros_req]
        self.check(1, "f1.trazabilidad", "Cada caso de abuso enlaza al menos un requerimiento existente",
                   casos and not sin_enlace, f"sin enlace: {sin_enlace}" if sin_enlace else "")

    # Fase 2 ---------------------------------------------------------------
    def fase2(self):
        ruta = "seguridad/fase-2/dfd.drawio.svg"
        svg = self.gh.archivo(ruta) or ""
        editado = len(self.gh.commits_de(ruta)) >= 2
        self.check(2, "f2.dfd", "El DFD fue editado e incluye al menos una frontera de confianza",
                   editado and "frontera" in svg.lower(),
                   "sin editar" if not editado else ("sin «frontera»" if "frontera" not in svg.lower() else ""))
        filas = tabla_markdown(self.gh.archivo("seguridad/fase-2/matriz-riesgos.md"))
        validas, casos_citados = [], set()
        for f in filas:
            p, i, r = (entero(columna(f, k)) for k in ("probabilidad", "impacto", "riesgo"))
            refs = referencias(columna(f, "caso"))
            if p in (1, 2, 3) and i in (1, 2, 3) and r == p * i and refs:
                validas.append(f)
                casos_citados |= refs
        self.check(2, "f2.matriz", f"La matriz 3 por 3 tiene al menos {MIN_RIESGOS} riesgos con P × I correcto y caso de abuso",
                   len(validas) >= MIN_RIESGOS, f"{len(validas)} filas válidas")
        casos = {c["number"] for c in self.de_tipo("caso-de-abuso")}
        faltan = sorted(casos - casos_citados)
        self.check(2, "f2.cobertura", "Todos los casos de abuso aparecen en la matriz",
                   casos and not faltan, f"faltan: {faltan}" if faltan else "")

    # Fase 3 ---------------------------------------------------------------
    def workflows(self):
        return {n: sin_comentarios(self.gh.archivo(f".github/workflows/{n}"))
                for n in self.gh.listar(".github/workflows") if n.endswith((".yml", ".yaml"))}

    def fase3(self):
        wfs = self.workflows()
        pr = wfs.get("fase3-seguridad-pr.yml", "")
        herramientas = all(h in pr.lower() for h in ("semgrep", "gitleaks", "dependency-review"))
        self.check(3, "f3.workflow", "fase3-seguridad-pr.yml corre Semgrep, Gitleaks y Dependency Review",
                   herramientas, "")
        n = self.gh.corridas_exitosas("fase3-seguridad-pr.yml", event="pull_request")
        self.check(3, "f3.pr", "El workflow de seguridad corrió en verde sobre un pull request",
                   n > 0, f"{n} corridas")
        reqs = {r["number"] for r in self.de_tipo("requerimiento")}
        archivos = self.gh.listar("seguridad/fase-3/semgrep")
        reglas = []
        for nombre in archivos:
            if not nombre.endswith((".yml", ".yaml")):
                continue
            base = nombre.rsplit(".", 1)[0]
            texto = self.gh.archivo(f"seguridad/fase-3/semgrep/{nombre}") or ""
            m = re.search(r"requerimiento:\s*['\"]?#?(\d+)", texto)
            prueba = [a for a in archivos if a.startswith(base + ".") and not a.endswith((".yml", ".yaml"))]
            con_ruleid = any("ruleid:" in (self.gh.archivo(f"seguridad/fase-3/semgrep/{a}") or "") for a in prueba)
            if m and int(m.group(1)) in reqs and con_ruleid:
                reglas.append(nombre)
        self.check(3, "f3.regla", "Hay una regla propia de Semgrep con prueba que verifica un requerimiento",
                   reglas, ", ".join(reglas))
        dep = self.gh.archivo(".github/dependabot.yml") or self.gh.archivo(".github/dependabot.yaml") or ""
        self.check(3, "f3.dependabot", "dependabot.yml vigila las dependencias de app/",
                   re.search(r"directory:\s*['\"]?/app", dep), "")
        sin_fijar = []
        for nombre, texto in wfs.items():
            for linea in texto.splitlines():
                m = re.match(r"\s*-?\s*uses:\s*(\S+)", linea)
                if m and not m.group(1).startswith("./") and not RE_SHA.search(m.group(1)):
                    sin_fijar.append(f"{nombre}: {m.group(1)}")
        self.check(3, "f3.fijadas", "Todas las actions están fijadas por hash de commit",
                   wfs and not sin_fijar, "; ".join(sin_fijar[:5]))
        sin_permisos = [n for n, t in wfs.items() if not re.search(r"^permissions:", t, re.M)]
        self.check(3, "f3.permisos", "Cada workflow declara permissions en el nivel superior",
                   wfs and not sin_permisos, ", ".join(sin_permisos))
        reglas_rama = self.gh.get(f"/rules/branches/{self.rama}") or []
        tipos = {r.get("type") for r in reglas_rama}
        self.check(3, "f3.rama", "Un ruleset exige pull request para integrar a la rama principal",
                   "pull_request" in tipos, ", ".join(sorted(t for t in tipos if t)))
        sc = [n for n, t in wfs.items() if "ossf/scorecard-action" in t]
        n_sc = sum(self.gh.corridas_exitosas(n) for n in sc)
        self.check(3, "f3.scorecard", "OpenSSF Scorecard corrió al menos una vez",
                   n_sc > 0, f"{n_sc} corridas")

    # Fase 4 ---------------------------------------------------------------
    def pruebas(self):
        textos = []
        for nombre in self.gh.listar("seguridad/fase-4/pruebas"):
            if nombre.startswith("test_") and nombre.endswith(".py"):
                textos.append(self.gh.archivo(f"seguridad/fase-4/pruebas/{nombre}") or "")
        return "\n".join(textos)

    def fase4(self):
        dast = sin_comentarios(self.gh.archivo(".github/workflows/fase4-dast.yml"))
        n = self.gh.corridas_exitosas("fase4-dast.yml")
        self.check(4, "f4.dast", "fase4-dast.yml corre ZAP y pytest y terminó en verde",
                   "zaproxy" in dast.lower() and "zap-" in dast.lower() and "pytest" in dast and n > 0, f"{n} corridas")
        casos = {c["number"] for c in self.de_tipo("caso-de-abuso")}
        codigo = self.pruebas()
        marcadas = [int(x) for x in re.findall(r"@pytest\.mark\.caso_abuso\(\s*(\d+)\s*\)", codigo)]
        validas = [x for x in marcadas if x in casos]
        self.check(4, "f4.pruebas", f"Al menos {MIN_PRUEBAS} pruebas marcadas con un caso de abuso existente",
                   len(validas) >= MIN_PRUEBAS, f"{len(validas)} pruebas")
        hallazgos = self.de_tipo("hallazgo")
        trazados = [h for h in hallazgos if referencias(campo(secciones(h["body"]), "trazabilidad"))]
        herramientas = {campo(secciones(h["body"]), "herramienta") for h in trazados} - {""}
        self.check(4, "f4.hallazgos",
                   f"Al menos {MIN_HALLAZGOS} hallazgos trazados de {MIN_HERRAMIENTAS} herramientas distintas",
                   len(trazados) >= MIN_HALLAZGOS and len(herramientas) >= MIN_HERRAMIENTAS,
                   f"{len(trazados)} hallazgos, {len(herramientas)} herramientas")

    # Fase 5 ---------------------------------------------------------------
    def fase5(self):
        rel = sin_comentarios(self.gh.archivo(".github/workflows/fase5-release.yml")).lower()
        partes = all(p in rel for p in ("trivy", "sbom", "cosign", "attest-build-provenance"))
        n = self.gh.corridas_exitosas("fase5-release.yml")
        self.check(5, "f5.release", "fase5-release.yml escanea, genera SBOM, firma, atesta y terminó en verde",
                   partes and n > 0, f"{n} corridas")
        releases = self.gh.get("/releases") or []
        con_sbom = [r["tag_name"] for r in releases if any("sbom" in a["name"].lower() for a in r.get("assets", []))]
        self.check(5, "f5.sbom", "Un GitHub Release publica el SBOM", con_sbom, ", ".join(con_sbom[:3]))
        digest = next((m.group() for r in releases for m in [re.search(r"sha256:[0-9a-f]{64}", r.get("body") or "")] if m), "")
        atestaciones = (self.gh.get(f"/attestations/{digest}") or {}).get("attestations", []) if digest else []
        self.check(5, "f5.attestation", "El digest de la imagen del release tiene attestations verificables en GitHub",
                   atestaciones, f"{len(atestaciones)} attestations" if digest else "el release no cita el digest sha256")
        corregidas = len(re.findall(r"@pytest\.mark\.corregida\b", self.pruebas()))
        cerrados = [h for h in self.de_tipo("hallazgo")
                    if h["state"] == "closed" and campo(secciones(h["body"]), "decisión").startswith("Corregir")]
        self.check(5, "f5.correcciones",
                   f"Al menos {MIN_CORREGIDAS} debilidades trazadas corregidas (prueba «corregida» e issue cerrado)",
                   corregidas >= MIN_CORREGIDAS and len(cerrados) >= MIN_CORREGIDAS,
                   f"{corregidas} pruebas, {len(cerrados)} issues")
        ignorados = self.gh.archivo("seguridad/fase-5/.trivyignore.yaml") or ""
        ids = len(re.findall(r"^\s*-\s*id:", ignorados, re.M))
        valores = re.findall(r"^[ \t]*statement:[ \t]*(.*)$", ignorados, re.M)
        just = sum(1 for v in valores if v.strip().strip("'\"").strip())
        self.check(5, "f5.lineabase", "Cada excepción de la línea base tiene justificación",
                   ids == just, f"{ids} excepciones, {just} justificadas")
        ruta = "seguridad/fase-5/presentacion.md"
        texto = self.gh.archivo(ruta) or ""
        self.check(5, "f5.presentacion", "La presentación está completa",
                   len(self.gh.commits_de(ruta)) >= 2 and "COMPLETAR" not in texto, "")

    def reflexiones(self):
        salida = []
        for nombre in self.gh.listar("seguridad/reflexiones"):
            if not nombre.endswith(".md") or nombre.lower() in {"readme.md", "plantilla.md"}:
                continue
            autores = {(c.get("author") or {}).get("login", "").lower() for c in self.gh.commits_de(f"seguridad/reflexiones/{nombre}")}
            usuario = nombre[:-3].lower()
            salida.append({"archivo": nombre, "autor_coincide": usuario in autores})
        return salida

    def evaluar(self):
        for n, _ in FASES:
            getattr(self, f"fase{n}")()
        fases = []
        for n, nombre in FASES:
            checks = self.checks[n]
            logrados = sum(c["ok"] for c in checks)
            fases.append({"id": n, "nombre": nombre, "completa": logrados == len(checks),
                          "logro": round(logrados / len(checks), 3) if checks else 0, "checks": checks})
        actual = next((f["id"] for f in fases if not f["completa"]), len(FASES))
        app = re.search(r'^APP_NOMBRE="?([^"\n]+)', self.gh.archivo("lab/app.env") or "", re.M)
        return {
            "repo": self.gh.repo,
            "app": app.group(1) if app else "",
            "generado": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "fase_actual": actual,
            "puntaje": round(sum(f["logro"] for f in fases) / len(fases) * 100, 1),
            "fases": fases,
            "reflexiones": self.reflexiones(),
        }


def sincronizar(ev, estado):
    """Crea etiquetas, etiqueta issues según sus formularios y desbloquea fases."""
    gh = ev.gh
    existentes = {e["name"] for e in gh.paginar("/labels")}
    for nombre, (color, desc) in ETIQUETAS.items():
        if nombre not in existentes:
            gh.post("/labels", {"name": nombre, "color": color, "description": desc})
    for issue in ev.issues.values():
        campos = secciones(issue.get("body"))
        tiene = {e["name"] for e in issue.get("labels", [])}
        nuevas = set()
        cat = campo(campos, "categoría")
        if cat:
            clave = cat.split(" ")[0] if cat[:1] in "STRIDE" and cat[1:2] in " ·" else cat
            if clave in CATEGORIAS:
                nuevas.add(CATEGORIAS[clave])
        cap = re.match(r"V(\d{1,2})\b", campo(campos, "capítulo"))
        if cap:
            nuevas.add(f"asvs:V{cap.group(1)}")
        herramienta = campo(campos, "herramienta")
        if herramienta in HERRAMIENTAS:
            nuevas.add(HERRAMIENTAS[herramienta])
        if campo(campos, "decisión").startswith("Corregir"):
            nuevas.add("corregir")
        if nuevas - tiene:
            gh.post(f"/issues/{issue['number']}/labels", {"labels": sorted(nuevas - tiene)})
    for fase in estado["fases"]:
        n = fase["id"]
        abiertas = [i for i in ev.de_tipo(f"fase-{n}") if i["title"].startswith(f"Fase {n}")]
        desbloqueada = n == 0 or estado["fases"][n - 1]["completa"]
        if desbloqueada and not abiertas:
            cuerpo = gh.archivo(f"lab/fases/fase-{n}.md") or f"Instrucciones de la fase {n}."
            gh.post("/issues", {"title": f"Fase {n} · {fase['nombre']}", "body": cuerpo, "labels": [f"fase-{n}"]})
        for issue in abiertas:
            if fase["completa"] and issue["state"] == "open":
                gh.post(f"/issues/{issue['number']}/comments",
                        {"body": f"Checkpoint de la fase {n} superado. Se desbloquea la fase siguiente."})
                gh.patch(f"/issues/{issue['number']}", {"state": "closed", "state_reason": "completed"})


def resumen_markdown(estado):
    lineas = [f"## Checkpoints de {estado['repo']}", "",
              f"Puntaje de checkpoints: **{estado['puntaje']} %**. Fase actual: **{estado['fase_actual']}**.", ""]
    for f in estado["fases"]:
        marca = "completa" if f["completa"] else f"{int(f['logro'] * 100)} %"
        lineas += [f"### Fase {f['id']} · {f['nombre']} ({marca})", "", "| | Condición | Detalle |", "|:--|:--|:--|"]
        for c in f["checks"]:
            lineas.append(f"| {'✅' if c['ok'] else '❌'} | {c['descripcion']} | {c['detalle']} |")
        lineas.append("")
    return "\n".join(lineas)


def sitio(estado, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    with open(os.path.join(carpeta, "estado.json"), "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
    filas = []
    for fase in estado["fases"]:
        items = "".join(
            f"<li class='{'ok' if c['ok'] else 'no'}'>{html.escape(c['descripcion'])}"
            f"<small>{html.escape(c['detalle'])}</small></li>" for c in fase["checks"])
        filas.append(f"<section><h2>Fase {fase['id']} · {html.escape(fase['nombre'])}"
                     f"<span>{int(fase['logro'] * 100)} %</span></h2><ul>{items}</ul></section>")
    reportes = []
    raiz = os.path.join(carpeta, "reportes")
    if os.path.isdir(raiz):
        for dirpath, _, archivos in sorted(os.walk(raiz)):
            for a in sorted(archivos):
                rel = os.path.relpath(os.path.join(dirpath, a), carpeta)
                reportes.append(f"<li><a href='{html.escape(rel)}'>{html.escape(rel)}</a></li>")
    pagina = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reporte {html.escape(estado['repo'])}</title>
<style>
:root{{--fondo:#fafaf9;--texto:#1c1917;--suave:#78716c;--ok:#15803d;--no:#b91c1c;--borde:#e7e5e4}}
@media (prefers-color-scheme:dark){{:root{{--fondo:#1c1917;--texto:#f5f5f4;--suave:#a8a29e;--ok:#4ade80;--no:#f87171;--borde:#44403c}}}}
body{{font:16px/1.5 system-ui,sans-serif;background:var(--fondo);color:var(--texto);max-width:56rem;margin:0 auto;padding:1.5rem 1rem}}
h1{{font-size:1.5rem;margin:0 0 .25rem}} h2{{font-size:1.05rem;display:flex;justify-content:space-between;border-bottom:1px solid var(--borde);padding-bottom:.25rem}}
ul{{list-style:none;padding:0}} li{{padding:.2rem 0}} li::before{{content:"✗ ";color:var(--no)}} li.ok::before{{content:"✓ ";color:var(--ok)}}
small{{color:var(--suave);margin-left:.5rem}} p{{color:var(--suave)}}
</style></head><body>
<h1>{html.escape(estado['app'] or estado['repo'])}</h1>
<p>{html.escape(estado['repo'])} · checkpoints {estado['puntaje']} % · generado {html.escape(estado['generado'])}</p>
{''.join(filas)}
<section><h2>Reportes del pipeline</h2><ul>{''.join(reportes) or '<li class=ok>Todavía no hay reportes publicados.</li>'}</ul></section>
</body></html>"""
    with open(os.path.join(carpeta, "index.html"), "w", encoding="utf-8") as f:
        f.write(pagina)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    p.add_argument("--lote", help="JSON con [{\"equipo\": ..., \"repo\": ...}] para el verificador central")
    p.add_argument("--salida", help="archivo JSON de salida")
    p.add_argument("--sitio", help="carpeta donde escribir index.html y estado.json para GitHub Pages")
    p.add_argument("--desbloquear", action="store_true", help="sincroniza etiquetas y abre el issue de la fase siguiente")
    args = p.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    if args.lote:
        with open(args.lote, encoding="utf-8") as f:
            equipos = json.load(f)
        resultados = []
        for e in equipos:
            estado = Evaluacion(GitHub(e["repo"], token)).evaluar()
            estado["equipo"] = e.get("equipo", e["repo"])
            resultados.append(estado)
            print(f"{estado['equipo']}: {estado['puntaje']} %", file=sys.stderr)
        if args.salida:
            with open(args.salida, "w", encoding="utf-8") as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
        return 0

    if not args.repo:
        p.error("falta --repo o la variable GITHUB_REPOSITORY")
    ev = Evaluacion(GitHub(args.repo, token))
    estado = ev.evaluar()
    if args.desbloquear:
        sincronizar(ev, estado)
    texto = resumen_markdown(estado)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    if args.salida:
        with open(args.salida, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
    if args.sitio:
        sitio(estado, args.sitio)
    return 0


if __name__ == "__main__":
    sys.exit(main())
