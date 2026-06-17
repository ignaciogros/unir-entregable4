[English version](README.md)

# Flask CI/CD Demo

Aplicación web mínima en Python con Flask, contenerizada con Docker y desplegada de forma automática en Azure mediante un pipeline de CI/CD con GitHub Actions.

## Descripción del proyecto

Este proyecto tiene como objetivo demostrar el ciclo completo de integración y despliegue continuos (CI/CD) para una aplicación web en contenedor. Cualquier push a la rama `main` desencadena automáticamente tres jobs secuenciales:

1. **test** — se ejecutan las pruebas unitarias con `pytest` para garantizar que la aplicación funciona correctamente antes de construir la imagen.
2. **build-and-push** — se construye la imagen Docker y se sube a Azure Container Registry (ACR).
3. **deploy** — se despliega la imagen en Azure Container Instances (ACI), sustituyendo el contenedor anterior.

El resultado es una aplicación siempre actualizada y accesible públicamente en Azure sin ninguna intervención manual.

## Requisitos previos

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recomendado) **o** `pip`
- [Docker](https://www.docker.com/) — opcional, para pruebas locales con contenedor
- Cuenta de Azure con una suscripción activa (solo para ejecutar el pipeline)

## Instalación

### Recomendado — uv

```bash
uv venv .venv
source .venv/bin/activate        # macOS/Linux
source .venv/Scripts/activate    # Windows Git Bash
.venv\Scripts\Activate.ps1       # Windows PowerShell
uv pip install -r requirements.txt
```

### Alternativa — pip

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
source .venv/Scripts/activate    # Windows Git Bash
.venv\Scripts\Activate.ps1       # Windows PowerShell
pip install -r requirements.txt
```

## Ejecutar en local

```bash
python app.py
```

Abre <http://localhost:5000> en el navegador. Deberías ver:

```
¡Hola! Soy una aplicación desplegada con CI/CD.
```

## Ejecutar los tests

```bash
pytest          # todos los tests
pytest -q       # salida compacta (igual que en CI)
pytest tests/test_app.py::test_root   # test individual
```

Los tests usan el `test_client()` de Flask directamente sobre el objeto `app`, sin necesidad de levantar un servidor.

## Docker

### Construir la imagen localmente

```bash
docker build -t flask-cicd .
```

### Ejecutar en primer plano

```bash
docker run --rm -p 5000:5000 flask-cicd
```

Detener con `Ctrl+C`. Abre <http://localhost:5000>.

### Ejecutar en segundo plano

```bash
docker run -d --name flask-cicd -p 5000:5000 flask-cicd
```

### Ver logs / detener / eliminar

```bash
docker logs flask-cicd
docker stop flask-cicd
docker rm flask-cicd
```

### Ejecutar la imagen publicada desde Azure Container Registry

```bash
# Autenticarse en ACR
az acr login --name acrentregable4202606

# Descargar y ejecutar la imagen de una ejecución concreta
docker run --rm -p 5000:5000 \
  acrentregable4202606.azurecr.io/flask-entregable4:<RUN_NUMBER>
```

Sustituye `<RUN_NUMBER>` por el número de ejecución de GitHub Actions (visible en la pestaña *Actions* del repositorio).

## Pipeline CI/CD

El fichero `.github/workflows/ci-cd.yml` se dispara en cada push a `main` y ejecuta tres jobs secuenciales:

### Job 1 — test

- Descarga el código fuente.
- Instala Python 3.11 usando `actions/setup-python@v5`.
- Instala las dependencias de `requirements.txt`.
- Ejecuta `pytest -q` y bloquea el pipeline si algún test falla.

### Job 2 — build-and-push

- Se autentica en Azure mediante el secret `AZURE_CREDENTIALS`.
- Se autentica en ACR.
- Construye la imagen Docker con la etiqueta `<acrName>.azurecr.io/flask-entregable4:<run_number>`.
- Sube la imagen a ACR.

### Job 3 — deploy

- Elimina el contenedor anterior en ACI (si existe) y espera a que se elimine completamente.
- Crea una nueva instancia en Azure Container Instances con la imagen recién publicada.
- Usa el DNS label fijo `flask-entregable4`, de modo que la URL pública no cambia entre despliegues.
- Imprime la URL pública al final del job.

### Secret requerido

La única credencial necesaria se configura en *Settings → Secrets and variables → Actions*:

| Secret | Descripción |
|---|---|
| `AZURE_CREDENTIALS` | JSON del service principal de Azure |

Para crear el service principal:

```bash
az ad sp create-for-rbac --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-entregable4-github \
  --json-auth
```

Copia el JSON resultante y guárdalo como secret `AZURE_CREDENTIALS`.

### Variables del workflow

Los valores no sensibles se definen como `env:` al inicio del fichero del workflow:

| Variable | Valor |
|---|---|
| `ACR_NAME` | `acrentregable4202606` |
| `IMAGE_NAME` | `flask-entregable4` |
| `ACI_NAME` | `aci-entregable4` |
| `RESOURCE_GROUP` | `rg-entregable4-github` |
| `LOCATION` | `westeurope` |
| `CONTAINER_PORT` | `5000` |
| `DNS_LABEL` | `flask-entregable4` |

La etiqueta de imagen usa `${{ github.run_number }}`; el DNS label es fijo.

## Aplicación desplegada

Tras cada ejecución exitosa del pipeline, Azure asigna automáticamente una URL pública al contenedor con el formato:

```
http://flask-entregable4.westeurope.azurecontainer.io:5000
```

La URL es estable entre despliegues — solo cambia el tag de la imagen. La URL exacta también se imprime al final del job **deploy** en la consola de Actions.

## Arquitectura

```
GitHub (push a main)
        │
        ▼
GitHub Actions (.github/workflows/ci-cd.yml)
  ├── test          → pytest sobre el código fuente
  ├── build-and-push → imagen Docker → ACR (acrentregable4202606)
  └── deploy        → ACI (aci-entregable4) en westeurope
                           │
                           ▼
               http://flask-entregable4.westeurope.azurecontainer.io:5000
```

### Ficheros principales

| Fichero | Propósito |
|---|---|
| `app.py` | App Flask — un único endpoint `GET /` |
| `requirements.txt` | Dependencias: `flask` y `pytest` |
| `Dockerfile` | Imagen basada en `python:3.11-slim` |
| `tests/test_app.py` | Test unitario del endpoint raíz |
| `.github/workflows/ci-cd.yml` | Pipeline de CI/CD completo |
