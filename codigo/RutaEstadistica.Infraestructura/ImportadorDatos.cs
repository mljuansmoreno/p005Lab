using System.Globalization;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Xml;
using System.Xml.Linq;
using RutaEstadistica.Contratos;
namespace RutaEstadistica.Infraestructura;

public static class ImportadorDatos
{
    public const long LimiteBytes = 50 * 1024 * 1024;
    public static string Hash(byte[] contenido) => Convert.ToHexStringLower(SHA256.HashData(contenido));
    public static async Task<ConjuntoDatos> ImportarAsync(string ruta, OpcionesImportacion opciones, string? hoja = null, CancellationToken cancelacion = default)
    {
        var archivo = new FileInfo(ruta);
        if (archivo.Length > LimiteBytes) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
        var contenido = await File.ReadAllBytesAsync(ruta, cancelacion);
        List<string[]> filas;
        if (archivo.Extension.Equals(".xlsx", StringComparison.OrdinalIgnoreCase)) filas = LeerLibro(contenido, hoja);
        else if (archivo.Extension.ToLowerInvariant() is ".csv" or ".tsv")
        {
            string texto;
            try { texto = new UTF8Encoding(false, true).GetString(contenido).TrimStart('\uFEFF'); }
            catch (DecoderFallbackException) { throw new ErrorAplicacion("DATOS_CODIFICACION_INVALIDA"); }
            filas = LeerDelimitado(texto, opciones.Separador, cancelacion);
        }
        else throw new ErrorAplicacion("DATOS_FORMATO_NO_ADMITIDO");
        if (filas.Count == 0 || filas[0].Length == 0) throw new ErrorAplicacion("DATOS_INSUFICIENTES");
        var etiquetas = opciones.Cabecera ? filas[0] : Enumerable.Range(1, filas[0].Length).Select(indice => $"Columna {indice}").ToArray();
        if (opciones.Cabecera) filas.RemoveAt(0);
        if (etiquetas.Length > 200 || filas.Count > 100000 || filas.Any(fila => fila.Length != etiquetas.Length)) throw new ErrorAplicacion("DATOS_DIMENSIONES_INVALIDAS");
        foreach (var fila in filas) for (var indice = 0; indice < fila.Length; indice++) if (fila[indice] == opciones.MarcadorFaltante) fila[indice] = "";
        return new(etiquetas.Select((etiqueta, indice) => new ColumnaDatos($"c{indice + 1:D3}", etiqueta)).ToList(), filas, Hash(contenido), archivo.Name);
    }
    public static List<string[]> LeerDelimitado(string texto, char separador, CancellationToken cancelacion = default)
    {
        var filas = new List<string[]>(); var campos = new List<string>(); var campo = new StringBuilder();
        var entreComillas = false; var cerrada = false;
        for (var indice = 0; indice < texto.Length; indice++)
        {
            if (indice % 4096 == 0) cancelacion.ThrowIfCancellationRequested();
            var caracter = texto[indice];
            if (caracter == '"')
            {
                if (entreComillas && indice + 1 < texto.Length && texto[indice + 1] == '"') { campo.Append('"'); indice++; }
                else if (entreComillas) { entreComillas = false; cerrada = true; }
                else if (campo.Length == 0 && !cerrada) entreComillas = true;
                else throw new ErrorAplicacion("DATOS_CSV_INVALIDO");
            }
            else if (!entreComillas && (caracter == separador || caracter is '\r' or '\n'))
            {
                campos.Add(campo.ToString()); campo.Clear(); cerrada = false;
                if (campos.Count > 200) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
                if (caracter != separador)
                {
                    filas.Add(campos.ToArray()); campos.Clear();
                    if (caracter == '\r' && indice + 1 < texto.Length && texto[indice + 1] == '\n') indice++;
                    if (filas.Count > 100001) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
                }
            }
            else { if (cerrada) throw new ErrorAplicacion("DATOS_CSV_INVALIDO"); campo.Append(caracter); }
        }
        if (entreComillas) throw new ErrorAplicacion("DATOS_CSV_INVALIDO");
        if (campo.Length > 0 || campos.Count > 0 || cerrada) { campos.Add(campo.ToString()); filas.Add(campos.ToArray()); }
        return filas;
    }
    public static ConjuntoDatos ConfirmarRoles(ConjuntoDatos datos, IReadOnlyDictionary<string, string> roles, OpcionesImportacion opciones)
    {
        var columnas = datos.Columnas.Select(columna => columna with { Rol = roles.GetValueOrDefault(columna.Id, "texto") }).ToList();
        var filas = datos.Filas.Select(fila => fila.ToArray()).ToList();
        var formato = new NumberFormatInfo { NumberDecimalSeparator = opciones.Decimal.ToString(), NumberGroupSeparator = opciones.Miles == '\0' ? "\uFFFF" : opciones.Miles.ToString() };
        for (var indice = 0; indice < columnas.Count; indice++)
        {
            if (!new[] { "texto", "numerica", "categorica", "ordinal", "identificador", "fecha" }.Contains(columnas[indice].Rol)) throw new ErrorAplicacion("DATOS_ROL_INVALIDO");
            foreach (var fila in filas)
            {
                if (fila[indice] == "") continue;
                if (columnas[indice].Rol == "numerica")
                {
                    var estilos = NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint | NumberStyles.AllowExponent;
                    if (opciones.Miles != '\0') estilos |= NumberStyles.AllowThousands;
                    if (!double.TryParse(fila[indice], estilos, formato, out var valor) || !double.IsFinite(valor)) throw new ErrorAplicacion("DATOS_NUMERO_INVALIDO");
                    fila[indice] = valor.ToString("R", CultureInfo.InvariantCulture);
                }
                if (columnas[indice].Rol == "fecha" && !DateTime.TryParseExact(fila[indice], opciones.FormatoFecha, CultureInfo.InvariantCulture, DateTimeStyles.None, out _)) throw new ErrorAplicacion("DATOS_FECHA_INVALIDA");
            }
        }
        return datos with { Columnas = columnas, Filas = filas };
    }
    private static XDocument LeerXml(ZipArchiveEntry entrada)
    {
        using var flujo = entrada.Open();
        using var lector = XmlReader.Create(flujo, new XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit, XmlResolver = null, MaxCharactersInDocument = 100 * 1024 * 1024 });
        return XDocument.Load(lector);
    }
    public static List<string> ListarHojas(byte[] contenido)
    {
        using var archivo = AbrirLibro(contenido); XNamespace espacio = "http://schemas.openxmlformats.org/spreadsheetml/2006/main";
        return LeerXml(archivo.GetEntry("xl/workbook.xml") ?? throw new ErrorAplicacion("DATOS_LIBRO_INVALIDO")).Descendants(espacio + "sheet").Select(hoja => (string)hoja.Attribute("name")!).ToList();
    }
    private static ZipArchive AbrirLibro(byte[] contenido)
    {
        var archivo = new ZipArchive(new MemoryStream(contenido));
        if (archivo.Entries.Count > 1000 || archivo.Entries.Sum(entrada => entrada.Length) > 200 * 1024 * 1024 || archivo.Entries.Any(entrada => entrada.FullName.Contains("vbaProject", StringComparison.OrdinalIgnoreCase) || entrada.FullName.Contains("externalLinks", StringComparison.OrdinalIgnoreCase))) { archivo.Dispose(); throw new ErrorAplicacion("DATOS_LIBRO_INVALIDO"); }
        return archivo;
    }
    private static List<string[]> LeerLibro(byte[] contenido, string? hoja)
    {
        using var archivo = AbrirLibro(contenido);
        XNamespace espacio = "http://schemas.openxmlformats.org/spreadsheetml/2006/main";
        XNamespace relaciones = "http://schemas.openxmlformats.org/officeDocument/2006/relationships";
        var libro = LeerXml(archivo.GetEntry("xl/workbook.xml") ?? throw new ErrorAplicacion("DATOS_LIBRO_INVALIDO"));
        var hojas = libro.Descendants(espacio + "sheet").ToList();
        if (hoja is null) throw new ErrorAplicacion("DATOS_HOJA_SIN_CONFIRMAR");
        var elegida = hojas.SingleOrDefault(elemento => (string?)elemento.Attribute("name") == hoja) ?? throw new ErrorAplicacion("DATOS_HOJA_INVALIDA");
        var vinculos = LeerXml(archivo.GetEntry("xl/_rels/workbook.xml.rels")!);
        var destino = (string?)vinculos.Root!.Elements().Single(elemento => (string?)elemento.Attribute("Id") == (string?)elegida.Attribute(relaciones + "id")).Attribute("Target");
        if (destino is null || destino.Contains("..") || destino.Contains(':')) throw new ErrorAplicacion("DATOS_LIBRO_INVALIDO");
        var ruta = destino.StartsWith('/') ? destino.TrimStart('/') : "xl/" + destino;
        var compartidos = archivo.GetEntry("xl/sharedStrings.xml") is { } entrada ? LeerXml(entrada).Descendants(espacio + "si").Select(elemento => string.Concat(elemento.Descendants(espacio + "t").Select(texto => texto.Value))).ToList() : [];
        var filas = new List<string[]>();
        long octetosExpandidos = 0;
        foreach (var fila in LeerXml(archivo.GetEntry(ruta) ?? throw new ErrorAplicacion("DATOS_LIBRO_INVALIDO")).Descendants(espacio + "row"))
        {
            var valores = new SortedDictionary<int, string>();
            foreach (var celda in fila.Elements(espacio + "c"))
            {
                if (celda.Element(espacio + "f") != null) throw new ErrorAplicacion("DATOS_FORMULA_NO_ADMITIDA");
                var referencia = (string?)celda.Attribute("r") ?? throw new ErrorAplicacion("DATOS_LIBRO_INVALIDO");
                if (!System.Text.RegularExpressions.Regex.IsMatch(referencia, "^[A-Z]{1,3}[1-9][0-9]{0,6}$")) throw new ErrorAplicacion("DATOS_LIBRO_INVALIDO");
                var indice = 0; foreach (var letra in referencia.TakeWhile(char.IsLetter)) indice = indice * 26 + letra - 'A' + 1;
                if (indice is < 1 or > 200) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
                var texto = celda.Element(espacio + "v")?.Value ?? string.Concat(celda.Descendants(espacio + "t").Select(elemento => elemento.Value));
                if ((string?)celda.Attribute("t") == "s") texto = compartidos[int.Parse(texto, CultureInfo.InvariantCulture)];
                // Una cadena compartida puede repetirse miles de veces sin aumentar el tamaño del ZIP.
                octetosExpandidos += Encoding.UTF8.GetByteCount(texto);
                if (octetosExpandidos > LimiteBytes) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
                if (!valores.TryAdd(indice - 1, texto)) throw new ErrorAplicacion("DATOS_LIBRO_INVALIDO");
            }
            filas.Add(Enumerable.Range(0, valores.Count > 0 ? valores.Keys.Max() + 1 : 0).Select(indice => valores.GetValueOrDefault(indice, "")).ToArray());
            if (filas.Count > 100001) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
        }
        var ancho = filas.Count > 0 ? filas.Max(fila => fila.Length) : 0;
        return filas.Select(fila => fila.Concat(Enumerable.Repeat("", ancho - fila.Length)).ToArray()).ToList();
    }
    public static string CsvNormalizado(ConjuntoDatos datos)
    {
        var cabecera = string.Join(',', datos.Columnas.Select(columna => EscaparCsv(columna.Id)));
        var filas = datos.Filas.Select(fila => string.Join(',', fila.Select(valor => EscaparCsv(valor))));
        return string.Join("\n", new[] { cabecera }.Concat(filas)) + "\n";
    }
    public static string EscaparCsv(string valor, bool seguro = false) => "\"" + ((seguro && valor.TrimStart().StartsWithAny('=', '+', '-', '@', '\t', '\r')) ? "'" : "") + valor.Replace("\"", "\"\"") + "\"";
    private static bool StartsWithAny(this string texto, params char[] caracteres) => texto.Length > 0 && caracteres.Contains(texto[0]);
}
