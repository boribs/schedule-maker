import unittest
import schedule

def fast_course():
    return schedule.Course('12345', '000', 'Some course', '000', 'Some professor')

class RangeCollisionTester(unittest.TestCase):
    """
    There are four scenarios. Given ranges A and B:
        1. A's end collides with B's beginning.
        2. A is entirely inside B.

    And their counterparts:
        3. B's end collides with A's beginning.
        4. B is entirely inside A.

    This test case is testing that the collision detector function works as intended.
    """

    def test_collision_scenario_1(self):
        a = schedule.CourseSchedule('0700-0859', 'room')
        b = schedule.CourseSchedule('0800-0959', 'room')

        self.assertTrue(a.time_collision(b))
        self.assertTrue(b.time_collision(a))

    def test_collision_scenario_2(self):
        a = schedule.CourseSchedule('0800-0859', 'room')
        b = schedule.CourseSchedule('0700-0959', 'room')

        self.assertTrue(a.time_collision(b))
        self.assertTrue(b.time_collision(a))

    def test_no_collision_with_same_limit(self):
        a = schedule.CourseSchedule('0800-0900', 'room')
        b = schedule.CourseSchedule('0900-1000', 'room')

        self.assertFalse(a.time_collision(b))
        self.assertFalse(b.time_collision(a))

class CourseScheduleAddDayTester(unittest.TestCase):
    def test_add_day_on_empty(self):
        for d in 'LAMJVS':
            t, r = ('0700-0759', 'room')
            c = fast_course()
            c.add_day(d, t, r)

            self.assertEqual(len(c.schedule), 1)
            self.assertEqual(c.schedule[d], schedule.CourseSchedule(t, r))

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
