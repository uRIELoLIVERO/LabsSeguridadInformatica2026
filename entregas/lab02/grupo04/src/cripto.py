#!/usr/bin/env python3
"""
cripto.py — Laboratorio 02. CLI con cuatro subcomandos. Solo biblioteca estándar.

Cada subcomando tiene un bloque TODO que hoy lanza NotImplementedError. Tu trabajo
es completarlos. NO modifiques la firma de las funciones ni la interfaz de la CLI.
La función xor_cifrar() ya está implementada como referencia: leela, es la base de
casi todo el lab.
"""
import argparse
import hashlib
import hmac
import sys

# ---------------------------------------------------------------------------
# REFERENCIA (ya implementada). Leela antes de empezar.
# ---------------------------------------------------------------------------
def xor_cifrar(datos: bytes, clave: bytes) -> bytes:
    """Cifra (y descifra) por XOR de clave repetida. XOR es involutivo:
    aplicar la misma clave dos veces devuelve el original."""
    return bytes(b ^ clave[i % len(clave)] for i, b in enumerate(datos))


# ---------------------------------------------------------------------------
# B.1 — romper XOR de clave de 1 byte por análisis de frecuencia.
# ---------------------------------------------------------------------------
def romper_xor_1byte(cifrado: bytes) -> tuple[int, bytes]:
    """Prueba las 256 claves posibles de 1 byte y devuelve (clave, texto_claro)
    de la más probable de ser lenguaje natural.

    Estrategia: para cada candidato, contamos cuántos bytes son caracteres
    frecuentes en español/inglés (letras comunes + espacio). El candidato con
    mayor score es el texto en claro. Esto demuestra por qué un cifrado clásico
    de clave corta NO protege nada: fuerza bruta sobre 256 posibilidades es trivial.
    """
    # Caracteres frecuentes en texto natural español/inglés
    FRECUENTES = set(
        b' \t\n'                          # espacios y saltos
        b'eEaAoOiInNsStTrRlLdDcCuUmMpP'  # letras más comunes ES/EN
        b'fFgGhHbByYvVkKwWjJxXzZqQ'      # resto del alfabeto
        b'.,;:!?\'"()-'                    # puntuación habitual
    )

    mejor_score = -1
    mejor_clave = 0
    mejor_texto = b''

    for k in range(256):
        candidato = bytes(b ^ k for b in cifrado)
        score = sum(1 for b in candidato if b in FRECUENTES)
        if score > mejor_score:
            mejor_score = score
            mejor_clave = k
            mejor_texto = candidato

    return mejor_clave, mejor_texto


# ---------------------------------------------------------------------------
# B.2 — MAC ingenuo vs HMAC.
# ---------------------------------------------------------------------------
def mac_ingenuo(clave: bytes, msg: bytes) -> str:
    """Devuelve sha256(clave || msg) en hex. Es lo que MUCHA gente hace...
    y es vulnerable a length-extension. Lo implementás para después romperlo
    conceptualmente en el informe."""
    return hashlib.sha256(clave + msg).hexdigest()

def mac_hmac(clave: bytes, msg: bytes) -> str:
    """Devuelve el HMAC-SHA256 en hex. Esta es la forma CORRECTA."""
    return hmac.new(clave, msg, hashlib.sha256).hexdigest()

def verificar_mac(esperado: str, recibido: str) -> bool:
    """Compara dos MAC en hex. DEBE ser en tiempo constante para no filtrar
    información por el tiempo de comparación."""
    return hmac.compare_digest(esperado, recibido)


def main() -> int:
    ap = argparse.ArgumentParser(description="Herramientas de cripto (Lab 02).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("xor", help="cifrar/descifrar por XOR (hex de salida)")
    p.add_argument("--texto", required=True)
    p.add_argument("--clave", required=True)

    p = sub.add_parser("romper", help="romper un cifrado XOR de 1 byte (hex de entrada)")
    p.add_argument("--hex", required=True, help="cifrado en hexadecimal")

    p = sub.add_parser("mac", help="calcular MAC de un mensaje")
    p.add_argument("--clave", required=True)
    p.add_argument("--msg", required=True)
    p.add_argument("--modo", choices=["ingenuo", "hmac"], default="hmac")

    a = ap.parse_args()
    if a.cmd == "xor":
        print(xor_cifrar(a.texto.encode(), a.clave.encode()).hex())
    elif a.cmd == "romper":
        k, claro = romper_xor_1byte(bytes.fromhex(a.hex))
        print(f"clave=0x{k:02x}")
        print(claro.decode(errors="replace"))
    elif a.cmd == "mac":
        fn = mac_ingenuo if a.modo == "ingenuo" else mac_hmac
        print(fn(a.clave.encode(), a.msg.encode()))
    return 0

if __name__ == "__main__":
    sys.exit(main())