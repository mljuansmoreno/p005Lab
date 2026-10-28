ARG IMAGEN_SDK=mcr.microsoft.com/dotnet/sdk:10.0.403
ARG IMAGEN_R=rocker/r-ver:4.5.2
FROM ${IMAGEN_SDK} AS compilacion
WORKDIR /fuente
COPY . .
RUN dotnet publish codigo/RutaEstadistica.ServidorLocal -c Release -r linux-x64 --self-contained true -o /publicado
FROM ${IMAGEN_R}
RUN apt-get update && apt-get install -y --no-install-recommends libicu76 libssl3t64 curl && rm -rf /var/lib/apt/lists/*
WORKDIR /aplicacion
COPY --from=compilacion /publicado/ ./
COPY motor_r ./motor_r
RUN mkdir -p runtime/biblioteca runtime/R/bin && ln -s /usr/local/bin/Rscript runtime/R/bin/Rscript && Rscript --vanilla -e "install.packages('https://cran.r-project.org/src/contrib/Archive/jsonlite/jsonlite_2.0.0.tar.gz',repos=NULL,lib='runtime/biblioteca')" && R_LIBS_USER=/aplicacion/runtime/biblioteca R CMD INSTALL -l runtime/biblioteca motor_r/rutaanalitica && useradd -u 1654 -m analista
ENV ASPNETCORE_URLS=http://0.0.0.0:8787
ENV RUTA_ESTADISTICA_ARCHIVO_SECRETO=/run/secrets/motor
USER 1654:1654
HEALTHCHECK --interval=20s --timeout=3s CMD curl -fsS -H "Authorization: Bearer $(cat /run/secrets/motor)" -H "Host: localhost" http://127.0.0.1:8787/salud || exit 1
ENTRYPOINT ["/aplicacion/RutaEstadistica.ServidorLocal"]
