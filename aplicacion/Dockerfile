FROM python:3.13.18-alpine3.24@sha256:9ef1a599f863231c3d91e941389bfdc4a2d6070557243d54df1a4e57015b960e
# La web no usa SQLite. Retirarlo antes de copiar a la etapa final evita
# trasladar la extensión y conserva la base oficial intacta como origen.
RUN rm -rf /usr/local/lib/python3.13/sqlite3 \
    && rm -rf /usr/local/lib/python3.13/ensurepip /usr/local/lib/python3.13/site-packages/pip* \
    && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.13 \
    && find /usr/local/lib/python3.13/lib-dynload \( -name '_sqlite3*.so' -o -name '_ssl*.so' -o -name '_hashlib*.so' \) -delete

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
    python -c 'import importlib.util, hashlib, zlib; assert importlib.util.find_spec("sqlite3") is None'
# Solo HTTP local: SHA-256 usa la implementación HACL* de CPython.
RUN apk upgrade --no-cache \
    && apk del --no-network --purge apk-tools libcrypto3 libssl3 \
    && test ! -e /usr/lib/libcrypto.so.3 \
    && test ! -e /usr/lib/libssl.so.3
WORKDIR /aplicacion
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY aplicacion/verificar_runtime.py ./
RUN python verificar_runtime.py
COPY aplicacion/web.py aplicacion/probar_compose.py guiones/datos_sinteticos.py ./
USER 1654:1654
EXPOSE 8080
CMD ["python", "web.py"]
