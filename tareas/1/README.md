# Ejercicios de sincronización

    Tarea creada: 2022.10.15
	Entrega: 2022.10.22

Vimos ya los principales patrones de sincronización empleando
semáforos, y mencionamos también la existencia de otros (variables de
condición, señales y manejadores Unix...)

Ahora toca el turno a ustedes: Van a resolver un problema de programación
concurrente en el que sea necesario emplear algún mecanismo de sincronización.

## Calificaciones y comentarios

Pueden [consultar aquí las calificaciones y comentarios a sus
soluciones](./revision.org).

## Los problemas

Les mostré una presentación con siete problemas de sincronización.  Si todo fue
como lo planeé, resolvimos ya uno de los problemas en clase, con lo cual
quedarían seis (y si no hicimos una solución en clase, pueden elegir entre los
siete). La presentación, como todas las demás, está en [el sitio Web de la
materia](http://gwolf.sistop.org/), y lleva por título [Ejercicios de
sincronización](http://gwolf.sistop.org/laminas/06b-ejercicios-sincronizacion.pdf).

## La tarea

Lo que les toca a ustedes hacer es elegir uno de los problemas presentados, e
implementarlo como un programa ejecutable.

Pueden hacerlo _en el lenguaje de programación que quieran_ y _usando cualquier
mecanismo de sincronización_. Eso sí, sólo se considerará entregada si
efectivamente usan sincronización (**no valen** implementaciones secuenciales ni
verificación de estado con condicionales...)

Ojo, algunos de los ejercicios plantean _refinamientos_: El problema
puede resolverse de forma "simplista", buscando únicamente cumplirlo,
o pueden dedicarle un rato más y hacerlo mejor, de forma más
elegante o más correcta. Una buena implementación base llega hasta el
10; si entran a alguno de los refinamientos (¡háganmelo saber en la
documentación!) les doy crédito adicional.

## Preparando

Recuerda actualizar la rama principal (`main`) de tu repositorio local
con el de `prof`. Uniendo lo que cubrimos hasta ahora (refiérete al
[punto 8 de la práctica 1](../../practicas/1/README.md) y al [punto 7
de la práctica 2](../../practicas/2/README.md):

    $ git checkout main
    $ git pull prof main

Puedes crear una rama para realizar en ella tu tarea, si te acomoda ese flujo de
trabajo:

    $ git branch tarea_ejercicio_sincro
	$ git checkout tarea_ejercicio_sincro

## La entrega

Pueden resolver el problema de forma individual o en equipos de dos
personas.

Entréguenmelo, como siempre, en el directorio correspondiente
siguiendo la nomenclatura acordada en la práctica 1.

Todas las entregas deben contar con un archivo de texto en que se
detalle:

- El problema que decidieron resolver
- El lenguaje y entorno en que lo desarrollaron.
  - ¿Qué tengo que saber / tener / hacer para ejecutar su programa en mi
    computadora?
- La estrategia de sincronización (mecanismo / patrón) que emplearon para
  lograrlo
- Si están implementando alguno de los refinamientos
- Cualquier duda que tengan. Si notan que algún pedazo de la implementación
  podría mejorar, si algo no les terminó de quedar bien...

Ojo: Recuerden que les pido que lo entreguen _incluso si no les funciona
perfectamente_ (o incluso si no les funciona, punto). Intentar resolver el
problema tiene mérito, independientemente de si lo logran. ¡Me comprometo a
intentar resolver sus dudas!

¡Ah! Y consideren, naturalmente, la _estética_. ¿El código del programa
desarrollado es _elegante_? (¿da gusto leerlo?) ¿Le trabajaron un poco a que la
entrega sea _bonita y fácil de seguir visualmente_, a nivel interfaz usuario?
Si se nota un esfuerzo adicional más allá de volcar mensajes de estado a
pantalla, también lo sabré valorar 😉
