# p005Lab

Estadisticas hechas interactivas

proyecto integración continua
Politecnico Grancolombiano
Juan Sebastián Moreno Díaz

Aplicación Ruta Estadística: consulte [LEEME.md](LEEME.md) y [estado de entrega](documentacion/estado_entrega.md).

## Demostración de dos servicios con Docker

Repositorio [mljuansmoreno/p005Lab](https://github.com/mljuansmoreno/p005Lab). La rama de entrega es `entrega/ruta-estadistica-compose`. Consulte sus commits con `git log --oneline origin/main..HEAD` y el SHA exacto con `git rev-parse HEAD`.

Requisitos: Docker Engine o Docker Desktop en modo de contenedores Linux, Compose v2 con `up --wait` y soporte para `linux/amd64`. Compruebe `docker info --format '{{.OSType}}'` (debe decir `linux`) y `docker compose version`.

Desde la raíz, cree `.env` a partir de `.env.example` y genere un archivo de secreto nuevo fuera del repositorio. En PowerShell:

```powershell
Copy-Item .env.example .env
$archivo = New-TemporaryFile
$bytes = [byte[]]::new(32)
$generador = [Security.Cryptography.RandomNumberGenerator]::Create()
$generador.GetBytes($bytes)
$generador.Dispose()
[IO.File]::WriteAllText($archivo.FullName, [BitConverter]::ToString($bytes).Replace('-', ''))
$env:RUTA_ESTADISTICA_ARCHIVO_SECRETO = $archivo.FullName
```

En Linux con Bash y OpenSSL:

```bash
cp .env.example .env
privado="$(mktemp -d)"
export RUTA_ESTADISTICA_ARCHIVO_SECRETO="$privado/motor.secreto"
openssl rand -hex 32 > "$RUTA_ESTADISTICA_ARCHIVO_SECRETO"
chmod 0444 "$RUTA_ESTADISTICA_ARCHIVO_SECRETO"
```

La variable de sesión prevalece sobre la ruta ficticia de `.env`. En Linux, el directorio privado restringe el acceso en el host y el modo de lectura permite que los procesos sin privilegios lean el archivo montado. Compose inyecta el archivo en tiempo de ejecución como `/run/secrets/motor`.

```console
docker compose --progress plain build
docker compose up -d --wait
docker ps --filter label=com.docker.compose.project=ruta-estadistica-demo
docker network inspect ruta-estadistica-demo_analisis
docker compose exec -T aplicacion python probar_compose.py
```

Mientras los servicios estén activos, abra [127.0.0.1:8080](http://127.0.0.1:8080) y pulse **Calcular ejemplo**. Solo se publica el puerto de la aplicación en loopback. Su servidor envía la carga y el trabajo por HTTP al destino interno `motor:8787`, espera el estado final y descarga el ZIP. La prueba imprime el destino, el identificador del trabajo, la huella SHA-256, seis filas y la media que devolvió R. Su código de salida es distinto de cero si el resultado difiere de la solicitud, del hash o de `25/6` con tolerancia relativa de `1e-10`.

Al terminar, ejecute `docker compose down --remove-orphans` y borre el secreto temporal. En PowerShell use `Remove-Item -LiteralPath $archivo.FullName` y `Remove-Item Env:RUTA_ESTADISTICA_ARCHIVO_SECRETO`. En Bash use `rm -f "$RUTA_ESTADISTICA_ARCHIVO_SECRETO"`, `rmdir "$privado"` y `unset RUTA_ESTADISTICA_ARCHIVO_SECRETO`.

### Organización y ciclo de vida

- `aplicacion/` contiene la interfaz Python, su Dockerfile y la prueba HTTP. `guiones/datos_sinteticos.py` comparte el CSV con la prueba nativa.
- `contenedores/Dockerfile` empaqueta la API .NET de `codigo/RutaEstadistica.ServidorLocal/` y los cálculos de `motor_r/`. El Host `motor` se habilita con `RUTA_ESTADISTICA_PERMITIR_HOST_MOTOR=1` en Compose. El motor exige Bearer, rechaza `Origin` y comprueba la propiedad del trabajo.
- El motor conserva cargas en memoria y archivos de trabajo en `/tmp` sobre tmpfs. Al cargar datos o encolar trabajos se depuran las cargas y los trabajos terminados con más de 15 minutos. Compose elimina los datos temporales al detener el contenedor.
- El [modo Docker del escritorio](documentacion/docker.md) usa su propia configuración en `contenedores/compose.yaml`. El [inicio nativo de WinUI](LEEME.md#inicio-de-desarrollo) sigue usando R local.

El trabajo **Docker Linux y cálculo entre contenedores** se ejecuta en `push` y `pull_request`. Conserva cinco salidas en el artefacto `docker-linux-<SHA>` cuando la ejecución y la revisión de credenciales concluyen correctamente. El trabajo de Windows conserva sus verificaciones nativas. [GitHub Actions](https://github.com/mljuansmoreno/p005Lab/actions/workflows/verificacion.yaml).

La evidencia del artículo corresponde al commit `3434ff2f5c7dc836636644299a6957eafad16f57`, con Docker Linux verificado en GitHub Actions. [Check de Docker Linux](https://github.com/mljuansmoreno/p005Lab/actions/runs/42565818761/job/128991978147) · [PR en borrador](https://github.com/mljuansmoreno/p005Lab/pull/1).

El artículo reúne la matriz de 150 puntos y las cinco capturas del registro. [DOCX](documentacion/ruta-estadistica-articulo.docx) · [PDF](documentacion/ruta-estadistica-articulo.pdf).
