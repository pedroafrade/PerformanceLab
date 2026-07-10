"""
PerformanceLab v1.0

metrics.py

Métricas para comparação entre sensores.
"""

import numpy as np


# ==========================================================
# Erro médio (Bias)
# ==========================================================

def bias(error):

    error = np.asarray(error)

    return np.mean(error)


# ==========================================================
# Mean Absolute Error
# ==========================================================

def mae(error):

    error = np.asarray(error)

    return np.mean(np.abs(error))


# ==========================================================
# Root Mean Square Error
# ==========================================================

def rmse(error):

    error = np.asarray(error)

    return np.sqrt(np.mean(error ** 2))


# ==========================================================
# Standard Deviation
# ==========================================================

def std(error):

    error = np.asarray(error)

    return np.std(error, ddof=1)


# ==========================================================
# Minimum
# ==========================================================

def minimum(error):

    error = np.asarray(error)

    return np.min(error)


# ==========================================================
# Maximum
# ==========================================================

def maximum(error):

    error = np.asarray(error)

    return np.max(error)


# ==========================================================
# Median
# ==========================================================

def median(error):

    error = np.asarray(error)

    return np.median(error)


# ==========================================================
# Percentil
# ==========================================================

def percentile(error, q):

    error = np.asarray(error)

    return np.percentile(error, q)


# ==========================================================
# Limits of Agreement (Bland-Altman)
# ==========================================================

def limits_of_agreement(error):

    b = bias(error)

    s = std(error)

    return (

        b - 1.96 * s,

        b + 1.96 * s

    )


# ==========================================================
# Mean Absolute Percentage Error
# ==========================================================

def mape(reference, target):

    reference = np.asarray(reference)

    target = np.asarray(target)

    mask = reference != 0

    reference = reference[mask]

    target = target[mask]

    return np.mean(

        np.abs(

            (reference - target)

            / reference

        )

    ) * 100


# ==========================================================
# Coefficient of Variation
# ==========================================================

def coefficient_of_variation(error):

    error = np.asarray(error)

    return (

        std(error)

        / np.mean(np.abs(error))

    ) * 100
