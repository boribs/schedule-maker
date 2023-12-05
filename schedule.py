from __future__ import annotations
import xlrd # pip install xlrd==1.2.0
import copy
import tabulate

VALID_DAYS = 'LAMJVS'

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

    def time_key(self):
        return int(f'{self.time[0]}{self.time[1]}')

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

    def add_day(self, day: str, time: str, room: str) -> bool:
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
        assert day in VALID_DAYS

        if self.schedule.get(day, None) is None:
            return True

        for t in self.schedule[day]:
            for s in schedule:
                if t.time_collision(s):
                    return False

        return True

    def __repr__(self):
        s = f'{self.nrc}, {self.name}, {self.professor}\n'
        return s + '\n'.join(f'{key}: {self.schedule[key]}' for key in self.schedule.keys())

def parse_file(filename: str) -> dict[int, Course]:
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
) -> dict[str, Course]:
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
    def __init__(self):
        self.schedule = {}
        self.nrcs = []

    def can_add_course(self, course: Course):
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
        self.nrcs.append(course.nrc)

        for day in course.schedule.keys():
            if self.schedule.get(day, None) is None:
                self.schedule[day] = []

            self.schedule[day].extend(course.schedule[day])

    def sort(self):
        for day in self.schedule.keys():
            self.schedule[day].sort(key=lambda n: n.time_key())

        return self

    def table(self):
        keys = self.schedule.keys()
        headers = ['Horario'] + [day for day in VALID_DAYS if day in keys]
        ranges = [CourseSchedule(f'{i:>02}00-{i:>02}59', None, None) for i in range(7, 21)]

        rows = []
        for r in ranges:
            row = [r]
            for day in self.schedule.keys():
                for t in self.schedule[day]:
                    if r.time_collision(t):
                        row.append(t)
                        break
                else:
                    row.append(None)

            rows.append(row)

        return tabulate.tabulate(rows, headers=headers)

def combine_r(prot, possibilities, combinations):
    if len(possibilities) == 0:
        combinations.append(prot)
        print(prot.schedule, prot.nrcs)
        return

    next_pos = possibilities[1:]
    for p in possibilities[0]:
        if prot.can_add_course(p):
            child = copy.deepcopy(prot)
            child.add_course(p)

            combine_r(child, next_pos, combinations)

if __name__ == '__main__':
    courses_by_nrc = parse_file('p2024.xlsx')
    courses_by_name = collect_courses(
        courses_by_nrc,
        [
            'Redes Inalambricas',
            'Mineria de Datos',
            'Arquitectura de Computadoras',
            'Dllo. de Aplicaciones Moviles',
            'Tec.de Inteligencia Artificial',
            'Progra. Concurrente y Paralela',
        ],
        prof_blacklist=[
            'SANCHEZ - GALVEZ MARIA EUGENIA',
            'CERON - GARNICA CARMEN',
            'ZACARIAS - FLORES FERNANDO',
        ],
        time_restrictions={
            'L' : ['0700-0859', '1300-1459'],
            'A' : ['0700-0859', '1300-1459'],
            'M' : ['0700-0859', '1300-1459'],
            'J' : ['0700-0859', '1300-1459'],
            'V' : ['0700-0859', '1300-1459'],
            'S' : ['0700-0859', '1300-1459'],
        }
    )

    c = list(courses_by_name.values())

    combinations = []
    combine_r(SchedulePrototype(), c, combinations)
