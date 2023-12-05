from __future__ import annotations
import xlrd # pip install xlrd==1.2.0

class CourseSchedule:
    """
    This class stores individual course's class time and classroom.
    It's basically a named tuple, but with time format conversion.
    """

    def __init__(self, time: str, room: str):
        self.time = self.parse_time(time)
        self.room = room

    def parse_time(self, time: str) -> tuple[int, int]:
        assert len(time) == 9 and type(time) == str and time[4] == '-'
        val = tuple(map(int, time.split('-')))
        assert val[0] < val[1]

        return val

    def time_collision(self, other: CourseSchedule) -> bool:
        """
        Returns True only if this object's time collides with `schedule`'s time.
        """

        assert type(other) == type(self)

        if (self.time[0] < other.time[0] < self.time[1] or
            other.time[0] < self.time[0] < other.time[1] or
            (self.time[0] >= other.time[0] and self.time[1] <= other.time[1]) or
            (other.time[0] >= self.time[0] and other.time[1] <= self.time[1])
        ):
            return True

        return False

    def __repr__(self):
        return f'{self.time[0]}-{self.time[1]} :: {self.room}'

    def __eq__(self, other):
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
        assert day in 'LAMJVS'

        cs = CourseSchedule(time, room) # schedule we're trying to add

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

    def __repr__(self):
        s = f'{self.nrc}, {self.name}, {self.professor}\n'
        return s + '\n'.join(f'{key}: {self.schedule[key]}' for key in self.schedule.keys())

class SchedulePrototype:
    def __init__(self):
        pass

courses_by_nrc = {}
courses_by_name = {}

def parse_file(filename: str):
    global courses_by_nrc, courses_by_name

    d = xlrd.open_workbook(filename)
    sheet = d.sheet_by_index(0)

    for r in range(1, sheet.nrows):
        row = [sheet.cell_value(r, c) for c in range(sheet.ncols)]
        nrc, key, name, sec, day, time, prof, room, _ = row

        if courses_by_nrc.get(nrc, None) is None:
            courses_by_nrc[nrc] = Course(int(nrc), key, name, sec, prof)

        courses_by_nrc[nrc].add_day(day, time, room)

        # associate nrcs of courses with name, to compare classes
        if courses_by_name.get(name, None) is None:
            courses_by_name[name] = []

        courses_by_name[name].append(courses_by_nrc[nrc])

class Node:
    def __init__(self, nrc):
        self.nrc = nrc
        self.children = []

    def __repr__(self):
        return f'{self.nrc}'

datos = [
    ['1', '2'],
    ['a', 'b'],
    ['F', 'G'],
]
combinaciones = []


def combina_r(nodo, posibilidades, prog):
    if len(posibilidades) == 0:
        print(prog)
        return

    next_pos = posibilidades[1:]
    for i, p in enumerate(posibilidades[0]):
        nodo.children.append(Node(p))
        next_prog = prog.copy() + [p]
        combina_r(nodo.children[i], next_pos, next_prog)

    return nodo


if __name__ == '__main__':
    # parse_file('p2024.xlsx')
    n = combina_r(Node(0), datos, [])
    # print(n.children[0].children[0].children)



"""

{
'nombre de materia' : [curso1, curso2, curso3, ...],
'nombre de materia' : [curso1, curso2, curso3, ...],
'nombre de materia' : [curso1, curso2, curso3, ...],
     ...
}







"""
