using System.Net;
using System.Text;
using System.Text.Json;
using RutaEstadistica.Contratos;
namespace RutaEstadistica.Infraestructura;
public static class Exportador
{
    public static void Exportar(string origen, string destino, bool hojaCalculoSegura)
    {
        if (Directory.Exists(destino)) throw new ErrorAplicacion("EXPORTACION_DESTINO_EXISTENTE");
        Directory.CreateDirectory(destino);
        var resultado = JsonSerializer.Deserialize<JsonElement>(File.ReadAllText(Path.Combine(origen, "resultado.json")));
        var imagen = Convert.ToBase64String(File.ReadAllBytes(Path.Combine(origen, "figura.png")));
        var informe = "<!doctype html><html lang=\"es\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\"><meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; img-src data:; style-src 'unsafe-inline'\"><title>Ruta Estadística</title><style>body{font:18px system-ui;max-width:1000px;margin:3em auto;padding:1em}img{max-width:100%}pre{white-space:pre-wrap}</style><h1>Ruta Estadística</h1><p>" + WebUtility.HtmlEncode(resultado.GetProperty("interpretacion").GetString()) + "</p><img alt=\"Gráfico del análisis; cifras y exclusiones detalladas a continuación\" src=\"data:image/png;base64," + imagen + "\"><h2>Evidencia numérica y procedencia</h2><pre>" + WebUtility.HtmlEncode(resultado.ToString()) + "</pre></html>";
        File.WriteAllText(Path.Combine(destino, "informe.html"), informe, new UTF8Encoding(false));
        foreach (var nombre in new[] { "entrada.csv", "solicitud.json", "resultado.json", "figura.png" }) File.Copy(Path.Combine(origen, nombre), Path.Combine(destino, nombre));
        var cifras = resultado.GetProperty("cifras").EnumerateObject().Select(cifra => ImportadorDatos.EscaparCsv(cifra.Name, hojaCalculoSegura) + "," + ImportadorDatos.EscaparCsv(cifra.Value.ToString(), hojaCalculoSegura));
        var filas = new List<string> { "\"indicador\",\"valor\"" }; filas.AddRange(cifras);
        if (resultado.GetProperty("tablas").ValueKind == JsonValueKind.Array)
            foreach (var fila in resultado.GetProperty("tablas").EnumerateArray()) filas.Add(ImportadorDatos.EscaparCsv(fila.GetProperty("categoria").GetString()!, hojaCalculoSegura) + "," + ImportadorDatos.EscaparCsv(fila.GetProperty("frecuencia").ToString(), hojaCalculoSegura));
        File.WriteAllLines(Path.Combine(destino, "resultados.csv"), filas, new UTF8Encoding(true));
        File.WriteAllText(Path.Combine(destino, "reproducir.R"), "# Ejecute en este directorio con rutaanalitica 0.1.0 y jsonlite instalados.\nsolicitud <- jsonlite::fromJSON('solicitud.json', simplifyVector = FALSE)\ndatos <- read.csv('entrada.csv', colClasses = 'character', check.names = FALSE, na.strings = '', fileEncoding = 'UTF-8')\nresultado <- rutaanalitica::analizar(solicitud, datos, getwd())\njsonlite::write_json(resultado, 'resultado_reproducido.json', auto_unbox = TRUE, null = 'null', digits = NA)\n", new UTF8Encoding(false));
    }
}
