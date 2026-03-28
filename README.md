# PYME-Ledger - ERP Contable 

Sistema de contabilidad profesional para micro y pequeñas empresas (PYMES) basado en Beancount y el Plan Contable General Empresarial (PCGE) peruano.

## Diferenciales para PYMES

Este modelo incluye el **Ciclo de Operaciones**:
1. **Compras (60):** Registro de mercaderías con IGV (40).
2. **Existencias (20):** Control de inventario en almacén.
3. **Ventas (70):** Generación de ingresos operativos.
4. **Costo de Ventas (69):** Cálculo automático del margen bruto.

## Estándar de Cuentas PYME-PCGE

### 1) Activos Realizables e Inmovilizados
- **Mercaderías (20):** `Assets:PE:20:2011:Mercaderias:Almacen:ID`
- **Equipos (33):** `Assets:PE:33:3331:Maquinaria:Equipo:UsoInterno`

### 2) Tributos y Deudas
- **Tributos por Pagar (40):** `Liabilities:PE:40:4011:IGV:Pendiente`
- **Proveedores (42):** `Liabilities:PE:42:4212:Proveedores:RazonSocial:Factura`

### 3) Resultados Operativos
- **Ventas (70):** `Income:PE:70:7011:Ventas:Canal:Producto`
- **Costo de Ventas (69):** `Expenses:PE:69:6911:CostoVentas:Mercaderias`

## Flujo de Trabajo (Micro-SaaS)

1. **Venta al Contado:**
   - Cargo a Caja (10)
   - Abono a Ventas (70) e IGV (40)
2. **Reconocimiento de Costo:**
   - Cargo a Costo de Ventas (69)
   - Abono a Mercaderías (20)

## Estructura de Datos
- `data/core/accounts.bean`: Catálogo de cuentas PYME.
- `data/core/commodities.bean`: Monedas y activos.
- `data/ledger/2026/`: Libros de ventas, compras y diario.
