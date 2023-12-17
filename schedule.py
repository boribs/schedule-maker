from __future__ import annotations
import argparse
import copy
import json
import xlrd # pip install xlrd==1.2.0
import tabulate
from enum import Enum, auto

VALID_DAYS = 'LAMJVS'
DAY_DICT = {
    'L' : 'Lunes',
    'A' : 'Martes',
    'M' : 'Miércoles',
    'J' : 'Jueves',
    'V' : 'Viernes',
    'S' : 'Sábado',
}

class ConfigKey(Enum):
    PROFESSOR_BLACKLIST = auto()
    TIME_RESTRICTIONS = auto()
    CLASS_NAMES = auto()

CONFIG_KEYS = {
    ConfigKey.PROFESSOR_BLACKLIST : 'sin-profesores',
    ConfigKey.TIME_RESTRICTIONS : 'sin-horarios',
    ConfigKey.CLASS_NAMES : 'materias',
}

CONFIG_FILENAME = 'schedule-config.json'
CONFIG_BODY = {
    ConfigKey.CLASS_NAMES : ['Materia 1', 'Materia 2'],
    ConfigKey.PROFESSOR_BLACKLIST : ['Profesor 1', 'Profesor 2'],
    # 'con-profesores' : ['Profesor 1', 'Profesor 2'],
    # 'sin-cursos' : [],
    # 'con-cursos' : [],
    ConfigKey.TIME_RESTRICTIONS : {
        'L' : ['0700-0859', '1300-1459'],
        'A' : ['0700-0859', '1300-1459'],
        'M' : ['0700-0859', '1300-1459'],
        'J' : ['0700-0859', '1300-1459'],
        'V' : ['0700-0859', '1300-1459']
    }
}

# TODO: I don't like your name
class CourseSchedule:
    """
    This class stores individual course's class time and classroom.
    It's basically a named tuple, but with time format conversion.
    """

    def __init__(self, time: str, room: str, nrc: int):
        self.time = self.parse_time(time)
        self.room = room
        self.nrc = nrc

    def parse_time(self, time: str) -> tuple[int, int]:
        assert len(time) == 9 and time[4] == '-'
        val = tuple(map(int, time.split('-')))
        assert val[0] < val[1]

        return val

    def time_collision(self, other: CourseSchedule) -> bool:
        """
        Returns True only if this object's time collides with `schedule`'s time.
        """

        if (self.time[0] < other.time[0] < self.time[1] or
            other.time[0] < self.time[0] < other.time[1] or
            (self.time[0] >= other.time[0] and self.time[1] <= other.time[1]) or
            (other.time[0] >= self.time[0] and other.time[1] <= self.time[1])
        ):
            return True

        return False

    def time_key(self) -> int:
        """
        Returns a key. can be used to sort different time blocks.
        """

        return int(f'{self.time[0]}{self.time[1]}')

    # TODO: I don't like your name
    def pretty_print(self) -> str:
        """
        Returns a string with this time block's range, but with a nicer format.
        'hh:mm - hh:mm'
        """

        t = (str(self.time[0]), str(self.time[1]))
        f = lambda s: f'{s[:-2]:>02}:{s[-2:]}'

        return f'{f(t[0])} - {f(t[1])}'

    def __repr__(self):
        # return f'{self.time[0]}-{self.time[1]} :: {self.room}'
        return f'{self.time[0]}-{self.time[1]}::{self.nrc}'

    def __eq__(self, other: any):
        if type(self) != type(other):
            return False
        else:
            return self.time == other.time and self.room == other.room

class Course:
    """
    A Course's data.
    """

    def __init__(self, nrc: int, key: str, name: str, sec: str, prof: str):
        self.nrc = nrc
        self.name = name
        self.key = key
        self.professor = prof
        self.section = sec
        self.schedule = {}

    # TODO: I don't like your name
    def add_day(self, day: str, time: str, room: str) -> bool:
        """
        Adds a classe's time block on `day`.

        Each course is composed on classes. Classes are just time blocks
        stored on a day's list (self.schedule[day]).
        A course can only have one of each class per day, that is, there
        cannot be repeated classes on the same day.
        """

        assert day in VALID_DAYS

        cs = CourseSchedule(time, room, self.nrc) # schedule we're trying to add

        # empty day, no problem
        if self.schedule.get(day, None) is None:
            self.schedule[day] = [cs]
            return True

        # check if classes collide
        for c_sch in self.schedule[day]:
            if c_sch.time_collision(cs):
                return False

        # no collisions, add schedule
        self.schedule[day].append(cs)

        return True

    def time_available(self, day: str, schedule: list[CourseSchedule]) -> bool:
        """
        Checks if this course's time blocks fit with `schedule` on `day`.
        """

        assert day in VALID_DAYS

        if self.schedule.get(day, None) is None:
            return True

        for t in self.schedule[day]:
            for s in schedule:
                if t.time_collision(s):
                    return False

        return True

    def initials(self):
        """
        Returs this course's name initials.
        For example:

        Tecnologías de la Información -> TdlI
        Minería de Datos              -> MdD
        Redes Inalámbricas            -> RI
        """
        return ''.join(map(lambda s: s[0], self.name.split()))

    def __repr__(self):
        s = f'{self.nrc}, {self.name}, {self.professor}\n'
        return s + '\n'.join(f'{key}: {self.schedule[key]}' for key in self.schedule.keys())

def parse_file(filename: str) -> dict[int, Course]:
    """
    Parses .xlsx file and returns a dictionary [nrc -> Course].
    This file has to have the same format as classes/p2024.xlsx.
    """

    courses_by_nrc = {}

    d = xlrd.open_workbook(filename)
    sheet = d.sheet_by_index(0)

    for r in range(1, sheet.nrows):
        row = [sheet.cell_value(r, c) for c in range(sheet.ncols)]
        nrc, key, name, sec, day, time, prof, room, _ = row

        if courses_by_nrc.get(nrc, None) is None:
            courses_by_nrc[nrc] = Course(int(nrc), key, name, sec, prof)

        courses_by_nrc[nrc].add_day(day, time, room)

    return courses_by_nrc

def collect_courses(
        courses_by_nrc: dict[int, Course],
        names: list[str],
        prof_blacklist: list[str] = [],
        time_restrictions: dict[str, list[str]] = {},
) -> dict[str, list[Course]]:
    """
    Gets all relevant courses considering filters:
        - names: the names of the courses
        - prof_blacklist: unwanted professors
        - time_restrictions: unwanted time blocks
    """

    courses = {name : [] for name in names}
    time_restrictions = {
        key : [CourseSchedule(s, '...', 0) for s in time_restrictions[key]]
        for key in time_restrictions.keys()
    }

    for nrc in courses_by_nrc.keys():
        course = courses_by_nrc[nrc]
        not_blacklist = course.professor not in prof_blacklist

        time_available = True
        for day in course.schedule.keys():
            if time_restrictions.get(day, None):
                if not course.time_available(day, time_restrictions[day]):
                    time_available = False
                    break

        if course.name in names and not_blacklist and time_available:
            courses[course.name].append(course)

    return courses

class SchedulePrototype:
    """
    Holder class for complete schedule.
    """

    def __init__(self):
        self.schedule = {}
        self.nrcs = []

    def can_add_course(self, course: Course) -> bool:
        """
        Checks if a course's time blocks don't collide with existing ones.
        """

        for day in course.schedule.keys():
            # day not in schedule, no collision
            if self.schedule.get(day, None) is None:
                continue
            else:
                for sp_time_block in self.schedule[day]:
                    for c_time_block in course.schedule[day]:
                        if sp_time_block.time_collision(c_time_block):
                            return False

        return True

    def add_course(self, course: Course):
        """
        Adds a course's time blocks.
        Doesn't consider compatibility with existing schedule.
        """

        self.nrcs.append(course.nrc)

        for day in course.schedule.keys():
            if self.schedule.get(day, None) is None:
                self.schedule[day] = []

            self.schedule[day].extend(course.schedule[day])

    def sort(self) -> SchedulePrototype:
        """
        Sorts all time blocks. Returns self.
        """

        for day in self.schedule.keys():
            self.schedule[day].sort(key=lambda n: n.time_key())

        return self

    def table(self, courses_by_nrc: dict[int, Course]) -> str:
        """
        Returns a string that represents a table containing relevant
        data for the schedule. Output looks like this:
        ```txt
        Horario        Lunes    Martes    Miércoles    Jueves    Viernes
        -------------  -------  --------  -----------  --------  ---------
        07:00 - 07:59
        08:00 - 08:59
        09:00 - 09:59
        10:00 - 10:59
        11:00 - 11:59  MdD      MdD       MdD          TIA       TIA
        12:00 - 12:59  TIA      MdD       MdD          TIA       TIA
        13:00 - 13:59
        14:00 - 14:59
        15:00 - 15:59  DdAM     DdAM      DdAM         PCyP      PCyP
        16:00 - 16:59  PCyP     DdAM      DdAM         PCyP      PCyP
        17:00 - 17:59  RI       RI        RI           AdC       AdC
        18:00 - 18:59  AdC      RI        RI           AdC       AdC
        19:00 - 19:59
        20:00 - 20:59
        ```
        """

        keys = [day for day in VALID_DAYS if day in self.schedule.keys()]
        headers = ['Horario'] + [DAY_DICT[day] for day in keys]
        ranges = [CourseSchedule(f'{i:>02}00-{i:>02}59', None, None) for i in range(7, 21)]

        rows = []
        for r in ranges:
            row = [r.pretty_print()] + [None] * 5
            for i, day in enumerate(keys):
                for t in self.schedule[day]:
                    if r.time_collision(t):
                        row[i + 1] = courses_by_nrc[t.nrc].initials()
                        break

            rows.append(row)

        return tabulate.tabulate(rows, headers=headers)

    def show(self, course_by_nrc: dict[int, Course]):
        """
        Prints course nrc, names and professor as well as the table.
        Output looks like this:
        ```txt
        58469  [RI]    Redes Inalambricas              SORIANO - ROSAS JOSE ISABEL
        58478  [MdD]   Mineria de Datos                TECUANHUEHUE - VERA PEDRO
        51821  [AdC]   Arquitectura de Computadoras    MALDONADO - GARCIA ABRAHAM
        57340  [DdAM]  Dllo. de Aplicaciones Moviles   ELVIRA - ENRIQUEZ ROBERTO
        57690  [TIA]   Tec.de Inteligencia Artificial  OLMOS - PINEDA IVAN
        58546  [PCyP]  Progra. Concurrente y Paralela  VARGAS - LOMELI MIGUEL

        Horario        Lunes    Martes    Miércoles    Jueves    Viernes
        -------------  -------  --------  -----------  --------  ---------
        07:00 - 07:59
        08:00 - 08:59
        09:00 - 09:59
        10:00 - 10:59
        11:00 - 11:59  AdC      TIA       TIA          AdC       AdC
        12:00 - 12:59  TIA      TIA       TIA          AdC       AdC
        13:00 - 13:59
        14:00 - 14:59
        15:00 - 15:59  DdAM     PCyP      PCyP         DdAM      DdAM
        16:00 - 16:59  PCyP     PCyP      PCyP         DdAM      DdAM
        17:00 - 17:59           MdD       MdD
        18:00 - 18:59  MdD      MdD       MdD
        19:00 - 19:59           RI        RI
        20:00 - 20:59  RI       RI        RI
        ```
        """

        data = []
        for nrc in self.nrcs:
            course = courses_by_nrc[nrc]
            data.append([nrc, f'[{course.initials()}]', f'{course.name}', course.professor])

        print(tabulate.tabulate(data, tablefmt='plain') + '\n')
        print(self.table(course_by_nrc))
        print('\n\n\n')

def combine_r(prot, possibilities, combinations):
    """
    Recursive method. Gets all possible schedule combinations given `possibilities`.
    """

    if len(possibilities) == 0:
        combinations.append(prot)
        return

    next_pos = possibilities[1:]
    for p in possibilities[0]:
        if prot.can_add_course(p):
            child = copy.deepcopy(prot)
            child.add_course(p)

            combine_r(child, next_pos, combinations)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    parser.add_argument('-c', '--config')
    args = parser.parse_args()

    if not args.data.endswith('.xlsx') and not args.data.endswith('.xls'):
        print('Schedule data file must be .xls/.xlsx termina.')
        exit(1)

    config_file = args.config if args.config else CONFIG_FILENAME

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f'No config file found. Creating {CONFIG_FILENAME}')

        with open(CONFIG_FILENAME, 'w') as c:
            c.write(json.dumps(CONFIG_BODY, indent=4))

        exit(1)

    courses_by_nrc = parse_file(args.data)
    courses_by_name = collect_courses(
        courses_by_nrc,
        config[CONFIG_KEYS[ConfigKey.CLASS_NAMES]],
        prof_blacklist=config[CONFIG_KEYS[ConfigKey.PROFESSOR_BLACKLIST]],
        time_restrictions=config[CONFIG_KEYS[ConfigKey.TIME_RESTRICTIONS]]
    )

    c = list(courses_by_name.values())

    combinations = []
    combine_r(SchedulePrototype(), c, combinations)

    for prot in combinations:
        prot.show(courses_by_nrc)
