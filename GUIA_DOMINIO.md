# Guía: Conectar Dominio DreamHost con Railway (o externa)

El objetivo es que tu app alojada en Railway (para que no se apague nunca) se vea bajo tu dominio `observatoriocongreso.cl` alojado en DreamHost.

## Opción 1: Subdominio (⭐⭐⭐⭐⭐ Recomendada)
Es la opción **más rápida, estable y profesional**. Tu app se vería en:
`https://informe.observatoriocongreso.cl` (o `kast.observatoriocongreso.cl`).

**Pasos:**
1.  En **Railway**: Ve a Settings > Domains e ingresa `informe.observatoriocongreso.cl`. Railway te dará un valor CNAME (ej: `app-123.up.railway.app`).
2.  En **DreamHost Panel**:
    *   Ve a **Domains** > **Manage Domains**.
    *   Haz clic en **DNS** debajo de `observatoriocongreso.cl`.
    *   Añade un registro:
        *   **Type**: CNAME
        *   **Host**: `informe`
        *   **Value**: `app-123.up.railway.app` (el que te dio Railway).
3.  ¡Listo! En minutos tu app carga segura y directa.

---

## Opción 2: Carpeta/Sub-ruta (⭐⭐ Compleja y Riesgosa)
Tu objetivo: `observatoriocongreso.cl/informe-kast`.

Esto es técnicamente difícil en Hosting Compartido porque Streamlit necesita **Websockets** (conexión en vivo), y los servidores compartidos de DreamHost (Apache/Nginx) suelen bloquear o cortar estas conexiones cuando intentas hacer un "túnel" (Reverse Proxy) desde una carpeta.

**Posibles soluciones (de mejor a peor):**

### A. Redirección Simple (Funcional)
Cuando alguien entra a `observatoriocongreso.cl/informe-kast`, el navegador automáticamente cambia la URL y lo lleva a `informe.observatoriocongreso.cl`.
*   **Pros**: 100% fiable.
*   **Contras**: El usuario ve que la URL cambió.

### B. Reverse Proxy en .htaccess (Probablemente fallará)
Intentar engañar al servidor para que sirva el contenido de Railway sin cambiar la URL.
En tu carpeta `/informe-kast` en DreamHost crearías un `.htaccess`:
```apache
RewriteEngine On
RewriteRule ^$ https://tu-app-railway.app/ [P,L]
```
> **Riesgo:** DreamHost Shared suele bloquear la bandera `[P]` (Proxy) por seguridad. Además, Streamlit se desconectará frecuentemente ("Please wait...").

### C. Iframe (La "trampa")
Creas una carpeta `informe-kast` en DreamHost y dentro un archivo `index.html` que carga tu app dentro de una ventana.
```html
<style>body, html {margin: 0; padding: 0; height: 100%; overflow: hidden;}</style>
<iframe src="https://tu-app-railway.app" width="100%" height="100%" frameborder="0"></iframe>
```
*   **Pros**: La URL se mantiene como tú quieres.
*   **Contras**: Puede dar problemas en móviles y la experiencia de usuario no es tan nativa.

## Resumen
Te recomiendo encarecidamente la **Opción 1 (Subdominio)**. Es el estándar de la industria para separar aplicaciones (ej: `app.google.com`, `drive.google.com`).
