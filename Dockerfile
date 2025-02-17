# Usar Python 3.9 como base
FROM python:3.9-slim

#RUN apt-get update && apt-get install -y \
#    ffmpeg 

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el contenido del proyecto
COPY ./src /app/

# Instalar dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar los certificados SSL
COPY ./src/ssl /app/ssl

# Exponer el puerto 8000
EXPOSE 8000

# Ejecutar el servidor con HTTPS
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/ssl/local-key.pem", "--ssl-certfile", "/app/ssl/local-cert.pem"]
