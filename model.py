import numpy as np
import pandas as pd


class DynamicalSystem(object):
    def __init__(self, a, b, c, r_ww, r_vv, x_ini=None):
        """

        :param a:
        :param b:
        :param c:
        :param r_ww:
        :param r_vv:
        :param x_ini:
        """
        self.a = a
        self.b = b
        self.c = c
        self.r_ww = r_ww
        self.r_vv = r_vv
        self.w = None
        self.v = None
        self.x_t = np.zeros((self.a.shape[0], 1)) if x_ini is None else x_ini
        self.x_t1 = None
        self.u_t = np.zeros((self.b.shape[1], 1))
        self.t = 0
        self.y_t = None
        self.history = []

    @staticmethod
    def expand_cols(name, vec):
        """

        :param name:
        :param vec:
        :return:
        """
        vec = vec.ravel()
        n = int(vec.shape[0])
        names = [f"{name}.{i+1}" for i in range(n)]
        d = dict(zip(names, vec))
        return d

    def update_history(self):
        """

        :return:
        """
        self.t += 1
        state = {'t': self.t}
        state.update(self.expand_cols('x_t', self.x_t))
        state.update(self.expand_cols('u_t', self.u_t))
        state.update(self.expand_cols('w_t', self.w))
        state.update(self.expand_cols('y_t', self.y_t))
        state.update(self.expand_cols('v_t', self.v))
        self.history.append(state)

    @staticmethod
    def _sample_noise(cov, n):
        """

        :param cov:
        :param n:
        :return:
        """
        return np.random.multivariate_normal(np.zeros(cov.shape[0]), cov, n).T

    @staticmethod
    def _x_step(a, b, w, x_t1, u):
        """

        :param a:
        :param b:
        :param w:
        :param x_t1:
        :param u:
        :return:
        """
        return np.dot(a, x_t1) + np.dot(b, u) + w

    def x_step(self, u=None):
        """

        :param u:
        :return:
        """
        self.u_t = u if u is not None else self.u_t
        self.w = self._sample_noise(self.r_ww, 1)
        self.x_t1 = self.x_t
        self.x_t = self._x_step(self.a, self.b, self.w, self.x_t1, self.u_t)
        return self.x_t

    @staticmethod
    def _y_step(x_t, c, v):
        """

        :param x_t:
        :param c:
        :param v:
        :return:
        """
        return np.dot(c, x_t) + v

    def y_step(self, u=None):
        """

        :param u:
        :return:
        """
        x_t = self.x_step(u=u)
        self.v = self._sample_noise(self.r_vv, 1)
        self.y_t = self._y_step(x_t, self.c, self.v)
        self.update_history()
        return self.y_t

    def y_steps(self, n_steps, u=None):
        """

        :param n_steps:
        :param u:
        :return:
        """
        _ = [self.y_step(u=u) for _ in range(n_steps)]

    def get_history(self):
        """

        :return:
        """
        return pd.DataFrame(self.history)


if __name__ == '__main__':
    _dim_x = 1
    _dim_y = 1
    _dim_u = 1

    _r_ww = np.diag([0.01]*_dim_x)
    _r_vv = np.diag([0.001]*_dim_y)

    _a = 0.97 * np.identity(_dim_x)
    _b = 100 * np.ones((_dim_x, _dim_u))
    _c = 2 * np.ones((_dim_y, _dim_x))

    _u = 300 * 1e-6 * np.ones((_dim_u, 1))
    _xini = 2.5*np.ones((_dim_x, 1))

    ds = DynamicalSystem(_a, _b, _c, _r_ww, _r_vv, x_ini=_xini)
    ds.y_steps(u=_u, n_steps=100)

    df_hist = ds.get_history()
    print()

