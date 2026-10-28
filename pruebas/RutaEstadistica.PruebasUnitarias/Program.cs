using System.IO.Compression;
using System.Text;
using RutaEstadistica.Contratos;
using RutaEstadistica.Dominio;
using RutaEstadistica.Infraestructura;
using RutaEstadistica.Aplicacion;

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
        intermediario.Revocar();
        try { await intermediario.AtenderAsync(new("obtener_resumen_datos", proyecto.Id)); throw new Exception("Revocación ignorada"); }
        catch (ErrorAplicacion error) { Verificar(error.Codigo == "MCP_DESHABILITADO", "Revocación MCP es inmediata"); }
    }
    if (args.Length > 0)
    {
        var csv = ImportadorDatos.CsvNormalizado(preparados); var hash = ImportadorDatos.Hash(Encoding.UTF8.GetBytes(csv));
        var solicitud = new SolicitudAnalisis(1, Guid.NewGuid().ToString("N"), proyecto.Id, hash, hash, "descriptivo", ["c002"], PoliticaFaltantes: "excluir_confirmados");
        var trabajo = Path.Combine(temporal, "trabajo");
        var resultado = await new MotorRLocal(Path.GetFullPath(args[0])).EjecutarAsync(solicitud, csv, trabajo, CancellationToken.None);
        Verificar(resultado.Contenido.GetProperty("cifras").GetProperty("media").GetDouble() == 2, "Trabajador R real devuelve media conocida con exclusión");
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
    }
    Console.WriteLine($"TOTAL: {verificadas} comprobaciones correctas.");
}
finally { Microsoft.Data.Sqlite.SqliteConnection.ClearAllPools(); Directory.Delete(temporal, true); }
