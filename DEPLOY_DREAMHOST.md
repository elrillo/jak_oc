# Guía de Despliegue: Streamlit en DreamHost (VPS/DreamCompute)

Esta guía explica cómo mantener tu aplicación Streamlit **siempre activa** utilizando un servidor privado (VPS) de DreamHost.

> **⚠️ IMPORTANTE:** Esto **NO funcionará en el plan "Shared Hosting"** (Hosting Compartido) básico de DreamHost, ya que Streamlit necesita un proceso permanente que los planes compartidos no permiten. Necesitas un **VPS** o **DreamCompute**.

## 1. Requisitos Previos
*   Acceso SSH a tu servidor DreamHost (VPS).
*   Usuario con permisos de administrador (sudo) (en DreamCompute) o acceso a instalar paquetes Python (en VPS).

## 2. Estrategia: Ejecución Continua
Para que la web no se "apague", usaremos una herramienta llamada **Systemd** (estándar en Linux) o **Docker** para que la aplicación se reinicie automáticamente si falla o si se reinicia el servidor.

### Opción A: Usando Python Virtualenv + Systemd (Recomendada para VPS ligeros)

#### Paso 1: Preparar el Entorno
Conéctate por SSH a tu servidor y clona el repositorio:

```bash
# Ir a tu carpeta de webs
cd ~
git clone https://github.com/elrillo/jak_oc.git
cd jak_oc

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### Paso 2: Crear el Archivo de Servicio
Este archivo le dice al servidor "mantén esto corriendo por siempre".

Crea un archivo llamado `jak_oc.service` en `/etc/systemd/system/`:

```bash
sudo nano /etc/systemd/system/jak_oc.service
```

Pega el siguiente contenido (ajusta las rutas a tu usuario real):

```ini
[Unit]
Description=Streamlit JAK Observatorio
After=network.target

[Service]
User=TU_USUARIO_LINUX
WorkingDirectory=/home/TU_USUARIO_LINUX/jak_oc
ExecStart=/home/TU_USUARIO_LINUX/jak_oc/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### Paso 3: Activar el Servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable jak_oc
sudo systemctl start jak_oc
```

Tu app estará corriendo en `http://TU_IP_SERVER:8501`.

### Opción B: Usando Docker (Más robusta)

Si tu VPS soporta Docker (DreamCompute lo hace):

1.  Crear un `Dockerfile` en el proyecto (ya lo puedes subir al repo).
2.  Construir y correr:

```bash
docker build -t jak_app .
docker run -d --restart always -p 80:8501 jak_app
```

## 3. Configurar Dominio (Proxy Inverso)
Para no usar el puerto `:8501` y usar tu dominio (ej. `midominio.com`), debes configurar Apache o Nginx en DreamHost para que reenvíe el tráfico.

**Ejemplo Nginx:**
```nginx
location / {
    proxy_pass http://localhost:8501;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## Alternativas "Always On" (Si no tienes VPS)

Si tu plan es **Shared Hosting** básico y no quieres pagar un VPS ($10-$15/mes), te recomiendo:

1.  **Railway.app**: Tiene un plan Hobby (~$5/mes) que mantiene apps activas 24/7. Es muy fácil de conectar con GitHub.
2.  **Render.com**: Similar a Railway.
3.  **Ploomber Cloud**: Especializado en data apps.

Estas opciones son más baratas y fáciles de configurar que administrar un VPS Linux completo.
