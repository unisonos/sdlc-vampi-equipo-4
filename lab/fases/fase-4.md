## Fase 4 · Análisis dinámico y pruebas de abuso

**Touchpoints de McGraw:** 3 (pruebas de penetración) y 4 (pruebas basadas en riesgo).
**Rol que lidera:** Equipo rojo.

El pipeline **sigue solo reportando**. Las pruebas de abuso deben fallar mientras la app sea vulnerable: ese rojo es lo esperado.

### Predicción

Antes de correr ZAP, anoten en este issue qué alertas esperan. ¿Qué debilidades de sus casos de abuso puede ver un escáner dinámico y cuáles no?

### Tareas

- [ ] Copiar `lab/workflows/fase4-dast.yml` a `.github/workflows/` y completar el paso de ZAP. Esta app usa el modo indicado en `ZAP_MODO` de `lab/app.env`.
- [ ] Escribir al menos **3 pruebas pytest** en `seguridad/fase-4/pruebas/`, cada una desde un caso de abuso y marcada con `@pytest.mark.caso_abuso(N)`.
- [ ] Correrlas en el Codespace contra la app levantada antes de subirlas.
- [ ] Registrar como «Hallazgo» lo que encontraron Semgrep, Gitleaks, Dependabot, ZAP y las pruebas. Al menos 4 hallazgos trazados, de al menos 3 herramientas.
- [ ] Decidir en cada hallazgo: corregir, aceptar con justificación o falso positivo. Elegir al menos 3 para corregir en la fase 5.

### Checkpoint

| Condición | Verificación |
|:---|:---|
| `fase4-dast.yml` corre ZAP y pytest y terminó en verde | `f4.dast` |
| Al menos 3 pruebas marcadas con un caso de abuso existente | `f4.pruebas` |
| Al menos 4 hallazgos trazados de 3 herramientas distintas | `f4.hallazgos` |

Guía: https://ic8071-sdlc-2026s2.github.io/sdlc-guia/fase-4/
