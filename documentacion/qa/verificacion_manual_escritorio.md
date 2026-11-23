# Verificación manual de escritorio

## Teclado

Estado de la ejecución manual: pendiente. Preparar una cuenta de prueba de Windows y un proyecto sintético. Registrar SHA, compilación de Windows, versión de la aplicación y distribución de teclado. Iniciar la aplicación con teclado y dejar el ratón sin utilizar.

1. Recorrer la navegación con Tab, Mayús+Tab y las flechas. Anotar en orden los controles enfocados desde «Inicio y proyectos» hasta «Configuración y ayuda». Aprobar si cada cambio de foco se ve y se puede volver al control anterior.
2. Activar «Probar ejemplo» con Enter o Espacio. Pasar por pregunta, datos, preparación y ruta. Elegir un análisis válido y alcanzar «Calcular». Registrar el texto del resultado y el control que recibe el foco.
3. Recorrer resultados, interpretación y exportación. Abrir un diálogo y cerrarlo con Escape. Verificar que el foco regresa a un control identificable, y que el contenido largo se puede recorrer sin quedar atrapado.

Registrar por paso la tecla, el control anterior, el siguiente y la evidencia. Si un paso requiere ratón o el foco se pierde, guardar el primer paso reproducible y clasificar el recorrido como fallido.

## Contraste y escala

Estado de la ejecución manual: pendiente. En una cuenta de prueba, anotar el tema, resolución y escala iniciales. Abrir el mismo ejemplo sintético. Repetir el recorrido con temas claro, oscuro y de contraste del sistema a 100 %, 150 % y 200 %. Registrar por separado las combinaciones disponibles.

En cada combinación, enfocar «Apariencia», un botón de acción y una celda de resultados. Anotar si se distinguen foco, selección y estado deshabilitado. Abrir «5 · Resultados», recorrer hasta el final con teclado y comprobar que todas las etiquetas, cifras y acciones quedan accesibles mediante desplazamiento. Una etiqueta truncada sin acceso al texto completo, o una acción inalcanzable, hace fallar esa combinación.

Guardar una captura de la misma vista por combinación, con la resolución y el porcentaje reales. Restaurar las preferencias originales de la cuenta al terminar. La comprobación automática de claves de recursos está en [el auditor XAML](../../guiones/ci/verificar_recursos_winui.py).
