"""FEAT-020 threaded order claim regression, offline and without Midtrans."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest

from photobooth.payment_orders import OrderStore


class ConcurrentOrderTests(unittest.TestCase):
    def test_exactly_one_claim_across_threads(self):
        with tempfile.TemporaryDirectory() as directory:
            store = OrderStore(Path(directory) / "orders.sqlite")
            try:
                order = store.create("PB001", {"template_a": 1}, 10000)
                store.attach_provider(order, order)
                self.assertTrue(store.confirm_provider_status(order, order, 10000, "settlement"))
                with ThreadPoolExecutor(max_workers=16) as pool:
                    outcomes = list(pool.map(lambda _: store.claim(order, "PB001"), range(64)))
                self.assertEqual(sum(outcomes), 1)
                self.assertTrue(store.status(order, "PB001")["claimed"])
            finally:
                store.close()

    def test_two_connections_cannot_double_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.sqlite"
            first, second = OrderStore(path), OrderStore(path)
            try:
                order = first.create("PB001", {"template_a": 1}, 10000)
                first.attach_provider(order, order)
                first.confirm_provider_status(order, order, 10000, "settlement")
                with ThreadPoolExecutor(max_workers=2) as pool:
                    outcomes = list(pool.map(lambda store: store.claim(order, "PB001"),
                                             (first, second)))
                self.assertEqual(sum(outcomes), 1)
            finally:
                first.close()
                second.close()


if __name__ == "__main__":
    unittest.main()
