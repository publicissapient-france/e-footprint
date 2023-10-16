import unittest
from footprint_model.constants.units import u
from pytz import UnknownTimeZoneError
from footprint_model.core.usage.time_intervals import TimeIntervals


class TestTimeIntervals(unittest.TestCase):
    def setUp(self):
        self.name = "test_intervals"
        self.time_intervals = [[0, 5], [6, 10], [15, 20]]
        self.timezone = "Asia/Tokyo"
        self.intervals_obj = TimeIntervals(self.name, self.time_intervals, self.timezone)

    def test_check_time_intervals_validity(self):
        self.intervals_obj.check_time_intervals_validity(self.time_intervals)

    def test_invalid_start_time(self):
        with self.assertRaises(ValueError):
            self.intervals_obj.check_time_intervals_validity([[5, 3], [7, 10]])

    def test_interval_overlap(self):
        with self.assertRaises(ValueError):
            self.intervals_obj.check_time_intervals_validity([[0, 5], [4, 10]])

    def test_init(self):
        # Invalid timezone should raise error
        with self.assertRaises(UnknownTimeZoneError):
            TimeIntervals(self.name, self.time_intervals, "Nonexistent/Timezone")

    def test_pubsub_topics_to_listen_to(self):
        self.assertEqual(self.intervals_obj.pubsub_topics_to_listen_to, [self.intervals_obj.utc_time_intervals])

    def test_update_hourly_usage(self):
        self.intervals_obj.update_hourly_usage()

        for i in range(24):
            if 0 <= i < 5 or 6 <= i < 10 or 15 <= i < 20:
                self.assertEqual(self.intervals_obj.hourly_usage.value[i].value, 1 * u.dimensionless)
            else:
                self.assertEqual(self.intervals_obj.hourly_usage.value[i].value, 0 * u.dimensionless)


if __name__ == '__main__':
    unittest.main()

