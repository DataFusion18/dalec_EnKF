#!/usr/bin/env python
"""
DALEC ensemble Kalman filter (EnKF) ...

Reference:
---------
* Williams et al. (2005) An improved analysis of forest carbon dynamics using
  data assimilation. Global Change Biology 11, 89–105.
* Evensen (2003) The Ensemble Kalman Filter: theoretical formulation and
  practical implementation. Ocean Dynamics, 53, 343-367

"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

__author__  = "Martin De Kauwe"
__version__ = "1.0 (07.03.2018)"
__email__   = "mdekauwe@gmail.com"

import numpy as np
import sys

def main(fname):

    met = pd.read_csv(fname)

    # initialise structures
    mp = GenericClass()
    p = GenericClass()
    c = GenericClass()

    setup_initial_conditions(mp, p, c)

    # Setup matrix holding ensemble members (A)
    A = np.zeros((c.ndims, c.nrens))

    # Setup ensemble covariance matrix of the errors (Q)
    Q = np.zeros((c.ndims, c.nrens))

    # model errors
    p_k = np.zeros(c.ndims)

    # Initialise the ensemble (A)
    A = initialise_ensemble(mp, c, A)

    # Initial error covariance matrix Q matrix
    Q = initialise_error_covariance(c, Q)

    rho = setup_stochastic_model_error()

class GenericClass:
    pass

def setup_initial_conditions(mp, p, c):

    # dalec model values
    mp.t1 = 4.41E-06
    mp.t2 = 0.473267
    mp.t3 = 0.314951
    mp.t4 = 0.434401
    mp.t5 = 0.00266518
    mp.t6 = 2.06E-06
    mp.t7 = 2.48E-03
    mp.t8 = 2.28E-02
    mp.t9 = 2.65E-06
    mp.cf0 = 57.7049
    mp.cw0 = 769.863
    mp.cr0 = 101.955
    mp.cl0 = 40.4494
    mp.cs0 = 9896.7

    # acm parameterisation
    p.a0 = 2.155;
    p.a1 = 0.0142;
    p.a2 = 217.9;
    p.a3 = 0.980;
    p.a4 = 0.155;
    p.a5 = 2.653;
    p.a6 = 4.309;
    p.a7 = 0.060;
    p.a8 = 1.062;
    p.a9 = 0.0006;

    # location - oregon
    p.lat = 44.4;

    c.nrobs = 0
    c.sla = 111.
    c.ndims = 16
    c.nrens = 200
    c.max_params = 15
    c.seed = 0

    c.POS_RA = 0
    c.POS_AF = 1
    c.POS_AW = 2
    c.POS_AR = 3
    c.POS_LF = 4
    c.POS_LW = 5
    c.POS_LR = 6
    c.POS_CF = 7
    c.POS_CW = 8
    c.POS_CR = 9
    c.POS_RH1 = 10
    c.POS_RH2 = 11
    c.POS_D = 12
    c.POS_CL = 13
    c.POS_CS = 14
    c.POS_GPP = 15

def initialise_ensemble(mp, c, A):

    for j in range(c.nrens):
        A[c.POS_RA, j] = 1.0 * np.random.normal(0.0, 0.1 * 1.0)
        A[c.POS_AF, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_AW, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_AR, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_LF, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_LW, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_LR, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_RH1, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_RH2, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_D, j] = 0.3 * np.random.normal(0.0, 0.1 * 0.3)
        A[c.POS_GPP, j] = 1.0 * np.random.normal(0.0, 0.1 * 1.0)
        A[c.POS_CF, j] = mp.cf0 * np.random.normal(0.0, 0.1 * mp.cf0)
        A[c.POS_CW, j] = mp.cw0 * np.random.normal(0.0, 0.1 * mp.cw0)
        A[c.POS_CR, j] = mp.cr0 * np.random.normal(0.0, 0.1 * mp.cr0)
        A[c.POS_CL, j] = mp.cl0 * np.random.normal(0.0, 0.1 * mp.cl0)
        A[c.POS_CS, j] = mp.cs0 * np.random.normal(0.0, 0.1 * mp.cs0)

    return A

def initialise_error_covariance(c, Q):

    for i in range(c.ndims):
        for j in range(c.nrens):
            Q[i,j] = np.random.normal(0.0, 1.0)

    return Q

def setup_stochastic_model_error():
    """
    Set up stochastic model error according to eqn 42 - Evenson, 2003. This
    ensures that the variance growth over time becomes independent of alpha and
    delta_t (as long as the dynamical model is linear).
    """
    # timestep
    delta_t = 1.0

    # specified time decorrelation length s.
    tau = 1.0

    # The factor a should be related to the time step used, eqn 32
    # (i.e. this is zero)
    alpha = 1.0 - (delta_t / tau)

    # number of timesteps per time unit
    n = 1.0

    num = (1.0 - alpha)**2
    den = n - 2.0 * alpha * n * alpha**2 + (2.0 * alpha)**(n + 1.0)
    rho = np.sqrt(1.0 / delta_t * num / den)

    return rho

if __name__ == "__main__":

    fname = "data/dalec_drivers.OREGON.no_obs.csv"
    main(fname)
