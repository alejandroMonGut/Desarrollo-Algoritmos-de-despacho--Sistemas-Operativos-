# Simulación de Algoritmos de Despacho de Procesos (CPU Scheduling)

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Estado-Finalizado-success?style=for-the-badge)

Este proyecto es una herramienta gráfica desarrollada en Python para la simulación, visualización y análisis comparativo de distintos algoritmos de planificación de CPU (Dispatch Algorithms). Diseñado como parte del currículo de **Sistemas Operativos** de la carrera de Ingeniería de Sistemas.

##  Autores

* **Alejandro Montoya Gutierrez** - *Estudiante de Ingeniería de Sistemas*
* **Arian Valencia Soto** - *Estudiante de Ingeniería de Sistemas*

---

##  Descripción del Proyecto

El software permite a los usuarios modelar una carga de trabajo de "n" procesos, definiendo sus tiempos de llegada, ráfagas de CPU (Burst Time) y prioridades. A través de una interfaz gráfica intuitiva, el sistema simula cómo diferentes algoritmos gestionan estos procesos, generando:

1.  **Diagramas de Gantt:** Visualización temporal de la ejecución.
2.  **Métricas de Rendimiento:** Cálculo automático de tiempos de espera y tiempos de sistema (retorno).
3.  **Comparativa Final:** Resumen que determina cuál algoritmo ofrece el mejor rendimiento promedio para el lote de procesos ingresado.

##  Algoritmos Implementados

El simulador incluye lógica para los siguientes algoritmos:

### No Expropiativos (Non-Preemptive)
* **FIFO (First-In, First-Out):** Atiende los procesos en estricto orden de llegada.
* **SJF (Shortest Job First):** Prioriza el proceso con la ráfaga más corta disponible.
* **Prioridad:** Ejecuta el proceso con la prioridad más alta (valor numérico menor indica mayor prioridad).

### Expropiativos (Preemptive / Quantum based)
* **Round Robin (Estándar/FIFO):** Asigna un Quantum de tiempo rotativo en orden de llegada.
* **Round Robin (Optimizado SJF):** Variante que ordena la cola de listos basándose en el tiempo restante.
* **Round Robin (Optimizado Prioridad):** Variante que ordena la cola de listos basándose en la prioridad.

---

## Requisitos e Instalación

### Prerrequisitos
* **Python 3.6** o superior.
* Librería **Tkinter** (Normalmente incluida en la instalación estándar de Python).

### Ejecución
1. Clona este repositorio o descarga el archivo `Algoritmos_Despacho.py`.
2. Abre una terminal en la carpeta del proyecto.
3. Ejecuta el siguiente comando:

```bash
python main.py
```
---
# Guía de uso



## 1. Inicio de la Simulación

Al ejecutar el programa, se encontrará con la **Pantalla de Bienvenida**.

1.  **Cantidad de Procesos:** En el campo central, ingrese el número entero de procesos que desea simular (por defecto aparece `4`).
    * *Nota:* Se recomienda un número entre 3 y 10 para una visualización óptima, aunque el sistema soporta más.
2.  **Confirmación:** Haga clic en el botón verde **"Iniciar Configuración"**.
    * Si ingresa un valor no válido (letra o número negativo), el sistema mostrará una alerta de error.

---

## 2. Configuración de Parámetros

En esta pantalla definirá las propiedades de cada proceso y del sistema.

### A. Configuración Global
* **Quantum (Round Robin):** En la parte superior, defina el valor del Quantum (tiempo máximo de CPU por turno). Este valor es crucial para los algoritmos *Round Robin*.
    * Valor por defecto: `2`.

### B. Tabla de Procesos
El sistema genera automáticamente datos de prueba, pero usted puede editar cada celda:

| Columna | Descripción | Unidades |
| :--- | :--- | :--- |
| **Proceso** | Identificador único (P1, P2, P3...) | N/A |
| **T. Llegada** | Momento en el que el proceso entra a la cola de listos. | Unidades de Tiempo (UT) |
| **Ráfaga** | Cantidad total de CPU que necesita el proceso para terminar. | Unidades de Tiempo (UT) |
| **Prioridad** | Valor numérico de importancia. **(0 = Mayor prioridad)**. | Entero |

> **Tip:** Puede usar la rueda del ratón para desplazarse verticalmente si la lista de procesos es larga.

3.  Una vez configurados los datos, presione el botón **"Calcular y Simular"** para procesar los algoritmos.

---

## 3. Visualización de Resultados

El simulador mostrará los resultados algoritmo por algoritmo.

### Navegación
Use los botones en la parte inferior para moverse entre las diferentes estrategias:
* **< Anterior / Siguiente >**: Cambia entre FIFO, SJF, Prioridad y las variantes de Round Robin.
* **Configuración**: Le permite volver atrás para cambiar los datos de entrada sin cerrar el programa.

### Panel Izquierdo: Métricas
Aquí encontrará una tabla detallada con los tiempos calculados para cada proceso:
* **Esp (TE - Tiempo de Espera):** Tiempo que el proceso pasó en la cola de listos sin ejecutarse.
* **Sis (TS - Tiempo de Sistema):** Tiempo total desde que el proceso llegó hasta que terminó (`Espera + Ráfaga`).
* **Resumen:** Al final de la tabla se muestran los promedios globales del algoritmo actual.

### Panel Derecho: Diagrama de Gantt
Es la representación visual de la línea de tiempo de la CPU.
* **Eje X:** Representa el tiempo transcurrido.
* **Bloques de Color:** Representan qué proceso (P1, P2...) está usando la CPU en ese instante.
* **Scroll:**
    * **Vertical:** Use la rueda del ratón para bajar si hay muchos procesos.
    * **Horizontal:** Mantenga presionada la tecla `Shift` + rueda del ratón (o use la barra inferior) para ver la línea de tiempo completa si la simulación es larga.

---

## 4. Comparativa Final

Después de revisar el último algoritmo, presione el botón **"VER COMPARATIVA FINAL >"**.

Esta pantalla muestra una tabla resumen que clasifica todos los algoritmos ejecutados:
1.  **Promedio de Espera:** El indicador principal de eficiencia.
2.  **Promedio de Sistema:** Indicador secundario.

### El Ganador
En la parte inferior, el sistema resaltará en un recuadro verde **cuál fue el algoritmo más eficiente** (el que logró el menor tiempo de espera promedio) para el conjunto de datos que usted ingresó.

---

## 5. Reinicio

Para comenzar una nueva simulación con una cantidad diferente de procesos, haga clic en el botón **"Reiniciar Simulación"** en la pantalla final.