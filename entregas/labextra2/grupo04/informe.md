# Entregable — Lab Extra 2: El repo que delata

**Grupo:** 04 · **Integrantes:** ver `INTEGRANTES.md` [completar si lo prefieren aquí]

**Declaración de uso de IA:** Usamos Claude (asistente de IA de Anthropic) durante el laboratorio para entender el README y la rúbrica, proponer qué comandos probar en cada paso, y redactar un primer borrador de este informe a partir de las salidas que nosotros ejecutamos. En este laboratorio el asistente no corrió comandos dentro del repo del caso: todos los `git` y `./ctf` sobre `repo-delata` los ejecutamos nosotros. El asistente sí creó la rama `labextra2-grupo04` y la carpeta de entrega. Revisamos el borrador, reescribimos las partes de análisis con nuestras palabras, y verificamos cada hallazgo contra los archivos de `evidencia/salidas/`. [Confirmar: qué parte redactó y revisó cada integrante.]

---

## 1. Línea de tiempo de la filtración

Commits del caso (`git --no-pager log --all --date=short --format='%h | %an | %ad | %s'`), más el commit recuperado del reflog, que no aparece en `git log --all`.

| Fecha | Autor | Commit | Qué pasó | ¿Expone algo? |
|---|---|---|---|---|
| 2026-08-05 | dev-jperez | `0abdf95` (`feature/pasarela-pagos`) | Agrega `.env.pasarela` con `PAGOS_SECRET`. El mensaje del archivo dice "NO COMMITEAR ESTO". | Sí: secreto de la pasarela de pagos, en una rama abandonada. |
| 2026-08-10 | dev-jperez | `de33a75` (`main`, inicial) | Crea `app.py` y `README.md`. El token se toma de la variable de entorno `PHANTOM_API_TOKEN`. | No: el código no contiene el token. |
| 2026-08-10 | dev-jperez | `9333f2b` (hotfix) | Crea `config.py` con `PHANTOM_API_TOKEN = "FLAG{git_log_no_olvida}"`. | Sí: token en texto plano. |
| 2026-08-11 | dev-jperez | `eafb81c` (fix "sacar credenciales") | Quita la línea del token de `config.py`. El token sigue en la historia. | No en el árbol actual; sí en el historial. |
| 2026-08-12 | dev-jperez | `bc9d0db` (commit "wip: notas del cluster nuevo") | Agrega `notas_investigacion.txt` con `staging_key`. Este commit después queda fuera de todas las ramas. | Sí: llave de staging. Recuperado del reflog (ver R2). |
| (sin fecha en la salida del reflog) | dev-jperez | reset a `HEAD~1` (`HEAD@{4}`) | Mueve `main` a `eafb81c`, y `bc9d0db` queda sin referencias. | Es la acción que "borra" el commit de la vista normal. |
| 2026-08-20 | dev-jperez | `fa714bd` (`main`, HEAD) | Agrega una sección "Estado" en `README.md` que dice "Historia limpia. Sin secretos". | No expone nada directamente, pero la afirmación es falsa. |

Notas del grupo: [completar el análisis de tiempo de exposición con sus propias palabras].

## 2. Hallazgos

### R1 — Secreto en commit viejo

- Comandos:
  ```bash
  git --no-pager log -p --all > entregas/labextra2/grupo04/evidencia/salidas/r1.txt
  sed -n '20,37p' entregas/labextra2/grupo04/evidencia/salidas/r1.txt
  sed -n '38,54p' entregas/labextra2/grupo04/evidencia/salidas/r1.txt
  ```
- Salida relevante (`eafb81c`): se quitan las líneas `PHANTOM_API_TOKEN = "FLAG{git_log_no_olvida}"` y `DEBUG = True`.
- Salida relevante (`9333f2b`): se crea `config.py` con el token en la línea 2.
- Secreto expuesto: `PHANTOM_API_TOKEN`, que habilita el acceso a la API de deploy. Quedó en la historia aunque el commit posterior lo haya sacado.
- Flag entregada: `./ctf submit extra2 R1`.

### R2 — Commit "perdido"

- Comandos:
  ```bash
  git --no-pager reflog > entregas/labextra2/grupo04/evidencia/salidas/r2-reflog.txt
  git --no-pager show bc9d0db
  ```
- Cómo se llegó: el reflog muestra `bc9d0db` como commit creado antes del `reset` (`HEAD@{5}`), y muestra el `reset` a `HEAD~1` (`HEAD@{4}`). Con el hash del reflog, `git show` muestra el contenido aunque ninguna rama lo apunte.
- Secreto expuesto: `staging_key` en `notas_investigacion.txt`.
- Flag entregada: `./ctf submit extra2 R2`.

### R3 — Rama abandonada

- Comandos: `git branch -a` y `git --no-pager log --all` (muestra `feature/pasarela-pagos` con `0abdf95`).
- Secreto expuesto: `PAGOS_SECRET` en `.env.pasarela`, en la rama `feature/pasarela-pagos`.
- Flag entregada: `./ctf submit extra2 R3`.

## 3. Evaluación de exposición

**Cómo se evalúa.** Hay que separar dos preguntas: qué tan fácil es encontrar el secreto, y cuánto tiempo estuvo disponible. Para la primera, miramos si el secreto tiene un formato reconocible (por ejemplo, una variable como `PAGOS_SECRET=` o `PHANTOM_API_TOKEN=`) y en qué rama o commit aparece, porque los escáneres buscan esos patrones en todo el historial y en todas las ramas, no solo en `main`. Para la segunda, miramos cuántos días pasaron entre el commit que introdujo el secreto y el que lo quitó, y si el repo habría sido público en ese período.

**Análisis del grupo (borrador, revisar).** Si el repo hubiera sido público desde el commit inicial del 2026-08-05, el primer secreto que encontraría un escáner sería `PAGOS_SECRET` en `.env.pasarela` (`0abdf95`), porque tiene la forma `CLAVE=valor` y el archivo se llama `.env`. Ese secreto no se quitó nunca: sigue en la rama `feature/pasarela-pagos`. El token `PHANTOM_API_TOKEN` (`9333f2b`) estuvo expuesto desde el 2026-08-10 hasta el 2026-08-11, unas 15 horas según las fechas de los commits, pero como los commits quedan en la historia, la exposición sigue hasta que se rote el token. La `staging_key` (`bc9d0db`) no está en ninguna rama, pero sigue accesible por hash mientras el objeto exista en el repo. [Completar: estimación de tiempo hasta encontrarlo, con su justificación.]

## 4. Plan de remediación (respondiendo P4)

Borrador en orden de prioridad (revisar):

1. **Rotar los tres secretos** (`PHANTOM_API_TOKEN`, `PAGOS_SECRET` y `staging_key`). Es lo único que corta el acceso real: cualquiera que tenga una copia del repo puede usar el secreto mientras siga vigente.
2. **Revisar los registros de uso** de cada credencial, desde el primer commit que la expuso, para detectar si ya se usó.
3. **Avisar a quienes clonaron o forkearon**, porque ya tienen copias y no se pueden borrar desde el servidor.
4. **Reescribir la historia** (con `git filter-repo` o similar) y hacer force-push. Va después de la rotación, porque no deshace el acceso a las copias que ya existen.
5. **Lecciones aprendidas:** no commitear archivos `.env`, usar `.gitignore`, escanear secretos antes del commit (pre-commit hook) y en el servidor al hacer push.

Por qué la reescritura es lo menos urgente: el secreto ya estuvo disponible, y reescribir la historia solo evita que nuevos clones lo vean.

## 5. Preguntas P1–P5

Borrador (revisar y reescribir con sus palabras):

**P1. Línea de tiempo y exposición.** El token `PHANTOM_API_TOKEN` se introdujo en `9333f2b` (2026-08-10, 18:47) y se quitó en `eafb81c` (2026-08-11, 10:05). El commit de limpieza no alcanza, porque el token queda en el diff de `eafb81c` y en `9333f2b`, que siguen en la historia.

**P2. Modelo de git.** `reset --hard` mueve la referencia de la rama, pero no borra los objetos. Los comandos que lo demuestran son `git --no-pager reflog` (muestra el `reset` y el hash del commit anterior) y `git --no-pager show bc9d0db` (muestra el contenido aunque ninguna rama lo apunte).

**P3. Rama abandonada.** Si el repo fuera público, cualquier escáner que revise todas las ramas encuentra `.env.pasarela`. Si fuera privado con 30 colaboradores, cualquiera con acceso al repo tiene el secreto, y cada clon lo guarda aunque la rama se borre.

**P4. Remediación.** Ver la sección 4: rotación primero, reescritura de historia después.

**P5. Prevención.** Dos mecanismos: un pre-commit hook que escanee secretos en la máquina del dev antes de cada commit, y un escaneo o protección de push en el servidor, que bloquee el push si detecta un secreto. [Completar con las fuentes del research.]

## 6. Evidencia de progreso

- Salidas de cada reto:
  - [R1: `git log -p --all`](evidencia/salidas/r1.txt)
  - [R2: `git reflog`](evidencia/salidas/r2-reflog.txt)
  - [R3: ramas](evidencia/salidas/r3-ramas.txt) y [R3: commit `0abdf95`](evidencia/salidas/r3.txt)
- Registro de comandos: [`evidencia/comandos.txt`](evidencia/comandos.txt), generado con `history` desde la terminal del caso. Incluye también los intentos que fallaron. Lo que ejecutó el asistente en este laboratorio (creación de la rama `labextra2-grupo04` y de la carpeta de entrega) no aparece en ese historial, porque se corrió en otra sesión; se anota aquí.
