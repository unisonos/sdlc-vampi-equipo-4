# Equipo

Una fila por integrante. El usuario de GitHub va sin espacios; el checkpoint de la fase 0 lo lee de esta tabla. Los roles rotan por sesión: nadie repite rol. En el equipo de 5, la quinta persona de cada sesión toma Relatoría.

| Nombre | Usuario de GitHub | Sesión 2 (fases 1 y 2) | Sesión 3 (fase 3) | Sesión 4 (fase 4) | Sesión 5 (fase 5) |
|:---|:---|:---|:---|:---|:---|
| Nombre Apellido | usuario | Arquitectura | AppSec | DevSecOps | Equipo rojo |
| Nombre Apellido | usuario | AppSec | DevSecOps | Equipo rojo | Arquitectura |
| Nombre Apellido | usuario | DevSecOps | Equipo rojo | Arquitectura | AppSec |
| Nombre Apellido | usuario | Equipo rojo | Arquitectura | AppSec | DevSecOps |

## Roles

- **Arquitectura.** Dueña del DFD, de las fronteras de confianza y de la matriz de riesgos. Decide qué se corrige y qué se acepta.
- **AppSec.** Dueña de los casos de abuso, los requerimientos ASVS y la regla propia de Semgrep. Revisa cada hallazgo y lo traza.
- **DevSecOps.** Dueña de los workflows: permisos, actions fijadas, gates, firma y attestations.
- **Equipo rojo.** Ataca la app levantada, escribe las pruebas de abuso y hace la predicción antes de cada herramienta.
- **Relatoría** (solo en el equipo de 5). Lleva la bitácora de decisiones de la sesión y prepara la presentación final.

Quien tiene el rol lo lidera y responde por el resultado de esa fase, pero todo el equipo trabaja en ella.
