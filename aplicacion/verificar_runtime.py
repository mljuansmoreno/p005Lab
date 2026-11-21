"""Contrato del runtime HTTP local sin bibliotecas TLS ni instaladores."""
import hashlib
import importlib.util
from pathlib import Path

PROHIBIDOS = ("_ssl", "_hashlib", "sqlite3", "pip", "ensurepip")

def verificar():
    presentes = [nombre for nombre in PROHIBIDOS if importlib.util.find_spec(nombre) is not None]
    bibliotecas = [p.name for raiz in (Path("/lib"), Path("/usr/lib"), Path("/usr/local/lib"))
                   for patron in ("libssl.so*", "libcrypto.so*") for p in raiz.rglob(patron)]
    if presentes or bibliotecas:
        raise RuntimeError("El runtime contiene dependencias ajenas al contrato HTTP local")
    if hashlib.sha256(b"abc").hexdigest() != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad":
        raise RuntimeError("SHA-256 no coincide con el vector conocido")
    from http.client import HTTPConnection
    from urllib.request import build_opener
    import zipfile
    import zlib
    assert HTTPConnection and build_opener and zipfile.ZipFile and zlib.crc32(b"abc") == 891568578
    return {"http_local": True, "sha256": "HACL*", "openssl": False, "instaladores": False}

if __name__ == "__main__":
    import json
    print(json.dumps(verificar(), sort_keys=True))
