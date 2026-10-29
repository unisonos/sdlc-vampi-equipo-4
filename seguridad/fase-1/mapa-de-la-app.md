# Mapa de la app · VAmPI

Este documento es andamiaje para la fase 1. Describe qué hace VAmPI, cómo está
organizada y qué datos guarda, para que su equipo pueda dibujar el DFD y escribir
los casos de abuso. No es una lista de debilidades: esas las encuentra usted con
las herramientas y el análisis de las fases siguientes.

## Qué es

VAmPI (The Vulnerable API) es una API REST hecha con Flask. No tiene interfaz web:
todo son endpoints JSON. La especificación OpenAPI 3 vive dentro de la app y se
publica en `/openapi.json`; además hay un Swagger UI navegable en `/ui/` para
probar los endpoints a mano.

El dominio es sencillo: personas que se registran, inician sesión y guardan
"libros". Cada libro tiene un título y un secreto. La idea de negocio es que el
secreto de un libro solo lo debería ver quien lo creó.

El stack: Python 3.11, Flask 2.2 y Connexion 2.14 (Connexion enruta las peticiones
a las funciones de Python a partir del archivo OpenAPI), con SQLAlchemy sobre una
base SQLite en un archivo. La autenticación es con tokens JWT en la cabecera
`Authorization: Bearer <token>`.

## Cómo se arranca y se puebla

La base arranca vacía. Hay un endpoint, `GET /createdb`, que crea las tablas y las
llena con datos de ejemplo. `lab/app.sh` lo llama automáticamente al levantar la
app (está configurado como `APP_RUTA_INICIAL`). Si llama a un endpoint y recibe un
error de base de datos, vuelva a pasar por `/createdb`.

Cuentas de ejemplo que crea `/createdb`:

| Usuario | Contraseña | ¿Admin? | Correo |
|:---|:---|:---|:---|
| `name1` | `pass1` | no | `mail1@mail.com` |
| `name2` | `pass2` | no | `mail2@mail.com` |
| `admin` | `pass1` | sí | `admin@mail.com` |

A cada usuario se le crea también un libro con un título tipo `bookTitleNN` (el
número es aleatorio en cada corrida de `/createdb`) y un secreto asociado.

## Roles

VAmPI tiene tres niveles de acceso:

- **Anónimo (sin token).** Puede ver información básica de los usuarios y la lista
  de libros, registrarse e iniciar sesión.
- **Usuario autenticado (con token JWT).** Además puede ver sus propios datos,
  agregar libros, consultar un libro, cambiar su correo y su contraseña.
- **Administrador.** Un usuario autenticado cuya cuenta tiene la marca `admin`.
  Algunas operaciones, como borrar usuarios, están pensadas solo para este rol.

El token se obtiene en `POST /users/v1/login` y dura lo que indique
`tokentimetolive` (en el laboratorio, 3600 segundos). Se manda en cada petición
protegida como `Authorization: Bearer <token>`.

## Endpoints principales

| Método | Ruta | Acceso previsto | Qué hace |
|:---|:---|:---|:---|
| GET | `/` | anónimo | Mensaje de bienvenida; indica si la app corre en modo vulnerable |
| GET | `/createdb` | anónimo | Crea y puebla la base con los datos de ejemplo |
| GET | `/openapi.json` | anónimo | Especificación OpenAPI 3 de la API |
| GET | `/ui/` | anónimo | Swagger UI para probar la API |
| GET | `/users/v1` | anónimo | Lista de usuarios con información básica |
| GET | `/users/v1/_debug` | (operación de depuración) | Todos los detalles de todos los usuarios |
| POST | `/users/v1/register` | anónimo | Registra un usuario |
| POST | `/users/v1/login` | anónimo | Inicia sesión y devuelve un token JWT |
| GET | `/me` | autenticado | Datos del usuario del token |
| GET | `/users/v1/{username}` | anónimo | Datos de un usuario por nombre |
| DELETE | `/users/v1/{username}` | administrador | Borra un usuario |
| PUT | `/users/v1/{username}/email` | autenticado | Cambia el correo |
| PUT | `/users/v1/{username}/password` | autenticado | Cambia la contraseña |
| GET | `/books/v1` | anónimo | Lista de libros (título y dueño) |
| POST | `/books/v1` | autenticado | Agrega un libro con título y secreto |
| GET | `/books/v1/{book_title}` | autenticado (dueño) | Devuelve un libro con su secreto |

La columna "Acceso previsto" describe la intención del diseño. Parte de su trabajo
en las fases 1, 2 y 4 es comprobar si la app de verdad respeta esa intención.

## Datos que guarda

Dos tablas en SQLite (`app/database/`):

- **users**: `id`, `username`, `password`, `email`, `admin` (booleano).
- **books**: `id`, `book_title`, `secret_content`, `user_id` (dueño).

Un usuario tiene muchos libros; cada libro pertenece a un usuario.

## Autenticación JWT

- El token se genera al iniciar sesión y se firma con el algoritmo HS256 usando una
  clave que vive en la configuración de la app (`app/config.py`).
- El token lleva en su carga útil el `sub` (el nombre de usuario), la fecha de
  emisión `iat` y la de expiración `exp`.
- En cada endpoint protegido, la función `token_validator` lee la cabecera
  `Authorization`, extrae el token y lo decodifica con `User.decode_auth_token`
  (`app/models/user_model.py`). Si el token es válido, se obtiene el usuario del
  campo `sub`.

## Dónde vive cada parte en `app/`

```
app/
  app.py                     punto de entrada; lee las variables vulnerable y tokentimetolive
  config.py                  configuración de Flask, la base y la clave de firma; carga la OpenAPI
  openapi_specs/
    openapi3.yml             la especificación: rutas, parámetros y a qué función va cada una
    VAmPI.postman_collection.json   colección Postman de ejemplo
  api_views/
    main.py                  / y /createdb
    users.py                 registro, login, /me, consulta y borrado de usuarios, cambio de correo y contraseña
    books.py                 listado, alta y consulta de libros
    json_schemas.py          esquemas JSON para validar los cuerpos de las peticiones
  models/
    user_model.py            modelo User, generación y validación del JWT, consultas de usuario
    books_model.py           modelo Book
  database/                  carpeta donde SQLite crea el archivo de la base
  Dockerfile                 imagen de la app (Python 3.11 Alpine)
  requirements.txt           dependencias de Python con sus versiones
```

## Para la fase 1

- Recorra la API con el Swagger UI (`/ui/`) o con `curl`. Registre un usuario,
  inicie sesión, guarde un libro y consúltelo.
- Para cada carta de Cornucopia que le toque, pregúntese: en esta API, ¿quién
  podría hacer algo que el diseño no quería? Piense en los endpoints de arriba y en
  la columna "Acceso previsto".
- El modo `vulnerable` de la app está encendido en el laboratorio. Corregir una
  debilidad no es apagar ese interruptor: es cambiar el código para que la
  operación sea segura aunque el interruptor siga encendido.
