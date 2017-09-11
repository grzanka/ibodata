import math

import numpy as np

from beprof.profile import Profile


class LateralProfile(Profile):
    def penumbra_right(self):
        """
        In case of good data returns floating-point number
        In case of corrupted data returns nan
        """
        return self.x_at_y(0.1, True) - self.x_at_y(0.9, True)

    def penumbra_left(self):
        """
        In case of good data returns floating-point number
        In case of corrupted data returns nan
        """
        return self.x_at_y(0.9) - self.x_at_y(0.1)

    def field_ratio(self, level):
        """
        In case of good data returns floating-point number
        Level has to be >= 0.0 and <= 1 or exception is raised
        In case of corrupted data returns nan
        """
        if level < 0.0 or level > 1.0:
            raise ValueError("Expected level to be between 0.0 and 1.0")
        return self.width(level) / self.width(0.5)

    def symmetry(self, level):
        """
        In case of good data returns floating-point number
        Level has to be >= 0 and <= 1 or exception is raised
        In case of corrupted data returns nan
        """
        if level < 0 or level > 1.0:
            raise ValueError("Expected level to be between 0 and 1")
        a = math.fabs(self.x_at_y(level, False))
        b = math.fabs(self.x_at_y(level, True))
        return (math.fabs(a - b) / (a + b)) * 200.0

    def flatness_50(self):
        """
        Returns floating-point number
        In case of corrupted data returns nan
        Returns value between points if max/min value occurs on border
        """
        d = (self.penumbra_left() + self.penumbra_right()) / 2
        if np.isnan(d):
            return np.nan
        left = self.x_at_y(0.5) + 2.0 * d
        right = self.x_at_y(0.5, True) - 2.0 * d

        p_max = np.max(np.append(self.y[np.logical_and(self.x <= right, self.x >= left)],
                                 [self.y_at_x(right), self.y_at_x(left)]))
        p_min = np.min(np.append(self.y[np.logical_and(self.x <= right, self.x >= left)],
                                 [self.y_at_x(right), self.y_at_x(left)]))

        return ((p_max - p_min) / (p_max + p_min)) * 100.0

    def flatness_90(self):
        """
        Returns floating-point number
        In case of corrupted data returns nan
        Returns value between points if max/min value occurs on border
        """
        d = (self.penumbra_left() + self.penumbra_right()) / 2
        if np.isnan(d):
            return np.nan
        left = self.x_at_y(0.9) + d
        right = self.x_at_y(0.9, True) - d

        p_max = np.max(
            np.append(self.y[np.logical_and(self.x <= right, self.x >= left)], [self.y_at_x(right), self.y_at_x(left)]))
        p_min = np.min(
            np.append(self.y[np.logical_and(self.x <= right, self.x >= left)], [self.y_at_x(right), self.y_at_x(left)]))

        return ((p_max - p_min) / (p_max + p_min)) * 100.0

    def asymmetry(self):
        """
        If everything is fine returns float
        In case of corrupted data returns nan
        Add area between mid and the nearest points if there's no 0 value in self.x
        area_left and area_right are DataSet and it propagates to result so it has to be converted to float
        """
        area_left = np.trapz(x=self.x[self.x <= 0], y=self.y[self.x <= 0])
        area_right = np.trapz(x=self.x[self.x >= 0], y=self.y[self.x >= 0])

        if np.argwhere(self.x == 0).size == 0:
            left_index_arr = np.argwhere(self.x < 0)
            area_left += np.trapz(x=np.append(self.x[left_index_arr[left_index_arr.size - 1]], [.0]),
                                  y=np.append(self.y[left_index_arr[left_index_arr.size - 1]], self.y_at_x(0)))

            right_index_arr = np.argwhere(self.x > 0)
            area_right += np.trapz(x=np.append([.0], self.x[right_index_arr[0]]),
                                   y=np.append(self.y_at_x(0), self.y[right_index_arr[0]]))

        result = ((area_left - area_right) / (area_left + area_right)) * 100.0

        return float(result)

    def normalize(self, dt, allow_cast=True):
        """
        Doesn't return anything
        In case of corrupted data raises ValueError
        Translate y to bring y.min() to 0 (noise substraction) and then
        normalize to 1 over [-dt, +dt] area from the mid of the profile
        if allow_cast is set to True, division not in place and casting may occur.
        If division in place is not possible and allow_cast is False
        an exception is raised.
        """
        try:
            self.y /= 1.0
        except TypeError:
            if not allow_cast:
                raise TypeError("Division in place is not possible and casting is not allowed")

        self.y -= self.y.min()

        a = self.y.max() / 2.0
        w = self.width(a)
        if np.isnan(w):
            raise ValueError("Part of profile is missing.")
        mid = self.x_at_y(a) + w / 2.0
        if allow_cast:
            self.x = self.x - mid
        else:
            self.x -= mid

        norm_section_y = self.y[np.fabs(self.x) <= dt]
        norm_section_x = self.x[np.fabs(self.x) <= dt]
        area = np.trapz(x=norm_section_x, y=norm_section_y)

        """
        if there's no point on the edge normalization is not perfectly accurate
        and we are normalizing over smaller area than [-dt, +dt]
        That's why we interpolate points on the edge below.
        """
        if np.argwhere(self.x == -dt).size == 0:
            coords_y = (self.y_at_x(-dt), norm_section_y[0])
            coords_x = (-dt, norm_section_x[0])
            area += np.trapz(x=coords_x, y=coords_y)

        if np.argwhere(self.x == dt).size == 0:
            coords_y = (norm_section_y[len(norm_section_y) - 1], self.y_at_x(dt))
            coords_x = (norm_section_x[len(norm_section_x) - 1], dt)
            area += np.trapz(x=coords_x, y=coords_y)

        ave = area / (2.0 * dt)

        if allow_cast:
            self.y = self.y / ave
        else:
            self.y /= ave
