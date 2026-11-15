FROM python:3.13.18-alpine3.23@sha256:bf88c40985006a79ca25458159a4da1dffc457f9ae234e948b2d6df56ca5ebd2
# La web no usa SQLite. Retirarlo antes de copiar a la etapa final evita
# trasladar la extensión y conserva la base oficial intacta como origen.
RUN rm -rf /usr/local/lib/python3.13/sqlite3 \
    && find /usr/local/lib/python3.13/lib-dynload -name '_sqlite3*.so' -delete

FROM alpine:3.23@sha256:469c9ea410b9215eaee7976ba6c0639039b444be8e5d638f7abbada189971eb2
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
WORKDIR /aplicacion
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY aplicacion/web.py aplicacion/probar_compose.py guiones/datos_sinteticos.py ./
USER 1654:1654
EXPOSE 8080
CMD ["python", "web.py"]
