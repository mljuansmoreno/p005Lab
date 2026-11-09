using System.Diagnostics;
using System.Text.Json;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using Windows.Storage.Pickers;
using RutaEstadistica.Aplicacion;
using RutaEstadistica.Contratos;
using RutaEstadistica.Dominio;
using RutaEstadistica.Infraestructura;
namespace RutaEstadistica.Escritorio;
public sealed partial class VentanaPrincipal : Window
{
    private readonly ModeloVista modelo = new();
    private readonly RepositorioProyectos repositorio;
    private CoordinadorAnalisis? coordinador;
    private ProyectoAnalisis? proyecto;
    private ConjuntoDatos? datos;
    private ConjuntoDatos? datosImportados;
    private string? rutaArchivo;
    private string? ultimoTrabajo;
    private CancellationTokenSource? cancelacion;
    private bool inicializando = true;
    private readonly string recursos = AppContext.BaseDirectory;
    private readonly string rutaTema = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RutaEstadistica", "tema.txt");
    private readonly IntermediarioMcp intermediario;
    private long revisionInterfaz;
    private bool esResultadoHistorico;
    public VentanaPrincipal()
    {
        InitializeComponent(); ((FrameworkElement)Content).DataContext = modelo;
        var tema = LeerTema();
        SelectorTema.SelectedItem = SelectorTema.Items.OfType<ComboBoxItem>()
            .First(opcion => Equals(opcion.Tag, tema.ToString()));
        AplicarTema(tema);
        AppWindow.Resize(new Windows.Graphics.SizeInt32(1280, 900));
        repositorio = new(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RutaEstadistica", "proyectos"));
        intermediario = new(repositorio, new MotorRLocal(recursos));
        _ = Task.Run(intermediario.EscucharAsync);
        ActualizarProyectos(); inicializando = false; Navegacion.SelectedItem = Navegacion.MenuItems[0];
        Closed += (_, _) => { cancelacion?.Cancel(); intermediario.Dispose(); };
    }
    private ElementTheme LeerTema()
    {
        try
        {
            return File.ReadAllText(rutaTema) switch
            {
                nameof(ElementTheme.Dark) => ElementTheme.Dark,
                nameof(ElementTheme.Default) => ElementTheme.Default,
                _ => ElementTheme.Light
            };
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return ElementTheme.Light;
        }
    }
    private void AplicarTema(ElementTheme tema)
    {
        Raiz.RequestedTheme = tema;
        AppWindow.TitleBar.PreferredTheme = tema switch
        {
            ElementTheme.Light => TitleBarTheme.Light,
            ElementTheme.Dark => TitleBarTheme.Dark,
            _ => TitleBarTheme.Legacy
        };
    }
    private void CambiarTema(object remitente, SelectionChangedEventArgs argumentos)
    {
        if (inicializando || SelectorTema.SelectedItem is not ComboBoxItem { Tag: string opcion })
            return;

        AplicarTema(Enum.Parse<ElementTheme>(opcion));
        try
        {
            File.WriteAllText(rutaTema, opcion);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            modelo.Estado = "El tema se aplicó, pero no se pudo guardar la preferencia.";
        }
    }
    private void ActualizarProyectos() => ListaProyectos.ItemsSource = repositorio.Listar();
    private async Task EjecutarSeguro(Func<Task> accion)
    {
        try { await accion(); }
        catch (Exception error) { modelo.Estado = error is ErrorAplicacion conocido ? Mensaje(conocido.Codigo) : error is OperationCanceledException ? "TRABAJO_CANCELADO: operación cancelada." : "OPERACION_FALLIDA: revisa permisos, formato y disponibilidad del motor. No se modifican tus datos originales."; }
    }
    private static string Mensaje(string codigo) => codigo + ": " + (codigo switch
    {
        "MOTOR_NO_DISPONIBLE" => "Falta el motor R distribuido. Ejecuta preparar_desarrollo.ps1 y vuelve a compilar.",
        "DATOS_NUMERO_INVALIDO" => "Esta columna contiene texto donde se esperaba un número; revisa el separador decimal.",
        "DATOS_FALTANTES_SIN_CONFIRMAR" => "Revisa los faltantes y confirma su exclusión si corresponde.",
        "DATOS_CONSTANTES" => "La variación es insuficiente para este método.",
        "TRABAJO_CANCELADO" => "Cálculo cancelado; puedes intentarlo otra vez.",
        "TRABAJO_TIEMPO_AGOTADO" => "El cálculo superó 60 segundos. Revisa el tamaño y método.",
        "DOCKER_NO_DISPONIBLE" => "El motor Docker no responde; selecciona Local o revisa la configuración avanzada.",
        _ => "Revisa las opciones, el diseño y los permisos. Consulta el catálogo de errores con este código."
    });
    private void ExigirProyecto() { if (proyecto is null) throw new ErrorAplicacion("PROYECTO_NO_ABIERTO"); }
    private void Mostrar(int paso) => Navegacion.SelectedItem = Navegacion.MenuItems[paso];
    private void CambiarPaso(NavigationView remitente, NavigationViewSelectionChangedEventArgs argumentos)
    {
        if (inicializando) return;
        if (argumentos.SelectedItem is not NavigationViewItem elemento || !int.TryParse(elemento.Tag?.ToString(), out var paso)) return;
        if (paso == 4 && esResultadoHistorico) Invalidar();
        var paneles = new[] { PanelInicio, PanelPregunta, PanelDatos, PanelPreparacion, PanelRuta, PanelResultados, PanelInterpretacion, PanelEvidencia, PanelConfiguracion };
        for (var indice = 0; indice < paneles.Length; indice++) paneles[indice].Visibility = indice == paso ? Visibility.Visible : Visibility.Collapsed;
    }
    private void CrearProyecto(object remitente, RoutedEventArgs argumentos) => _ = EjecutarSeguro(() => { proyecto = repositorio.Crear(NombreProyecto.Text); datos = null; datosImportados = null; LimpiarResultado(); ActualizarProyectos(); CargarProyecto(); Mostrar(1); return Task.CompletedTask; });
    private void CargarProyecto()
    {
        Invalidar();
        inicializando = true; Pregunta.Text = proyecto!.Pregunta; Contexto.Text = proyecto.Contexto;
        NombreProyecto.Text = proyecto.Nombre; datos = repositorio.LeerDatos(proyecto.Id); datosImportados = datos;
        LimpiarResultado(); ActualizarDatos(); inicializando = false;
        _ = EjecutarSeguro(ActualizarHistorialAsync);
        modelo.Estado = $"Proyecto «{proyecto.Nombre}» abierto y guardado.";
    }
    private void AbrirProyecto(object remitente, SelectionChangedEventArgs argumentos) { if (ListaProyectos.SelectedItem is ProyectoAnalisis elegido) { proyecto = elegido; CargarProyecto(); } }
    private void GuardarContexto(object remitente, TextChangedEventArgs argumentos)
    {
        if (inicializando || proyecto is null) return;
        _ = EjecutarSeguro(() => { proyecto = proyecto with { Pregunta = Pregunta.Text, Contexto = Contexto.Text }; repositorio.Guardar(proyecto); modelo.Estado = "Cambios guardados."; return Task.CompletedTask; });
    }
    private void RenombrarProyecto(object remitente, RoutedEventArgs argumentos) => _ = EjecutarSeguro(() => { ExigirProyecto(); if (string.IsNullOrWhiteSpace(NombreProyecto.Text)) throw new ErrorAplicacion("PROYECTO_NOMBRE_INVALIDO"); proyecto = proyecto! with { Nombre = NombreProyecto.Text }; repositorio.Guardar(proyecto); ActualizarProyectos(); return Task.CompletedTask; });
    private void DuplicarProyecto(object remitente, RoutedEventArgs argumentos) => _ = EjecutarSeguro(() => { ExigirProyecto(); proyecto = repositorio.Duplicar(proyecto!.Id); ActualizarProyectos(); CargarProyecto(); return Task.CompletedTask; });
    private async void EliminarProyecto(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        ExigirProyecto(); var dialogo = new ContentDialog { XamlRoot = Content.XamlRoot, RequestedTheme = Raiz.RequestedTheme, Title = "¿Eliminar este proyecto?", Content = "Se creará un archivo recuperable en respaldos. Los informes ya exportados se conservan.", PrimaryButtonText = "Eliminar con respaldo", CloseButtonText = "Conservar", DefaultButton = ContentDialogButton.Close };
        if (await dialogo.ShowAsync() != ContentDialogResult.Primary) return;
        repositorio.EliminarConRespaldo(proyecto!.Id); proyecto = null; datos = null; datosImportados = null; LimpiarResultado(); ActualizarProyectos(); modelo.Estado = "Proyecto eliminado con respaldo recuperable.";
    });
    private FileOpenPicker Selector(params string[] extensiones)
    {
        var selector = new FileOpenPicker(); WinRT.Interop.InitializeWithWindow.Initialize(selector, WinRT.Interop.WindowNative.GetWindowHandle(this));
        foreach (var extension in extensiones) selector.FileTypeFilter.Add(extension); return selector;
    }
    private async Task SeleccionarRuta(string ruta)
    {
        rutaArchivo = ruta; ArchivoElegido.Text = Path.GetFileName(ruta); Hojas.ItemsSource = null;
        if (Path.GetExtension(ruta).Equals(".xlsx", StringComparison.OrdinalIgnoreCase))
        {
            if (new FileInfo(ruta).Length > ImportadorDatos.LimiteBytes) throw new ErrorAplicacion("DATOS_LIMITE_EXCEDIDO");
            Hojas.ItemsSource = await Task.Run(() => ImportadorDatos.ListarHojas(File.ReadAllBytes(ruta)));
        }
        Mostrar(2); modelo.Estado = "Confirma separadores, cabecera, faltantes y hoja antes de importar.";
    }
    private async void SeleccionarArchivo(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () => { ExigirProyecto(); var archivo = await Selector(".csv", ".tsv", ".xlsx").PickSingleFileAsync(); if (archivo != null) await SeleccionarRuta(archivo.Path); });
    private void ArrastrarArchivo(object remitente, DragEventArgs argumentos) => argumentos.AcceptedOperation = Windows.ApplicationModel.DataTransfer.DataPackageOperation.Copy;
    private async void SoltarArchivo(object remitente, DragEventArgs argumentos) => await EjecutarSeguro(async () => { ExigirProyecto(); var archivos = await argumentos.DataView.GetStorageItemsAsync(); if (archivos.Count == 1 && archivos[0] is Windows.Storage.StorageFile archivo) await SeleccionarRuta(archivo.Path); });
    private OpcionesImportacion Opciones() => new(new[] { ';', ',', '\t' }[Separador.SelectedIndex], Decimal.SelectedIndex == 0 ? ',' : '.', new[] { '\0', '.', ',' }[Miles.SelectedIndex], TieneCabecera.IsChecked == true, MarcadorFaltante.Text, FormatoFecha.Text);
    private async void ImportarDatos(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        ExigirProyecto(); if (rutaArchivo is null) throw new ErrorAplicacion("DATOS_ARCHIVO_NO_ELEGIDO");
        Invalidar(); cancelacion = new(); modelo.Estado = "Importando y validando datos…";
        var opciones = Opciones(); var hoja = Hojas.SelectedItem as string;
        var proyectoImportacion = proyecto!.Id; var cancelacionImportacion = cancelacion.Token; var rutaImportacion = rutaArchivo;
        var nuevosDatos = await Task.Run(() => ImportadorDatos.ImportarAsync(rutaImportacion, opciones, hoja, cancelacionImportacion));
        if (proyecto?.Id != proyectoImportacion || cancelacionImportacion.IsCancellationRequested) return;
        // No capturar campos mutables de la ventana: el usuario puede abrir otro proyecto durante la escritura.
        await Task.Run(() => repositorio.GuardarDatos(proyectoImportacion, nuevosDatos, File.ReadAllBytes(rutaImportacion)));
        if (proyecto?.Id != proyectoImportacion || cancelacionImportacion.IsCancellationRequested) return;
        datos = nuevosDatos; datosImportados = datos;
        LimpiarResultado(); ActualizarDatos(); modelo.Estado = "Vista previa lista. Confirma los roles antes de calcular.";
    });
    private void ActualizarDatos()
    {
        Roles.Children.Clear(); ColumnaPrimera.ItemsSource = datos?.Columnas; ColumnaSegunda.ItemsSource = datos?.Columnas;
        if (datos is null) { VistaPrevia.Text = ""; Calidad.Text = "Importa datos o prueba el ejemplo."; return; }
        VistaPrevia.Text = string.Join(" | ", datos.Columnas.Select(columna => columna.Etiqueta)) + "\n" + string.Join("\n", datos.Filas.Take(200).Select(fila => string.Join(" | ", fila)));
        var faltantes = datos.Filas.Sum(fila => fila.Count(valor => valor == ""));
        var duplicadas = datos.Filas.Count - datos.Filas.Select(fila => JsonSerializer.Serialize(fila)).Distinct().Count();
        var constantes = datos.Columnas.Where((columna, indice) => datos.Filas.Select(fila => fila[indice]).Distinct().Count() <= 1).Select(columna => columna.Etiqueta);
        Calidad.Text = $"{datos.Filas.Count} filas y {datos.Columnas.Count} columnas. {faltantes} celdas faltantes. {duplicadas} filas duplicadas candidatas. Constantes: {string.Join(", ", constantes)}. No se elimina ningún registro automáticamente.";
        foreach (var columna in datos.Columnas)
        {
            var selector = new ComboBox { Header = columna.Etiqueta + " (" + columna.Id + ")", Tag = columna.Id, ItemsSource = new[] { "texto", "numerica", "categorica", "ordinal", "identificador", "fecha" }, SelectedItem = columna.Rol, HorizontalAlignment = HorizontalAlignment.Stretch };
            Roles.Children.Add(selector);
        }
    }
    private async void ConfirmarRoles(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        ExigirProyecto(); if (datosImportados is null) throw new ErrorAplicacion("DATOS_INSUFICIENTES");
        var proyectoPreparacion = proyecto!.Id; var datosOrigen = datosImportados;
        Invalidar(); var revisionPreparacion = Interlocked.Read(ref revisionInterfaz);
        var roles = Roles.Children.OfType<ComboBox>().ToDictionary(selector => (string)selector.Tag, selector => (string)selector.SelectedItem);
        var opciones = Opciones(); var preparados = await Task.Run(() => ImportadorDatos.ConfirmarRoles(datosOrigen, roles, opciones));
        if (proyecto?.Id != proyectoPreparacion || revisionPreparacion != Interlocked.Read(ref revisionInterfaz)) return;
        await Task.Run(() =>
        {
            var directorio = repositorio.Directorio(proyectoPreparacion);
            RepositorioProyectos.EscribirAtomico(Path.Combine(directorio, "preparacion_" + Guid.NewGuid().ToString("N") + ".json"), JsonSerializer.Serialize(preparados, Serializacion.Opciones));
            repositorio.GuardarDatos(proyectoPreparacion, preparados, File.ReadAllBytes(Directory.GetFiles(directorio, "original_*").First(ruta => Path.GetFileName(ruta).Contains(preparados.HashOriginal))));
        });
        if (proyecto?.Id != proyectoPreparacion || revisionPreparacion != Interlocked.Read(ref revisionInterfaz)) return;
        datos = preparados;
        LimpiarResultado(); ActualizarDatos(); Mostrar(4); modelo.Estado = "Roles confirmados. Selecciona método, variables y condiciones.";
    });
    private void DeshacerPreparacion(object remitente, RoutedEventArgs argumentos) { if (datosImportados != null) { datos = datosImportados; LimpiarResultado(); ActualizarDatos(); modelo.Estado = "Preparación revertida en memoria. Confirma de nuevo para guardar."; } }
    private void ModificarParametros(object remitente, SelectionChangedEventArgs argumentos) { if (!inicializando) { Invalidar(); if (Condiciones != null) Condiciones.Text = Validacion.ProponerRuta(TipoAnalisis.SelectedIndex switch { 1 => "cuestionario", 2 or 3 => "comparar", 4 or 5 => "asociar", 6 => "modelar", _ => "resumir" }, TipoAnalisis.SelectedIndex == 3 ? "pareado" : "independiente"); } }
    private void CambiarConfianza(NumberBox remitente, NumberBoxValueChangedEventArgs argumentos) { if (!inicializando) Invalidar(); }
    private void InvalidarResultado(object remitente, RoutedEventArgs argumentos) { if (!inicializando) Invalidar(); }
    private void Invalidar() { Interlocked.Increment(ref revisionInterfaz); coordinador?.Invalidar(); cancelacion?.Cancel(); LimpiarResultado(); }
    private void LimpiarResultado()
    {
        ultimoTrabajo = null; esResultadoHistorico = false;
        if (Cifras != null) Cifras.Text = "";
        if (Figura != null) Figura.Source = null;
        if (TablaCifras != null) TablaCifras.ItemsSource = null;
        if (TablaFrecuencias != null) TablaFrecuencias.ItemsSource = null;
        if (PanelFrecuencias != null) PanelFrecuencias.Visibility = Visibility.Collapsed;
        if (ResumenResultado != null) ResumenResultado.Text = "";
        if (OrigenResultado != null) OrigenResultado.Text = "Calcula o abre un resultado guardado.";
        if (OpcionesResultado != null) OpcionesResultado.Text = "";
        modelo.Interpretacion = "Calcula con los parámetros actuales para obtener una interpretación.";
    }
    private async Task ActualizarHistorialAsync()
    {
        if (proyecto is null) return;
        var proyectoId = proyecto.Id;
        var entradas = await Task.Run(() => repositorio.ListarHistorial(proyectoId));
        if (proyecto?.Id != proyectoId) return;
        SelectorHistorial.ItemsSource = entradas;
        Historial.Text = $"{entradas.Count} cálculos completados con evidencia verificable. No se incluyen trabajos interrumpidos o archivos dañados.";
    }
    private void MostrarResultado(ResultadoAnalisis resultado, SolicitudAnalisis solicitud, string directorio, bool historico)
    {
        ultimoTrabajo = directorio; esResultadoHistorico = historico;
        OrigenResultado.Text = historico ? "Cálculo histórico · consulta de solo lectura" : "Cálculo actual";
        ResumenResultado.Text = PresentacionResultados.Recuentos(resultado);
        OpcionesResultado.Text = $"Solicitud: {solicitud.SolicitudId}. Variables: {string.Join(", ", solicitud.Columnas)}. Confianza: {solicitud.Confianza:P0}. Inferencia confirmada: {(solicitud.InferenciaConfirmada ? "sí" : "no")}. Política de faltantes: {solicitud.PoliticaFaltantes}. Revisión: {solicitud.HashDatos}.";
        TablaCifras.ItemsSource = PresentacionResultados.Cifras(resultado);
        var frecuencias = PresentacionResultados.Frecuencias(resultado);
        TablaFrecuencias.ItemsSource = frecuencias; PanelFrecuencias.Visibility = frecuencias.Count > 0 ? Visibility.Visible : Visibility.Collapsed;
        Cifras.Text = resultado.Contenido.ToString();
        modelo.Interpretacion = resultado.Contenido.GetProperty("interpretacion").GetString()!;
        Figura.Source = new BitmapImage(new Uri(Path.Combine(directorio, "figura.png")));
        Mostrar(5);
    }
    private async void VerCalculoGuardado(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        ExigirProyecto(); if (SelectorHistorial.SelectedItem is not EntradaHistorial entrada) throw new ErrorAplicacion("TRABAJO_NO_ENCONTRADO");
        var proyectoId = proyecto!.Id; Invalidar(); var revisionActual = Interlocked.Read(ref revisionInterfaz);
        var lectura = await Task.Run(() => repositorio.LeerTrabajo(proyectoId, entrada.Id));
        if (proyecto?.Id != proyectoId || revisionActual != Interlocked.Read(ref revisionInterfaz)) return;
        MostrarResultado(lectura.Resultado, lectura.Solicitud, lectura.Directorio, true);
        modelo.Estado = "Cálculo guardado abierto con su solicitud y datos originales. Puedes volver a exportarlo.";
    });
    private async void Calcular(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        ExigirProyecto(); if (datos is null || ColumnaPrimera.SelectedItem is not ColumnaDatos primera) throw new ErrorAplicacion("DATOS_COLUMNA_INVALIDA");
        var tipo = Validacion.Tipos[TipoAnalisis.SelectedIndex];
        var columnas = tipo is "descriptivo" or "cuestionario" ? new[] { primera.Id } : ColumnaSegunda.SelectedItem is ColumnaDatos segunda ? new[] { primera.Id, segunda.Id } : [];
        var seleccionadas = datos.Columnas.Where(columna => columnas.Contains(columna.Id)).ToArray();
        if (tipo != "cuestionario" && primera.Rol != "numerica" || tipo is "pearson" or "spearman" or "lineal" or "pareado" && seleccionadas.Any(columna => columna.Rol != "numerica")) throw new ErrorAplicacion("DATOS_ROL_INVALIDO");
        cancelacion?.Cancel(); cancelacion = new(); LimpiarResultado(); var revisionActual = Interlocked.Increment(ref revisionInterfaz);
        var csv = ImportadorDatos.CsvNormalizado(datos); var hash = ImportadorDatos.Hash(System.Text.Encoding.UTF8.GetBytes(csv));
        var solicitud = new SolicitudAnalisis(1, Guid.NewGuid().ToString("N"), proyecto!.Id, hash, hash, tipo, columnas, Confianza.Value, ExcluirFaltantes.IsChecked == true ? "excluir_confirmados" : "rechazar", ConfirmarInferencia.IsChecked == true, ConfirmarPares.IsChecked == true);
        var directorio = Path.Combine(proyecto.Directorio, "trabajo_" + solicitud.SolicitudId);
        IMotorAnalisis motor = Motor.SelectedIndex == 0 ? new MotorRLocal(recursos) : await MotorDocker.CrearAsync();
        coordinador ??= new(motor); coordinador = new(motor);
        modelo.Estado = "Calculando… puedes cancelar. Solicitud " + solicitud.SolicitudId;
        var resultado = await coordinador.EjecutarAsync(solicitud, datos, directorio, cancelacion.Token);
        if (resultado is null || revisionActual != Interlocked.Read(ref revisionInterfaz) || proyecto?.Id != solicitud.ProyectoId) return;
        MostrarResultado(resultado, solicitud, directorio, false);
        await ActualizarHistorialAsync();
        modelo.Estado = "Cálculo completado y guardado. Revisa resultados e interpretación.";
    });
    private void CancelarCalculo(object remitente, RoutedEventArgs argumentos) { cancelacion?.Cancel(); modelo.Estado = "Cancelación solicitada…"; }
    private async void ProbarEjemplo(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        proyecto = repositorio.Crear("Ejemplo sintético · mediciones");
        var contenido = System.Text.Encoding.UTF8.GetBytes("valor;grupo;predictor\n10;A;1\n12;A;2\n14;A;3\n17;B;4\n19;B;5\n21;B;6\n");
        var ruta = Path.Combine(proyecto.Directorio, "ejemplo.csv"); await File.WriteAllBytesAsync(ruta, contenido);
        datosImportados = await ImportadorDatos.ImportarAsync(ruta, new());
        datos = ImportadorDatos.ConfirmarRoles(datosImportados, new Dictionary<string, string> { ["c001"] = "numerica", ["c002"] = "categorica", ["c003"] = "numerica" }, new());
        repositorio.GuardarDatos(proyecto.Id, datos, contenido); proyecto = proyecto with { Pregunta = "¿Cómo se distribuyen estas seis mediciones?" }; repositorio.Guardar(proyecto);
        ActualizarProyectos(); CargarProyecto(); ColumnaPrimera.SelectedIndex = 0; ColumnaSegunda.SelectedIndex = 1; Mostrar(4); modelo.Estado = "Ejemplo listo. Pulsa Calcular para obtener resultados reales con R.";
    });
    private async void ExportarInforme(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        if (ultimoTrabajo is null) throw new ErrorAplicacion("RESULTADO_NO_DISPONIBLE");
        var selector = new FolderPicker(); selector.FileTypeFilter.Add("*"); WinRT.Interop.InitializeWithWindow.Initialize(selector, WinRT.Interop.WindowNative.GetWindowHandle(this));
        var carpeta = await selector.PickSingleFolderAsync(); if (carpeta is null) return;
        var origen = ultimoTrabajo; var destino = Path.Combine(carpeta.Path, "RutaEstadistica_" + DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()); var seguro = CsvSeguro.IsChecked == true;
        await Task.Run(() => Exportador.Exportar(origen, destino, seguro)); modelo.Estado = "Informe, tablas, figura y reproducción exportados.";
    });
    private async void ExportarProyecto(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        ExigirProyecto(); var selector = new FileSavePicker { SuggestedFileName = "proyecto" }; selector.FileTypeChoices.Add("Proyecto Ruta Estadística", new List<string> { ".rutaestadistica" }); WinRT.Interop.InitializeWithWindow.Initialize(selector, WinRT.Interop.WindowNative.GetWindowHandle(this));
        var archivo = await selector.PickSaveFileAsync(); if (archivo is null) return;
        // El selector ya obtuvo la elección explícita de reemplazo del usuario.
        if (File.Exists(archivo.Path)) File.Delete(archivo.Path); await Task.Run(() => repositorio.ExportarProyecto(proyecto!.Id, archivo.Path)); modelo.Estado = "Proyecto portátil exportado.";
    });
    private async void ImportarProyecto(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () => { var archivo = await Selector(".rutaestadistica").PickSingleFileAsync(); if (archivo is null) return; proyecto = await Task.Run(() => repositorio.ImportarProyecto(archivo.Path)); ActualizarProyectos(); CargarProyecto(); });
    private async void ComprobarDocker(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () => { await MotorDocker.CrearAsync(); modelo.Estado = "Motor Docker disponible y compatible con contrato 1."; });
    private void AbrirCarpeta(object remitente, RoutedEventArgs argumentos) => Process.Start(new ProcessStartInfo(repositorio.Raiz) { UseShellExecute = true });
    private async void AutorizarMcp(object remitente, RoutedEventArgs argumentos) => await EjecutarSeguro(async () =>
    {
        ExigirProyecto();
        var dialogo = new ContentDialog { XamlRoot = Content.XamlRoot, RequestedTheme = Raiz.RequestedTheme, Title = "Autorizar integración para este proyecto", Content = "El cliente conectado podrá recibir nombres de columnas, recuentos y resultados autorizados. Si usa un modelo en la nube, esos contenidos pueden salir del equipo. Autoriza solo un cliente de confianza. La concesión caduca al cerrar o revocar.", PrimaryButtonText = "Autorizar este proyecto", CloseButtonText = "Cancelar", DefaultButton = ContentDialogButton.Close };
        if (await dialogo.ShowAsync() != ContentDialogResult.Primary) return;
        intermediario.Conceder(new(proyecto!.Id, true, PermitirCalculos.IsChecked == true, false, PermitirExportaciones.IsChecked == true)); intermediario.Activar(); EstadoIntegracion.Text = "Integración MCP ACTIVA · proyecto: " + proyecto.Nombre; modelo.Estado = "Integración activa. Puedes revocar todos los permisos en Configuración.";
    });
    private void RevocarMcp(object remitente, RoutedEventArgs argumentos) { intermediario.Revocar(); EstadoIntegracion.Text = "Integración MCP deshabilitada"; modelo.Estado = "Todos los permisos MCP revocados y cálculos pendientes cancelados."; }
}
