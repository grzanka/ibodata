import numpy as np

from beprof.profile import Profile


class DepthProfile(Profile):

    def ran(self, level=0.9):
        return self.x_at_y(level, True)

    def max_plat_ratio(self):
        return self.y.max() / self.y[0]

    def distal_falloff(self):
        return self.x_at_y(0.1, True) - self.x_at_y(0.9, True)

    def modulation(self, level):
        """
        if there's not y equal level from left x_at_y() returns NaN.
        In that case instead of taking x_at_y(level), this function takes first x
        """
        if np.isnan(self.x_at_y(level)):
            return self.x_at_y(level, True) - self.x[0]
        else:
            return self.x_at_y(level, True) - self.x_at_y(level)

    def normalize(self, allow_cast=True):
        """
        Scale and translate y to be in range(0,1)
        Normalize before calling other methods
        """
        self.y -= self.y.min()

        if allow_cast:
            self.y = self.y / self.y.max()
        else:
            self.y /= self.y.max()
