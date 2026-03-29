# 📊 Capa de Datos (Beancount)

Esta carpeta contiene la persistencia del sistema. En lugar de una base de datos SQL, utilizamos archivos de texto plano que siguen la sintaxis de **Beancount**.

## 📁 Organización
- **main.beancount:** El archivo maestro. Incluye todas las definiciones y archivos anuales. Contiene también las configuraciones de visualización para Fava.
- **core/accounts.bean:** Plan Contable General Empresarial (PCGE) adaptado para Perú. Define las cuentas de Activo, Pasivo, Patrimonio, Ingresos y Gastos.
- **core/commodities.bean:** Catálogo de productos (SKUs) y monedas (PEN, USD).
- **ledger/YYYY/transactions.bean:** Registro cronológico de todas las operaciones (Ventas, Compras, Pagos).

## 📝 Reglas de Integridad
1. **Partida Doble:** Todas las transacciones deben sumar cero.
2. **PCGE:** Se respeta la codificación de cuentas peruana (ej. 10 para Caja, 20 para Mercaderías, 70 para Ventas).
3. **Costo Real:** Las mercaderías se registran con su costo unitario entre llaves `{}` para permitir la valorización automática del inventario (Kardex).

## 🛠️ Herramientas
Puedes editar estos archivos manualmente con cualquier editor de texto o mediante la interfaz de **Fava** en el puerto 5001.
