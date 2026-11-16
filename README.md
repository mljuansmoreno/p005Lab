# Ruta Estadística · p005Lab

Proyecto de Integración Continua del Politécnico Grancolombiano, por Juan Sebastián Moreno Díaz. Ruta Estadística guía un análisis desde la pregunta y los datos hasta los resultados, su interpretación y la evidencia reproducible. Los cálculos los realiza el paquete R `rutaanalitica`; la aplicación no requiere una cuenta ni un modelo de lenguaje.

| Si quiere… | Empiece aquí |
| --- | --- |
| Ver un cálculo real en el navegador, sin instalar R ni .NET en el host | [Demostración web con Docker](#demostración-de-dos-servicios-con-docker) |
| Abrir proyectos, analizar sus archivos y exportar evidencia | [Aplicación de escritorio en Windows](#aplicación-de-escritorio) |
| Construir y comprobar la entrega con CI | [Jenkins](#integración-continua-con-jenkins) y [Docker en GitHub Actions](#pruebas-de-docker-realizadas) |
| Revisar qué controles de seguridad se ejecutaron | [Ciberseguridad: verificaciones realizadas](#ciberseguridad-verificaciones-realizadas) |

Los resultados de esta guía corresponden a las revisiones, fechas y ejecuciones indicadas. Los pasos de reproducción explican qué esperar al ejecutarlos en otro equipo. Para ver los cambios consolidados, consulte la [evolución de la entrega](#evolución-de-la-entrega).

## Arquitectura y alcance

| Componente | Responsabilidad |
| --- | --- |
| `aplicacion/` | Web Python de la demo. Sirve el formulario, envía un CSV sintético, consulta el trabajo y presenta el resultado. |
| `codigo/RutaEstadistica.ServidorLocal` y `motor_r/` | API .NET y trabajador R. La API admite el trabajo y devuelve su estado y resultado; R calcula las cifras. |
| `codigo/RutaEstadistica.Escritorio` | Cliente WinUI en español. Usa R local o, por elección, el adaptador a un motor Docker. |
| `codigo/` (capas compartidas) y `contratos/` | Validación, coordinación, persistencia, exportación y esquemas de entrada y salida. |
| `codigo/RutaEstadistica.ServidorMcp` | Servidor stdio con permisos concedidos desde el escritorio por proyecto y por sesión. |
| `pruebas/`, `guiones/`, `jenkins/` y `.github/workflows/` | Datos sintéticos, compilación, pruebas, CI y recolección de evidencias. |

La demo usa [`docker-compose.yml`](docker-compose.yml) en la raíz y publica la web en `127.0.0.1:8080`. La web conecta también con la red bridge interna `analisis`, donde resuelve `motor:8787` por DNS y usa HTTP autenticado. El motor de la demo carece de puerto publicado. La opción Docker de WinUI usa [otro Compose](contenedores/compose.yaml): publica solo el motor en `127.0.0.1:8787`. Jenkins tiene [su propio Compose](jenkins/compose.yaml) para el controlador.

[Arquitectura](documentacion/arquitectura.md) · [Mapa del código](documentacion/mapa_codigo.md) · [API y contratos](documentacion/contratos_y_api.md) · [Métodos en R](documentacion/motor_r_y_metodos.md).

## Demostración de dos servicios con Docker

### 1. Preparar el entorno y clonar

Necesita Git, un daemon Docker activo en modo Linux y Docker Compose V2 con soporte para `up --wait` y `--wait-timeout`. El motor requiere `linux/amd64`; compruebe que su entorno admite esa plataforma. En Windows puede usar Docker Desktop en modo Linux, desde PowerShell o desde una distribución WSL2 con la integración de Docker habilitada. En Linux use Bash y tenga OpenSSL para generar el secreto. La primera construcción necesita acceso a los registros de imágenes y repositorios de paquetes.

```console
git clone https://github.com/mljuansmoreno/p005Lab.git
cd p005Lab
git switch main
git rev-parse --short HEAD
docker info --format '{{.OSType}}/{{.Architecture}}'
docker compose version
```

`docker info` debe responder desde el servidor y mostrar `linux` como tipo. Si ya tiene el checkout, entre a la carpeta que contiene `README.md`, `docker-compose.yml` y `Jenkinsfile` y omita la clonación. Ejecute los pasos siguientes desde esa raíz.

### Preparar el secreto

**2.** Copie `.env.example` a `.env` si este último no existe. El valor predeterminado de `RUTA_ESTADISTICA_ARCHIVO_SECRETO` es `./credenciales/motor.secreto` y el de `RUTA_ESTADISTICA_PUERTO_WEB` es `8080`. Los bloques siguientes crean el archivo de la ruta predeterminada; si ya configuró otra ruta, verifique que apunte a su archivo. Use solo el bloque de su terminal.

**PowerShell**

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
New-Item -ItemType Directory -Force credenciales | Out-Null
if (!(Test-Path credenciales/motor.secreto)) {
    $bytes = [byte[]]::new(32)
    $generador = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generador.GetBytes($bytes) } finally { $generador.Dispose() }
    Set-Content -LiteralPath credenciales/motor.secreto -Value ([BitConverter]::ToString($bytes).Replace('-', '')) -Encoding ASCII -NoNewline
}
```

**Bash**

```bash
[ -f .env ] || cp .env.example .env
mkdir -p -m 0700 credenciales
if [ ! -f credenciales/motor.secreto ]; then
  (umask 077; openssl rand -hex 32 > credenciales/motor.secreto)
  chmod 0444 credenciales/motor.secreto
fi
```

Compose monta el mismo archivo como `/run/secrets/motor` en ambos servicios. En Linux, el directorio privado restringe el acceso desde el host y el modo `0444` permite la lectura del montaje por los usuarios de los contenedores. Mantenga el archivo fuera de Git, los logs y las capturas. `.gitignore` y `.dockerignore` excluyen las rutas predeterminadas.

### Arrancar y probar

**3.** Valide la configuración, construya y espere a que los servicios estén sanos.

```console
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 90
docker compose ps
```

`aplicacion` y `motor` deben aparecer saludables. Solo `aplicacion` debe tener un puerto publicado en el host. La primera construcción puede tardar más que un arranque posterior; el plazo de espera se aplica al arranque de los servicios.

**4.** Abra [http://127.0.0.1:8080](http://127.0.0.1:8080) y pulse **Calcular ejemplo**. El formulario debe mostrar **6 filas** con media **25/6**, aproximadamente **4,16666666666667**. Use el puerto que configuró si cambió el predeterminado. El ejemplo web es fijo y difiere del ejemplo del escritorio.

**5.** Compruebe las sondas y repita el cálculo automáticamente. Use `curl` en Bash o `curl.exe` en PowerShell, y ajuste el puerto de las URLs si lo cambió.

```bash
curl --fail --show-error http://127.0.0.1:8080/salud
curl --fail --show-error http://127.0.0.1:8080/listo
docker compose exec -T aplicacion python probar_compose.py
```

`/salud` comprueba que la web vive; `/listo` comprueba la disponibilidad del motor. El cliente de prueba usa la misma ruta de cálculo que el formulario y comprueba el estado `completado`, el destino `motor:8787`, los identificadores del trabajo y la solicitud, la huella SHA-256 del CSV, las seis filas y la media. Los identificadores son propios de cada ejecución.

### 6. Diagnosticar, recuperar y detener

```console
docker compose ps -a
docker compose logs --tail=80 aplicacion motor
docker network inspect ruta-estadistica-demo_analisis
```

La red de ese nombre corresponde al nombre de proyecto predeterminado. En la inspección espere una red `bridge` interna con ambos servicios; sus IP pueden cambiar. Si el puerto está ocupado, cambie `RUTA_ESTADISTICA_PUERTO_WEB` en `.env` y vuelva a levantar Compose. Si el motor no está sano, compruebe primero el modo Linux del daemon, la ruta del secreto y que ambos procesos puedan leer el montaje. Un fallo de compilación requiere revisar la salida de la construcción; si falla el arranque, revise los estados y logs de ambos servicios.

Para comprobar la recuperación en su propia demo, detenga el motor, mantenga la web en marcha y confirme los códigos HTTP con `curl -i` (o `curl.exe -i`). Después recréelo y repita el cálculo:

```bash
docker compose stop motor
curl -i http://127.0.0.1:8080/salud
curl -i http://127.0.0.1:8080/listo
docker compose up -d --force-recreate --no-deps --wait --wait-timeout 90 motor
curl -i http://127.0.0.1:8080/listo
docker compose exec -T aplicacion python probar_compose.py
```

Se espera HTTP 200 en `/salud` y HTTP 503 en `/listo` durante la caída; luego HTTP 200 en `/listo` y un nuevo cálculo válido. Para terminar, ejecute `docker compose down --remove-orphans` desde la misma carpeta y con el mismo nombre de proyecto. Puede conservar el secreto para volver a arrancar o eliminar el archivo local después de desmontar los servicios.

[Operación y diagnóstico de Compose](documentacion/operacion_compose.md).

## Pruebas de Docker realizadas

| Ejecución | Resultado observado |
| --- | --- |
| [GitHub Actions 42566314429](https://github.com/mljuansmoreno/p005Lab/actions/runs/42566314429) | Docker Linux pasó. Windows quedó sin ejecutar las pruebas nativas porque la descarga de R devolvió HTTP 504. |
| [GitHub Actions 42755729490](https://github.com/mljuansmoreno/p005Lab/actions/runs/42755729490), rama del PR #1 `4c173dc` | Pasaron Windows con siete rutas HTTP usando R real y Docker Linux con seis filas y media de 25/6. |
| [GitHub Actions 42844551193](https://github.com/mljuansmoreno/p005Lab/actions/runs/42844551193), rama `abc71d6`, fusión de prueba `deb14c0` | Pasaron Windows y Docker Linux. El anexo registra la construcción de ambas imágenes, los dos servicios sanos, el puerto web en loopback, la red y el cálculo. |
| [GitHub Actions 43754604687](https://github.com/mljuansmoreno/p005Lab/actions/runs/43754604687), `911f2cb`; [43801811485](https://github.com/mljuansmoreno/p005Lab/actions/runs/43801811485), `48d8a4e` | Pasaron los trabajos Windows, Docker y secretos en las revisiones indicadas. |
| [GitHub Actions 43810516949](https://github.com/mljuansmoreno/p005Lab/actions/runs/43810516949), `295325f` | Windows, Docker Linux y secretos aprobaron el mismo SHA de cierre. |
| [Jenkins alojado #10501](https://github.com/mljuansmoreno/p005Lab/actions/runs/43805486879) | Tras detener el motor se observaron HTTP 200 en vida y HTTP 503 en disponibilidad. Se registraron IDs distintos antes y después de recrearlo, HTTP 200 en disponibilidad y otro cálculo válido. |

En el [workflow de verificación](.github/workflows/verificacion.yaml), busque `docker-linux-<SHA>` bajo **Artifacts**. `00-entorno.json` distingue la revisión ejecutada de la rama o fusión de prueba, y registra versiones e imágenes; `01-compilacion.txt` a `05-calculo.txt` muestran construcción, arranque, procesos, red y cálculo. Las ejecuciones que incluyen recuperación publican `06-recuperacion.txt`. GitHub Actions y Jenkins comparten comprobaciones de Compose, pero cada artefacto acredita su propia ejecución.

[Evidencias paso a paso](documentacion/evidencias_compose.md) · [Artículo en PDF](documentacion/ruta-estadistica-articulo.pdf) · [Artículo en DOCX](documentacion/ruta-estadistica-articulo.docx).

## Aplicación de escritorio

### Inicio de desarrollo

**1. Instale los requisitos.** Use Windows x64 con PowerShell 7 (`pwsh`), .NET SDK **10.0.403**, Windows SDK **10.0.26100.0** y R **4.5.2 x64**. Compruebe `dotnet --list-sdks` y la ubicación de `bin/Rscript.exe` en la instalación de R. El guion de compilación prefiere `.herramientas/dotnet/dotnet.exe` cuando existe. La restauración necesita acceso a NuGet si no hay caché.

**2. Prepare recursos y publique.** Si solo quiere usar el escritorio, ejecute `git clone https://github.com/mljuansmoreno/p005Lab.git` y entre a `p005Lab`. Docker no interviene en el análisis con R local. Desde la raíz del checkout, ajuste `-RutaR` a la instalación que comprobó.

```powershell
./guiones/preparar_desarrollo.ps1 -RutaR 'C:/Program Files/R/R-4.5.2' -AdquirirJson
./guiones/compilar.ps1 -Publicar
```

La primera orden adquiere `jsonlite` para una biblioteca aislada, instala `rutaanalitica` y copia R, las bibliotecas y el trabajador a `salidas/recursos`. La segunda compila y publica el escritorio con esos recursos. Si falta el SDK o el script no encuentra R, corrija el requisito antes de continuar.

**3. Abra el ejecutable y pruebe el ejemplo.**

```powershell
./salidas/aplicacion/RutaEstadistica.Escritorio.exe
```

En **Inicio** pulse **Probar ejemplo**, conserve el motor **Local** y pulse **Calcular** en la ruta de análisis. El ejemplo nativo contiene las mediciones 10, 12, 14, 17, 19 y 21: la media esperada es **15,5**. Abra **Resultados**, **Interpretación** y **Evidencia**. La carpeta publicada lleva R y las bibliotecas, por lo que un análisis local no descarga dependencias.

**4. Ejecute las regresiones de desarrollo**, cuando quiera comprobar R y la integración local de .NET:

```powershell
./guiones/ejecutar_pruebas.ps1
```

[Instalación de desarrollo](documentacion/instalacion_desarrollo.md) · [Recorrido reproducible](documentacion/recorrido_completo.md) · [Errores y soluciones](documentacion/errores_y_soluciones.md).

Para sus datos: cree un proyecto, escriba la pregunta, seleccione archivo, confirme opciones de lectura y luego roles. No se infiere el significado a partir del nombre. CSV/TSV UTF-8 y XLSX sin fórmulas: 50 MiB, 100.000 registros sin contar encabezado, 200 columnas. Los límites se aplican sin truncamiento silencioso. La vista previa contiene hasta 200 filas.

Las funciones disponibles incluyen descriptivos, frecuencias de respuesta única, Welch, mediciones pareadas confirmadas, Pearson/Spearman y relación lineal simple. La inferencia está desactivada inicialmente. PDF, regresión múltiple y respuestas múltiples no están implementados.

Los proyectos se guardan en `%LOCALAPPDATA%/RutaEstadistica/proyectos`, sin cifrado propio. Eliminar conserva un respaldo portátil. HTML, CSV, PNG y un guion R se exportan a una carpeta nueva. Los archivos portátiles contienen datos privados: revise antes de compartir.

### Opciones avanzadas

Docker: [preparación voluntaria](documentacion/docker.md), `./guiones/iniciar_contenedores.ps1 -Construir`; seleccione Docker en Configuración. No se instala Docker ni se modifican características de Windows automáticamente.

MCP: [consentimiento y lanzador](documentacion/mcp.md). La aplicación debe estar abierta; autorice un proyecto en Configuración y revoque allí mismo. No active con un cliente que no sea de confianza.

### Repositorio

`codigo`: escritorio y capas .NET; `motor_r`: cálculos; `pruebas`: comprobaciones sintéticas; `contratos`: esquemas; `contenedores`: motor Linux; `empaquetado`: manifiesto MSIX; `guiones`: preparación, compilación y verificación.

[Manual](documentacion/manual_usuario.md) · [Desarrollo](documentacion/instalacion_desarrollo.md) · [Mapa del código](documentacion/mapa_codigo.md) · [Depuración](documentacion/depuracion.md) · [Limitaciones](documentacion/limitaciones_y_pendientes.md).

No se incluyen capturas de una interfaz que no haya sido ejecutada. Las capturas verificadas, cuando existan, se conservan en `salidas/informes`.

## Integración continua con Jenkins

[Instalación](documentacion/jenkins.md) · [Operación y reproducción](documentacion/operacion_jenkins.md) · [Informe de semana 5](documentacion/entrega_semana5.md). GitHub Actions conserva los trabajos de Windows, Docker y secretos.
