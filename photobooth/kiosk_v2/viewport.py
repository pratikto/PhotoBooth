"""Live viewport scaling confined to GUI v2; no global Kivy density changes."""

from kivy.graphics.transformation import Matrix
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter


class PortraitViewport(FloatLayout):
    """Keep the page's minimum content budget while fitting any window size.

    At the original portrait QA sizes the layout is unchanged. Short/narrow
    windows scale the entire native widget tree, including fonts, spacing,
    video and touch coordinates. Extra width/height still flows into layouts;
    no letterbox, page rebuild, media restart or cart reset is needed on resize.
    """

    viewport_scale = NumericProperty(1)

    def __init__(self, content, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.surface = Scatter(size_hint=(None, None),
                               do_translation=False, do_rotation=False,
                               do_scale=False, auto_bring_to_front=False)
        content.size_hint = (None, None)
        self.surface.add_widget(content)
        self.add_widget(self.surface)
        self.bind(size=self._fit, pos=self._fit)
        self._fit()

    def _fit(self, *_args):
        width, height = max(1, self.width), max(1, self.height)
        scale = min(1, width / dp(452), height / dp(900))
        self.viewport_scale = scale
        self.surface.size = self.content.size = (width / scale, height / scale)
        self.content.pos = (0, 0)
        self.surface.transform = Matrix().translate(self.x, self.y, 0).scale(scale, scale, 1)
