# ⚙️ Ledger API (Backend Engine)

Este módulo es el corazón lógico del sistema. Implementa una **Clean Architecture** para desacoplar la lógica contable de la interfaz web.

## 🧱 Capas de la Aplicación

### 1. Capa de Infraestructura (`core/`)
- **beancount_wrapper.py:** Encapsula la librería Beancount. Proporciona métodos para ejecutar queries BQL (Beancount Query Language) y normalizar tipos de datos (Amount, Inventory -> Float).

### 2. Capa de Aplicación (`services/`)
- **accounting_service.py:** Orquesta el cálculo de utilidades, patrimonio y consolidación de activos. No sabe que existe la web, solo sabe de contabilidad.
- **inventory_service.py:** Gestiona el catálogo de productos, el cálculo de stock real y la generación de asientos contables de venta.

### 3. Capa de Interfaz (`api/` - dentro de views.py)
- **views.py:** Controladores de Django REST Framework. Reciben el JSON del cliente, invocan al servicio correspondiente y devuelven la respuesta estandarizada.

## 🔄 Flujo de Datos
1. Una petición `POST /api/pos/sale/` llega a `views.py`.
2. La vista invoca a `InventoryService.record_sale()`.
3. El servicio utiliza `BeancountWrapper` para validar datos y finalmente escribe el asiento en el archivo físico.
4. El sistema responde un `201 Created` al frontend.
