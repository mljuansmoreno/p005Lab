# Revisión de riesgos de la API

Referencia de clasificación [OWASP API Security Top 10, edición 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/). El servicio se ejecuta en loopback o en la red interna de Compose. El navegador utiliza el servicio web como intermediario.

| Riesgo OWASP | Evidencia de este proyecto | Límite de la comprobación |
|---|---|---|
| API1, acceso a objetos | QA-181 a QA-183 contrastan proyecto, trabajo y resultado en HTTP. | El identificador de proyecto aporta aislamiento lógico. La instalación comparte una credencial. |
| API2, autenticación | QA-178 a QA-180 comprueban esquema, valor vacío y respuesta pública uniforme. | La rotación de una credencial en una instalación operativa requiere una prueba de despliegue propia. |
| API3, propiedades de objetos | QA-185 exige contenido de datos explícito. QA-193 comprueba la respuesta pública de error. | Estos casos cubren campos concretos del contrato. |
| API4, consumo de recursos | QA-186 a QA-190 comprueban límites JSON, HTTP, filas y almacén. | Son límites de admisión. La capacidad sostenida depende del equipo y del tamaño de las entradas. |
| API5, autorización de funciones | QA-182 verifica la cancelación por proyecto. | No hay roles administrativos diferenciados en el modelo probado. |
| API6, flujos de negocio sensibles | QA-123 y QA-124 ejercitan la cola y el vencimiento del trabajo. | Queda abierta la evaluación de uso sostenido por varios clientes autorizados. |
| API7, solicitudes del servidor a destinos no previstos | QA-191 y QA-192 prueban el destino del motor antes de crear el cliente. | La revisión considera las rutas de configuración del cliente web. |
| API8, configuración | QA-167 a QA-170 comprueban identidad del proceso, capacidades y secretos de Compose. QA-199 comprueba los workflows. | Los equipos de despliegue administran su propio host y daemon de Docker. |
| API9, inventario | QA-125 comprueba el estado y código del endpoint retirado. | La prueba cubre las rutas distribuidas en esta revisión. |
| API10, consumo de otras API | QA-164 ejercita la incompatibilidad de contrato entre servicios. | La paridad del contrato depende de las versiones de las dos imágenes desplegadas. |

Los casos de HTTP se encuentran en la [suite del servidor](../../pruebas/api/test_trabajos_http.py). Los límites del cliente se prueban en la [suite web](../../pruebas/test_aplicacion_web.py) y los del despliegue en la [suite Compose](../../pruebas/contenedores/test_despliegue.py).
