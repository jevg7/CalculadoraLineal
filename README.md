<!-- HEADER DEL PROYECTO -->

<div align="center">
<h1 style="font-size: 3em;">📐 Linear Workbench</h1>
<p style="font-size: 1.2em;">
<strong>Tu laboratorio digital definitivo para el Álgebra Lineal.</strong>
</p>

<!-- SOBRE EL PROYECTO -->

💡 Sobre el Proyecto

Linear Workbench es una herramienta computacional diseñada para estudiantes, ingenieros y matemáticos que necesitan realizar operaciones de álgebra lineal de manera rápida, precisa y visual.

A diferencia de las calculadoras tradicionales, Linear Workbench está diseñado como un "banco de trabajo" donde puedes definir matrices, guardar variables y visualizar transformaciones en tiempo real.

¿Por qué Linear Workbench?

🚀 Rápido: Algoritmos optimizados para cálculos instantáneos.

🧠 Didáctico: Muestra los pasos intermedios (Reducción de Gauss, búsqueda de determinantes, etc.).

⚡ Versátil: Soporta desde aritmética básica hasta métodos numéricos complejos.

<!-- CARACTERÍSTICAS -->

⚡ Características Principales

Aquí es donde la magia sucede. Linear Workbench soporta:

Aritmética Matricial: Suma, resta, multiplicación, inversa, transpuesta.

Sistemas de Ecuaciones: Resolución por Gauss-Jordan, Regla de Cramer y Matriz Inversa.

Espacios Vectoriales: Cálculo de base y dependencia lineal.

Métodos Numéricos: Herramientas avanzadas para aproximaciones y cálculos iterativos.

<!-- TECNOLOGÍAS -->

🛠️ Tecnologías Utilizadas

Este proyecto destaca por tener su propio motor de cálculo. No dependemos de librerías externas para la lógica lineal principal.

<div align="center">


Backend / Lógica:
Implementación 100% propia. Todos los algoritmos de álgebra lineal (Gauss, Inversas, Multiplicaciones) fueron desarrollados por el equipo.

Interfaz:
Frontend moderno y reactivo para una experiencia de usuario fluida

Auxiliar:
Utilizado exclusivamente para el cálculo simbólico de derivadas en el método de Newton-Raphson.

</div>

<!-- GALERÍA DE IMÁGENES (GRID HTML) -->

📸 Capturas de Pantalla

<table width="100%">
<tr>
<td width="50%" align="center">
<strong>Panel de Matrices</strong>




<img src="https://github.com/user-attachments/assets/b99dfd2d-0717-41d9-806b-6095ca642151" width="100%" alt="Panel de Matrices">
</td>
<td width="50%" align="center">
<strong>Operaciones con Matrices</strong>




<img src="https://github.com/user-attachments/assets/5cacf67f-13d5-45e5-86b7-3464148f7523" width="100%" alt="Operaciones">
</td>
</tr>
<tr>
<td width="50%" align="center">
<strong>Sistemas Lineales</strong>




<img src="https://github.com/user-attachments/assets/a9a5039b-7cab-4b2f-914e-6f1b978cee3d" width="100%" alt="Sistemas Lineales">
</td>
<td width="50%" align="center">
<strong>Métodos Numéricos</strong>




<img src="https://github.com/user-attachments/assets/ab80df66-2270-49c7-b03d-ab24130ad405" width="100%" alt="Metodos Numericos">
</td>
</tr>
</table>

<!-- INSTALACIÓN -->

🚀 Instalación y Uso

Sigue estos pasos para configurar tu propio banco de trabajo localmente.

Prerrequisitos

Git

Python 3.x

Node.js

Pasos de Instalación

Clona el repositorio

git clone [https://github.com/jevg7/CalculadoraLineal.git](https://github.com/jevg7/CalculadoraLineal.git)
cd LinearWorkbench

# Asegúrate de estar en la carpeta del backend
Configura el Backend (Python)

cd backend
pip install -r requirements.txt


Configura el Frontend (React)
(Abre una nueva terminal en la carpeta raíz/frontend)

# Asegúrate de estar en la carpeta del frontend
npm install


Ejecución

Necesitarás dos terminales corriendo simultáneamente:

Terminal 1: Backend

cd backend
uvicorn app:app --reload


Terminal 2: Frontend

npm run dev


<div align="center">
<sub>Construido con ❤️ y muchas matrices</sub>
<br />
<a href="https://www.google.com/search?q=https://github.com/jevg7/CalculadoraLineal">Repositorio Oficial</a>
</div>
