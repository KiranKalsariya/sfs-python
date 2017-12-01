"""Compute the sound field generated by a sound source.

The Green's function describes the spatial sound propagation over time.

.. include:: math-definitions.rst

"""

from __future__ import division
import numpy as np
from .. import util
from .. import defs


def point(xs, signal, observation_time, grid, c=None):
    r"""Source model for a point source: 3D Green's function.

    Calculates the scalar sound pressure field for a given point in
    time, evoked by source excitation signal.

    Parameters
    ----------
    xs : (3,) array_like
        Position of source in cartesian coordinates.
    signal : (N,) array_like + float
        Excitation signal consisting of (mono) audio data and a sampling
        rate (in Hertz).  A `DelayedSignal` object can also be used.
    observation_time : float
        Observed point in time.
    grid : triple of array_like
        The grid that is used for the sound field calculations.
        See `sfs.util.xyz_grid()`.
    c : float, optional
        Speed of sound.

    Returns
    -------
    numpy.ndarray
        Scalar sound pressure field, evaluated at positions given by
        *grid*.

    Notes
    -----
    .. math::

        g(x-x_s,t) = \frac{1}{4 \pi |x - x_s|} \dirac{t - \frac{|x -
        x_s|}{c}}

    """
    xs = util.asarray_1d(xs)
    data, samplerate, signal_offset = util.as_delayed_signal(signal)
    data = util.asarray_1d(data)
    grid = util.as_xyz_components(grid)
    if c is None:
        c = defs.c
    r = np.linalg.norm(grid - xs)
    # evaluate g over grid
    weights = 1 / (4 * np.pi * r)
    delays = r / c
    base_time = observation_time - signal_offset
    return weights * np.interp(base_time - delays,
                               np.arange(len(data)) / samplerate,
                               data, left=0, right=0)


def point_image_sources(x0, signal, observation_time, grid, L, max_order,
                        coeffs=None, c=None):
    """Point source in a rectangular room using the mirror image source model.

    Parameters
    ----------
    x0 : (3,) array_like
        Position of source in cartesian coordinates.
    signal : (N,) array_like + float
        Excitation signal consisting of (mono) audio data and a sampling
        rate (in Hertz).  A `DelayedSignal` object can also be used.
    observation_time : float
        Observed point in time.
    grid : triple of array_like
        The grid that is used for the sound field calculations.
        See `sfs.util.xyz_grid()`.
    L : (3,) array_like
        Dimensions of the rectangular room.
    max_order : int
        Maximum number of reflections for each image source.
    coeffs : (6,) array_like, optional
        Reflection coeffecients of the walls.
        If not given, the reflection coefficients are set to one.
    c : float, optional
        Speed of sound.

    Returns
    -------
    numpy.ndarray
        Scalar sound pressure field, evaluated at positions given by
        *grid*.

    """
    if coeffs is None:
        coeffs = np.ones(6)

    positions, order = util.image_sources_for_box(x0, L, max_order)
    source_strengths = np.prod(coeffs**order, axis=1)

    p = 0
    for position, strength in zip(positions, source_strengths):
        if strength != 0:
            p += strength * point(position, signal, observation_time, grid, c)

    return p
