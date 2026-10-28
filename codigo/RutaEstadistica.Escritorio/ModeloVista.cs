using System.ComponentModel;
using System.Runtime.CompilerServices;
namespace RutaEstadistica.Escritorio;
public sealed class ModeloVista : INotifyPropertyChanged
{
    private string estado = "Crea un proyecto o prueba el ejemplo sin conexión.";
    public string Estado { get => estado; set { estado = value; Notificar(); } }
    private string interpretacion = "El resultado aparecerá después de confirmar los datos y calcular.";
    public string Interpretacion { get => interpretacion; set { interpretacion = value; Notificar(); } }
    public event PropertyChangedEventHandler? PropertyChanged;
    private void Notificar([CallerMemberName] string? nombre = null) => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nombre));
}
