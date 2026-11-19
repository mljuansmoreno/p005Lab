FROM python:3.13.18-alpine3.24@sha256:9ef1a599f863231c3d91e941389bfdc4a2d6070557243d54df1a4e57015b960e
# La web no usa SQLite. Retirarlo antes de copiar a la etapa final evita
# trasladar la extensión y conserva la base oficial intacta como origen.
RUN rm -rf /usr/local/lib/python3.13/sqlite3 \
    && find /usr/local/lib/python3.13/lib-dynload -name '_sqlite3*.so' -delete

FROM alpine:3.24@sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf
ENV PATH=/usr/local/bin:$PATH
COPY --from=0 /usr/local/ /usr/local/
RUN set -eu -o pipefail; \
    apk add --no-cache --virtual .detector-runtime pax-utils; \
    dependencias="$(scanelf --needed --nobanner --format '%n#p' --recursive /usr/local \
        | tr ',' '\n' | sort -u \
        | awk 'NF && system("[ -e /usr/local/lib/" $1 " ]") != 0 { print "so:" $1 }')"; \
    test -n "$dependencias"; \
    apk add --no-cache --virtual .python-rundeps $dependencias; \
    apk del --no-network .detector-runtime; \
    if apk info -e sqlite-libs; then exit 1; fi; \
    python -c 'import importlib.util, ssl, zlib; assert importlib.util.find_spec("sqlite3") is None'
# Alpine 3.24 corrigió los cuatro avisos de OpenSSL en 3.5.9-r1.
RUN apk upgrade --no-cache \
    && apk add --no-cache 'libcrypto3>=3.5.9-r1' 'libssl3>=3.5.9-r1'
WORKDIR /aplicacion
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY aplicacion/web.py aplicacion/probar_compose.py guiones/datos_sinteticos.py ./
USER 1654:1654
EXPOSE 8080
CMD ["python", "web.py"]
