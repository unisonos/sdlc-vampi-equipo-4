# Fase 1 · Casos de abuso y requerimientos

Los casos de abuso y los requerimientos viven como issues, no como archivos. Se crean con los formularios **Caso de abuso** y **Requerimiento de seguridad** de la pestaña Issues. Este archivo explica cómo llenarlos y trae un ejemplo completo.

## Paso a paso

1. Lean `mapa-de-la-app.md`: qué hace la app, quién la usa y qué datos guarda.
2. Abran https://copi.owasp.org, creen un juego con la edición **Website App** y repartan las cartas. Por cada carta, la persona que la tiene responde: ¿esto le puede pasar a nuestra app? ¿Dónde?
3. Cada «sí» con un lugar concreto es un caso de abuso. Escríbanlo con el formulario.
4. Por cada caso, busquen en ASVS 5.0, nivel 1, el requerimiento que lo impediría. Escríbanlo con el formulario y enlacen ambos con #n.

## Ejemplo de caso de abuso

Este ejemplo es de una billetera electrónica ficticia, no de su app. Los números de issue son ilustrativos.

| Campo | Valor |
|:---|:---|
| Actor malicioso | Cliente registrado de la billetera, sin privilegios |
| Objetivo del atacante | Sacar dinero de la cuenta de otra persona sin que lo autorice |
| Categoría | T · Manipulación |
| Carta de Cornucopia | El código de la carta que inspiró el caso, por ejemplo VE5 |
| Componente afectado | `POST /api/transferencias` |
| CWE | CWE-20 |
| Requerimientos que lo mitigan | #8 |

Escenario:

```
Dado un cliente autenticado con saldo de ₡10 000 y la cuenta destino de otra persona
Cuando envía POST /api/transferencias con monto -5000 hacia esa cuenta
Entonces su saldo sube a ₡15 000 y el de la otra persona baja en ₡5 000
```

## Ejemplo de requerimiento

| Campo | Valor |
|:---|:---|
| Identificador ASVS 5.0 | 2.2.1 |
| Capítulo ASVS | V2 · Validación y lógica de negocio |
| Requerimiento | La API de transferencias debe rechazar montos menores o iguales a cero y mayores que el saldo disponible. |
| Casos de abuso que mitiga | #3 |
| Cómo se verificará | Prueba pytest escrita desde el caso de abuso (fase 4) |

Criterios de aceptación:

```
Dado un cliente autenticado con saldo de ₡10 000
Cuando envía POST /api/transferencias con monto -5000
Entonces la API responde 400 y ningún saldo cambia
```

## Qué hace bueno a un caso de abuso

- Nombra un endpoint, una pantalla o un archivo concreto de la app.
- El «Entonces» describe un daño que alguien notaría: dinero, datos, privilegios o disponibilidad.
- Se puede convertir en una prueba automática en la fase 4.
