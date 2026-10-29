# Fase 3 · Regla propia de Semgrep

Escriban una regla que verifique uno de sus requerimientos: que el código de `app/` lo cumpla o que nadie lo rompa en un PR futuro.

## Convención

Por cada regla hay dos archivos en esta carpeta, con el mismo nombre base:

```
seguridad/fase-3/semgrep/
  sql-armado-con-fstring.yml   la regla
  sql-armado-con-fstring.py    la prueba: código que debe disparar la regla y código que no
```

La extensión del archivo de prueba es la del lenguaje: `.py`, `.ts`, `.js` o `.rb`. En la prueba, el comentario `ruleid: <id>` va en la línea anterior a la que debe disparar la regla, y `ok: <id>` en la anterior a la que no debe dispararla. En TypeScript el comentario empieza con `//`; en Python y Ruby, con `#`.

La regla cita el issue del requerimiento en `metadata.requerimiento`. El checkpoint `f3.regla` lo verifica.

## Ejemplo (billetera ficticia, Python)

Regla `sql-armado-con-fstring.yml`:

```yaml
rules:
  - id: sql-armado-con-fstring
    languages: [python]
    severity: ERROR
    message: >-
      Consulta SQL armada con un f-string. Pase los valores como parámetros
      para cumplir el requerimiento #9.
    metadata:
      requerimiento: "#9"
      asvs: "1.2.4"
      cwe: "CWE-89"
    pattern: $CURSOR.execute(f"...", ...)
```

Prueba `sql-armado-con-fstring.py`:

```python
def buscar_mal(cursor, texto):
    # ruleid: sql-armado-con-fstring
    cursor.execute(f"SELECT * FROM comercios WHERE nombre LIKE '%{texto}%'")


def buscar_bien(cursor, texto):
    # ok: sql-armado-con-fstring
    cursor.execute("SELECT * FROM comercios WHERE nombre LIKE ?", (f"%{texto}%",))
```

## Cómo probarla

En el Codespace:

```bash
semgrep --test seguridad/fase-3/semgrep
semgrep scan app --config seguridad/fase-3/semgrep
```

Para iterar rápido, peguen la regla y un fragmento de código en https://semgrep.dev/playground.
