using Microsoft.UI.Xaml;
namespace RutaEstadistica.Escritorio;
public partial class App : Application
{
    private Window? ventana;
    public App() => InitializeComponent();
    protected override void OnLaunched(LaunchActivatedEventArgs argumentos) { ventana = new VentanaPrincipal(); ventana.Activate(); }
}
