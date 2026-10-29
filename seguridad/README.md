# Artefactos de seguridad

Aquí queda todo lo que el equipo produce, salvo lo que vive como issue (casos de abuso, requerimientos y hallazgos) o como workflow (`.github/workflows/`).

```
fase-1/README.md              cómo escribir casos de abuso y requerimientos, con ejemplo
fase-1/mapa-de-la-app.md      componentes, roles y datos de la app
fase-2/dfd.drawio.svg         diagrama de flujo de datos con fronteras de confianza
fase-2/matriz-riesgos.md      matriz de riesgos 3 por 3
fase-3/semgrep/               regla propia de Semgrep y su prueba
fase-4/pruebas/               pruebas pytest escritas desde los casos de abuso
fase-5/.trivyignore.yaml      línea base del gate, con cada excepción justificada
fase-5/presentacion.md        guion de la presentación final
reflexiones/                  una reflexión por integrante
```

## La cadena de trazabilidad

Cada debilidad debe poder seguirse de punta a punta:

```
carta de Cornucopia → caso de abuso (#n) → requerimiento ASVS (#m) → riesgo (R-0x)
  → regla de Semgrep o prueba pytest → hallazgo (#k) → corrección (PR) o excepción justificada
```

Un hallazgo sin traza no suma. Una traza sin evidencia en el repositorio tampoco.
