# Informe — Laboratorio 02 · Criptografía

**Grupo:** 04 · **Integrantes:** *Facundo Anil - Antunez Jeremias - Olivero Uriel - Lelli Matias* · **Fecha:** 2026-10-16

---

## 0. Declaración de uso de IA

Se utilizó Claude como asistente para la redacción de secciones del informe y como soporte conceptual para la comprensión de los ataques descriptos. La implementación del código fue realizada y verificada manualmente por el grupo.

---

## 1. Parte A — Análisis de la falla

**Caso 4 — Zoom "End-to-End Encryption" (2020)**

### A.1 — Qué prometía el sistema

Zoom comercializaba sus videollamadas como protegidas con **cifrado end-to-end (E2E)**, término que en criptografía implica que solo los participantes de la llamada pueden acceder al contenido: ni siquiera el proveedor del servicio puede descifrar lo que se transmite. Esta promesa figuraba en el sitio oficial de Zoom, en materiales de ventas y en la interfaz de usuario (que mostraba un candado verde con la leyenda "Zoom is using an end to end encrypted connection") [1][2].

### A.2 — El mal uso concreto

El problema no estuvo en el algoritmo criptográfico en sí (se usaba AES-128), sino en **quién controlaba las claves**. Las claves de sesión se **generaban y distribuían a través de los servidores de Zoom**, lo que significa que Zoom tenía acceso a ellas en todo momento. En la práctica, el esquema era un cifrado en tránsito estándar (TLS entre cliente y servidor), no E2E: Zoom cifraba la conexión del cliente A a sus servidores, y luego del servidor a los demás participantes, teniendo en todo momento la clave para descifrar el contenido intermedio [1].

Adicionalmente, se detectó que parte del tráfico de llamadas —incluyendo claves de cifrado— era enrutado a través de **servidores ubicados en China**, aun cuando todos los participantes estaban fuera de ese país, exponiendo potencialmente esas claves a la jurisdicción de la ley china [2][3].

### A.3 — Qué propiedad se rompió y cómo se explotó

La propiedad rota fue la **confidencialidad** (y parcialmente la **autenticidad**, dado que los participantes no podían verificar que nadie más estuviese escuchando).

El vector de explotación era que Zoom —o cualquier actor con acceso a sus servidores (empleados malintencionados, gobiernos con ordenes judiciales, o atacantes que comprometieran la infraestructura)— podía **descifrar y acceder al contenido de cualquier llamada**. No se necesitaba romper ningún algoritmo: bastaba con obtener la clave de sesión de los servidores de Zoom. Esto es exactamente lo que el cifrado E2E está diseñado para impedir.

El FTC (Federal Trade Commission) de Estados Unidos investigó y sancionó a Zoom en 2020 por estas afirmaciones engañosas [4].

### A.4 — La forma correcta de haberlo hecho

Para implementar E2E real, las claves de cifrado deben **generarse y permanecer exclusivamente en los dispositivos de los participantes**, nunca en los servidores del proveedor. El esquema correcto es usar criptografía de clave pública (por ejemplo, Diffie-Hellman efímero) para negociar claves de sesión directamente entre los clientes, de modo que el servidor solo retransmita datos cifrados que él mismo no puede descifrar. Signal Protocol es un ejemplo de implementación correcta de E2E ampliamente auditada [5].

**Fuentes:**

[1] Zoom Blog — "A Message to Our Users" (2020-04-01): https://blog.zoom.us/a-message-to-our-users/

[2] Citizen Lab — "Move Fast and Roll Your Own Crypto: A Quick Look at the Confidentiality of Zoom Meetings" (2020-04-03): https://citizenlab.ca/2020/04/move-fast-roll-your-own-crypto-a-quick-look-at-the-confidentiality-of-zoom-meetings/

[3] The Intercept — "Zoom Meetings Aren't End-to-End Encrypted, Despite Misleading Marketing" (2020-03-31): https://theintercept.com/2020/03/31/zoom-meeting-encryption/

[4] FTC — "FTC Requires Zoom to Enhance its Security Practices as Part of Settlement" (2020-11-09): https://www.ftc.gov/news-events/news/press-releases/2020/11/ftc-requires-zoom-enhance-its-security-practices-part-settlement

[5] Signal Protocol Documentation: https://signal.org/docs/

---

## 2. Parte B.1 — Romper el XOR

### Implementación

La función `romper_xor_1byte()` prueba las 256 claves posibles de 1 byte. Para cada candidato, descifra el texto y puntúa el resultado según cuántos bytes corresponden a caracteres frecuentes en texto natural (letras del alfabeto, espacio, puntuación). La clave con mayor score es la más probable.

### Resultado obtenido

```bash
$ python3 src/cripto.py romper --hex $(cat data/muestra/reto_xor.hex)
clave=0x37
Memo interno PhantomCorp: la clave del wifi de invitados es Phantom-Guest-2026. No compartir fuera de la empresa.
```

**Clave encontrada:** `0x37` (decimal: 55)  
**Mensaje en claro:** `Memo interno PhantomCorp: la clave del wifi de invitados es Phantom-Guest-2026. No compartir fuera de la empresa.`

### Por qué el cifrado clásico de clave corta falla

Un cifrado XOR de 1 byte tiene exactamente **256 claves posibles**. Probarlas todas toma microsegundos en cualquier computadora moderna: no existe "espacio de claves" que proteja. Incluso si la clave fuera de 2 bytes (65 536 posibilidades) o 4 bytes (~4 mil millones), la fuerza bruta sigue siendo trivialmente rápida. La conclusión es que **la longitud de la clave importa fundamentalmente**: para ser seguro, el espacio de claves debe ser astronómicamente grande (AES usa claves de 128 o 256 bits, lo que hace inviable la fuerza bruta). Un cifrado clásico de clave corta no ofrece confidencialidad real.

---

## 3. Parte B.2 — Autenticación de mensajes

### B.2.1 — ¿Por qué `sha256(clave || mensaje)` es vulnerable a length-extension?

SHA-256 (como MD5 y SHA-1) usa la construcción **Merkle-Damgård**: el estado interno del hash al terminar de procesar el mensaje es exactamente lo que se expone como resultado. Esto permite a un atacante continuar el cómputo del hash desde ese estado final, como si fuera el estado intermedio de un mensaje más largo.

**Ejemplo concreto de ataque:** Supongamos que el servidor autentica mensajes con `MAC = sha256(clave || msg)` y un atacante intercepta:

```
msg    = "pago=100&dest=alice"
MAC    = sha256(clave || "pago=100&dest=alice")
```

Sin conocer `clave`, el atacante puede calcular:

```
MAC' = sha256(clave || "pago=100&dest=alice" || padding || "&dest=mallory&pago=9999")
```

donde `padding` es el relleno estándar que SHA-256 agrega internamente al primer bloque. El atacante puede computar `MAC'` a partir del `MAC` original (que es el estado interno de SHA-256 tras procesar el primer bloque), y así forjar un mensaje extendido con una MAC válida, **sin conocer la clave en ningún momento**. El servidor verificará `MAC'` contra el mensaje extendido y lo aceptará como auténtico.

Esto es posible porque el resultado de `sha256(clave || msg)` filtra el estado interno de SHA-256, y Merkle-Damgård permite reanudar el cómputo desde ese estado.

### B.2.2 — ¿Cómo lo resuelve HMAC estructuralmente?

HMAC (definido en RFC 2104) usa la clave **dos veces**, en dos capas de hash:

```
HMAC(K, m) = H( (K ⊕ opad) || H( (K ⊕ ipad) || m ) )
```

El hash interno `H((K ⊕ ipad) || m)` produce un resultado que es la entrada al hash externo, que a su vez está prefijado con `(K ⊕ opad)`. Esto significa que:

1. El resultado final de HMAC **no es el estado interno de ningún hash individual**: es el hash externo, cuyo input incluye la clave nuevamente. Un atacante que intente un length-extension sobre el hash interno solo obtiene `H((K ⊕ ipad) || m)`, que es la entrada al hash externo, no la salida final del HMAC.
2. Para forjar un `HMAC'` válido para un mensaje extendido, el atacante necesitaría conocer el estado interno del hash externo, lo que requiere conocer `K`.

En resumen: HMAC "envuelve" el hash interno con una segunda aplicación keyed, rompiendo la propiedad que hace posible el length-extension.

### B.2.3 — ¿Qué ataque evita `hmac.compare_digest`?

Evita el **timing attack** (ataque de temporización).

Una comparación de strings estándar (`mac1 == mac2` en Python) retorna `False` en cuanto encuentra el primer byte diferente. Esto significa que el tiempo de ejecución varía según **cuántos bytes coinciden antes de la primera diferencia**. Un atacante que pueda medir el tiempo de respuesta del servidor puede usar esta información para adivinar la MAC byte a byte.

**Ejemplo concreto:** Imaginemos que la MAC correcta es `"ab3f..."`. Un atacante prueba sistemáticamente:

- Envía MAC `"00..."` → respuesta en 1 μs (falla en el primer byte)
- Envía MAC `"aa..."` → respuesta en 1 μs (falla en el primer byte)
- Envía MAC `"ab..."` → respuesta en 1.2 μs (el primer byte coincide, falla en el segundo)

Al medir diferencias de tiempo —incluso de nanosegundos— el atacante puede recuperar la MAC completa byte a byte, sin necesidad de conocer la clave. Con suficientes muestras estadísticas, esto es factible incluso a través de la red.

`hmac.compare_digest` compara **siempre todos los bytes** independientemente de dónde se encuentre la primera diferencia, haciendo que el tiempo de comparación sea constante. Esto elimina el canal lateral temporal y hace el ataque inviable.

---

## 4. Bitácora

```bash
# Generar el reto XOR
python3 data/generar_datos.py

# Romper el XOR
python3 src/cripto.py romper --hex $(cat data/muestra/reto_xor.hex)
# clave=0x37
# Memo interno PhantomCorp: la clave del wifi de invitados es Phantom-Guest-2026. No compartir fuera de la empresa.

# Verificar cifrado básico
python3 src/cripto.py xor --texto hola --clave K
# 2324272a

# Calcular MAC ingenuo
python3 src/cripto.py mac --clave secreta --msg "pago 100" --modo ingenuo
# a8cc54c07b3acb7470c25ab9eea5234bfa2562e37298eee275e39a457004b725

# Calcular HMAC
python3 src/cripto.py mac --clave secreta --msg "pago 100" --modo hmac
# 5ec4a52407221836a66e8d654d914aaa4b18bd31cf31907348bcd292677b902e
```