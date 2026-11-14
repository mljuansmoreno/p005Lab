# Evidencias de Docker Compose

El 10 de noviembre de 2026, GitHub Actions verificó Docker Linux y Windows para el commit de rama `abc71d65a8a4082355e26253a10e5be0649c971d` del PR #1. El código que ejecutó el runner fue la fusión de prueba `deb14c09b1ac256a06113409045f755ca9c39a0a`. Las salidas de esta guía son extractos de ese registro. [Ejecución](https://github.com/mljuansmoreno/p005Lab/actions/runs/42844551193) · [Registro de Docker](https://github.com/mljuansmoreno/p005Lab/actions/runs/42844551193/job/129928419006) · [Artefacto con las cinco salidas](https://github.com/mljuansmoreno/p005Lab/actions/runs/42844551193/artifacts/13776579729).

Para repetir la prueba, prepare la credencial con las instrucciones de [arranque del README](../README.md#preparar-el-secreto). Ejecute los comandos desde la raíz.

## Compilar las imágenes

```console
docker compose --progress plain build
```

En `01-compilacion.txt`, las líneas `motor Built` y `aplicacion Built` confirman la construcción de las dos imágenes.

## Arrancar y comprobar los servicios

```console
docker compose up -d --wait --wait-timeout 90
docker ps --filter label=com.docker.compose.project=ruta-estadistica-demo
```

En `02-arranque.txt`, ambos contenedores llegan al estado `Healthy`. Extracto de `03-docker-ps.txt`, con las columnas de estado, puertos y nombre:

```text
Up 5 seconds (healthy)   127.0.0.1:8080->8080/tcp   ruta-estadistica-demo-aplicacion-1
Up 11 seconds (healthy)  8787/tcp                   ruta-estadistica-demo-motor-1
```

El navegador entra por el puerto publicado de `aplicacion`. El motor escucha en el puerto 8787 dentro de Docker.

## Inspeccionar la red

```console
docker network inspect ruta-estadistica-demo_analisis
```

Compruebe que el campo `Driver` sea `bridge` y que `Containers` tenga las entradas de la aplicación y del motor. `04-red.txt` contiene estos campos del registro:

```text
ruta-estadistica-demo_analisis (bridge)
ruta-estadistica-demo-motor-1 172.18.0.2/16
ruta-estadistica-demo-aplicacion-1 172.18.0.3/16
```

Docker asigna las IP al arrancar. La aplicación contacta al motor por el nombre DNS `motor`.

## Comprobar el cálculo entre contenedores

```console
docker compose exec -T aplicacion python probar_compose.py
```

La prueba llama a `POST /analizar` dentro de `aplicacion`. La aplicación carga un CSV sintético en `motor:8787`, crea un trabajo, espera a que termine y descarga el cálculo de R. Salida de `05-calculo.txt`:

```json
{
  "destino": "motor:8787",
  "trabajo_id": "1161b39b46754d9f9a117dd0853814ba",
  "solicitud_id": "e45e370bfa404493939b425d5b040002",
  "estado": "completado",
  "sha256": "4c4bcaecdea0a6f5169163dbd34fc0c82d8982148e354f92d4431d6114120499",
  "filas_analizadas": 6,
  "media": 4.16666666666667
}
```

Los identificadores cambian en cada ejecución. La prueba exige que el trabajo termine, que la huella corresponda al CSV de entrada y que la media coincida con `25/6`.

## Detener la demostración

```console
docker compose down --remove-orphans
```

El [artículo de entrega](ruta-estadistica-articulo.pdf) conserva las capturas de una ejecución anterior.
