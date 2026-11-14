FROM python:3.13.18-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72
WORKDIR /aplicacion
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY aplicacion/web.py aplicacion/probar_compose.py guiones/datos_sinteticos.py ./
USER 1654:1654
EXPOSE 8080
CMD ["python", "web.py"]
