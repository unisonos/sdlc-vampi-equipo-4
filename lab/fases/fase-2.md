## Fase 2 · Análisis de riesgo arquitectónico

**Touchpoint de McGraw:** 2 (análisis de riesgo arquitectónico).
**Rol que lidera:** Arquitectura.

### Tareas

- [ ] Abrir `seguridad/fase-2/dfd.drawio.svg` en https://app.diagrams.net o con la extensión Draw.io del Codespace.
- [ ] Dibujar el DFD de VAmPI: entidades externas, procesos, almacenes de datos y flujos. Partir del mapa de la app.
- [ ] Marcar cada frontera de confianza con un rectángulo punteado rotulado «Frontera de confianza: …».
- [ ] Recorrer cada flujo que cruza una frontera con STRIDE. Cada amenaza nueva puede volverse un caso de abuso.
- [ ] Completar `seguridad/fase-2/matriz-riesgos.md`: al menos 6 riesgos, con probabilidad e impacto de 1 a 3 y riesgo = P × I.
- [ ] Cada caso de abuso de la fase 1 aparece en la matriz.

### Checkpoint

| Condición | Verificación |
|:---|:---|
| El DFD fue editado e incluye al menos una frontera de confianza | `f2.dfd` |
| La matriz tiene al menos 6 riesgos con P × I correcto y caso de abuso | `f2.matriz` |
| Todos los casos de abuso aparecen en la matriz | `f2.cobertura` |

Guía: https://ic8071-sdlc-2026s2.github.io/sdlc-guia/fase-2/
