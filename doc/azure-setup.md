# Configuración de Azure

Todos los comandos utilizan **PowerShell** y **Azure CLI**.

## Iniciar sesión y ver la suscripción activa

```powershell
az login
az account show --output table
```

## Definir variables

Deben coincidir exactamente con los valores `env:` del workflow `.github/workflows/ci-cd.yml`.

```powershell
$RG         = "rg-entregable4-github"
$LOCATION   = "westeurope"
$ACR_NAME   = "acrentregable4202606"
$IMAGE_NAME = "flask-entregable4"
$ACI_NAME   = "aci-entregable4"

Write-Host "Resource Group : $RG"
Write-Host "ACR            : $ACR_NAME"
```

## Crear el grupo de recursos

```powershell
az group create `
  --name $RG `
  --location $LOCATION
```

## Crear Azure Container Registry (SKU Basic, acceso admin activado)

El acceso admin es necesario para que ACI pueda autenticarse con ACR al desplegar.

```powershell
az acr create `
  --resource-group $RG `
  --name $ACR_NAME `
  --sku Basic `
  --admin-enabled true
```

## Registrar el proveedor de Azure Container Instances

```powershell
az provider register --namespace Microsoft.ContainerInstance
```

Esperar hasta que el siguiente comando devuelva `Registered`:

```powershell
az provider show `
  --namespace Microsoft.ContainerInstance `
  --query registrationState `
  --output tsv
```

## Crear el service principal para GitHub Actions

```powershell
$SUBSCRIPTION_ID = az account show --query id --output tsv

az ad sp create-for-rbac `
  --name "sp-github-entregable4" `
  --role contributor `
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG" `
  --json-auth
```

El comando devuelve un JSON con este formato:

```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "...",
  "activeDirectoryEndpointUrl": "...",
  "resourceManagerEndpointUrl": "...",
  ...
}
```

Copiar el JSON completo (incluidas las llaves `{}`).

## Añadir el secret en GitHub

En el repositorio de GitHub:

**Settings → Secrets and variables → Actions → New repository secret**

| Nombre | Valor |
|---|---|
| `AZURE_CREDENTIALS` | JSON completo del paso anterior |

## Verificar el ACR

```powershell
az acr repository list `
  --name $ACR_NAME `
  --output table
```

Estará vacío hasta el primer push del pipeline. Tras una ejecución exitosa del workflow:

```powershell
az acr repository show-tags `
  --name $ACR_NAME `
  --repository $IMAGE_NAME `
  --output table
```
