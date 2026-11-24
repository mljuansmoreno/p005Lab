# Ruta Estadística · p005Lab

[Rúbrica de Jenkins y verificación de evidencias](Verificacion_Rubrica.md)

Proyecto de Integración Continua del Politécnico Grancolombiano, por Juan Sebastián Moreno Díaz. Ruta Estadística guía un análisis desde la pregunta y los datos hasta los resultados, su interpretación y la evidencia reproducible. Los cálculos los realiza el paquete R `rutaanalitica`; la aplicación no requiere una cuenta ni un modelo de lenguaje.

| Si quiere… | Empiece aquí |
| --- | --- |
| Ver un cálculo real en el navegador, sin instalar R ni .NET en el host | [Demostración web con Docker](#demostración-de-dos-servicios-con-docker) |
| Abrir proyectos, analizar sus archivos y exportar evidencia | [Aplicación de escritorio en Windows](#aplicación-de-escritorio) |
| Construir y comprobar la entrega con CI | [Jenkins](#integración-continua-con-jenkins) y [Docker en GitHub Actions](#pruebas-de-docker-realizadas) |
| Revisar qué controles de seguridad se ejecutaron | [Ciberseguridad: verificaciones realizadas](#ciberseguridad-verificaciones-realizadas) |

Los resultados de esta guía corresponden a las revisiones, fechas y ejecuciones indicadas. Los pasos de reproducción explican qué esperar al ejecutarlos en otro equipo. Para ver los cambios consolidados, consulte la [evolución de la entrega](#evolución-de-la-entrega).

## Estado de la revisión `03edc5a`

El 23 de noviembre de 2026 (Bogotá), Docker Linux y credenciales aprobaron en `main`. El trabajo Windows llegó a 148 comprobaciones correctas del arnés .NET y falló después, en la validación documental. Jenkins alojado terminó con éxito sobre el mismo SHA. [Verificación Windows y Docker](https://github.com/mljuansmoreno/p005Lab/actions/runs/45318939053) · [Jenkins](https://github.com/mljuansmoreno/p005Lab/actions/runs/45318939185).

El verificador encontró dos enlaces a `ruta-estadistica-articulo.pdf` en `documentacion/estado_entrega.md` y `documentacion/evidencias_compose.md`. El PDF se había retirado del repositorio. Para reproducir la comprobación desde la raíz, ejecute `./guiones/verificar_documentacion.ps1` con PowerShell. [Registro de Windows](https://github.com/mljuansmoreno/p005Lab/actions/runs/45318939053).

En el cierre QA-250 (`3f44fb2`), ambos workflows aprobaron. Para comparar resultados entre revisiones, abra el trabajo de la misma plataforma y compruebe su SHA. [Windows y Docker de QA-250](https://github.com/mljuansmoreno/p005Lab/actions/runs/45233851177) · [Jenkins de QA-250](https://github.com/mljuansmoreno/p005Lab/actions/runs/45233850871).

### Qué se puede hacer desde el repositorio

- **Probar el cálculo de extremo a extremo** con los datos sintéticos de la demo y un navegador. La demo web tiene un formulario de ejemplo fijo. El escritorio es la interfaz para importar y analizar datos propios.
- **Trabajar con datos en Windows** con proyectos, métodos estadísticos, interpretación y exportaciones reproducibles. Puede usar el motor R local o el motor opcional en Docker.
- **Desarrollar o evaluar la entrega** desde un clon público. Consulte los [contratos de la API](documentacion/contratos_y_api.md), la [guía de pruebas](documentacion/pruebas_y_calidad.md) y el [anexo de CI](documentacion/evidencias-jenkins/README.md) para distinguir los pasos reproducibles de los resultados ya observados.
- **Revisar los 250 cambios numerados de QA** (pruebas, mediciones, procedimientos e informes, más dos correcciones adicionales de integración) en el [informe de auditoría](documentacion/qa/informe_final.md), con cobertura, regresiones, limitaciones e instrucciones para recuperar los SHA publicados.

Antes de reproducir una evidencia, ejecute `git rev-parse HEAD` y compárelo con el SHA de la ficha. El contenido de `main` sigue evolucionando.

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

El repositorio separa las herramientas de ejecución, los contratos y sus comprobaciones. `contratos/` define los formatos compartidos; `motor_r/` concentra el cálculo estadístico y `pruebas/` cubre unidades y flujos de integración. El [bloqueo de imágenes base](contenedores/bases.lock.json) permite cotejar los Dockerfiles con sus fuentes y huellas. [Mapa del código](documentacion/mapa_codigo.md).

### Del CSV al resultado

El trabajador nativo lee `solicitud.json` y `entrada.csv` mediante el contrato 1. Escribe `resultado.json` y `figura.png` en el directorio del trabajo. El adaptador admite hasta 8 MiB para el JSON del resultado. [Contrato del trabajador](documentacion/contratos_y_api.md).

En la API HTTP versión 2, `POST /datos` devuelve el `datos_id` y la huella del CSV. `POST /trabajos` responde 202 con el identificador. Consulte `GET /trabajos/{id}` con el proyecto y descargue `GET /trabajos/{id}/resultado` cuando el estado sea `completado`. El ZIP contiene las cifras y la figura. [Rutas y respuestas](documentacion/contratos_y_api.md).

El motor calcula un trabajo y admite otro en espera. Una cola llena devuelve 429. El plazo de ejecución de R es de 60 s y el del cliente es de 90 s. Tras recibir el identificador, el cliente puede solicitar la cancelación con `DELETE /trabajos/{id}`. [Ciclo del trabajo](documentacion/contratos_y_api.md).

La API conserva hasta cuatro revisiones de datos y 100 MiB de CSV en total. Cada CSV normalizado admite hasta 50 MiB, 100.000 registros y 200 columnas. La carga HTTP completa admite 60 MiB, incluidos los escapes JSON. Una recarga idéntica en el mismo proyecto reutiliza el identificador. [Límites de carga](documentacion/contratos_y_api.md).

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

**4.** Abra [http://127.0.0.1:8080](http://127.0.0.1:8080) y pulse **Calcular ejemplo**. El formulario debe mostrar **6 filas** con media **25/6**, aproximadamente **4,16666666666667**. Use el puerto que configuró si cambió el predeterminado. La regresión QA-149 reproduce el envío del formulario en Chromium y comprueba esa misma media con R real. [Defecto y reparación](documentacion/qa/defectos_y_regresiones.md).

**5.** Compruebe las sondas y repita el cálculo automáticamente. Use `curl` en Bash o `curl.exe` en PowerShell, y ajuste el puerto de las URLs si lo cambió.

```bash
curl --fail --show-error http://127.0.0.1:8080/salud
curl --fail --show-error http://127.0.0.1:8080/listo
docker compose exec -T aplicacion python probar_compose.py
```

En el puerto web, `/salud` comprueba que el proceso responde y `/listo` comprueba la disponibilidad del motor. El endpoint `/salud` del propio motor requiere autenticación y devuelve las versiones de API y contrato. El cliente de prueba usa la misma ruta de cálculo que el formulario y comprueba el estado `completado`, el destino `motor:8787`, los identificadores del trabajo y la solicitud, la huella SHA-256 del CSV, las seis filas y la media. Los identificadores son propios de cada ejecución.

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

Para repetir la suite de despliegue con imágenes existentes, configure `RUTA_QA_IMAGEN_APLICACION` y `RUTA_QA_IMAGEN_MOTOR` con las etiquetas del mismo build. Ejecute `python guiones/ci/probar_junit.py pruebas/contenedores salidas/qa/reportes/compose.xml`. [Reproducción de las suites](documentacion/qa/ejecucion_y_mantenimiento.md).

### Compartir resultados de una prueba local

Para una demostración pública use el CSV sintético del repositorio. Si usa el escritorio con datos propios, revise la exportación y el proyecto antes de compartirlos: pueden incluir datos originales, identificadores y resultados. Use una copia sintética para capturas, incidencias y pruebas de CI. Mantenga credenciales, `.env`, volcados y registros sin redactar fuera de Git y de los artefactos públicos. [Seguridad y privacidad](documentacion/seguridad_y_privacidad.md).

## Pruebas de Docker realizadas

| Ejecución | Resultado observado |
| --- | --- |
| [Docker Linux de `03edc5a`](https://github.com/mljuansmoreno/p005Lab/actions/runs/45318939053) | El trabajo de Docker terminó con éxito. El fallo de la ejecución global corresponde al trabajo Windows. |
| [GitHub Actions 42566314429](https://github.com/mljuansmoreno/p005Lab/actions/runs/42566314429) | Docker Linux pasó. Windows quedó sin ejecutar las pruebas nativas porque la descarga de R devolvió HTTP 504. |
| [GitHub Actions 42755729490](https://github.com/mljuansmoreno/p005Lab/actions/runs/42755729490), rama del PR #1 `4c173dc` | Pasaron Windows con siete rutas HTTP usando R real y Docker Linux con seis filas y media de 25/6. |
| [GitHub Actions 42844551193](https://github.com/mljuansmoreno/p005Lab/actions/runs/42844551193), rama `abc71d6`, fusión de prueba `deb14c0` | Pasaron Windows y Docker Linux. El anexo registra la construcción de ambas imágenes, los dos servicios sanos, el puerto web en loopback, la red y el cálculo. |
| [GitHub Actions 43754604687](https://github.com/mljuansmoreno/p005Lab/actions/runs/43754604687), `911f2cb`; [43801811485](https://github.com/mljuansmoreno/p005Lab/actions/runs/43801811485), `48d8a4e` | Pasaron los trabajos Windows, Docker y secretos en las revisiones indicadas. |
| [GitHub Actions 43810516949](https://github.com/mljuansmoreno/p005Lab/actions/runs/43810516949), `295325f` | Windows, Docker Linux y secretos aprobaron el mismo SHA de cierre. |
| [Jenkins alojado #10501](https://github.com/mljuansmoreno/p005Lab/actions/runs/43805486879) | Tras detener el motor se observaron HTTP 200 en vida y HTTP 503 en disponibilidad. Se registraron IDs distintos antes y después de recrearlo, HTTP 200 en disponibilidad y otro cálculo válido. |

En el [workflow de verificación](.github/workflows/verificacion.yaml), busque `docker-linux-<SHA>` bajo **Artifacts**. `00-entorno.json` distingue la revisión ejecutada de la rama o fusión de prueba, y registra versiones e imágenes; `01-compilacion.txt` a `05-calculo.txt` muestran construcción, arranque, procesos, red y cálculo. Las ejecuciones que incluyen recuperación publican `06-recuperacion.txt`. GitHub Actions y Jenkins comparten comprobaciones de Compose, pero cada artefacto acredita su propia ejecución.

Para consultar JUnit y cobertura, descargue `qa-python`, `qa-windows` o `qa-docker` desde la ejecución de la plataforma. Un trabajo interrumpido puede dejar informes parciales. El artefacto `historial-qa` identifica los commits de la serie auditada. [Definición de los artefactos](.github/workflows/verificacion.yaml).

[Evidencias paso a paso](documentacion/evidencias_compose.md).

## Reproducir y evaluar QA-250

Desde la raíz del clon, ejecute `python guiones/ci/probar_python.py --suite rapida` para revisar el contrato documental sin levantar servicios. Para coordinación y web, ejecute `python guiones/ci/probar_python.py`. El motivo de cada omisión figura en la salida de la suite. [Ejecución y dependencias](documentacion/qa/ejecucion_y_mantenimiento.md).

Para verificar los identificadores QA-001 a QA-250, use un clon con historial completo y acceso al remoto. El auditor comprueba la ascendencia y los objetos publicados y escribe `historial.md` e `historial.json` en `salidas/qa/auditoria/`. [Trazabilidad por caso](documentacion/qa/trazabilidad_casos.md).

```console
git fetch origin main
python guiones/ci/auditar_serie_qa.py --hasta 3f44fb2ce694839927a200283d983469eed8651d --completo
```

### Resultados de referencia

Las cifras siguientes proceden de la revisión `1e7d92f`. Los resultados remotos se extrajeron de JUnit y el ensayo de navegador se ejecutó en Windows local. [Ejecución remota](https://github.com/mljuansmoreno/p005Lab/actions/runs/45231440353) · [Evidencia y condiciones de medición](documentacion/qa/cobertura_y_limites.md).

| Plataforma y suite | Resultado en `1e7d92f` |
| --- | --- |
| Linux · coordinación Python | 103 descubiertas, 102 aprobadas y una omitida. |
| Linux · web y resiliencia | 33 pruebas web y 9 de resiliencia aprobadas. |
| Windows · API HTTP con R | 44 pruebas aprobadas. Para repetirlas con el servidor y R preparados, ejecute `python guiones/ci/probar_junit.py pruebas/api salidas/qa/reportes/api.xml`. |
| Docker Linux · configuración y despliegue | 24 pruebas aprobadas sobre la topología y las imágenes del build. |
| Windows local · navegador | 7 pruebas aprobadas. Compile el servidor en Release, prepare R e instale Playwright con Chromium o Edge. Ejecute `python guiones/ci/probar_navegador.py`. |

El arnés .NET registró 148 comprobaciones con el trabajador R. Para Pearson se contrastaron diez permutaciones con semilla `20261123`. La suite nativa de `rutaanalitica` registró éxito sin emitir un conteo por caso. [Estrategia y oráculos](documentacion/qa/estrategia_y_oraculos.md).

### Cobertura por componente

| Componente | Medición en `1e7d92f` | Umbral del proyecto | Código medido |
| --- | ---: | ---: | --- |
| Python | 42,20 % | 35 % | `aplicacion` y `guiones/ci`, con coverage.py 7.17.5. |
| .NET | 501/645 líneas (77,67 %) | 70 % | Contratos, dominio, aplicación e infraestructura, con dotnet-coverage 18.12.0. |
| R | 93/102 líneas (91,18 %) | 85 % | Código instrumentable de `rutaanalitica`, con covr 4.0.0. |

Cada umbral se evalúa por separado. WinUI, MCP y el proceso HTTP quedan fuera de esas cifras de cobertura de líneas. Para evaluar un cambio de umbral, la guía pide comparar dos ejecuciones en la misma plataforma y conservar los XML. [Cobertura y límites](documentacion/qa/cobertura_y_limites.md).

### Rendimiento observado en Windows

Tras el calentamiento, con 10.000 filas y 30 muestras, la importación .NET registró una mediana de 3,81 ms y un p95 de 22,36 ms. El descriptivo de R, incluida la figura, registró 350 y 400 ms respectivamente. En 60 consultas autenticadas de salud en loopback, la mediana fue 3,68 ms y el p95 fue 5,53 ms. [Mediciones locales](documentacion/qa/cobertura_y_limites.md).

Con 100 y 50.000 filas, el pico observado del árbol de procesos con R pasó de 157.130.752 a 179.834.880 bytes. El muestreo se hizo cada 25 ms y la suma puede contar páginas compartidas varias veces. La carga sostenida queda pendiente de evaluación. [Riesgos y condiciones de aceptación](documentacion/qa/riesgos_abiertos.md).

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

### Analizar sus datos y guardar evidencia

1. En **Inicio**, cree o abra un proyecto. Escriba la pregunta y el contexto. Puede renombrar, duplicar o importar proyectos desde esa pantalla.
2. En **Datos**, importe CSV o TSV en UTF-8, o seleccione una hoja de un XLSX sin fórmulas, macros ni vínculos externos. Confirme el separador, decimales, encabezado, fechas y marcador de faltantes. Los límites generales son 50 MiB, 100.000 filas de datos y 200 columnas. La vista previa presenta hasta 200 filas y el cálculo conserva la entrada completa. QA-041 y QA-043 comprueban el diagnóstico público al importar un XLSX sin catálogo de relaciones o truncado. [Regresiones del importador](documentacion/qa/defectos_y_regresiones.md).
3. En **Preparación**, confirme los roles y revise faltantes, duplicados candidatos y constantes. Los identificadores conservan ceros iniciales. La exclusión por faltantes exige confirmación y queda registrada; la aplicación no elimina automáticamente valores atípicos.
4. En **Ruta**, elija descriptivos, frecuencias de respuesta única, Welch, pares confirmados, Pearson/Spearman o regresión lineal simple. Seleccione las variables en el orden que indique el método. Confirme las condiciones antes de activar la inferencia y pulse **Calcular**.
5. En **Resultados** e **Interpretación**, revise cifras, gráfico, procedencia y límites. La pantalla separa el redondeo de presentación de los valores guardados. En **Evidencia** puede abrir un cálculo guardado; la aplicación coteja la solicitud y el hash del CSV antes de mostrarlo. La regresión QA-054 exige una huella hexadecimal de 64 caracteres y comprueba el rechazo de un salto de línea final. [Validación de huellas](documentacion/qa/defectos_y_regresiones.md).
6. En **Evidencia**, exporte a una carpeta nueva. Puede abrir `informe.html` sin conexión y, con el paquete R instalado, ejecutar `Rscript --vanilla reproducir.R` desde la carpeta exportada. Compare las cifras; la fecha y duración pueden variar. La exportación incluye CSV, PNG, solicitud, entrada normalizada y resultado. Use la opción CSV seguro al compartir texto que se abrirá en una hoja de cálculo.

Los proyectos se guardan en `%LOCALAPPDATA%\RutaEstadistica\proyectos`, sin cifrado propio. La exportación portátil `.rutaestadistica` conserva datos y hashes; importar crea otro proyecto, y eliminar deja un respaldo. Revise el contenido antes de compartirlo.

La aplicación abre con tema claro; en **Apariencia** puede cambiar a **Oscuro** o **Según Windows**. La preferencia se guarda por perfil y la interfaz contempla el contraste del sistema. La actualización también organizó los títulos, botones, tablas, avisos y superficies de resultados de WinUI y de la demo. [Manual](documentacion/manual_usuario.md) · [Datos y persistencia](documentacion/datos_y_persistencia.md).

### Opciones del escritorio: Docker y MCP

**Usar Docker como motor.** Arranque el motor de escritorio con Docker en modo Linux. En PowerShell, desde la raíz:

```powershell
./guiones/iniciar_contenedores.ps1 -Construir
docker ps --filter label=com.docker.compose.project=ruta-estadistica
```

Abra la aplicación nativa, seleccione **Docker** en Configuración y calcule. Este modo usa `127.0.0.1:8787`; el guion administra la credencial en el perfil local y el motor no monta los proyectos. Para volver al motor nativo, seleccione **Local**; para detener el motor de escritorio ejecute `./guiones/detener_contenedores.ps1`. Véase [configuración del motor Docker del escritorio](documentacion/docker.md).

**Usar MCP.** Abra el escritorio, autorice el proyecto en Configuración y lance el servidor stdio desde un cliente de confianza con la [configuración MCP del repositorio](documentacion/mcp.md). Revocar el acceso o cerrar la aplicación elimina las concesiones de sesión. El ensayo por stdio verificó la revisión del protocolo, las nueve herramientas y el acceso sin concesión. El ensayo con un cliente externo sigue pendiente. [Cliente de prueba](guiones/probar_mcp.py).

**Alcance de la entrega.** La publicación y el arranque de WinUI tienen evidencia, pero el recorrido gráfico completo y la validación de accesibilidad siguen pendientes. Las pruebas Docker de la demo tampoco acreditan por sí solas la paridad completa del escritorio entre motores. El MSIX de desarrollo documentado se creó sin firma; no acredita instalación limpia, actualización, WACK ni aprobación de Microsoft Store. No incluye exportación directa de resultados a PDF, regresión múltiple ni cuestionarios de respuesta múltiple. [Estado](documentacion/estado_entrega.md) · [Continuidad](documentacion/continuidad.md) · [Limitaciones](documentacion/limitaciones_y_pendientes.md) · [Empaquetado](documentacion/empaquetado_y_publicacion.md).

## Integración continua con Jenkins

El controlador de referencia usa Jenkins LTS **2.580.2** con Java 21 y plugins fijados. Escucha en `127.0.0.1:9090`, conserva el estado en un volumen y tiene cero ejecutores. Un agente Linux amd64 con un ejecutor se conecta por WebSocket y ejecuta Docker. El [`Jenkinsfile`](Jenkinsfile) obtiene `main` por SCM; `H/2 * * * *` consulta cambios aproximadamente cada dos minutos. La verificación nativa de Windows continúa en GitHub Actions.

### 1. Preparar e iniciar el controlador

Necesita Docker Linux amd64 y Compose V2. En el agente Linux o Ubuntu WSL2 necesita Java 21, Bash, Git, Python 3.10 o posterior, jq, curl, OpenSSL, tar y sha256sum. Reserve al menos 3 GiB libres en el checkout, asegure el acceso al socket Unix de Docker y compruebe que el agente pueda llegar a `127.0.0.1:9090`. Use un agente dedicado para este repositorio: el acceso al socket permite administrar las cargas del daemon.

```console
docker compose -f jenkins/compose.yaml config --quiet
docker compose -f jenkins/compose.yaml up -d --build
docker compose -f jenkins/compose.yaml ps
```

Abra [Jenkins local](http://127.0.0.1:9090/). Para desbloquear la primera instalación, lea la clave en una terminal privada con `docker compose -f jenkins/compose.yaml exec -T controlador cat /var/jenkins_home/secrets/initialAdminPassword`. Complete el asistente, cree el administrador local y configure la URL en loopback. Conserve autenticación y protección CSRF y deje desactivado el registro público de usuarios.

### 2. Configurar el nodo y el job

1. En **Administrar Jenkins → Nodos**, mantenga al controlador con cero ejecutores. Cree un agente permanente `linux-docker` con un ejecutor, etiqueta `linux-docker`, directorio remoto `/var/tmp/ruta-estadistica-agente` y uso reservado para trabajos con esa etiqueta. Seleccione el método en el cual el agente inicia la conexión con el controlador.
2. Cree el job Pipeline `ruta-estadistica-main`. En **Pipeline script from SCM**, seleccione Git y use `https://github.com/mljuansmoreno/p005Lab.git`, rama `*/main` y ruta `Jenkinsfile`. El checkout público solo requiere lectura.
3. Desde la página del nodo, tome su credencial y guárdela en el Linux del agente. Desde la raíz del checkout en Bash, el bloque siguiente la recibe sin mostrarla. Mantenga esa terminal abierta mientras trabaja el agente.

```bash
umask 077
install -d -m 700 /var/tmp/ruta-estadistica-agente
read -rs -p 'Credencial del nodo: ' RUTA_CI_CONEXION
printf '\n'
printf '%s\n' "$RUTA_CI_CONEXION" > /var/tmp/ruta-estadistica-agente/conexion.secreto
unset RUTA_CI_CONEXION
chmod 600 /var/tmp/ruta-estadistica-agente/conexion.secreto
bash jenkins/iniciar_agente.sh
```

[Instalación completa, plantillas CLI y autoprueba aislada](documentacion/jenkins.md).

### 3. Ejecutar, revisar y apagar

1. Confirme que `linux-docker` está en línea y ejecute **Build Now** para inicializar la consulta del repositorio. Para verificar el disparo automático, observe **Git Polling Log** y la causa del siguiente build tras un cambio publicado en `main`. Use **Build with Parameters → RUTA_CI_SIN_CACHE** cuando necesite reconstruir las dos imágenes en frío.
2. El pipeline verifica secretos y fuentes, ejecuta pruebas de la web, construye y arranca Compose, revisa aislamiento y autenticación, ejecuta el cálculo y la recuperación, prueba R y escanea ambas imágenes. Cada ejecución usa un proyecto Compose y puerto propios. El cierre registra la limpieza y publica JUnit y un manifiesto SHA-256.
3. Abra **Console Output**, **Test Result** y **Artifacts**. Coteje la causa y el SHA de la consola con `00-entorno.json`. Revise `05-calculo.txt`, `06-recuperacion.txt`, `08-pruebas-r.txt`, `09-limpieza.txt`, `seguridad-aplicacion.json` y `seguridad-motor.json`, los XML de `reportes/` y `manifest.json`. Si falla, use JUnit para ubicar la etapa y confirme que se retiraron los recursos del proyecto de ese build.
4. Cuando la cola esté vacía, detenga el agente con `Ctrl+C` y ejecute `docker compose -f jenkins/compose.yaml stop` para conservar el volumen y el historial. Para reanudar, use `docker compose -f jenkins/compose.yaml up -d` y vuelva a conectar el agente.

Para ejecutar las comprobaciones en Bash sin un controlador, con los requisitos del agente instalados:

```bash
PYTHONPATH=aplicacion:guiones python3 guiones/ci/ejecutar.py local
```

Los informes locales quedan en `salidas/jenkins-ci/`. Una ejecución local mediante ese lanzador no tiene número de build Jenkins.

### Alternativa: Jenkins en un runner alojado

En **Actions → Jenkins en runner Linux → Run workflow**, elija `main`. El workflow construye un controlador temporal, conecta un agente y dispara el job. Para pedir reconstrucción sin caché y capturas, puede usar GitHub CLI autenticada con permisos para ejecutar el workflow:

```bash
gh workflow run jenkins-alojado.yaml --ref main -f sin_cache=true -f capturas=true
```

Descargue `jenkins-<SHA>-<intento>` y, si se solicitaron capturas, `jenkins-capturas-<SHA>-<intento>`. Compare el SHA del build con el de Actions y la huella del anexo publicada en el resumen. El flujo alojado demuestra un disparo manual; el sondeo SCM se observa en el controlador permanente. [Operación, recuperación y retención](documentacion/operacion_jenkins.md) · [Guía de capturas](documentacion/capturas_semana5.md).

El piloto automático alojado [#11101](documentacion/evidencias-jenkins/build-11101/README.md) comprueba que el SHA del push coincida con el checkout. El controlador permanente mantiene su propio historial de Poll SCM. El pipeline vigente registra **Checkout**, **Build** y **Test** por separado, coteja las imágenes OCI antes de usar las construidas y conserva la limpieza de los proyectos por ejecución.

### Pruebas de Jenkins realizadas

| Build | Resultado registrado |
| --- | --- |
| **Local #9**, `911f2cb`, disparo por cambio SCM | `SUCCESS`. Seis pruebas web y trece de integración, cálculo real, recuperación del motor, suite de R 4.5.2, escaneo de las dos imágenes y limpieza. |
| **Local #13**, `bfde9fd`, disparo manual | `SUCCESS`. Seis pruebas web y trece de integración; el manifiesto conserva el cálculo, la recuperación, R, ambos escaneos y el desmontaje. |
| **Autopruebas locales #3 y #4** | `FAILURE` esperado en la aserción de cálculo. Se archivó el desmontaje y en #4 JUnit registró explícitamente `limpieza` como correcta. |
| **Autoprueba local #5**, `d92408c` | `ABORTED` al cancelar durante el cálculo; JUnit y el registro de desmontaje conservan la limpieza. |
| [Alojado #10201](https://github.com/mljuansmoreno/p005Lab/actions/runs/43801819087), `48d8a4e` | `SUCCESS` manual, 20 pruebas JUnit aprobadas, cálculo de seis filas, ambos escaneos y limpieza. |
| [Alojado #10501](https://github.com/mljuansmoreno/p005Lab/actions/runs/43805486879) y [#10601](https://github.com/mljuansmoreno/p005Lab/actions/runs/43806089502) | #10501 conservó IDs distintos y HTTP 200/503/200 en la prueba de recuperación. #10601 cotejó escaneos de ambas imágenes con base de avisos común y verificó la limpieza del proyecto. |
| [Alojado #10801](https://github.com/mljuansmoreno/p005Lab/actions/runs/43807515338) y [#10901](https://github.com/mljuansmoreno/p005Lab/actions/runs/43808744863) | #10801 conservó vistas de estado, etapas y 20 pruebas aprobadas. #10901 verificó el modo de compilación sin caché solicitado. |
| [Alojado #11001](https://github.com/mljuansmoreno/p005Lab/actions/runs/43810524298), `295325f` | `SUCCESS` manual en unos 132 s, reconstrucción sin caché, 20 pruebas aprobadas (6 web y 14 de integración), recálculo, escaneo sin coincidencias altas ni críticas y desmontaje. [Windows, Docker y secretos](https://github.com/mljuansmoreno/p005Lab/actions/runs/43810516949) aprobaron para el mismo SHA. |

El build local #17 agotó el plazo de escaneo anterior después de archivar el informe de la web; el #19 fue abortado y carece de artefactos. Esos resultados no cuentan como aceptaciones. El ensayo local de coexistencia fue independiente del job: usó un par de imágenes para una demo descartable y dos proyectos CI en puertos distintos. Hubo cinco cálculos correctos: tres iniciales y otros dos después de retirar el primer proyecto CI. El ensayo retiró sus propios recursos al terminar.

[Informe de semana 5](documentacion/entrega_semana5.md) · [Matriz de aceptación](documentacion/matriz_semana5.md).

## Ciberseguridad: verificaciones realizadas

Los registros corresponden a inspecciones defensivas de este repositorio, sus contenedores e imágenes. Cada JSON conserva la fecha de Bogotá, el control y el SHA auditado. El [informe inicial](documentacion/informes/revision_ciberseguridad.md) conserva por separado el antecedente sobre `0aad2e5`.

### Perfil NIST y métodos de evaluación

El perfil `p005Lab-2026-11` define **75 comprobaciones del proyecto** vinculadas a **17 controles** de [NIST SP 800-53 Rev. 5, versión 5.2.0](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final). La tabla muestra las correspondencias que registró el [lote del 23 de noviembre](documentacion/informes/revisiones-seguridad/2026-11-23).

[NIST SP 800-53A Rev. 5, versión 5.2.0](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final) guía **51 exámenes** de configuración, artefactos y estado observado, y **24 pruebas** que ejecutan comprobaciones y comparan sus resultados con los criterios del perfil. El perfil no usa entrevistas. Las correspondencias documentan el alcance de esta evaluación del repositorio.

[NIST SP 800-190 (2017)](https://csrc.nist.gov/pubs/sp/800/190/final) guía la revisión de imágenes y contenedores. El perfil referencia §4.1.1 para vulnerabilidades de imágenes, §4.1.4 para secretos incorporados, §4.1.5 para confianza y procedencia de imágenes, §4.3.3 para separación de redes, §4.4.3 para configuración de ejecución y §4.4.4 para vulnerabilidades de las aplicaciones. El JSON de cada comprobación conserva la sección aplicable cuando el perfil la asigna.

| Control de SP 800-53 | Comprobaciones de este repositorio |
| --- | --- |
| **AC-3** · Aplicación del control de acceso | [`http-motor-autenticacion`](documentacion/informes/revisiones-seguridad/2026-11-23/http-motor-autenticacion.json) |
| **AC-6** · Privilegio mínimo | [`aplicacion-no-privilegiado`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-no-privilegiado.json), [`aplicacion-sin-capacidades`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-sin-capacidades.json), [`aplicacion-sin-privilegios-nuevos`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-sin-privilegios-nuevos.json), [`aplicacion-sin-socket-docker`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-sin-socket-docker.json), [`aplicacion-usuario`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-usuario.json), [`motor-no-privilegiado`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-no-privilegiado.json), [`motor-sin-capacidades`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-sin-capacidades.json), [`motor-sin-privilegios-nuevos`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-sin-privilegios-nuevos.json), [`motor-sin-socket-docker`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-sin-socket-docker.json), [`motor-usuario`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-usuario.json) |
| **AU-4** · Capacidad de almacenamiento de auditoría | [`aplicacion-logs-rotados`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-logs-rotados.json), [`motor-logs-rotados`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-logs-rotados.json) |
| **AU-9** · Protección de la información de auditoría | [`bitacoras-sin-secreto`](documentacion/informes/revisiones-seguridad/2026-11-23/bitacoras-sin-secreto.json) |
| **CM-2** · Configuración de referencia | [`git-acciones-fijadas`](documentacion/informes/revisiones-seguridad/2026-11-23/git-acciones-fijadas.json), [`git-base-python-fijada`](documentacion/informes/revisiones-seguridad/2026-11-23/git-base-python-fijada.json), [`git-bases-declaradas`](documentacion/informes/revisiones-seguridad/2026-11-23/git-bases-declaradas.json) |
| **CM-6** · Parámetros de configuración | [`aplicacion-no-privilegiado`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-no-privilegiado.json), [`aplicacion-raiz-solo-lectura`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-raiz-solo-lectura.json), [`aplicacion-reinicio-acotado`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-reinicio-acotado.json), [`aplicacion-sin-capacidades`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-sin-capacidades.json), [`aplicacion-sin-privilegios-nuevos`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-sin-privilegios-nuevos.json), [`aplicacion-sin-socket-docker`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-sin-socket-docker.json), [`git-archivos-privados`](documentacion/informes/revisiones-seguridad/2026-11-23/git-archivos-privados.json), [`git-checkout-verificacion`](documentacion/informes/revisiones-seguridad/2026-11-23/git-checkout-verificacion.json), [`git-contexto-exclusiones`](documentacion/informes/revisiones-seguridad/2026-11-23/git-contexto-exclusiones.json), [`git-secreto-ignorado`](documentacion/informes/revisiones-seguridad/2026-11-23/git-secreto-ignorado.json), [`http-csp`](documentacion/informes/revisiones-seguridad/2026-11-23/http-csp.json), [`http-nosniff`](documentacion/informes/revisiones-seguridad/2026-11-23/http-nosniff.json), [`http-sin-cache`](documentacion/informes/revisiones-seguridad/2026-11-23/http-sin-cache.json), [`http-sin-referente`](documentacion/informes/revisiones-seguridad/2026-11-23/http-sin-referente.json), [`modelo-dependencia-salud`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-dependencia-salud.json), [`modelo-dns-motor`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-dns-motor.json), [`modelo-dos-servicios`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-dos-servicios.json), [`modelo-motor-tmpfs`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-motor-tmpfs.json), [`modelo-web-sonda`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-web-sonda.json), [`motor-no-privilegiado`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-no-privilegiado.json), [`motor-raiz-solo-lectura`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-raiz-solo-lectura.json), [`motor-reinicio-acotado`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-reinicio-acotado.json), [`motor-sin-capacidades`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-sin-capacidades.json), [`motor-sin-privilegios-nuevos`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-sin-privilegios-nuevos.json), [`motor-sin-socket-docker`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-sin-socket-docker.json) |
| **CM-8** · Inventario de componentes | [`imagen-aplicacion-sbom`](documentacion/informes/revisiones-seguridad/2026-11-23/imagen-aplicacion-sbom.json), [`imagen-motor-sbom`](documentacion/informes/revisiones-seguridad/2026-11-23/imagen-motor-sbom.json) |
| **IA-5** · Gestión de autenticadores | [`aplicacion-secreto-montado`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-secreto-montado.json), [`bitacoras-sin-secreto`](documentacion/informes/revisiones-seguridad/2026-11-23/bitacoras-sin-secreto.json), [`git-archivos-privados`](documentacion/informes/revisiones-seguridad/2026-11-23/git-archivos-privados.json), [`git-checkout-verificacion`](documentacion/informes/revisiones-seguridad/2026-11-23/git-checkout-verificacion.json), [`git-contexto-exclusiones`](documentacion/informes/revisiones-seguridad/2026-11-23/git-contexto-exclusiones.json), [`git-historial-secretos`](documentacion/informes/revisiones-seguridad/2026-11-23/git-historial-secretos.json), [`git-secreto-ignorado`](documentacion/informes/revisiones-seguridad/2026-11-23/git-secreto-ignorado.json), [`http-motor-autenticacion`](documentacion/informes/revisiones-seguridad/2026-11-23/http-motor-autenticacion.json), [`imagen-aplicacion-sin-secreto`](documentacion/informes/revisiones-seguridad/2026-11-23/imagen-aplicacion-sin-secreto.json), [`imagen-motor-sin-secreto`](documentacion/informes/revisiones-seguridad/2026-11-23/imagen-motor-sin-secreto.json), [`modelo-motor-secreto`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-motor-secreto.json), [`modelo-secreto-archivo`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-secreto-archivo.json), [`modelo-web-secreto`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-web-secreto.json), [`motor-secreto-montado`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-secreto-montado.json) |
| **RA-5** · Monitoreo y escaneo de vulnerabilidades | [`imagen-aplicacion-critical`](documentacion/informes/revisiones-seguridad/2026-11-23/imagen-aplicacion-critical.json), [`imagen-aplicacion-high`](documentacion/informes/revisiones-seguridad/2026-11-23/imagen-aplicacion-high.json), [`imagen-motor-critical`](documentacion/informes/revisiones-seguridad/2026-11-23/imagen-motor-critical.json), [`imagen-motor-high`](documentacion/informes/revisiones-seguridad/2026-11-23/imagen-motor-high.json) |
| **SA-11** · Pruebas y evaluación del desarrollador | [`git-diff`](documentacion/informes/revisiones-seguridad/2026-11-23/git-diff.json), [`git-historial-secretos`](documentacion/informes/revisiones-seguridad/2026-11-23/git-historial-secretos.json), [`http-calculo-r`](documentacion/informes/revisiones-seguridad/2026-11-23/http-calculo-r.json), [`http-csp`](documentacion/informes/revisiones-seguridad/2026-11-23/http-csp.json), [`http-formulario`](documentacion/informes/revisiones-seguridad/2026-11-23/http-formulario.json), [`http-nosniff`](documentacion/informes/revisiones-seguridad/2026-11-23/http-nosniff.json), [`http-sin-cache`](documentacion/informes/revisiones-seguridad/2026-11-23/http-sin-cache.json), [`http-sin-referente`](documentacion/informes/revisiones-seguridad/2026-11-23/http-sin-referente.json) |
| **SC-39** · Aislamiento de procesos | [`aplicacion-espacios-nombres`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-espacios-nombres.json), [`motor-espacios-nombres`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-espacios-nombres.json) |
| **SC-5** · Protección contra denegación de servicio | [`aplicacion-limite-cpu`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-limite-cpu.json), [`aplicacion-limite-memoria`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-limite-memoria.json), [`aplicacion-limite-procesos`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-limite-procesos.json), [`motor-limite-cpu`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-limite-cpu.json), [`motor-limite-memoria`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-limite-memoria.json), [`motor-limite-procesos`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-limite-procesos.json) |
| **SC-7** · Protección de límites | [`aplicacion-red-analisis`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-red-analisis.json), [`modelo-motor-redes`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-motor-redes.json), [`modelo-motor-sin-puertos`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-motor-sin-puertos.json), [`modelo-red-bridge`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-red-bridge.json), [`modelo-red-interna`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-red-interna.json), [`modelo-web-loopback`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-web-loopback.json), [`modelo-web-redes`](documentacion/informes/revisiones-seguridad/2026-11-23/modelo-web-redes.json), [`motor-red-analisis`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-red-analisis.json), [`red-inspeccion-interna`](documentacion/informes/revisiones-seguridad/2026-11-23/red-inspeccion-interna.json), [`red-miembros-esperados`](documentacion/informes/revisiones-seguridad/2026-11-23/red-miembros-esperados.json) |
| **SI-11** · Manejo de errores | [`http-404`](documentacion/informes/revisiones-seguridad/2026-11-23/http-404.json) |
| **SI-4** · Monitoreo del sistema | [`aplicacion-salud`](documentacion/informes/revisiones-seguridad/2026-11-23/aplicacion-salud.json), [`http-disponibilidad`](documentacion/informes/revisiones-seguridad/2026-11-23/http-disponibilidad.json), [`http-vida`](documentacion/informes/revisiones-seguridad/2026-11-23/http-vida.json), [`motor-salud`](documentacion/informes/revisiones-seguridad/2026-11-23/motor-salud.json) |
| **SI-7** · Integridad de software, firmware e información | [`git-jsonlite-integridad`](documentacion/informes/revisiones-seguridad/2026-11-23/git-jsonlite-integridad.json) |
| **SR-4** · Procedencia | [`git-acciones-fijadas`](documentacion/informes/revisiones-seguridad/2026-11-23/git-acciones-fijadas.json), [`git-base-python-fijada`](documentacion/informes/revisiones-seguridad/2026-11-23/git-base-python-fijada.json), [`git-bases-declaradas`](documentacion/informes/revisiones-seguridad/2026-11-23/git-bases-declaradas.json) |

### Resultados por fecha

La columna NIST cuenta los JSON que contienen `referencia_nist`. Los informes históricos se presentan como se publicaron. «Sin detalle» indica que el JSON no permite verificar el número de coincidencias del escaneo. La ficha de imagen identifica la ejecución cuando está disponible.

| Fecha y revisión auditada | Correctos / evaluados | JSON con referencia NIST | Web: altas / críticas | Motor: altas / críticas |
| --- | ---: | ---: | ---: | ---: |
| [15 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-15), `dbcafcb` | 72 / 75 | 0 | 54 / 3 | 3 / 0 |
| [16 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-16), `295325f` | 74 / 75 | 0 | 0 / 0 | 0 / 0 |
| [17 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-17), `7eff1f8` | 75 / 75 | 75 | 0 / 0 | 0 / 0 |
| [18 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-18), `17d9ab1` | 75 / 75 | 75 | 0 / 0 | 0 / 0 |
| [19 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-19), `f31460e` | 75 / 75 | 75 | 0 / 0 | 0 / 0 |
| [20 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-20), `01bde3d` | 74 / 75 | 0 | 0 / 0 | 0 / 0 |
| [21 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-21), `c130cad` | 73 / 75 | 0 | 10 / 0 | 0 / 0 |
| [22 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-22), `154c56e` | 75 / 75 | 0 | 0 / 0 | 0 / 0 |
| [23 de noviembre de 2026](documentacion/informes/revisiones-seguridad/2026-11-23), `2e49ce8` | 75 / 75 | 75 | 0 / 0 | 0 / 0 |

El 16 de noviembre, el control [de secretos en el historial de Git](documentacion/informes/revisiones-seguridad/2026-11-16/git-historial-secretos.json) quedó marcado como hallazgo. El registro no identifica una credencial concreta ni documenta el cierre del hallazgo. Es un resultado separado del escaneo de imágenes.

| Grupo | Controles | Cobertura observada |
| --- | ---: | --- |
| Git, fuentes y contexto | 10 | Acciones y base Python fijadas, bases declaradas, integridad de la fuente de jsonlite, checkout de verificación, diff, historial de secretos, exclusiones del contexto, archivos privados y exclusión del secreto. |
| Bitácoras | 1 | Verificación de que los logs revisados no contenían el secreto. |
| Modelo de Compose | 14 | Dos servicios; dependencia por salud; redes y DNS; publicación web solo en loopback; ninguna publicación del motor; sonda web, secretos de archivo en ambos servicios y tmpfs del motor. |
| Contenedores activos | 30 | Quince inspecciones por servicio: usuario, modo no privilegiado, capacidades retiradas, prohibición de privilegios nuevos, espacios de nombres, raíz de solo lectura, ausencia del socket de Docker, secreto montado, CPU, memoria, procesos, rotación de logs, reinicios acotados, salud y red. |
| Red activa | 2 | La red se inspeccionó como interna y con los miembros esperados. |
| HTTP | 10 | Vida, disponibilidad, formulario, cálculo R, respuesta 404, autenticación del motor y cabeceras CSP, `nosniff`, de caché y de referente. |
| Imágenes | 8 | Por imagen: inventario SBOM, ausencia del secreto y conteos por severidad alta y crítica. |

Después de los hallazgos se migró la imagen web a Alpine, se mantuvo Python 3.13 sin su extensión SQLite y se excluyó `sqlite-libs`. En el motor Ubuntu Noble se actualizaron APT y Brotli y se fijaron mínimos corregidos. También se retiraron ejemplos de credenciales de la distribución de jsonlite, se ajustaron las exclusiones de Git y Docker y se incorporó Gitleaks para fuentes y archivos comprimidos publicables. [Remediación](documentacion/remediacion_imagenes.md) · [Seguridad y privacidad](documentacion/seguridad_y_privacidad.md).

El registro del 16 enlaza los escaneos de [Actions 43863992759](https://github.com/mljuansmoreno/p005Lab/actions/runs/43863992759): la base de avisos de ese escaneo fue `2026-11-16T06:30:54Z`; Syft inventarió **1.423** componentes para la web y **8.828** para el motor. La evidencia vincula por imagen el ID canónico y la huella del SBOM CycloneDX con los resultados de Grype. El build #11001 usó su propia base y se documenta por separado. Los números de severidad son coincidencias de aviso y paquete para esas imágenes y esa base, no una garantía de seguridad futura o una certificación del producto.

En Windows también quedaron registrados [los controles HTTP del servicio](documentacion/informes/api_seguridad.json), [la consulta NuGet de dependencias directas y transitivas](documentacion/informes/vulnerabilidades.json) y [la revisión de permisos MCP](documentacion/informes/mcp_stdio.json). El registro de NuGet no devolvió paquetes vulnerables para el escritorio en esa consulta; los informes Windows no sustituyen el análisis de capas Linux.

### Remediación y evidencia reciente

- El [informe de remediación](documentacion/remediacion_imagenes.md) documenta la imagen web mínima, la retirada de OpenSSL del runtime HTTP local y la comprobación de SHA-256. La web limita los destinos del motor a la topología local autorizada y evita proxies y redirecciones en esa comunicación.
- La revisión del historial y de archivos publicables, incluidos comprimidos, usa Gitleaks. Las [excepciones históricas de Jenkins](documentacion/secretos-historial-jenkins.md) se validan por huella individual y corresponden a versiones públicas de plugins. Los informes publicados conservan el estado del control y omiten los valores sensibles.
- La [corrida del 23 de noviembre](https://github.com/mljuansmoreno/p005Lab/actions/runs/45198362075) verificó Windows, Docker Linux y secretos sobre `2e49ce8`. Los 75 JSON publicados para esa fecha quedaron en `correcto`, con cero coincidencias altas o críticas en ambas imágenes. El perfil exige una base de avisos de hasta 48 horas y conserva la huella del inventario CycloneDX, el identificador de imagen y la ejecución en los controles de escaneo.

## Evolución de la entrega

| Etapa | Cambios incorporados |
| --- | --- |
| Escritorio y cálculo local | WinUI en español, importación CSV/TSV/XLSX, roles y exclusiones explícitas, paquete R con métodos estadísticos, persistencia local, exportación reproducible y MSIX de desarrollo. |
| API y continuidad de Windows | API revisión 2 por trabajos con carga, consulta, resultado ZIP y cancelación; adaptador Docker; tablas nativas y reapertura de resultados por identidad y hash; límites adicionales en XLSX y restauración bloqueada de dependencias. |
| Demo Docker y GitHub Actions | Dos servicios, puertos y redes separados, sondas de vida y disponibilidad, cálculo cruzado y recuperación. Se añadieron metadatos OCI, verificación de fuentes, huella de revisión, informes por intento y limpieza de recursos. En paralelo se conservó el trabajo nativo de Windows. |
| Interfaz y seguridad | Tema claro predeterminado, selector de apariencia persistente y ajustes de contraste; formularios, tablas y avisos revisados. Se incorporaron controles de aislamiento, autenticación, publicación de secretos, SBOM y bloqueo por coincidencias altas o críticas. |
| Jenkins y trazabilidad | Controlador y agente WebSocket, sondeo SCM, runner alojado y autoprueba aislada. Se ampliaron los plazos de arranque y escaneo a partir de fallos observados, se verificó la caché de herramientas y se agregó recuperación de limpieza por proyecto. JUnit, huellas, capturas autenticadas, evidencia de coexistencia y exportación a Word/PDF quedaron vinculados al build y a la revisión. |
| Cierre de Jenkins | El lote histórico de 84 commits llega a `295325f`. La entrega posterior de 155 commits parte de `baed0fb` y cierra en `2e49ce8`. |
| Auditorías y remediación | Los controles por fecha conservan el SHA evaluado y los estados publicados. La remediación separa los hallazgos históricos, los cambios del runtime y las comprobaciones posteriores. |

Para ver los cambios de Jenkins en orden y abrir cualquier revisión desde el checkout:

```console
git log --reverse --oneline 0b0a87d..295325f
git log --oneline -- documentacion/informes/revisiones-seguridad
```

Consulte el [plan de incrementos](documentacion/plan_commits_semana5.md), la [guía de mantenimiento](documentacion/guia_mantenimiento.md), la [compatibilidad](documentacion/versiones_y_compatibilidad.md) y las [licencias y fuentes](documentacion/licencias_y_dependencias.md).
