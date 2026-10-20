"""Offline simulation tests; no camera, payment, Kivy or hardware required."""
import random
import unittest
from photobooth.meong_fly import MeongFly, Pipe, CAT_X, CAT_LEFT, CAT_RIGHT, CAT_BOTTOM, CAT_TOP, PIPE_WIDTH, TARGET_SCORE, HEIGHT


class MeongFlyTests(unittest.TestCase):
    def test_starts_only_on_input(self):
        game = MeongFly(random.Random(1))
        game.step(0.02)
        self.assertEqual(game.status, "ready")
        game.start()
        self.assertEqual(game.status, "playing")
        self.assertLess(game.velocity, 0)

    def test_ground_collision(self):
        game = MeongFly()
        game.start()
        game.y = 1
        game.step(.02)
        self.assertEqual(game.status, "lost")

    def test_pipe_collision(self):
        game = MeongFly()
        game.start()
        game.pipes = [Pipe(CAT_X, 500)]
        game.step(.01)
        self.assertEqual(game.status, "lost")

    def test_score_once_and_win(self):
        game = MeongFly()
        game.start()
        game.pipes = [Pipe(CAT_X - PIPE_WIDTH - 25, 300)]
        game.step(.01)
        self.assertEqual(game.score, 1)
        game.step(.01)
        self.assertEqual(game.score, 1)
        game.score = TARGET_SCORE - 1
        game.pipes = [Pipe(CAT_X - PIPE_WIDTH - 25, 300)]
        game.step(.01)
        self.assertEqual(game.status, "won")

    def test_visible_sprite_edge_collision(self):
        game = MeongFly()
        game.start()
        game.y = 300
        game.pipes = [Pipe(CAT_X + CAT_RIGHT - 1, 500)]
        game.step(.01)
        self.assertEqual(game.status, "lost")

    def test_visible_sprite_bounds(self):
        for start_y in (CAT_BOTTOM - 1, HEIGHT - CAT_TOP + 5):
            with self.subTest(start_y=start_y):
                game = MeongFly()
                game.start()
                game.y = start_y
                game.step(.01)
                self.assertEqual(game.status, "lost")

    def test_score_only_after_entire_sprite_passes(self):
        game = MeongFly()
        game.start()
        game.y = 300
        game.pipes = [Pipe(CAT_X - CAT_LEFT - PIPE_WIDTH + 5, 300)]
        game.step(.01)
        self.assertEqual(game.score, 0)
        game.pipes[0].x = CAT_X - CAT_LEFT - PIPE_WIDTH - 1
        game.step(.01)
        self.assertEqual(game.score, 1)

    def test_reset(self):
        game = MeongFly()
        game.start()
        game.status = "lost"
        game.reset()
        self.assertEqual((game.score, game.status), (0, "ready"))


if __name__ == "__main__":
    unittest.main()
