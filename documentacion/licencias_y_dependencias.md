# Licencias y dependencias

Se propone GPL-3.0-or-later para las contribuciones nuevas de Ruta Estadística, conservando atribución del README original. Esta elección busca compatibilidad con la distribución de R; aún requiere revisión de la combinación concreta y condiciones del Store antes de publicar. El límite de proceso no se trata como conclusión jurídica.

| Componente | Licencia/documentos que deben acompañar |
|---|---|
| R 4.5.2 y paquetes recomendados | Conservar `COPYING`, `COPYRIGHT`, `share/licenses` y licencias por paquete. R permite términos GPL; inventario granular de nativos pendiente. |
| jsonlite 2.0.0 | MIT + archivo LICENSE del paquete; conservar aviso y fuente CRAN exacta. |
| rutaanalitica 0.1.0 | GPL-3 declarada, fuente completa en repositorio. |
| .NET / Windows App SDK | Avisos y licencias de sus paquetes/runtime; revisar redistribución real del conjunto publicado. |
| SQLitePCLRaw / SQLite | Revisar licencias de cada paquete fijado en lockfiles; no confundir wrappers con licencia del motor. |
| MCP SDK / Hosting | Licencias del paquete oficial y transitivas; inventario automatizado de nombres/versiones no equivale a revisión de obligaciones. |
| Iconos | Geometría propia generada en guion, sin recursos de terceros. Fuentes de UI provistas por sistema. |

El [SBOM de desarrollo](../distribucion/licencias/sbom.cdx.json) enumera dependencias resueltas desde lockfiles y R. No es aún un SBOM completo certificado del MSIX y de todas las capas Linux. Mantenga los avisos incluidos en los binarios originales; prepare fuentes de R y paquetes correspondientes a la versión efectivamente distribuida y registre el mecanismo de cumplimiento antes de entrega pública.

Las advertencias iniciales NuGet sobre SQLite motivaron actualización. Un informe de vulnerabilidades actual debe guardarse con fecha; no se asume ausencia por resolver correctamente. Consulte [versiones](versiones_y_compatibilidad.md) y [publicación](lista_publicacion_tienda.md).
