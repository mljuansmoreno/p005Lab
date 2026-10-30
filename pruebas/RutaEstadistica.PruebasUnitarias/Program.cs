using System.IO.Compression;
using System.Text;
using RutaEstadistica.Contratos;
using RutaEstadistica.Dominio;
using RutaEstadistica.Infraestructura;
using RutaEstadistica.Aplicacion;

Console.OutputEncoding = new System.Text.UTF8Encoding(false);
var verificadas = 0;
void Verificar(bool condicion, string descripcion) { if (!condicion) throw new Exception("FALLO: " + descripcion); Console.WriteLine("VERIFICADO: " + descripcion); verificadas++; }
void Rechazar(Action accion, string codigo) { try { accion(); throw new Exception("No se rechazó " + codigo); } catch (ErrorAplicacion error) { Verificar(error.Codigo == codigo, codigo); } }
var temporal = Path.Combine(Path.GetTempPath(), "ruta_pruebas_" + Guid.NewGuid().ToString("N")); Directory.CreateDirectory(temporal);
try
{
    var filas = ImportadorDatos.LeerDelimitado("nombre;valor\r\n\"José; Díaz\";\"1,5\"\r\n\"dos\nlineas\";2\r\n", ';');
    Verificar(filas.Count == 3 && filas[1][0] == "José; Díaz" && filas[2][0].Contains('\n'), "CSV conserva Unicode, comillas y saltos internos");
    Rechazar(() => ImportadorDatos.LeerDelimitado("a;\"sin cerrar", ';'), "DATOS_CSV_INVALIDO");
    var ruta = Path.Combine(temporal, "datos.csv"); var original = Encoding.UTF8.GetBytes("Código;Medición COP\n001;1,5\n002;2,5\n003;NA\n"); await File.WriteAllBytesAsync(ruta, original);
    var datos = await ImportadorDatos.ImportarAsync(ruta, new());
    Verificar(datos.Filas[0][0] == "001" && datos.Columnas[1].Etiqueta == "Medición COP", "Importación no convierte identificadores ni etiquetas");
    var preparados = ImportadorDatos.ConfirmarRoles(datos, new Dictionary<string, string> { ["c001"] = "identificador", ["c002"] = "numerica" }, new());
    Verificar(preparados.Filas[0][1] == "1.5" && preparados.Filas[0][0] == "001" && preparados.Filas[2][1] == "", "Conversión decimal explícita y faltantes");
    Rechazar(() => ImportadorDatos.ConfirmarRoles(datos, new Dictionary<string, string> { ["c002"] = "numerica" }, new(Decimal: '.')), "DATOS_NUMERO_INVALIDO");
    Verificar(ImportadorDatos.EscaparCsv("=1+1", true) == "\"'=1+1\"", "CSV seguro neutraliza fórmula de hoja de cálculo");
    var libro = Path.Combine(temporal, "libro.xlsx");
    using (var archivo = ZipFile.Open(libro, ZipArchiveMode.Create))
    {
        var partes = new Dictionary<string, string>
        {
            ["xl/workbook.xml"] = "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"Mediciones\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>",
            ["xl/_rels/workbook.xml.rels"] = "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Target=\"worksheets/sheet1.xml\"/></Relationships>",
            ["xl/worksheets/sheet1.xml"] = "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row r=\"1\"><c r=\"A1\" t=\"inlineStr\"><is><t>Código</t></is></c><c r=\"B1\" t=\"inlineStr\"><is><t>Valor</t></is></c></row><row r=\"2\"><c r=\"A2\" t=\"inlineStr\"><is><t>001</t></is></c><c r=\"B2\"><v>2.5</v></c></row></sheetData></worksheet>"
        };
        foreach (var parte in partes) { using var escritor = new StreamWriter(archivo.CreateEntry(parte.Key).Open()); escritor.Write(parte.Value); }
    }
    Verificar(ImportadorDatos.ListarHojas(await File.ReadAllBytesAsync(libro)).SequenceEqual(["Mediciones"]), "XLSX enumera hojas sin ejecutar contenido");
    var datosLibro = await ImportadorDatos.ImportarAsync(libro, new(), "Mediciones");
    Verificar(datosLibro.Filas[0][0] == "001" && datosLibro.Filas[0][1] == "2.5", "XLSX conserva texto y valores originales");
    try { await ImportadorDatos.ImportarAsync(libro, new()); throw new Exception("Hoja no confirmada aceptada"); }
    catch (ErrorAplicacion error) { Verificar(error.Codigo == "DATOS_HOJA_SIN_CONFIRMAR", "XLSX exige elección explícita de hoja"); }
    using (var archivo = ZipFile.Open(libro, ZipArchiveMode.Update))
    {
        archivo.GetEntry("xl/worksheets/sheet1.xml")!.Delete(); using var escritor = new StreamWriter(archivo.CreateEntry("xl/worksheets/sheet1.xml").Open());
        escritor.Write("<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row><c r=\"A1\"><f>1+1</f><v>2</v></c></row></sheetData></worksheet>");
    }
    try { await ImportadorDatos.ImportarAsync(libro, new(), "Mediciones"); throw new Exception("Fórmula aceptada"); }
    catch (ErrorAplicacion error) { Verificar(error.Codigo == "DATOS_FORMULA_NO_ADMITIDA", "XLSX rechaza fórmulas"); }
    var repositorio = new RepositorioProyectos(Path.Combine(temporal, "proyectos")); var proyecto = repositorio.Crear("Prueba con tildes á"); repositorio.GuardarDatos(proyecto.Id, preparados, original);
    Verificar(new RepositorioProyectos(repositorio.Raiz).LeerDatos(proyecto.Id)!.Filas[0][0] == "001", "SQLite y datos se reabren sin pérdida");
    var portatil = Path.Combine(temporal, "exportado.rutaestadistica"); repositorio.ExportarProyecto(proyecto.Id, portatil); var copia = repositorio.ImportarProyecto(portatil);
    Verificar(copia.Id != proyecto.Id && repositorio.LeerDatos(copia.Id)!.HashOriginal == datos.HashOriginal, "Archivo portátil valida hashes y crea identidad nueva");
    var malicioso = Path.Combine(temporal, "malicioso.zip"); using (var archivo = ZipFile.Open(malicioso, ZipArchiveMode.Create)) { using var escritor = new StreamWriter(archivo.CreateEntry("../escape.json").Open()); escritor.Write("{}"); }
    Rechazar(() => repositorio.ImportarProyecto(malicioso), "PROYECTO_ARCHIVO_INSEGURO");
    Rechazar(() => repositorio.Directorio("../fuera"), "PROYECTO_ID_INVALIDO");
    repositorio.EliminarConRespaldo(copia.Id); Verificar(!repositorio.Listar().Any(elemento => elemento.Id == copia.Id) && Directory.GetFiles(Path.Combine(repositorio.Raiz, "respaldos")).Length == 1, "Eliminar conserva respaldo recuperable");
    RepositorioProyectos.EscribirAtomico(Path.Combine(temporal, "atomico.json"), "uno"); RepositorioProyectos.EscribirAtomico(Path.Combine(temporal, "atomico.json"), "dos");
    Verificar(File.ReadAllText(Path.Combine(temporal, "atomico.json")) == "dos", "Reemplazo atómico conserva último contenido completo");
    using (var intermediario = new IntermediarioMcp(repositorio, new MotorRLocal(args.Length > 0 ? Path.GetFullPath(args[0]) : temporal)))
    {
        try { await intermediario.AtenderAsync(new("listar_proyectos_autorizados")); throw new Exception("MCP habilitado por omisión"); }
        catch (ErrorAplicacion error) { Verificar(error.Codigo == "MCP_DESHABILITADO", "MCP deshabilitado inicialmente"); }
        intermediario.Conceder(new(proyecto.Id, true, false, false, false)); intermediario.Activar();
        var autorizado = await intermediario.AtenderAsync(new("obtener_resumen_datos", proyecto.Id));
        Verificar(System.Text.Json.JsonSerializer.Serialize(autorizado).Contains("filas"), "MCP permite resumen autorizado");
        try { await intermediario.AtenderAsync(new("obtener_resumen_datos", Guid.NewGuid().ToString("N"))); throw new Exception("Se filtró proyecto ajeno"); }
        catch (ErrorAplicacion error) { Verificar(error.Codigo == "MCP_PERMISO_DENEGADO", "MCP aísla proyectos"); }
        try { await intermediario.AtenderAsync(new("ejecutar_analisis", proyecto.Id)); throw new Exception("Se permitió cálculo sin permiso"); }
        catch (ErrorAplicacion error) { Verificar(error.Codigo == "MCP_PERMISO_DENEGADO", "MCP exige permiso independiente de ejecución"); }
        if (args.Length > 0)
        {
            intermediario.Conceder(new(proyecto.Id, true, true, false, false));
            var metadatos = System.Text.Json.JsonSerializer.SerializeToElement(await intermediario.AtenderAsync(new("obtener_resumen_datos", proyecto.Id)));
            var hash = metadatos.GetProperty("hash_datos").GetString()!;
            var solicitud = new SolicitudAnalisis(1, Guid.NewGuid().ToString("N"), proyecto.Id, hash, hash, "descriptivo", ["c002"], PoliticaFaltantes: "excluir_confirmados");
            var encolado = System.Text.Json.JsonSerializer.SerializeToElement(await intermediario.AtenderAsync(new("ejecutar_analisis", proyecto.Id, Solicitud: solicitud)));
            var id = encolado.GetProperty("trabajo_id").GetString()!;
            TrabajoAnalisis trabajo;
            var limite = DateTimeOffset.UtcNow.AddSeconds(30);
            do { await Task.Delay(100); trabajo = (TrabajoAnalisis)await intermediario.AtenderAsync(new("consultar_trabajo", proyecto.Id, id)); }
            while (trabajo.Estado is EstadoTrabajo.Pendiente or EstadoTrabajo.Ejecutando && DateTimeOffset.UtcNow < limite);
            Verificar(trabajo.Estado == EstadoTrabajo.Completado, "MCP ejecuta análisis R real con hash descubierto y permiso vigente");
            var resultado = System.Text.Json.JsonSerializer.Serialize(await intermediario.AtenderAsync(new("obtener_resultado", proyecto.Id, id)));
            Verificar(resultado.Contains("interpretacion") && !resultado.Contains("residuos") && !resultado.Contains(temporal), "MCP devuelve resultado limitado sin rutas ni registros");
        }
        intermediario.Revocar();
        try { await intermediario.AtenderAsync(new("obtener_resumen_datos", proyecto.Id)); throw new Exception("Revocación ignorada"); }
        catch (ErrorAplicacion error) { Verificar(error.Codigo == "MCP_DESHABILITADO", "Revocación MCP es inmediata"); }
    }
    await using (var gestor = new GestorTrabajosMotor(new MotorEsperaControlada(), temporal))
    {
        var csv = ImportadorDatos.CsvNormalizado(preparados); var hash = ImportadorDatos.Hash(Encoding.UTF8.GetBytes(csv));
        var carga = gestor.Cargar(new(proyecto.Id, csv));
        Verificar(carga.HashDatos == hash && carga.Filas == 3, "Carga de API registra revisión y recuentos sin truncar");
        var solicitud = new SolicitudAnalisis(1, Guid.NewGuid().ToString("N"), proyecto.Id, hash, hash, "descriptivo", ["c002"], PoliticaFaltantes: "excluir_confirmados");
        var primero = gestor.Encolar(new(carga.DatosId, solicitud));
        Rechazar(() => Validacion.Validar(solicitud with { Columnas = null! }, preparados), "CONTRATO_SOLICITUD_INVALIDA");
        Rechazar(() => Validacion.Validar(solicitud with { HashDatos = null! }, preparados), "DATOS_HASH_INVALIDO");
        Rechazar(() => Validacion.Validar(solicitud with { PoliticaFaltantes = "eliminar_sin_confirmar" }, preparados), "ANALISIS_OPCION_INVALIDA");
        var segundo = gestor.Encolar(new(carga.DatosId, solicitud with { SolicitudId = Guid.NewGuid().ToString("N") }));
        Rechazar(() => gestor.Encolar(new(carga.DatosId, solicitud)), "TRABAJO_COLA_LLENA");
        Rechazar(() => gestor.Consultar(primero.TrabajoId, Guid.NewGuid().ToString("N")), "TRABAJO_NO_ENCONTRADO");
        Rechazar(() => gestor.ObtenerResultado(primero.TrabajoId, proyecto.Id), "RESULTADO_NO_DISPONIBLE");
        Verificar(gestor.Cancelar(segundo.TrabajoId, proyecto.Id).Estado == "cancelado", "API cancela trabajo en espera sin afectar al primero");
        Verificar(gestor.Cancelar(primero.TrabajoId, proyecto.Id).Estado == "cancelado", "API reconoce cancelación del trabajo activo");
        Rechazar(() => gestor.Encolar(new(carga.DatosId, solicitud with { HashDatos = new string('0', 64) })), "DATOS_HASH_INVALIDO");
        for (var indice = 0; indice < 3; indice++) gestor.Cargar(new(proyecto.Id, csv));
        Rechazar(() => gestor.Cargar(new(proyecto.Id, csv)), "MOTOR_ALMACEN_LLENO");
    }
    Verificar(Directory.GetDirectories(temporal, "ruta_motor_*").Length == 0, "Cierre de API espera cancelación y limpia solamente sus temporales");
    Verificar(PresentacionResultados.Formatear(System.Text.Json.JsonSerializer.SerializeToElement(1.5)) == "1,5", "Presentación usa decimal colombiano sin alterar el valor almacenado");
    Verificar(PresentacionResultados.Formatear(System.Text.Json.JsonSerializer.SerializeToElement<object?>(null)) == "No disponible", "La tabla distingue una cifra ausente de cero");
    if (args.Length > 0)
    {
        var csv = ImportadorDatos.CsvNormalizado(preparados); var hash = ImportadorDatos.Hash(Encoding.UTF8.GetBytes(csv));
        var solicitud = new SolicitudAnalisis(1, Guid.NewGuid().ToString("N"), proyecto.Id, hash, hash, "descriptivo", ["c002"], PoliticaFaltantes: "excluir_confirmados");
        var idHistorial = Guid.NewGuid().ToString("N");
        var trabajo = Path.Combine(proyecto.Directorio, "trabajo_" + idHistorial);
        var resultado = await new MotorRLocal(Path.GetFullPath(args[0])).EjecutarAsync(solicitud, csv, trabajo, CancellationToken.None);
        Verificar(resultado.Contenido.GetProperty("cifras").GetProperty("media").GetDouble() == 2, "Trabajador R real devuelve media conocida con exclusión");
        Verificar(PresentacionResultados.Cifras(resultado).Any(fila => fila.Indicador == "Media" && fila.Valor == "2"), "Tabla nativa presenta la media calculada por R");
        Verificar(repositorio.ListarHistorial(proyecto.Id).Any(entrada => entrada.Id == idHistorial), "Historial descubre cálculos completos al reabrir el proyecto");
        var archivoHistorico = Path.Combine(temporal, "historico.rutaestadistica"); repositorio.ExportarProyecto(proyecto.Id, archivoHistorico);
        var copiaHistorica = repositorio.ImportarProyecto(archivoHistorico);
        Verificar(repositorio.LeerTrabajo(copiaHistorica.Id, idHistorial).Solicitud.SolicitudId == solicitud.SolicitudId, "Historial portátil conserva procedencia de la solicitud original");
        File.AppendAllText(Path.Combine(copiaHistorica.Directorio, "trabajo_" + idHistorial, "entrada.csv"), "alterado");
        Rechazar(() => repositorio.LeerTrabajo(copiaHistorica.Id, idHistorial), "DATOS_HASH_INVALIDO");
        Verificar(!repositorio.ListarHistorial(copiaHistorica.Id).Any(entrada => entrada.Id == idHistorial), "Historial no ofrece como válido un cálculo con entrada alterada");
        var exportado = Path.Combine(temporal, "informe"); Exportador.Exportar(trabajo, exportado, true);
        Verificar(File.ReadAllText(Path.Combine(exportado, "informe.html")).Contains("data:image/png;base64,") && File.Exists(Path.Combine(exportado, "reproducir.R")), "Exportación HTML incrusta PNG e incluye reproducción");
        var inicioR = new System.Diagnostics.ProcessStartInfo(Path.Combine(Path.GetFullPath(args[0]), "runtime", "R", "bin", "Rscript.exe")) { UseShellExecute = false, CreateNoWindow = true, WorkingDirectory = exportado, RedirectStandardError = true, RedirectStandardOutput = true };
        inicioR.ArgumentList.Add("--vanilla"); inicioR.ArgumentList.Add("reproducir.R"); inicioR.Environment["R_LIBS_USER"] = Path.Combine(Path.GetFullPath(args[0]), "runtime", "biblioteca");
        using (var procesoR = System.Diagnostics.Process.Start(inicioR)!) { var erroresR = procesoR.StandardError.ReadToEndAsync(); var salidaR = procesoR.StandardOutput.ReadToEndAsync(); await procesoR.WaitForExitAsync(); await erroresR; await salidaR; Verificar(procesoR.ExitCode == 0, "Guion exportado se ejecuta sobre su propia entrada"); }
        using (var reproducido = System.Text.Json.JsonDocument.Parse(await File.ReadAllTextAsync(Path.Combine(exportado, "resultado_reproducido.json"))))
            Verificar(reproducido.RootElement.GetProperty("cifras").GetProperty("media").GetDouble() == 2, "Reproducción exportada conserva resultado conocido");
        using var cancelacion = new CancellationTokenSource(); cancelacion.Cancel();
        try { await new MotorRLocal(Path.GetFullPath(args[0])).EjecutarAsync(solicitud, csv, Path.Combine(temporal, "cancelado"), cancelacion.Token); throw new Exception("Cancelación ignorada"); }
        catch (ErrorAplicacion error) { Verificar(error.Codigo == "TRABAJO_CANCELADO", "Cancelación termina trabajador propio"); }
        if (args.Length >= 3)
        {
            using var cliente = new System.Net.Http.HttpClient { BaseAddress = new Uri(args[1]) };
            cliente.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", (await File.ReadAllTextAsync(args[2])).Trim());
            var remoto = await new MotorDocker(cliente).EjecutarAsync(solicitud, csv, Path.Combine(temporal, "trabajo_http"), CancellationToken.None);
            Verificar(remoto.Contenido.GetProperty("cifras").GetProperty("media").GetDouble() == 2, "Adaptador Docker completa carga, sondeo y descarga frente a API real de Windows");
        }
    }
    Console.WriteLine($"TOTAL: {verificadas} comprobaciones correctas.");
}
finally { Microsoft.Data.Sqlite.SqliteConnection.ClearAllPools(); Directory.Delete(temporal, true); }

// Doble exclusivo de prueba: bloquea hasta cancelación para verificar colas sin inventar estadísticas.
sealed class MotorEsperaControlada : IMotorAnalisis
{
    public async Task<ResultadoAnalisis> EjecutarAsync(SolicitudAnalisis solicitud, string csv, string destino, CancellationToken cancelacion)
    {
        await Task.Delay(Timeout.Infinite, cancelacion);
        throw new ErrorAplicacion("MOTOR_CALCULO_FALLIDO");
    }
}
