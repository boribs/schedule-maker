# Creador de horarios

Para la FCC (BUAP)...

---

## ¿Cómo usar?

Asegurate de tener instalados `tabulate` y `xlrd`:
```bash
pip install tabulate xlrd==1.2.0
```

Simplemente ejecuta `schedule.py` y pasa el nombre del archivo con las clases. Tiene que ser `.xlsx`.
```bash
python schedule.py classes/p2024.xlsx > schedules.txt
```

El resultado será un documento con las combinaciones de horario posibles,
según los parámetros especificados.
```
58469  [RI]    Redes Inalambricas              SORIANO - ROSAS JOSE ISABEL
55098  [MdD]   Mineria de Datos                BELTRAN - MARTINEZ BEATRIZ
51821  [AdC]   Arquitectura de Computadoras    MALDONADO - GARCIA ABRAHAM
57340  [DdAM]  Dllo. de Aplicaciones Moviles   ELVIRA - ENRIQUEZ ROBERTO
57690  [TIA]   Tec.de Inteligencia Artificial  OLMOS - PINEDA IVAN
57662  [PCyP]  Progra. Concurrente y Paralela  MENDOZA - OLGUIN GUSTAVO EMILIO

Horario        Lunes    Martes    Miércoles    Jueves    Viernes
-------------  -------  --------  -----------  --------  ---------
07:00 - 07:59
08:00 - 08:59
09:00 - 09:59  MdD                             MdD       MdD
10:00 - 10:59                                  MdD       MdD
11:00 - 11:59  AdC      TIA       TIA          AdC       AdC
12:00 - 12:59  TIA      TIA       TIA          AdC       AdC
13:00 - 13:59
14:00 - 14:59
15:00 - 15:59  DdAM                            DdAM      DdAM
16:00 - 16:59                                  DdAM      DdAM
17:00 - 17:59           PCyP      PCyP
18:00 - 18:59  PCyP     PCyP      PCyP
19:00 - 19:59           RI        RI
20:00 - 20:59  RI       RI        RI
```

----

## Configuración

Por defecto se busca un archivo llamado `schedule-config.json`. Si no lo encuentra,
crea una plantilla con el siguiente contenido:
```json
{
    "materias": [
        "Materia 1",
        "Materia 2"
    ],
    "sin-profesores": [
        "Profesor 1",
        "Profesor 2"
    ],
    "con-profesores": [
        "Profesor 1",
        "Profesor 2"
    ],
    "sin-cursos" : [
        "nrc1",
        "nrc2"
    ],
    "con-cursos" : [
        "nrc1",
        "nrc2"
    ],
    "sin-horarios": {
        "L": [
            "0700-0859",
            "1300-1459"
        ],
        "A": [
            "0700-0859",
            "1300-1459"
        ],
        "M": [
            "0700-0859",
            "1300-1459"
        ],
        "J": [
            "0700-0859",
            "1300-1459"
        ],
        "V": [
            "0700-0859",
            "1300-1459"
        ]
    }
}
```

Bajo `materias` deben ir los nombres de las materias tal cual aparecen
en el documento.

En `sin-profesores` se anotan los profesores no deseados.

En `con-profesores` se anotan los profesores deseados. Solo se mostrarán horarios con clases de todos los profesores especificados.

En `sin-cursos` se anotan los NRCs de los cursos no deseados. Esto también puede ser usado para anotar los cursos llenos durante el registro de materias.

En `con-cursos` se anotan los cursos deseados. Solo se mostrarán horarios que contengan todos los cursos anotados.

En `sin-horarios` se antonan los horarios no deseados. El formato de las horas
debe ser el mismo que usa BUAP: "hhmm-hhmm".

Adicionalmente, se puede especificar una dirección para el archivo de configuración
usando el parámetro `--config` (`-c`):
```bash
python schedule.py data.xlsx -c config.json
```

----

## Roadmap

 ✔ Configuración externa. \
 ✔ Especificar `NRC`s de forma inclusiva y exclusiva. \
 ☐ Dar soporte a `PDF`s. \
 ☐ Dar soporte a otras facultades.
