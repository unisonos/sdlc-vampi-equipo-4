## Fase 3 · Análisis estático y cadena de suministro

**Touchpoint de McGraw:** 1 (revisión de código con herramientas).
**Rol que lidera:** DevSecOps, con AppSec en la regla propia.

En esta fase el pipeline **solo reporta**: los hallazgos no detienen el PR.

### Antes de correr cada herramienta: predicción

Anoten en un comentario de este issue qué creen que va a encontrar Semgrep, Gitleaks y Dependabot en VAmPI. Después comparen. Cada hallazgo que tracen va en un issue con el formulario «Hallazgo».

### Tareas

- [ ] Copiar `lab/workflows/fase3-seguridad-pr.yml` a `.github/workflows/` y completar los TODO: Gitleaks y Dependency Review.
- [ ] Escribir una **regla propia de Semgrep** que verifique uno de sus requerimientos, con su archivo de prueba. Instrucciones en `seguridad/fase-3/semgrep/README.md`. Probarla en https://semgrep.dev/playground.
- [ ] Crear `.github/dependabot.yml` que vigile las dependencias de `app/` y las actions.
- [ ] Copiar `lab/workflows/scorecard.yml` a `.github/workflows/`.
- [ ] Endurecer **todos** los workflows: `permissions:` mínimos en el nivel superior y actions fijadas por hash de commit (`uses: org/action@<sha de 40> # vX.Y.Z`).
- [ ] Crear un ruleset para `main` que exija pull request (**Settings → Rules → Rulesets**).
- [ ] Abrir un PR con estos cambios y verlo en verde.

### Checkpoint

| Condición | Verificación |
|:---|:---|
| `fase3-seguridad-pr.yml` corre Semgrep, Gitleaks y Dependency Review | `f3.workflow` |
| Ese workflow corrió en verde sobre un pull request | `f3.pr` |
| Hay una regla propia de Semgrep con prueba que cita un requerimiento | `f3.regla` |
| `dependabot.yml` vigila `app/` | `f3.dependabot` |
| Todas las actions están fijadas por hash | `f3.fijadas` |
| Cada workflow declara `permissions` en el nivel superior | `f3.permisos` |
| Un ruleset exige PR para `main` | `f3.rama` |
| OpenSSF Scorecard corrió al menos una vez | `f3.scorecard` |

Guía: https://ic8071-sdlc-2026s2.github.io/sdlc-guia/fase-3/
