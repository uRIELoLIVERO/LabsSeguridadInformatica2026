# Mini-research — Lab 01

**Grupo:** 04  
**Tema elegido:** 2 — La cadena de suministro de software como superficie de ataque  
**Cantidad de palabras:** 943 en las secciones de contenido, sin bibliografía ni declaración de IA.

## Planteo

Una organización puede proteger sus servidores y, aun así, incorporar un riesgo
mediante software que considera confiable. Sus aplicaciones incluyen código propio,
bibliotecas, herramientas de construcción y actualizaciones de proveedores. Cada
relación amplía la superficie de ataque y distribuye responsabilidades entre actores
que no controla completamente. SolarWinds/SUNBURST y Log4Shell muestran dos problemas
distintos de esa dependencia. La posición de este trabajo es que conocer los
componentes y verificar su procedencia son controles complementarios: un inventario
no garantiza integridad y una procedencia auténtica no garantiza ausencia de
vulnerabilidades. Confundir ambas garantías conduce a una falsa sensación de seguridad.

## Desarrollo

### Dos incidentes, dos mecanismos

En SolarWinds, el atacante introdujo una DLL maliciosa en el ciclo de software de
Orion. El archivo llegó firmado con el certificado legítimo del proveedor y, una
vez instalado, podía comunicarse con infraestructura del adversario. CISA describe
este vector como un compromiso de la cadena de suministro y advierte que no todas
las organizaciones que recibieron la puerta trasera sufrieron acciones posteriores
del atacante (Cybersecurity and Infrastructure Security Agency [CISA], 2021).
Distribuir el componente y explotar activamente cada instalación no son el mismo
hecho, por lo que tampoco corresponde contar automáticamente todas las
instalaciones como intrusiones equivalentes.

El modelo tradicional falla cuando asume que una actualización del proveedor,
con firma válida, necesariamente es segura. La firma permite comprobar la relación
del archivo con una clave, pero no demuestra que el proceso anterior a la firma
haya estado libre de manipulación. En un producto de administración con privilegios
amplios, esa confianza puede abrir acceso a otros sistemas. CISA (2021) destaca
precisamente los permisos habituales de Orion y recomienda limitar privilegios,
reconstruir componentes afectados y revisar las credenciales expuestas.

Log4Shell, en cambio, no exige que un atacante haya alterado la distribución
oficial de Log4j. CVE-2021-44228 afectaba funciones JNDI de Log4j Core: bajo las
condiciones vulnerables, contenido controlado por el atacante que llegaba al
registro podía provocar ejecución de código desde un servidor LDAP. Apache
distingue expresamente `log4j-core` de aplicaciones que utilizan únicamente
`log4j-api`, no afectadas por esa vulnerabilidad (Apache Software Foundation
[ASF], s. f.). El problema era una función vulnerable incorporada legítimamente,
no una actualización oficial convertida deliberadamente en troyano.

Ambos casos importan para la cadena de suministro, pero demandan respuestas
distintas. SolarWinds obliga a examinar cómo se produjo y distribuyó un artefacto;
Log4Shell obliga a identificar dónde existe una dependencia vulnerable y corregir
las instalaciones expuestas. La presencia de una biblioteca tampoco basta para
demostrar explotación: hay que considerar versión, componente, configuración y
forma de uso. Esta distinción evita que una lista de paquetes sustituya al análisis
técnico del riesgo.

### Qué aporta una SBOM

La NTIA define una Software Bill of Materials como un registro formal de los
componentes usados para construir software y de sus relaciones de suministro
(National Telecommunications and Information Administration [NTIA], 2021). Su
utilidad consiste en convertir la pregunta «¿usamos esta biblioteca?» en una
búsqueda verificable sobre productos y versiones, incluyendo dependencias que no
fueron seleccionadas directamente por el equipo. Ante una alerta como Log4Shell,
eso permite delimitar candidatos a revisión y consultar al proveedor con mayor
precisión.

Sin embargo, proponemos evaluar una SBOM por su utilidad operativa, no por su
mera existencia. Debe corresponder a la versión desplegada y mantenerse cuando
cambia el producto. Un documento desactualizado puede excluir precisamente el
componente vulnerable que interesa localizar. Además, describir ingredientes no
prueba que esos ingredientes sean seguros ni reemplaza el análisis de exposición.
La decisión de parchear necesita conectar el inventario con responsables,
prioridades y capacidad de desplegar una corrección.

### Qué aporta SLSA

SLSA aborda la confianza en el origen y la construcción del software. En la
versión 1.2, el recorrido Build distingue procedencia disponible en L1,
procedencia autenticada generada por una plataforma alojada en L2 y construcción
endurecida en L3. Este último nivel incorpora aislamiento entre ejecuciones y
protección del material utilizado para autenticar la procedencia frente a los
pasos de construcción definidos por usuarios (SLSA, s. f.-a).

La procedencia resulta útil cuando el consumidor verifica que el artefacto viene
del repositorio, revisión y constructor esperados. Acumular declaraciones sin
comprobarlas no establece esa relación. El propio modelo SLSA identifica el
compromiso de la plataforma de construcción de SolarWinds como una amenaza que
los niveles superiores buscan dificultar; no promete eliminar todo ataque ni
resolver el comportamiento de un productor malicioso (SLSA, s. f.-b).

## Tensión / límites

El límite central es que puede construirse fielmente software vulnerable. Un
Log4j afectado podría tener un inventario completo y una procedencia auténtica;
eso no corrige JNDI. A la inversa, una SBOM correcta no impide que un entorno
comprometido inserte código durante la construcción. Nuestra conclusión es que
composición, integridad y seguridad funcional deben evaluarse por separado,
aunque compartan evidencia.

Existe además una tensión práctica: exigir documentos puede ser sencillo para
un comprador y costoso para un proveedor pequeño. Si nadie actualiza el inventario
ni verifica la procedencia, el requisito termina siendo administrativo. Para una
PyME argentina, sería más útil comenzar por aplicaciones críticas, responsables
identificados y un procedimiento de actualización probado que recopilar archivos
sin capacidad de actuar. Esa priorización es una propuesta del trabajo, no una
garantía atribuida a los estándares.

## Cierre

La confianza en proveedores debe transformarse en evidencia comprobable y acciones
concretas. Una SBOM ayuda a saber qué se utiliza; SLSA ayuda a comprobar cómo se
obtuvo. Ninguno reemplaza los parches, la revisión del código, el mínimo privilegio
o la respuesta a incidentes. La lección profesional no es dejar de reutilizar
software, sino evitar que la reutilización implique confianza ilimitada. Cada
componente crítico necesita una forma de identificación, una expectativa de
procedencia y un responsable capaz de corregirlo cuando cambie la evidencia.

## Bibliografía

1. [PRIMARIA] Cybersecurity and Infrastructure Security Agency. (2021, 15 de abril). *Advanced persistent threat compromise of government agencies, critical infrastructure, and private sector organizations* (AA20-352A; versión revisada). https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-352a
2. [PRIMARIA] Apache Software Foundation. (s. f.). *Security* (entrada CVE-2021-44228). Apache Logging Services. Recuperado el 17 de octubre de 2026, de https://logging.apache.org/security.html#CVE-2021-44228
3. [PRIMARIA] National Telecommunications and Information Administration. (2021, 12 de julio). *The minimum elements for a Software Bill of Materials (SBOM)*. https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom
4. [PRIMARIA] SLSA. (s. f.-a). *Build: Track basics* (especificación v1.2). Recuperado el 17 de octubre de 2026, de https://slsa.dev/spec/v1.2/build-track-basics
5. [PRIMARIA] SLSA. (s. f.-b). *Supply chain threats* (especificación v1.2). Recuperado el 17 de octubre de 2026, de https://slsa.dev/spec/v1.2/threats-overview

## Declaración de uso de asistentes de IA

**¿Se usaron asistentes de IA?** Sí.

| Herramienta | Uso y alcance | Verificación |
|---|---|---|
| OpenCode con modelo de OpenAI | Asistencia en la búsqueda y contraste de fuentes, organización del argumento y redacción del documento. | Consulta de las cinco referencias primarias enlazadas y comprobación de su correspondencia con las afirmaciones. La lectura y validación personal final del responsable deben completarse antes del envío. |

**Verificación de fuentes:** las cinco referencias fueron consultadas durante la
preparación asistida. La revisión personal final corresponde al responsable de la
entrega y está pendiente antes del envío.
