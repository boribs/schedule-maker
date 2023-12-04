import unittest
import schedule

def fast_course():
    return schedule.Course('12345', '000', 'Some course', '000', 'Some professor')

class CourseScheduleAddDayTester(unittest.TestCase):

    def test_add_day_on_empty(self):
        for d in 'LAMJVS':
            t, r = ('0700-0759', 'room')
            c = fast_course().add_day(d, t, r)

            self.assertEqual(len(c.schedule), 1)
            self.assertEqual(c.schedule[d], schedule.ScheduleDay(t, r))

    def test_add_day_fails_on_other_day(self):
        pass

    def test_add_day_on_non_conflicting_schedule_1(self):
        pass

    def test_add_day_on_non_conflicting_schedule_2(self):
        pass

    def test_add_day_on_non_conflicting_schedule_3(self):
        pass

    def test_add_day_on_non_conflicting_schedule_4(self):
        pass

    def test_add_day_fails_on_conflicting_schedule_1(self):
        pass

    def test_add_day_fails_on_conflicting_schedule_2(self):
        pass

    def test_add_day_fails_on_conflicting_schedule_3(self):
        pass

    def test_add_day_fails_on_conflicting_schedule_4(self):
        pass

if __name__ == '__main__':
    unittest.main()
