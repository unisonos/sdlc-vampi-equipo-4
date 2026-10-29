## Fase 1 · Casos de abuso y requerimientos

**Touchpoints de McGraw:** 5 (casos de abuso) y 6 (requerimientos de seguridad).
**Rol que lidera:** AppSec.

### Tareas

- [ ] Leer `seguridad/fase-1/mapa-de-la-app.md`: componentes, roles y datos de VAmPI.
- [ ] Jugar una ronda de OWASP Cornucopia en https://copi.owasp.org (edición Website App). Por cada carta que aplique a la app, anotar la idea.
- [ ] Crear al menos **6 casos de abuso** con el formulario «Caso de abuso». Que cubran al menos **5 categorías** distintas (S, T, R, I, D, E, cadena de suministro, configuración).
- [ ] Crear al menos **6 requerimientos** con el formulario «Requerimiento de seguridad», tomados de ASVS 5.0 nivel 1. Si una debilidad no tiene requerimiento de nivel 1 (bitácoras, límite de peticiones, HttpOnly, secretos), use el de nivel 2.
- [ ] Enlazar: cada caso de abuso cita sus requerimientos (#n) y cada requerimiento cita los casos que mitiga.

El ejemplo completo de un caso y de un requerimiento está en `seguridad/fase-1/README.md`. Las etiquetas de STRIDE y de ASVS las pone el workflow «Checkpoints» a partir del formulario.

### Checkpoint

| Condición | Verificación |
|:---|:---|
| Al menos 6 casos de abuso | `f1.casos` |
| Los casos cubren al menos 5 categorías | `f1.categorias` |
| Cada caso tiene escenario Dado, Cuando, Entonces con contenido | `f1.gherkin` |
| Cada caso cita su carta de Cornucopia | `f1.cornucopia` |
| Al menos 6 requerimientos con identificador ASVS 5.0 | `f1.requerimientos` |
| Cada caso enlaza al menos un requerimiento existente | `f1.trazabilidad` |

Guía: https://ic8071-sdlc-2026s2.github.io/sdlc-guia/fase-1/
