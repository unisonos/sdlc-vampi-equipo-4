# Laboratorio SDLC Seguro · VAmPI

IC-8071 Seguridad del Software. Este repositorio es de su equipo. Contiene VAmPI, una aplicación intencionalmente vulnerable mantenida por la comunidad, y la estructura para llevarla por el ciclo de vida de desarrollo seguro: casos de abuso, requerimientos, análisis de riesgo arquitectónico, SAST, SCA, DAST y un release firmado.

> **Advertencia.** La app de `app/` es vulnerable a propósito. Úsela solo dentro de su Codespace o en el runner de Actions. No haga público el puerto del Codespace y no la despliegue en ningún servidor.

## La app

| | |
|:---|:---|
| Proyecto original | [VAmPI](https://github.com/erev0s/VAmPI) |
| Versión fijada | master (f16052dce83f05847133ec98f01c5193a41de7d8) |
| Stack | Python 3.11, Flask y Connexion; SQLite; API REST con OpenAPI, sin interfaz web |
| Licencia | MIT, ver `app/` y `app/ORIGEN.md` |

El código de `app/` es el del proyecto original sin cambios. Las correcciones que haga el equipo en la fase 5 quedan en el historial de este repositorio.

## Empezar: fase 0

1. Abra el Codespace: **Code → Codespaces → Create codespace on main**. Tarda unos minutos la primera vez.
2. Complete `EQUIPO.md` con nombres, usuarios de GitHub y la rotación de roles. Haga commit y push. Ese push corre los checkpoints y abre el issue **Fase 0**.
3. Active GitHub Pages: **Settings → Pages → Source: GitHub Actions**. Ahí se publica el reporte del equipo.
4. Levante la app en el Codespace:

   ```bash
   bash lab/app.sh levantar   # construye desde app/ y la levanta
   bash lab/app.sh rapido     # usa la imagen oficial si existe; más rápido
   bash lab/app.sh detener
   ```

5. Revise la pestaña **Actions**: «Fase 0 · CI» debe terminar en verde.

## Cómo se avanza

Cada fase llega como un issue. Cuando el workflow «Checkpoints» verifica que la fase está completa, cierra ese issue y abre el de la fase siguiente. El resumen de cada corrida queda en Actions y en la página del equipo en GitHub Pages.

| Fase | Qué se entrega | Dónde |
|:---|:---|:---|
| 0 | Equipo, Codespace y primer pipeline en verde | `EQUIPO.md`, Actions |
| 1 | Casos de abuso y requerimientos ASVS, enlazados entre sí | Issues con formulario |
| 2 | DFD con fronteras de confianza y matriz de riesgos 3 por 3 | `seguridad/fase-2/` |
| 3 | SAST, secretos, dependencias, regla propia de Semgrep y pipeline endurecido | `.github/`, `seguridad/fase-3/` |
| 4 | ZAP y pruebas automáticas escritas desde los casos de abuso | `.github/workflows/fase4-dast.yml`, `seguridad/fase-4/` |
| 5 | Imagen firmada, SBOM, procedencia, gate y presentación | `.github/workflows/fase5-release.yml`, `seguridad/fase-5/` |

La guía completa de cada fase está en https://ic8071-sdlc-2026s2.github.io/sdlc-guia/.

## Estructura

```
app/                  código de VAmPI (master (f16052dce83f05847133ec98f01c5193a41de7d8))
lab/                  infraestructura del laboratorio: app.sh, checkpoints, plantillas de workflows
seguridad/            artefactos del equipo por fase y reflexiones individuales
.github/              formularios de issues y workflows
.devcontainer/        configuración del Codespace
EQUIPO.md             integrantes y rotación de roles
```

## Reglas del repositorio

- Desde la fase 3, todo cambio a `main` entra por pull request.
- Cada persona escribe y sube su propia reflexión con su usuario: el commit es la evidencia.
- No borre issues ni reescriba el historial de `main`. Si algo sobra, ciérrelo con un comentario.
- No modifique `lab/checkpoints.py` ni `.github/workflows/checkpoints.yml`. La nota de checkpoints la calcula un verificador central con su propia copia.

## Plan B sin Codespaces

Si el Codespace no abre, presione la tecla `.` en la página del repositorio para editar en github.dev. Ahí no se puede levantar la app, pero todos los workflows corren en Actions: la app se construye, se escanea y se prueba en el runner.
