# Laboratorio 01 — Informe

## Identificación

| Campo             | Valor                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Grupo             | 04                                                                     |
| Caso asignado     | Equifax, 2017                                                          |
| Mini-research     | Tema 2 — La cadena de suministro de software como superficie de ataque |
| Fecha de revisión | 17/10/2026                                                             |

### Integrantes

La identificación se encuentra en [INTEGRANTES.md](INTEGRANTES.md).

# PARTE A — Análisis del incidente bajo la lente CIA

## A.1 — Cronología

Se utilizan los resultados preliminares publicados por Equifax el 15 de septiembre
de 2017, distinguiendo la fecha de cada hecho de la fecha del comunicado.

| Fecha                       | Hecho                                                                                                                                                          | Fuente                                                                  |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Principios de marzo de 2017 | Según Equifax, US-CERT divulgó la vulnerabilidad de Struts y su equipo de seguridad tomó conocimiento de ella.                                                 | Equifax (2017), “Questions Regarding Apache Struts”.                    |
| 13/05–30/07/2017            | Período en el que Equifax situó los accesos no autorizados a archivos con información personal.                                                                | Equifax (2017), “Questions Regarding Apache Struts”.                    |
| 29/07/2017                  | El equipo de seguridad observó tráfico sospechoso asociado al portal estadounidense de disputas y bloqueó el tráfico identificado.                             | Equifax (2017), “Specific Details of Incident”.                         |
| 30/07/2017                  | Ante actividad sospechosa adicional, Equifax retiró de servicio la aplicación afectada.                                                                        | Equifax (2017), “Specific Details of Incident”.                         |
| 02/08/2017                  | Equifax contactó a Mandiant para realizar una revisión forense del alcance de la intrusión.                                                                    | Equifax (2017), “Specific Details of Incident”.                         |
| 07/09/2017                  | Equifax anunció públicamente el incidente y puso a disposición medidas de asistencia a consumidores.                                                           | Equifax (2017), introducción y “Overview of Consumer Support Response”. |
| 15/09/2017                  | El comunicado detalló una estimación preliminar de 143 millones de consumidores estadounidenses potencialmente afectados y anunció el retiro del CIO y la CSO. | Equifax (2017), introducción y “Specific Details of Incident”.          |

## A.2 — Activo afectado

**Activo principal:** la información personal de consumidores accesible desde la
aplicación de disputas en línea de Equifax: nombres, números de Seguro Social,
fechas de nacimiento, domicilios y, en algunos casos, números de licencia de
conducir. El comunicado del 15 de septiembre estimaba 143 millones de consumidores
estadounidenses potencialmente afectados; esta cifra corresponde a ese corte de
la investigación y no se presenta como un total final (Equifax, 2017).

**Priorización:** se trata de datos identificatorios sensibles cuya exposición
puede facilitar la suplantación de identidad y fraudes. La confidencialidad de
esos registros sigue siendo relevante aun después de recuperar el servidor: a
diferencia de una contraseña, una fecha de nacimiento no puede rotarse.

**Otros activos:** aproximadamente 209.000 números de tarjetas y documentos de
disputas con información personal de unos 182.000 consumidores estadounidenses;
el comunicado también identificó acceso a información limitada de residentes del
Reino Unido y Canadá. La aplicación del portal es el activo tecnológico que
permitía acceder a la información y que debió retirarse temporalmente de servicio
(Equifax, 2017). No se equipara el portal con una única base de datos que contenga
todos los registros afectados.

## A.3 — Matriz CIA

| Propiedad            | ¿Se violó?                                             | Evidencia concreta                                                                                                                                                                                                                 |
| -------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Confidencialidad** | Sí                                                     | Equifax confirmó accesos no autorizados a archivos con datos personales entre mayo y julio y el acceso a números de tarjetas y documentos de disputas (Equifax, 2017).                                                             |
| **Integridad**       | No, no acreditada para los datos personales analizados | El comunicado describe accesos no autorizados, pero no identifica registros personales cuyo contenido haya sido alterado. Con esta evidencia no se sostiene una modificación de esos datos (Equifax, 2017).                        |
| **Disponibilidad**   | Parcial                                                | Equifax retiró de servicio la aplicación afectada el 30 de julio. Hubo una interrupción del portal como medida de contención; no se afirma una caída de todos sus sistemas ni un ataque de denegación de servicio (Equifax, 2017). |

**Propiedad más discutible: integridad.** La ausencia de una alteración documentada
no demuestra que cada dato haya permanecido idéntico. Por eso, la conclusión se
limita a que no hay evidencia suficiente en las fuentes utilizadas para marcar
una violación de integridad de los registros personales. La capacidad de ejecutar
código tampoco demuestra por sí sola que un registro concreto haya sido cambiado.

La clasificación depende del activo: modificar un programa sería una afectación
de integridad de ese programa, aunque los registros siguieran intactos. En esta
matriz se prioriza la información personal y se documenta por separado la
interrupción del servicio. Así se evita confundir la gravedad del incidente con
una demostración automática de las tres propiedades.

## A.4 — Encadenamiento amenaza → vulnerabilidad → impacto

Un actor externo con capacidad de explotar una aplicación web constituyó la
**amenaza**. Aprovechó la **vulnerabilidad** CVE-2017-5638 en Apache Struts,
identificada por Equifax como vector inicial. El boletín S2-045 explica que un
valor malicioso de la cabecera `Content-Type` podía producir ejecución remota de
código al procesar errores del analizador Jakarta Multipart (Apache Software
Foundation, 2017).

La vulnerabilidad estaba en la aplicación del portal de disputas; el **activo**
prioritario expuesto fue la información personal accesible a partir de ese
entorno. El **impacto** comprendió pérdida de confidencialidad, riesgo de fraude
para los consumidores, interrupción del portal e investigación forense y medidas
de asistencia que debió afrontar la empresa (Equifax, 2017). No se atribuye una
identidad o motivación específica al actor sin una fuente que la respalde.

## A.5 — Dos controles mitigantes

| Control                                                                                                                                                             | Propiedad protegida                                                                        | Aplicación al caso                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Inventario y gestión verificable de parches:** identificar aplicaciones y versiones, asignar responsables y comprobar técnicamente el cierre de alertas críticas. | Principalmente confidencialidad; también reduce el riesgo de alteración y de interrupción. | Equifax conocía la vulnerabilidad, pero el portal siguió siendo explotable. El boletín S2-045 recomendaba Struts 2.3.32 o 2.5.10.1. Aplicar y verificar la corrección en el portal habría eliminado ese vector conocido, sin garantizar protección contra cualquier otro ataque (Apache Software Foundation, 2017; Equifax, 2017).               |
| **Mínimo privilegio y segmentación del portal:** restringir sus conexiones, cuentas de servicio y consultas a los datos necesarios para cada función.               | Confidencialidad e integridad.                                                             | Una aplicación expuesta no debería disponer de acceso indiscriminado a información sensible. Limitar la información alcanzable y los permisos de escritura reduciría el alcance de un compromiso. Es una mitigación propuesta: no se afirma que el comunicado pruebe una topología concreta ni que segmentar vuelva imposible toda exfiltración. |

## A.6 — Fuentes consultadas (Parte A)

1. [PRIMARIA] Equifax. (2017, 15 de septiembre). _Equifax releases details on cybersecurity incident, announces personnel changes_. https://investor.equifax.com/news-events/press-releases/detail/237/equifax-releases-details-on-cybersecurity-incident
2. [PRIMARIA] Apache Software Foundation. (2017). _S2-045_. Apache Struts 2 Wiki. https://cwiki.apache.org/confluence/display/WW/S2-045

# PARTE B — Integridad con funciones de hash

## B.1 — Evidencia de ejecución

Ejecución con Python 3.13.15 en Windows. Los bloques siguientes contienen salida
real de la CLI. El ejecutor informa el código de retorno de cada proceso mediante
la línea `código de salida`. Los separadores `\` impresos describen rutas locales;
las claves almacenadas en el JSON usan `/`.

Para reproducir todos los escenarios sin modificar los datos de trabajo:

```bash
python -X utf8 -B src/test_integridad.py --evidencia
```

El ejecutor copia la CLI y el generador a un directorio temporal y genera allí la
muestra. Las pruebas de alteración se realizan sobre esa copia, que se elimina al
finalizar. Para ejecutar la batería de contratos y CLI:

```bash
python -B src/test_integridad.py -v
```

Resultado: 11 pruebas ejecutadas, 10 correctas y una omitida porque Windows no
permitió crear un enlace simbólico (`WinError 1314`). No se presenta esa prueba
como aprobada. Se cubren también archivos vacíos, directorios vacíos, un binario
mayor que el bloque de lectura, exclusión del manifiesto interno y el vector 1 de
HMAC-SHA256 del RFC 4231.

### Generación del manifiesto

```text
$ python src/integridad.py generar --dir data/muestra --salida manifest.sha256
Manifiesto generado: manifest.sha256
Directorio base:     data\muestra
Archivos indexados:  4
código de salida: 0
```

### Verificación sobre un directorio íntegro

```text
$ python src/integridad.py verificar --dir data/muestra --manifiesto manifest.sha256
Directorio:  data\muestra
Manifiesto:  manifest.sha256

  OK             4
  MODIFICADO     0
  FALTANTE       0
  NUEVO          0

INTEGRIDAD VERIFICADA — sin diferencias contra el manifiesto.
código de salida: 0
```

### Detección de la modificación de un byte

Se añadió exactamente el byte ASCII `X` a `transferencia.txt`. La operación
equivale a `printf 'X' >> data/muestra/transferencia.txt` en Bash. El ejecutor usa
Python para que la modificación funcione también sin `printf` en Windows:

```python
from pathlib import Path
p = Path('data/muestra/transferencia.txt')
p.write_bytes(p.read_bytes() + b'X')
```

La modificación terminó con código `0`; la verificación posterior produjo:

```text
$ python src/integridad.py verificar --dir data/muestra --manifiesto manifest.sha256
Directorio:  data\muestra
Manifiesto:  manifest.sha256

  OK             3
  MODIFICADO     1
  FALTANTE       0
  NUEVO          0

Hallazgos:
  [MODIFICADO] transferencia.txt

INTEGRIDAD COMPROMETIDA — 1 hallazgo(s).
código de salida: 1
```

### Detección de archivo faltante y de archivo nuevo

En la misma copia temporal, se quitó el byte agregado, se eliminó la política y
se creó un archivo adicional. La preparación terminó con código `0`:

```python
from pathlib import Path
p = Path('data/muestra/transferencia.txt')
p.write_bytes(p.read_bytes()[:-1])
Path('data/muestra/politica_seguridad.md').unlink()
Path('data/muestra/nuevo.txt').write_bytes(b'nuevo\n')
```

```text
$ python src/integridad.py verificar --dir data/muestra --manifiesto manifest.sha256
Directorio:  data\muestra
Manifiesto:  manifest.sha256

  OK             3
  MODIFICADO     0
  FALTANTE       1
  NUEVO          1

Hallazgos:
  [FALTANTE] politica_seguridad.md
  [NUEVO] nuevo.txt

INTEGRIDAD COMPROMETIDA — 2 hallazgo(s).
código de salida: 1
```

### Efecto avalancha

Las comillas simples preservan el signo `$` del mensaje cuando se usa Bash.

```text
$ python src/integridad.py avalancha --a 'transferencia: $1000' --b 'transferencia: $1001'
mensaje A: "transferencia: $1000"
  SHA-256: 341511c4c817d55f30c81e212d0e82b0b16dd5a58d49fe5e45c9d5c998ab794a
mensaje B: "transferencia: $1001"
  SHA-256: 5fb87fd7adf8a226f61c666a3ed140b147501b8a1b8e1822e57fc4b3925323d9

Distancia de Hamming: 139 de 256 bits (54.30 %)
Efecto avalancha: para entradas distintas se espera un valor cercano al 50 %.
código de salida: 0
```

**Interpretación:** la expectativa teórica es una proporción cercana al 50 %, no
exactamente 128 bits en cada par. Cambiar `0` por `1` modifica un solo bit ASCII
de la entrada, pero cambian 139 bits del digest. Esto ilustra el efecto avalancha;
un único ejemplo no demuestra por sí solo todas las propiedades de SHA-256.

### HMAC

```text
$ python src/integridad.py mac --clave secreto --mensaje 'transferir 1000'
mensaje:      "transferir 1000"
HMAC-SHA256:  96bc66546d55627136aeaaefbcead75520a57e19539834d03e74d705b70ff9fe
código de salida: 0

$ python src/integridad.py mac --clave secreto --mensaje 'transferir 1000' --verificar 96bc66546d55627136aeaaefbcead75520a57e19539834d03e74d705b70ff9fe
mensaje:      "transferir 1000"
HMAC-SHA256:  96bc66546d55627136aeaaefbcead75520a57e19539834d03e74d705b70ff9fe
tag recibido: 96bc66546d55627136aeaaefbcead75520a57e19539834d03e74d705b70ff9fe

TAG VÁLIDO — el mensaje es auténtico e íntegro.
código de salida: 0

$ python src/integridad.py mac --clave secreto --mensaje 'transferir 1000' --verificar 06bc66546d55627136aeaaefbcead75520a57e19539834d03e74d705b70ff9fe
mensaje:      "transferir 1000"
HMAC-SHA256:  96bc66546d55627136aeaaefbcead75520a57e19539834d03e74d705b70ff9fe
tag recibido: 06bc66546d55627136aeaaefbcead75520a57e19539834d03e74d705b70ff9fe

TAG INVÁLIDO — el mensaje fue alterado o la clave no es la correcta.
código de salida: 1
```

`secreto` es una clave de demostración del enunciado, no una recomendación de
clave para producción.

## B.2 — Decisiones de implementación

| Decisión                      | Implementación                                                                                                                 | Motivo                                                                                                                                                            |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alcance del recorrido         | Solo archivos regulares; se omiten enlaces simbólicos y no se recorren directorios enlazados mediante `rglob` en Python 3.10+. | Evitar incorporar el contenido de un destino externo y mantener un alcance definido. La prueba de creación de enlaces quedó omitida en este Windows por permisos. |
| Manifiesto dentro del árbol   | Se comparan rutas resueltas y se excluye tanto al generar como al verificar.                                                   | Evitar la autorreferencia y que aparezca como `NUEVO`.                                                                                                            |
| Portabilidad y orden          | Rutas relativas con `as_posix()` y claves/listas ordenadas.                                                                    | No depender de rutas absolutas ni del orden del sistema de archivos.                                                                                              |
| Archivos y directorios vacíos | Un archivo vacío tiene el SHA-256 de `b''`; un árbol sin archivos produce `{}` y cuatro categorías vacías al verificar.        | Son entradas válidas, sin diferencias de integridad.                                                                                                              |
| Uso de memoria                | Se reutiliza `sha256_archivo()` y su lectura binaria por bloques de 64 KiB.                                                    | No cargar archivos completos ni traducir saltos de línea.                                                                                                         |
| Estados de HMAC               | Se distingue `None` de `False`; el hexadecimal esperado es ASCII y se compara con `compare_digest()`.                          | Diferenciar falta de verificación de verificación fallida. Los tags no ASCII se rechazan sin una excepción de tipo.                                               |

**Límite operativo:** el directorio debe permanecer estable durante el recorrido.
La herramienta no implementa instantáneas ni bloqueo de archivos; no garantiza una
vista atómica si otro proceso modifica archivos mientras se calculan los hashes.

## B.3 — Preguntas de análisis

### 1. El manifiesto por sí solo no alcanza

Nada en un hash público impide que un atacante con escritura sobre los archivos y
el manifiesto modifique ambos. Puede reemplazar un contenido y registrar su nuevo
SHA-256: el verificador observará coincidencia porque perdió su referencia
confiable. No necesita encontrar una colisión ni romper SHA-256. El fallo está en
el modelo de confianza, no en el cálculo del digest.

Una alternativa es conservar el manifiesto en un medio de solo lectura o en otro
sistema con permisos independientes. Otra es autenticar sus bytes con HMAC usando
una clave que el atacante no pueda leer, o firmarlo con una clave privada fuera
del sistema vigilado. El verificador debe autenticar primero el manifiesto. Si
también puede reemplazarse por una versión antigua válida, hace falta proteger su
versión o frescura; una firma aislada no evita ese retroceso (Krawczyk et al., 1997).

### 2. Qué agrega HMAC y qué no

HMAC agrega autenticidad del origen e integridad respecto de quienes conocen una
clave compartida: un tercero sin esa clave no debería poder generar un tag válido
para un mensaje alterado. Un hash simple no aporta esa distinción porque cualquiera
puede calcularlo. La garantía depende de proteger la clave y usar un algoritmo
adecuado, como HMAC-SHA256, no una concatenación casera de clave y mensaje
(Krawczyk et al., 1997).

No agrega confidencialidad: el mensaje sigue siendo legible si se transmite sin
cifrar. Tampoco no repudio: tanto el emisor como el receptor pueden producir tags,
por lo que un tercero no puede atribuir exclusivamente su autoría a uno de ellos.
Además, un tag válido puede reutilizarse; evitar repeticiones requiere autenticar
un contador, un nonce o una marca temporal y comprobarla en el protocolo. HMAC no
protege ante alguien que ya conoce o robó la clave.

### 3. MD5 y SHA-1

La propiedad afectada es la resistencia a colisiones: encontrar dos mensajes
distintos con el mismo digest cuesta menos de lo que debería para una función
ideal. Eso no equivale a poder recuperar cualquier mensaje a partir de su hash,
que es un problema de preimagen, ni a encontrar una sustitución para cualquier
archivo prefijado, que es segunda preimagen. Los RFC 6151 y 6194 explican estas
distinciones y desaconsejan usar MD5 o SHA-1 donde se requiere resistencia a
colisiones, por ejemplo en firmas digitales (Turner y Chen, 2011; Polk et al., 2011).

Un checksum heredado para detectar errores accidentales, sin adversario y sin una
decisión de autenticidad basada en él, puede conservar utilidad; el RFC 6151 lo
admite explícitamente para MD5. Esto no justifica proteger descargas hostiles con
MD5 ni elegirlo para sistemas nuevos. Tampoco se deduce automáticamente que una
colisión del hash rompa HMAC con ese hash: la construcción y el modelo de ataque
son distintos. Para esta herramienta se utiliza SHA-256 y HMAC-SHA256, evitando
introducir algoritmos obsoletos por compatibilidad innecesaria.

### 4. Comparación en tiempo constante

Una comparación ordinaria puede terminar al encontrar una diferencia o tener
optimizaciones cuyo tiempo depende del contenido. Si un servicio expone esa
variación, un atacante puede enviar muchos tags candidatos, medir las respuestas
y buscar diferencias estadísticas relacionadas con prefijos correctos. No se
afirma que todo `==` permita recuperar un tag por Internet: la explotación depende
de la implementación, la resolución temporal y el ruido del entorno.

`hmac.compare_digest()` evita el cortocircuito basado en contenido y es la función
recomendada para esta comparación. Ambos argumentos deben ser del mismo tipo;
con `str`, deben ser ASCII. La longitud y el tipo pueden seguir siendo observables,
por lo que “tiempo constante” no significa que toda la aplicación tarde siempre
lo mismo. En esta CLI los tags calculados tienen 64 caracteres hexadecimales y las
entradas no ASCII se rechazan antes de compararlas (Python Software Foundation,
s. f.).

### 5. SHA-256 para contraseñas: mala idea

Las contraseñas humanas tienen un espacio de búsqueda mucho menor que una clave
aleatoria de 256 bits. Si un atacante roba sus hashes, puede ensayar contraseñas
de diccionario y calcular SHA-256 muy rápido, incluso en paralelo. No necesita
invertir matemáticamente la función: prueba entradas probables y compara sus
resultados. Una sal aleatoria y única evita reutilizar tablas precalculadas y
reconocer contraseñas iguales por hashes iguales, pero no encarece suficientemente
cada intento si solo se aplica SHA-256 una vez.

Se emplean funciones específicas con costo ajustable, como Argon2id, scrypt o
bcrypt. Argon2id y scrypt añaden un costo significativo de memoria además del
trabajo computacional; bcrypt permite ajustar el costo de cómputo, pero no ofrece
la misma propiedad de dureza de memoria. El RFC 9106 describe Argon2 y sus
parámetros de memoria, pasadas y paralelismo. Esos parámetros se eligen según el
presupuesto del servidor y se almacenan junto con la sal y el resultado para poder
verificar y migrar contraseñas posteriormente (Biryukov et al., 2021).

# Cierre

## Dificultades encontradas

- El informe conservaba una ejecución del esqueleto anterior a la implementación.
  Se reemplazó por resultados actuales reproducibles para evitar confundir un
  error histórico con el estado del programa.
- En Equifax fue necesario separar las estimaciones preliminares del total final
  y distinguir ausencia de evidencia de alteración de una prueba de integridad.
  Se priorizaron fuentes primarias efectivamente consultadas.
- Un tag no ASCII provocaba un `TypeError` en `compare_digest()`. Se incorporó un
  rechazo explícito y una prueba de la CLI para esa entrada.
- La consola de Windows podía representar incorrectamente caracteres acentuados.
  El ejecutor captura UTF-8 y se documenta `-X utf8` para reproducir la evidencia.
- La prueba de enlaces simbólicos requiere permisos que no están disponibles en
  este entorno. Su omisión queda registrada; no afecta las pruebas de los cuatro
  subcomandos exigidos.

## Distribución del trabajo

| Integrante       | Aportes declarados para este laboratorio         |
| ---------------- | ------------------------------------------------ |
| Olivero Uriel    | Inicio del trabajo y finalización de la entrega. |
| Anil Facundo     | Revision y aprobacion de entrega.                |
| Antunez Jeremias | Revision y aprobacion de entrega.                |
| Lelli Matias     | Revision y aprobacion de entrega.                |

## Declaración de uso de asistentes de IA

**¿Se usaron asistentes de IA?** Sí.

| Herramienta                   | Uso y alcance                                                                                                                                                       | Verificación                                                                                                                                                                                              |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OpenCode con modelo de OpenAI | Revisión del borrador y del código existente; correcciones puntuales, elaboración de pruebas y asistencia en la redacción del análisis técnico y del mini-research. | Consulta de las fuentes primarias enlazadas y ejecución de las pruebas y escenarios reproducibles documentados. La lectura y validación personal final del responsable deben completarse antes del envío. |

## Fuentes consultadas (general)

Las fuentes de la Parte A están detalladas en A.6. Referencias adicionales:

1. Krawczyk, H., Bellare, M., y Canetti, R. (1997). _HMAC: Keyed-hashing for message authentication_ (RFC 2104). RFC Editor. https://www.rfc-editor.org/rfc/rfc2104.html
2. Turner, S., y Chen, L. (2011). _Updated security considerations for the MD5 message-digest and the HMAC-MD5 algorithms_ (RFC 6151). RFC Editor. https://www.rfc-editor.org/rfc/rfc6151.html
3. Polk, T., Chen, L., Turner, S., y Hoffman, P. (2011). _Security considerations for the SHA-0 and SHA-1 message-digest algorithms_ (RFC 6194). RFC Editor. https://www.rfc-editor.org/rfc/rfc6194.html
4. Python Software Foundation. (s. f.). _hmac — Keyed-hashing for message authentication_. Python 3.10 documentation. https://docs.python.org/3.10/library/hmac.html
5. Biryukov, A., Dinu, D., Khovratovich, D., y Josefsson, S. (2021). _Argon2 memory-hard function for password hashing and proof-of-work applications_ (RFC 9106). RFC Editor. https://www.rfc-editor.org/rfc/rfc9106.html
6. Nystrom, M. (2005). _Identifiers and test vectors for HMAC-SHA-224, HMAC-SHA-256, HMAC-SHA-384, and HMAC-SHA-512_ (RFC 4231). RFC Editor. https://www.rfc-editor.org/rfc/rfc4231.html
