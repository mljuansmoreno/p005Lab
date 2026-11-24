# Motor Docker

Esta guía describe el modo Docker del escritorio con `contenedores/compose.yaml`. La demostración web de dos servicios usa el Compose de la raíz. [Arranque de la demostración](../README.md#demostración-de-dos-servicios-con-docker) · [Evidencias de red y cálculo](evidencias_compose.md).

Implementación en [Dockerfile](../contenedores/Dockerfile), [Compose](../contenedores/compose.yaml), `MotorDocker` y `ServidorLocal/Program.cs`. El escritorio permanece nativo. La API usa el mismo paquete R. El contenedor no monta la base ni carpetas del usuario.

## Preparación y ciclo de vida

Instale Docker Desktop por separado según [documentación oficial](https://docs.docker.com/desktop/setup/install/windows-install/). Requiere virtualización y un backend compatible, por ejemplo WSL 2. Revise los términos aplicables a su organización: no se afirma que sea gratuito para todas. No se redistribuye Docker Desktop.

```powershell
./guiones/iniciar_contenedores.ps1 -Construir
docker compose -f contenedores/compose.yaml ps
./guiones/detener_contenedores.ps1
docker image save ruta-estadistica-motor:0.1.1 -o motor-local.tar
docker image load -i motor-local.tar
```

Los comandos Compose manuales requieren `RUTA_ESTADISTICA_ARCHIVO_SECRETO` apuntando al archivo creado por el guion en el perfil de usuario. `docker image save/load` permite trasladar una imagen ya preparada sin conexión. Verifique su hash antes de cargarla.

El guion genera 48 bytes aleatorios y restringe ACL del archivo. No imprima ni versione su contenido. Compose monta el archivo como secreto. Docker puede acceder a él según permisos del host; esto no es un almacén de secretos frente al administrador del equipo.

La publicación es `127.0.0.1:8787`. El servicio escucha dentro del contenedor y exige Bearer, rechaza Origin y Host diferente de localhost/127.0.0.1. No habilita CORS. Sistema raíz solo lectura, usuario 1654, sin capacidades, sin privilegios nuevos, tmpfs 256 MiB, 1 GiB/2 CPU/64 procesos. No hay socket del daemon ni montaje de unidad.

```mermaid
flowchart LR
  Escritorio -->|CSV y contrato autenticados| Puerto[127.0.0.1:8787]
  Puerto --> Servicio[API contenedor]
  Servicio --> Temporal[Trabajo en tmpfs]
  Temporal --> R[Paquete R común]
  R -->|JSON y PNG| Escritorio
```

## Diagnóstico y límites

Si falta Docker/imagen o no hay salud compatible, seleccione Local. Compruebe `docker info`, estado del servicio y puerto; los guiones solo actúan sobre el servicio `motor` del proyecto `ruta-estadistica`. No ejecute limpiezas globales. Los logs HTTP se desactivan para evitar credenciales/valores accidentales.

Las bases SDK y R están fijadas por digest en el [inventario](../contenedores/bases.lock.json). La compilación comprueba la huella de jsonlite. Docker Linux construyó y probó el despliegue durante QA-250. La paridad documentada cubre nueve cifras del descriptivo. Para repetir la comparación con la imagen construida ejecute `python guiones/ci/paridad_numerica.py --imagen ruta-estadistica-motor:0.1.1` desde la raíz con R y el paquete preparados. [Alcance de QA](qa/informe_final.md).

El protocolo ahora es [API por trabajos, revisión 2](contratos_y_api.md). Las siete rutas estadísticas y el adaptador se comprobaron frente al servicio real en Windows usando R distribuido; no se presenta esto como paridad con Linux. La imagen anterior requiere reconstrucción explícita con `-Construir`.

Fuente de la base Noble: [inventario oficial Rocker](https://github.com/rocker-org/rocker-versioned2/wiki/r-ver_7a38a736e48e). La revisión de metadatos de registros no sustituye construir y ejecutar la imagen.
