# Operación de la demostración Docker

Los comandos se ejecutan desde la raíz con el [entorno del README](../README.md#preparar-el-secreto). Si configuró otro puerto, sustituya `8080` en las consultas.

| Señal | Resultado esperado | Qué revisar cuando falla |
| --- | --- | --- |
| `docker compose ps --all` | Ambos servicios aparecen como `healthy` | Si hay un reinicio, compruebe archivo de secreto, permisos y configuración antes de recrear |
| `GET /salud` en la web | HTTP 200, proceso web activo | Puerto local, contenedor web y estado de Docker |
| `GET /listo` en la web | HTTP 200, API autenticada y compatible | Con HTTP 503, compruebe salud del motor, montaje de la misma credencial y red interna |
| `POST /analizar` | Resultado descriptivo | HTTP 502 indica fallo del motor o respuesta inválida. HTTP 503 con `Retry-After` indica saturación |
| `docker compose logs --since 10m aplicacion` | Eventos JSON de análisis | Revise `estado_http` y `duracion_ms` para localizar fallos repetidos |

La interfaz admite hasta dos análisis y 16 conexiones concurrentes. El motor R ejecuta un trabajo a la vez. La web reintenta una vez las lecturas ante fallos transitorios. Docker recupera procesos que terminan con error hasta tres veces. El estado `unhealthy` permite detectar indisponibilidad y el operador decide cuándo recrear un servicio.

## Recuperar el motor

```console
docker compose up -d --no-deps --force-recreate --wait --wait-timeout 90 motor
curl http://127.0.0.1:8080/listo
docker compose exec -T aplicacion python probar_compose.py
```

El motor conserva los trabajos y datos en memoria y `tmpfs`. Su recreación elimina los trabajos previos. La aplicación web puede seguir sirviendo su página durante la interrupción. Para validar ese comportamiento en CI, consulte [evidencias](evidencias_compose.md).

## Cambiar el secreto

Detenga ambos servicios con `docker compose down`. Quite el archivo anterior de su ubicación privada y genere uno nuevo siguiendo el [README](../README.md#preparar-el-secreto). Inicie los servicios con `docker compose up -d --wait` y ejecute la prueba del cálculo. Ambos procesos cargan la credencial al iniciar.

## Alcance operativo

El despliegue usa un solo host, HTTP privado entre contenedores y un puerto web en loopback. Los registros quedan en el host y se rotan por tamaño. Los datos y trabajos son temporales. Una exposición a terceros requeriría definir y validar TLS, identidad de los usuarios y el modelo de persistencia correspondiente.

## Actualizar las imágenes base

1. Consulte la imagen candidata con `docker buildx imagetools inspect <imagen:etiqueta>`. Verifique la plataforma pública y copie el digest del índice o manifiesto según el Dockerfile.
2. Actualice la referencia fija en el Dockerfile correspondiente. Las referencias de .NET y R también se registran en [bases.lock.json](../contenedores/bases.lock.json).
3. Ejecute las pruebas de Windows y Docker en CI. Revise la procedencia de las dos imágenes y la prueba de recuperación en el artefacto.
4. Si una actualización falla, revise el cambio de digest y revierta el commit de la actualización para recuperar la referencia anterior.

[Redes de Compose](https://docs.docker.com/reference/compose-file/networks/) · [Rotación con el driver local de Docker](https://docs.docker.com/engine/logging/drivers/local/).
