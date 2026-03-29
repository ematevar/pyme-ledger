# ₿ PYME-Ledger Pro

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![Beancount](https://img.shields.io/badge/Engine-Beancount-red.svg)](https://beancount.github.io/)

**PYME-Ledger Pro** es un sistema de Punto de Venta (POS) e Inteligencia Financiera diseñado específicamente para el mercado peruano. Combina la agilidad de una interfaz moderna con el rigor de un motor contable de **Doble Entrada en Texto Plano**.

## 🎯 Propuesta de Única de Valor
A diferencia de los POS tradicionales que guardan datos en bases cerradas, PYME-Ledger utiliza **Beancount**, permitiendo que cada venta se convierta automáticamente en un asiento contable auditable (PCGE), portable y eterno.

---

## 🏗️ Arquitectura del Sistema (Clean Architecture)
El proyecto ha sido refactorizado siguiendo patrones de diseño robustos para garantizar modularidad y escalabilidad:

- **Interface Layer (api/):** Endpoints REST que gestionan la comunicación con el cliente.
- **Application Layer (services/):** Lógica de negocio pura (Contabilidad e Inventario).
- **Infrastructure Layer (core/):** Wrapper del motor Beancount que aísla la complejidad técnica de los archivos físicos.
- **Data Layer (data/):** Repositorio de archivos `.bean` (La base de datos legible por humanos).

---

## 📂 Estructura de Carpetas
```text
pyme-ledger/
├── data/               # Archivos contables Beancount (PCGE Perú)
├── ledger_api/         # Aplicación núcleo del sistema
│   ├── api/            # Vistas y controladores REST
│   ├── services/       # Servicios de negocio (Accounting, Inventory)
│   └── core/           # Wrapper técnico del motor Beancount
├── templates/          # Frontend React SPA (Single File Architecture)
├── pyme_ledger_pos/    # Configuración global del servidor Django
├── Dockerfile          # Definición del contenedor de aplicación
└── docker-compose.yml  # Orquestación de servicios (Web + Fava)
```

---

## 🚀 Instalación y Despliegue

### Requisitos
- Docker y Docker Compose

### Pasos
1. Clona el repositorio.
2. Ejecuta la orquestación:
   ```bash
   docker compose up -d
   ```
3. Accede a las interfaces:
   - **Frontend Principal:** [http://localhost:8000](http://localhost:8000)
   - **Fava (Analytics Avanzado):** [http://localhost:5001](http://localhost:5001)

---

## 📈 Roadmap de Desarrollo
- [x] Refactorización a Arquitectura de Capas.
- [x] Dashbord con Utilidad Neta y Valorización de Inventario.
- [ ] **Fase 2:** Integración con Gemini IA para consultoría financiera automática.
- [ ] **Fase 3:** Módulo de Facturación Electrónica (SUNAT).
- [ ] **Fase 4:** Aplicación móvil nativa para el POS.

---
*Desarrollado con un enfoque en la soberanía de datos y la transparencia financiera.*
