"""FEAT-021: isolated, offline Meong Fly prototype. No checkout or receipt access."""
from dataclasses import dataclass
import random

WIDTH, HEIGHT = 480, 640
CAT_X = 110
CAT_RADIUS = 15
GRAVITY = 820.0
FLAP_VELOCITY = -285.0
PIPE_SPEED = 165.0
# Asteroids use the same top/bottom gap collision geometry as Flappy Bird.
PIPE_WIDTH = 65
GAP_HEIGHT = 195
ROUND_SECONDS = 25.0
TARGET_SCORE = 6


@dataclass
class AsteroidGap:
    x: float
    gap_y: float
    scored: bool = False


Pipe = AsteroidGap  # Backward-compatible name for earlier prototype tests.


class MeongFly:
    """Deterministic frame-step simulation with injected random generator."""

    def __init__(self, rng=None):
        self.rng = rng if rng is not None else random.Random()
        self.reset()

    def reset(self):
        self.y = HEIGHT / 2
        self.velocity = 0.0
        self.elapsed = 0.0
        self.spawn_elapsed = 0.0
        self.score = 0
        self.pipes = []
        self.status = "ready"

    def start(self):
        if self.status == "ready":
            self.status = "playing"
            self.flap()

    def flap(self):
        if self.status == "playing":
            self.velocity = FLAP_VELOCITY

    def step(self, dt):
        if self.status != "playing":
            return
        # Clamp large frame gaps to prevent unbounded simulation jumps.
        dt = min(max(float(dt), 0.0), 0.05)
        self.elapsed += dt
        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt
        if self.y - CAT_RADIUS <= 0 or self.y + CAT_RADIUS >= HEIGHT:
            self.status = "lost"
            return
        self.spawn_elapsed += dt
        if self.spawn_elapsed >= 1.6:
            self.spawn_elapsed -= 1.6
            self.pipes.append(AsteroidGap(WIDTH + 10, self.rng.uniform(155, HEIGHT - 155)))
        for pipe in self.pipes:
            pipe.x -= PIPE_SPEED * dt
            if (CAT_X + CAT_RADIUS > pipe.x and
                    CAT_X - CAT_RADIUS < pipe.x + PIPE_WIDTH and
                    (self.y - CAT_RADIUS < pipe.gap_y - GAP_HEIGHT / 2 or
                     self.y + CAT_RADIUS > pipe.gap_y + GAP_HEIGHT / 2)):
                self.status = "lost"
                return
            if not pipe.scored and pipe.x + PIPE_WIDTH < CAT_X - CAT_RADIUS:
                pipe.scored = True
                self.score += 1
                if self.score >= TARGET_SCORE:
                    self.status = "won"
                    return
        self.pipes = [p for p in self.pipes if p.x + PIPE_WIDTH >= 0]
        if self.elapsed >= ROUND_SECONDS:
            self.status = "lost"
