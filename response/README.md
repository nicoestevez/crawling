Proceso de limpieza de dataset

# Tripletas Chile

Se concatenaron todos los archivos de tripletas correspondientes a Chile, y para su mejor visualización manual, se ordenó alfabéticamente por Sujeto. El propósito de ello es encontrar incongruencias de formato en la expresión como entidad del mismo Sujeto en la tripleta.

## Fuera de formato

Inesperadamente, el orden alfabético nos permitió encontrar y eliminar los siguientes datos anómalos al principio:

```
**Observación importante:** El fragmento presenta texto fragmentado, incompleto en varias secciones, con tablas parciales de datos financieros y referencias que no se desarrollan completamente. Muchas entidades se mencionan pero sus relaciones no están claramente establecidas en este fragmento específico.
- Fechas: 1585, 1586, 1620
- Institucos/establecimientos: tiánguez (mercado público), fundición real, iglesia
- Organizaciones/Unidades: Canton militar, bandas de Pincheira, montoneros
```

Por otra parte, se eliminaron también 'encabezados' inesperados del output del LLM extractor que se interpretaron como tuplas. Por ejemplo:

```
A continuación, presento las tripletas extraídas del fragmento, siguiendo estrictamente los principios de predicados estáticos y entidades inequívocas:
```

## Falta de contexto

Se eliminaron relaciones como las siguientes por falta de ocntexto para su comprensión:
```uno de los dos portugueses,ocupación,capitán de buque```

Y, como las siguientes, por tener valor de verdad dependiente de la época cronológica, sin estar ella explicitada:
```
viaje de Valparaíso al Callao,duración,veinticinco o treinta días
viaje de vuelta del Callao a Valparaíso,duración,tres y más meses
```

## Normalización de formato entidad

Se unificaron los nombres de entidades, principalmente personajes históricos, como por ejemplo de los siguientes 3 fraseos a 'Abate Juan Ignacio Molina'.

```
Abate Juan Ignacio Molina,autor de descripción sobre,minas de cobre en Chile
Abate Molina,año de declaración sobre minas de cobre,1752
Abate don Juan Ignacio Molina,autor de,Historia civil de Chile
```

## Variabilidad en relaciones

### Fechas

Se alteraron alrededor de 100 relaciones manualmente para que esta describiera mejor el formato de fecha. Por ejemplo, 'fecha de publicación' se cambió de la siguiente forma en este tipo de ejemplos:

```
artículo Los apóstoles,año de publicación,1872
El nímio correrpansal,mes de publicación,mayo de 1823
Artículo sobre censura de libros en El Araucano,fecha de publicación (sin año),22 de noviembre
```

Además, se eliminaron los "°" insertos en fechas y la ortografía arcaica de los meses del año.

Cuando fuese posible calcular una fecha exacta según el Objeto (por ejemplo el siguiente), este se reescribió como la fecha.
```El Araucano número 50,fecha de publicación,tres días después del 24 de agosto de 1831```

Las siguientes relaciones se consideraron fechas demasiado ambiguas, por lo que se decidió eliminarlas.
```
artículo Mercurio de Chile,fecha de publicación,marzo
padre Andrés Febres,fecha de publicación de escrito sobre cuestiones literarias,después de 1782
```


!!!!!! No sé qué hacer con esto
```
periódico La Opinión,fecha de publicación de informes fiscales,"números 13 a 19, desde el 26 de agosto hasta el 26 de octubre de 1830",chile4_5340
```

### Ocupaciones

| Cantidad de relaciones | Fraseo original | Refraseo |
|---|---|---|
| 2862 | cargo de | ocupación |
| 415 | cargo de trabajo | ocupación |
| 306 | cargo | ocupación |
| 415 | profesión | ocupación |

## Relaciones terminadas en preposiciones:

El fraseo como pregunta 'Cuál es {relación} de {entidad}? queda poco- o no-comprensible cuando una relación termina en preposición, por lo que se examinaron éstas.

### Eliminadas

Se eliminaron tuplas como las siguientes por incomprensibilidad o falta de contexto:
```
Antonio de Escobar,recurso presentado ante,la Audiencia
Congreso constituyente de Chile,propuesta de representación conjunta ante,Inglaterra y Estados Unidos
Agustín Gutiérrez Moreno,relación con,Antonio José de Irisarri
```

Y como las siguientes por imposibilidad de refraseo autoexplicativo:
```
Francisco García Sobarzo,litigante ante,Real Audiencia
Cortes reunidas en Córdoba,representante ante,Felipe II
Convictorio de San Francisco Javier,advocación religiosa previa bajo,beato Edmundo Campián
```

### Reescrituras masivas:

| Cantidad de relaciones | Fraseo original | Refraseo |
|---|---|---|
| 1473 | autor de | obra |
| 216 | fecha de | fecha |
| 124 | relación familiar con | pariente |
| 20 | (relación de )?parentesco con | pariente |


### Otros ejemplos de reescrituras

`Antonio de Hermida,arrendatario de,hacienda de la Dehesa` -> `propiedad arrendada`.
`Pedro de Valdivia,comandante militar bajo,Próspero Colona,chile1_1888` -> `superior como comandante militar`
