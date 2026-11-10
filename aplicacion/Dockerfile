FROM python:3.13.7-slim-bookworm
WORKDIR /aplicacion
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY aplicacion/requirements.txt ./
RUN python -m pip install --no-cache-dir --no-index -r requirements.txt
COPY aplicacion/*.py guiones/datos_sinteticos.py ./
USER 1654:1654
EXPOSE 8080
CMD ["python", "web.py"]
