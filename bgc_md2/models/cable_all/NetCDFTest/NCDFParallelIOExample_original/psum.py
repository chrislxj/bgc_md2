import sys
from mpi4py import MPI
import numpy as np
from netCDF4 import Dataset


def psum(a):
    locsum = np.sum(a)
    rcvBuf = np.array(0.0, "d")
    MPI.COMM_WORLD.Allreduce([locsum, MPI.DOUBLE], [rcvBuf, MPI.DOUBLE], op=MPI.SUM)
    return rcvBuf
