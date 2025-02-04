FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo Procfile
COPY Procfile /app/

# Copiar requirements.txt e instalar dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install honcho

# Copiar el resto del código
COPY ./src /app/

# Exponer los puertos necesarios
EXPOSE 5000 8000

# Usar honcho para manejar Flask y FastAPI
CMD ["honcho", "start"]
