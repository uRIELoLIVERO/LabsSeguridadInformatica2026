"""Pruebas de contratos y CLI. --evidencia reproduce los escenarios del informe.

Los archivos de prueba se crean en directorios temporales; la muestra de la
entrega y su manifiesto no se modifican.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

import integridad


ENTREGA = Path(__file__).resolve().parents[1]
TAG_RFC4231 = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"


@contextlib.contextmanager
def entorno_temporal():
    with tempfile.TemporaryDirectory(prefix="lab01-") as temporal:
        base = Path(temporal)
        (base / "src").mkdir()
        (base / "data").mkdir()
        shutil.copy2(ENTREGA / "src/integridad.py", base / "src/integridad.py")
        shutil.copy2(ENTREGA / "data/generar_datos.py", base / "data/generar_datos.py")
        yield base


def ejecutar(base: Path, *argumentos: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", *argumentos],
        cwd=base,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


class PruebasIntegridad(unittest.TestCase):
    def setUp(self):
        self.entorno = entorno_temporal()
        self.base = self.entorno.__enter__()
        self.addCleanup(self.entorno.__exit__, None, None, None)
        self.assertEqual(ejecutar(self.base, "data/generar_datos.py").returncode, 0)
        self.muestra = self.base / "data/muestra"

    def cli(self, *args):
        return ejecutar(self.base, "src/integridad.py", *args)

    def generar(self, salida="manifest.sha256"):
        resultado = self.cli("generar", "--dir", "data/muestra", "--salida", salida)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        return json.loads((self.base / salida).read_text(encoding="utf-8"))

    def verificar(self):
        return self.cli("verificar", "--dir", "data/muestra", "--manifiesto", "manifest.sha256")

    def test_generar_recursivo_posix_ordenado_y_determinista(self):
        manifiesto = self.generar()
        self.assertEqual(list(manifiesto), [
            "app.bin", "logs/acceso.log", "politica_seguridad.md", "transferencia.txt"
        ])
        self.assertEqual(self.generar(), manifiesto)

    def test_manifiesto_interno_no_se_incluye_ni_se_reporta_nuevo(self):
        salida = "data/muestra/manifest.sha256"
        self.generar(salida)
        manifiesto = self.generar(salida)
        self.assertNotIn("manifest.sha256", manifiesto)
        resultado = self.cli("verificar", "--dir", "data/muestra", "--manifiesto", salida)
        self.assertEqual(resultado.returncode, 0, resultado.stdout)

    def test_directorio_vacio_y_archivo_vacio(self):
        vacio = self.base / "vacio"
        vacio.mkdir()
        salida = self.base / "vacio.sha256"
        self.assertEqual(integridad.generar_manifiesto(vacio, salida), {})
        self.assertEqual(integridad.verificar_manifiesto(vacio, {}, salida), {
            "OK": [], "MODIFICADO": [], "FALTANTE": [], "NUEVO": []
        })
        (vacio / "sin_contenido").write_bytes(b"")
        self.assertEqual(integridad.generar_manifiesto(vacio, salida), {
            "sin_contenido": hashlib.sha256(b"").hexdigest()
        })

    def test_archivo_binario_mayor_que_un_bloque(self):
        contenido = bytes(range(256)) * 600
        ruta = self.muestra / "grande.bin"
        ruta.write_bytes(contenido)
        self.assertEqual(integridad.sha256_archivo(ruta), hashlib.sha256(contenido).hexdigest())

    def test_verificacion_intacta_devuelve_cero(self):
        self.generar()
        resultado = self.verificar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("INTEGRIDAD VERIFICADA", resultado.stdout)

    def test_modificacion_de_un_solo_byte_devuelve_uno(self):
        self.generar()
        with (self.muestra / "transferencia.txt").open("ab") as archivo:
            archivo.write(b"X")
        resultado = self.verificar()
        self.assertEqual(resultado.returncode, 1, resultado.stderr)
        self.assertIn("[MODIFICADO] transferencia.txt", resultado.stdout)

    def test_faltante_y_nuevo_conservan_las_cuatro_categorias(self):
        manifiesto = self.generar()
        (self.muestra / "politica_seguridad.md").unlink()
        (self.muestra / "nuevo.txt").write_bytes(b"nuevo\n")
        self.assertEqual(integridad.verificar_manifiesto(
            self.muestra, manifiesto, self.base / "manifest.sha256"
        ), {
            "OK": ["app.bin", "logs/acceso.log", "transferencia.txt"],
            "MODIFICADO": [], "FALTANTE": ["politica_seguridad.md"], "NUEVO": ["nuevo.txt"]
        })
        resultado = self.verificar()
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("[FALTANTE] politica_seguridad.md", resultado.stdout)
        self.assertIn("[NUEVO] nuevo.txt", resultado.stdout)

    def test_enlaces_simbolicos_se_excluyen(self):
        externo = self.base / "externo.txt"
        externo.write_bytes(b"fuera del alcance")
        enlace = self.muestra / "enlace.txt"
        try:
            enlace.symlink_to(externo)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"El sistema no permite crear enlaces: {exc}")
        manifiesto = self.generar()
        self.assertNotIn("enlace.txt", manifiesto)
        self.assertEqual(self.verificar().returncode, 0)

    def test_hamming_bits_iguales_y_longitudes_invalidas(self):
        self.assertEqual(integridad.distancia_hamming_bits(b"\x00", b"\xff"), 8)
        self.assertEqual(integridad.distancia_hamming_bits(b"abc", b"abc"), 0)
        with self.assertRaises(ValueError):
            integridad.distancia_hamming_bits(b"a", b"ab")

    def test_hmac_vector_publicado_y_tres_estados(self):
        clave = b"\x0b" * 20
        mensaje = b"Hi There"
        self.assertEqual(integridad.calcular_mac(clave, mensaje), (TAG_RFC4231, None))
        self.assertEqual(integridad.calcular_mac(clave, mensaje, TAG_RFC4231), (TAG_RFC4231, True))
        self.assertEqual(integridad.calcular_mac(clave, mensaje, "0" * 64), (TAG_RFC4231, False))

    def test_cli_hmac_valido_invalido_y_no_ascii(self):
        args = ("mac", "--clave", "secreto", "--mensaje", "transferir 1000")
        calculo = self.cli(*args)
        self.assertEqual(calculo.returncode, 0)
        tag = calculo.stdout.split("HMAC-SHA256:  ", 1)[1].strip()
        self.assertEqual(self.cli(*args, "--verificar", tag).returncode, 0)
        for invalido in ("0" * 64, "á", ""):
            with self.subTest(tag=invalido):
                resultado = self.cli(*args, "--verificar", invalido)
                self.assertEqual(resultado.returncode, 1, resultado.stderr)
                self.assertIn("TAG INVÁLIDO", resultado.stdout)


def mostrar_evidencia():
    """Ejecuta las órdenes reales en una copia temporal de los datos y la CLI."""
    with entorno_temporal() as base:
        resultado = ejecutar(base, "data/generar_datos.py")
        if resultado.returncode:
            raise RuntimeError(resultado.stderr)

        def mostrar(*argumentos, esperado=0):
            print("$ python " + shlex.join(argumentos))
            resultado = ejecutar(base, *argumentos)
            print(resultado.stdout, end="")
            if resultado.stderr:
                print(resultado.stderr, end="", file=sys.stderr)
            print(f"código de salida: {resultado.returncode}\n")
            if resultado.returncode != esperado:
                raise RuntimeError(f"Se esperaba salida {esperado}")
            return resultado

        cli = "src/integridad.py"
        verificar = (cli, "verificar", "--dir", "data/muestra", "--manifiesto", "manifest.sha256")
        mostrar(cli, "generar", "--dir", "data/muestra", "--salida", "manifest.sha256")
        mostrar(*verificar)
        mostrar("-c", "from pathlib import Path; p = Path('data/muestra/transferencia.txt'); p.write_bytes(p.read_bytes() + b'X')")
        mostrar(*verificar, esperado=1)
        mostrar("-c", "from pathlib import Path; p = Path('data/muestra/transferencia.txt'); p.write_bytes(p.read_bytes()[:-1]); Path('data/muestra/politica_seguridad.md').unlink(); Path('data/muestra/nuevo.txt').write_bytes(b'nuevo\\n')")
        mostrar(*verificar, esperado=1)
        mostrar(cli, "avalancha", "--a", "transferencia: $1000", "--b", "transferencia: $1001")
        mac_args = (cli, "mac", "--clave", "secreto", "--mensaje", "transferir 1000")
        resultado = mostrar(*mac_args)
        tag = resultado.stdout.split("HMAC-SHA256:  ", 1)[1].strip()
        mostrar(*mac_args, "--verificar", tag)
        alterado = ("0" if tag[0] != "0" else "1") + tag[1:]
        mostrar(*mac_args, "--verificar", alterado, esperado=1)


if __name__ == "__main__":
    if sys.argv[1:] == ["--evidencia"]:
        mostrar_evidencia()
    else:
        unittest.main()
