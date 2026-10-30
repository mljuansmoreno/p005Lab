using Microsoft.UI.Xaml;
namespace RutaEstadistica.Escritorio;
public partial class Aplicacion : Application
{
    private Window? ventana;
    public Aplicacion() => InitializeComponent();
    protected override void OnLaunched(LaunchActivatedEventArgs argumentos)
    {
        try { ventana = new VentanaPrincipal(); ventana.Activate(); }
        catch (Exception error)
        {
            var directorio = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RutaEstadistica");
            System.IO.Directory.CreateDirectory(directorio);
            // Solo el diagnóstico optativo de desarrollo conserva la traza; no contiene datos importados.
            if (Environment.GetEnvironmentVariable("RUTA_ESTADISTICA_DIAGNOSTICO_DESARROLLO") == "1")
                System.IO.File.WriteAllText(System.IO.Path.Combine(directorio, "inicio_desarrollo.txt"), error.ToString());
            ventana = new Window { Title = "Ruta Estadística · diagnóstico", Content = new Microsoft.UI.Xaml.Controls.TextBlock { Text = "INICIO_FALLIDO: no se pudo abrir el proyecto o la interfaz. Revisa los recursos y permisos de instalación.", TextWrapping = TextWrapping.Wrap, Margin = new Thickness(32) } };
            ventana.Activate();
        }
    }
}
