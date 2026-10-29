## Fase 5 · Release firmado y gate

**Touchpoint de McGraw:** 7 (operaciones de seguridad).
**Rol que lidera:** DevSecOps, con Arquitectura en la línea base.

Aquí el pipeline **bloquea**: el release no sale con vulnerabilidades altas o críticas sin justificar ni con pruebas de corrección en rojo.

### Tareas

- [ ] Corregir al menos **3 debilidades trazadas** (las que marcaron «Corregir»). Cada corrección entra por PR, cierra su issue de hallazgo y agrega `@pytest.mark.corregida` a su prueba.
- [ ] Copiar `lab/workflows/fase5-release.yml` a `.github/workflows/` y escribir cada paso: imagen en ghcr.io, escaneo con Trivy, SBOM, gate, firma con cosign y attestations.
- [ ] Completar la línea base `seguridad/fase-5/.trivyignore.yaml`: cada excepción con `statement`.
- [ ] Quitar `warn-only` de Dependency Review en el workflow de la fase 3.
- [ ] Publicar el release: `git tag v1.0.0 && git push origin v1.0.0`. En las notas va la línea `Imagen: ghcr.io/...@sha256:...`.
- [ ] Completar `seguridad/fase-5/presentacion.md` para la presentación de 5 a 7 minutos.
- [ ] Cada integrante sube su reflexión en `seguridad/reflexiones/<usuario>.md`.

### Checkpoint

| Condición | Verificación |
|:---|:---|
| `fase5-release.yml` escanea, genera SBOM, firma, atesta y terminó en verde | `f5.release` |
| Un GitHub Release publica el SBOM | `f5.sbom` |
| El digest del release tiene attestations verificables | `f5.attestation` |
| Al menos 3 debilidades corregidas: prueba `corregida` e issue cerrado | `f5.correcciones` |
| Cada excepción de la línea base tiene justificación | `f5.lineabase` |
| La presentación está completa | `f5.presentacion` |

Guía: https://ic8071-sdlc-2026s2.github.io/sdlc-guia/fase-5/
