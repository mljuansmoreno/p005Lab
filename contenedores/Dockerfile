ARG IMAGEN_SDK=mcr.microsoft.com/dotnet/sdk:10.0.403@sha256:de4fe90a98845d75910b9769662465c84de1a934665c431279d1382b2bddc02b
ARG IMAGEN_R=rocker/r-ver:4.5.2@sha256:fd4ccdd3a4a6f7ef805e2daeee2a0fe3bf126bc231f36351223baecf5a595a4c
FROM ${IMAGEN_SDK} AS compilacion
WORKDIR /fuente
COPY . .
RUN dotnet publish codigo/RutaEstadistica.ServidorLocal -c Release -r linux-x64 --self-contained true -o /publicado
FROM ${IMAGEN_R}
RUN apt-get update && apt-get install -y --no-install-recommends libicu74 libssl3t64 libgssapi-krb5-2 curl && rm -rf /var/lib/apt/lists/*
WORKDIR /aplicacion
COPY --from=compilacion /publicado/ ./
COPY motor_r ./motor_r
COPY distribucion/fuentes/jsonlite_2.0.0.tar.gz /tmp/jsonlite_2.0.0.tar.gz
# Comprobar la fuente antes de instalar; el archivo está versionado para no depender de su traslado en CRAN.
RUN printf '75eb910c82b350ec33f094779da0f87bff154c232e4ae39c9896a9b89f3ac82d  /tmp/jsonlite_2.0.0.tar.gz\n' | sha256sum -c - && mkdir -p runtime/biblioteca runtime/R/bin && ln -s /usr/local/bin/Rscript runtime/R/bin/Rscript && Rscript --vanilla -e "install.packages('/tmp/jsonlite_2.0.0.tar.gz',repos=NULL,lib='runtime/biblioteca')" && R_LIBS_USER=/aplicacion/runtime/biblioteca R CMD INSTALL -l runtime/biblioteca motor_r/rutaanalitica && rm /tmp/jsonlite_2.0.0.tar.gz && useradd -u 1654 -m analista
ENV ASPNETCORE_URLS=http://0.0.0.0:8787
ENV RUTA_ESTADISTICA_ARCHIVO_SECRETO=/run/secrets/motor
USER 1654:1654
HEALTHCHECK --interval=20s --timeout=3s CMD curl -fsS -H "Authorization: Bearer $(cat /run/secrets/motor)" -H "Host: localhost" http://127.0.0.1:8787/salud || exit 1
ENTRYPOINT ["/aplicacion/RutaEstadistica.ServidorLocal"]
