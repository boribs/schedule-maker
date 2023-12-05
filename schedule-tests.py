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

    def test_collision_with_same_range(self):
        a = schedule.CourseSchedule('0800-0900', 'room')
        b = schedule.CourseSchedule('0800-0900', 'room')

        self.assertTrue(a.time_collision(b))
        self.assertTrue(b.time_collision(a))

    def test_collision_that_didnt_work_for_some_reason(self):
        a = schedule.CourseSchedule('1100-1350', 'room')
        b = schedule.CourseSchedule('0700-1129', 'room')

        self.assertTrue(a.time_collision(b))
        self.assertTrue(b.time_collision(a))

class CourseScheduleAddDayTester(unittest.TestCase):
    """
    Tests for the Courses.add_day method.
    """

    def test_add_day_on_empty(self):
        for d in 'LAMJVS':
            t, r = ('0700-0759', 'room')
            c = fast_course()

            self.assertTrue(c.add_day(d, t, r))

            self.assertEqual(len(c.schedule), 1)
            self.assertEqual(len(c.schedule[d]), 1)
            self.assertEqual(c.schedule[d], [schedule.CourseSchedule(t, r)])

    def test_add_day_on_non_conflicting_schedule_same_day(self):
        c = fast_course()

        self.assertTrue(c.add_day('L', '0700-0759', 'room'))
        self.assertTrue(c.add_day('L', '0800-0859', 'room'))

        self.assertEqual(len(c.schedule), 1)
        self.assertEqual(len(c.schedule['L']), 2)
        self.assertEqual(
            c.schedule['L'],
            [
                schedule.CourseSchedule('0700-0759', 'room'),
                schedule.CourseSchedule('0800-0859', 'room'),
            ],
        )

    def test_add_day_on_non_conflicting_schedule_same_day(self):
        c = fast_course()

        self.assertTrue(c.add_day('L', '0700-0759', 'room'))
        self.assertTrue(c.add_day('L', '1000-1159', 'room'))

        self.assertEqual(len(c.schedule), 1)
        self.assertEqual(len(c.schedule['L']), 2)
        self.assertEqual(
            c.schedule['L'],
            [
                schedule.CourseSchedule('0700-0759', 'room'),
                schedule.CourseSchedule('1000-1159', 'room'),
            ],
        )

    def test_add_day_on_non_conflicting_schedule_different_day_different_schedule(self):
        c = fast_course()

        self.assertTrue(c.add_day('L', '0700-0759', 'room'))
        self.assertTrue(c.add_day('M', '1000-1159', 'room'))

        self.assertEqual(len(c.schedule), 2)
        self.assertEqual(len(c.schedule['L']), 1)
        self.assertEqual(len(c.schedule['M']), 1)
        self.assertEqual(
            c.schedule['L'],
            [schedule.CourseSchedule('0700-0759', 'room')]
        )
        self.assertEqual(
            c.schedule['M'],
            [schedule.CourseSchedule('1000-1159', 'room')]
        )

    def test_add_day_on_non_conflicting_schedule_different_day_same_schedule(self):
        c = fast_course()

        self.assertTrue(c.add_day('L', '0700-0759', 'room'))
        self.assertTrue(c.add_day('M', '0700-0759', 'room'))

        self.assertEqual(len(c.schedule), 2)
        self.assertEqual(len(c.schedule['L']), 1)
        self.assertEqual(len(c.schedule['M']), 1)
        self.assertEqual(
            c.schedule['L'],
            [schedule.CourseSchedule('0700-0759', 'room')]
        )
        self.assertEqual(
            c.schedule['M'],
            [schedule.CourseSchedule('0700-0759', 'room')]
        )

    def test_add_day_fails_on_conflicting_schedule_1(self):
        c = fast_course()

        self.assertTrue(c.add_day('L', '0700-0759', 'room'))
        self.assertFalse(c.add_day('L', '0730-0830', 'room'))

        self.assertEqual(len(c.schedule), 1)
        self.assertEqual(len(c.schedule['L']), 1)
        self.assertEqual(
            c.schedule['L'],
            [schedule.CourseSchedule('0700-0759', 'room')]
        )

    def test_add_day_fails_on_conflicting_schedule_2(self):
        c = fast_course()

        self.assertTrue(c.add_day('L', '0700-0959', 'room'))
        self.assertFalse(c.add_day('L', '0800-0859', 'room'))

        self.assertEqual(len(c.schedule), 1)
        self.assertEqual(len(c.schedule['L']), 1)
        self.assertEqual(
            c.schedule['L'],
            [schedule.CourseSchedule('0700-0959', 'room')]
        )

    def test_add_day_fails_on_conflicting_schedule_3(self):
        c = fast_course()

        self.assertTrue(c.add_day('L', '0800-0859', 'room'))
        self.assertFalse(c.add_day('L', '0730-0930', 'room'))

        self.assertEqual(len(c.schedule), 1)
        self.assertEqual(len(c.schedule['L']), 1)
        self.assertEqual(
            c.schedule['L'],
            [schedule.CourseSchedule('0800-0859', 'room')]
        )

class CourseTimeavailabilityTester(unittest.TestCase):
    def test_time_available_on_empty_schedule(self):
        c = fast_course()
        t = schedule.CourseSchedule('0700-0759', '...')

        for day in schedule.VALID_DAYS:
            self.assertTrue(c.time_available(day, [t]))

    def test_time_avaliale_on_available_time_1(self):
        c = fast_course()
        c.add_day('L', '0700-0759', '...')

        t = schedule.CourseSchedule('0800-0859', '...')
        self.assertTrue(c.time_available('L', [t]))

    def test_time_avaliale_on_available_time_2(self):
        c = fast_course()
        c.add_day('L', '1100-1359', '...')

        t = schedule.CourseSchedule('0700-1129', '...')
        self.assertFalse(c.time_available('L', [t]))

    def test_time_not_available(self):
        c = fast_course()
        c.add_day('L', '0700-0759', '...')

        t = schedule.CourseSchedule('0730-0829', '...')
        self.assertFalse(c.time_available('L', [t]))

    def test_time_available_with_longer_list(self):
        c = fast_course()
        c.add_day('M', '1100-1359', '...')

        t = [
            schedule.CourseSchedule('0730-0829', '...'),
            schedule.CourseSchedule('1430-1529', '...'),
        ]
        self.assertTrue(c.time_available('M', t))

    def test_time_not_available_with_longer_list(self):
        c = fast_course()
        c.add_day('M', '1100-1359', '...')

        t = [
            schedule.CourseSchedule('0730-1129', '...'),
            schedule.CourseSchedule('1430-1529', '...'),
        ]
        self.assertFalse(c.time_available('M', t))

if __name__ == '__main__':
    unittest.main()
