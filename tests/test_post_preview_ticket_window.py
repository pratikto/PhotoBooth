"""30 actually visible seconds, one NEXT/timeout transition, no restart."""
import unittest
import math

from photobooth.post_preview_ticket_window import VisibleTicketWindow


class VisibleTicketWindowTests(unittest.TestCase):
    def test_unrepresentable_deadline_never_starts_visible_window(self):
        for value in (1e308, -1e308, float('inf'), float('nan')):
            window = VisibleTicketWindow(monotonic=lambda: value)
            with self.assertRaises(ValueError):
                window.start(genuine_visible=True)
            self.assertFalse(window.active)

    def test_exact_absolute_deadline_across_float_precision_boundary(self):
        origin = math.nextafter(127., math.inf)
        tick = [origin]
        window = VisibleTicketWindow(monotonic=lambda: tick[0])
        window.start(genuine_visible=True)
        deadline = origin+30.
        tick[0] = math.nextafter(deadline, -math.inf)
        self.assertEqual(1, window.remaining())
        self.assertFalse(window.dismiss())
        tick[0] = deadline
        self.assertEqual(0, window.remaining())
        self.assertTrue(window.dismiss())

    def setUp(self):
        self.tick=[100.]
        self.window=VisibleTicketWindow(monotonic=lambda:self.tick[0])

    def test_not_started_until_genuine_visible_ack(self):
        self.assertIsNone(self.window.remaining())
        self.assertFalse(self.window.dismiss(next_pressed=True))
        with self.assertRaises(ValueError):
            self.window.start(genuine_visible=False)
        self.assertFalse(self.window.active)
        self.assertTrue(self.window.start(genuine_visible=True))
        self.assertEqual(30,self.window.remaining())
        self.assertFalse(self.window.start(genuine_visible=True))

    def test_true_30s_clock_and_timeout_once(self):
        self.window.start(genuine_visible=True)
        self.tick[0]=129.01
        self.assertEqual(1,self.window.remaining())
        self.assertFalse(self.window.dismiss())
        self.tick[0]=130.
        self.assertEqual(0,self.window.remaining())
        self.assertTrue(self.window.dismiss())
        self.assertFalse(self.window.dismiss())
        self.assertFalse(self.window.start(genuine_visible=True))

    def test_next_early_and_retire_do_not_reopen(self):
        self.window.start(genuine_visible=True)
        self.tick[0]=100.1
        self.assertTrue(self.window.dismiss(next_pressed=True))
        self.assertEqual(0,self.window.remaining())
        self.assertFalse(self.window.dismiss(next_pressed=True))
        other=VisibleTicketWindow(monotonic=lambda:self.tick[0])
        self.assertTrue(other.start(genuine_visible=True))
        other.retire()
        self.assertFalse(other.dismiss(next_pressed=True))
        self.assertFalse(other.start(genuine_visible=True))

    def test_provider_poll_and_printer_callback_have_no_timer_reset(self):
        self.window.start(genuine_visible=True)
        self.tick[0]=108.5
        self.assertEqual(22,self.window.remaining())
        # Repeated rendered callbacks attempt to start again; MUST be ignored.
        for _ in range(20):self.assertFalse(self.window.start(genuine_visible=True))
        self.assertEqual(22,self.window.remaining())


if __name__=='__main__': unittest.main()
