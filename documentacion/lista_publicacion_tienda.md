# Lista de publicación

Consultar antes de enviar las [políticas oficiales](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies) y [requisitos MSIX](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/app-package-requirements). Consulta inicial 27/10/2026: políticas 7.20. Revalidar en fecha de envío; el repositorio no prueba cumplimiento de todas las secciones.

| Área | Evidencia necesaria | Estado de liberación |
|---|---|---|
| Identidad/editor | Asociación real Partner Center | BLOQUEADO: dato externo no suministrado |
| Funcionamiento offline | Cuenta limpia sin R global completa ejemplo | PENDIENTE |
| Paquete | MakeAppx, instalación, actualización y alias | Ver [estado](estado_entrega.md); validación parcial no basta |
| Seguridad y capacidades | Revisión runFullTrust, parsers y API | PENDIENTE revisión independiente |
| Privacidad | Política publicada y URL real de soporte | BLOQUEADO: datos del propietario |
| Accesibilidad/localización | Teclado, lector, contraste y escalado | PENDIENTE |
| Licencias | Inventario y fuentes redistribuibles completos | PENDIENTE revisión de combinación GPL y dependencias |
| Docker | Imagen inmutable y paridad real | BLOQUEADO: no se ha ejecutado Docker |
| MCP | Cliente versionado y alias limpio, permisos/revocación | PENDIENTE aceptación completa |
| Certificación | Informe WACK y correcciones | PENDIENTE |
| Materiales | Capturas reales, descripción sin sobreafirmar | Texto de revisión disponible en distribución; capturas sujetas a ejecución |

No publique esta versión como completa mientras haya requisitos funcionales pendientes. Los campos de soporte/editor no se inventan. La preparación no autoriza envío, compra, cuentas ni uso de certificados. Véase [empaquetado](empaquetado_y_publicacion.md).
