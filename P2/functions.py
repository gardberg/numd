import numpy as np
from scipy import exp, sparse,sin,cos ,pi
from scipy.sparse.linalg import spsolve
from scipy.linalg import norm, eigh_tridiagonal
import matplotlib.pyplot as plt


def twopBVP(fvec, alpha, beta, L, N):
    # Two point boundry value problem solver.
    # fvec is a vector of the function values f from y´´ = f(x)
    # in the N points from 0 to L.

    dx = L/(N+1)

    subp = np.ones(N-1)
    mid = np.ones(N) * (-2)

    diagonals = [subp, mid, subp]

    T = sparse.diags(diagonals, [-1, 0, 1])

    # Create array for rhs of equation
    b = np.zeros(N)
    b[0] = -alpha/(dx*dx)
    b[-1] = -beta/(dx*dx)

    b = dx * dx * np.add(b, fvec)

    y = spsolve(T.tocsc(), b)

    # Append boundary values
    y = np.insert(y, 0, alpha)
    y = np.append(y, beta)

    return y


def test_f(x):
    # apply the function f to the array x
    # x assumed to be column np array [[a], [b]...]

    return exp(-x)


def test_fsin(x):
    # apply function fsin to array x
    # x assumed to be column np array
    return sin(x)


def exact_sin(x, alpha ,beta ,L):
    return alpha -sin(x) + x*(beta + sin(L)-alpha)/L


def exact_f(x, alpha, beta, L):
    return exp(-x) + alpha - 1 + (x/L) * (beta - alpha + 1 - exp(-L))


def vshBvp(alpha, beta, length, N):
    errors = np.array([])
    step_sizes = np.array([])

    for k in N:
        step_size = length / (k + 1)
        x = np.linspace(step_size, length - step_size, k)
        fvec = test_f(x)

        y = twopBVP(fvec, alpha, beta, length, k)

        x = np.insert(x, 0, 0)
        x = np.append(x, length)

        y_exact = exact_f(x, alpha, beta, length)

        err = norm(y-y_exact) / np.sqrt(k + 1)

        errors = np.append(errors, err)
        step_sizes = np.append(step_sizes, step_size)

    plt.loglog(step_sizes, errors)
    plt.grid()
    plt.show()
    
    
def func_q(x):
    #returns 1d array with -50kN
    return -5*10**4 * np.ones(len(x))


def func_I(x,L):
     return (3-2*np.power(cos(x*pi/L),12))* 10**-3
    

def beamSolve(fvec, L, N):
    # Solves the beam equation for given q, M, E and I

    # Bounry values:
    m0 = 0
    m1 = 0
    u0 = 0
    u1 = 0
    E = 1.9*10**11

    # Find M from M'' = q
    m = twopBVP(fvec,m0,m1,L,N)

    # Remove endpoints in order to use the solver in the next step
    m = np.delete(m,0)
    m = np.delete(m,-1)


    points = np.linspace(L/(N+1), L - L/(N+1), N)
    i_func = func_I(points, L)

    # Function values for u'' = M/IE
    fvec = np.divide(m,i_func*E)

    # Use solver to get solution for u
    u = twopBVP(fvec, u0, u1, L, N)
    return u


def sv_solver(alpha, beta, L, N):
    # Input: values of
    # N: Number of internal points

    # Returns: Eigenvalues and eigenfunctions for the operator

    dx = L / (N + 1)

    subp = (1/(dx * dx)) * np.ones(N - 1)
    mid = (1/(dx * dx)) * np.ones(N) * (-2)

    eigs, eig_vecs = eigh_tridiagonal(mid, subp)

    # Add boundry values to solutions
    left_bvs = np.ones(N) * alpha
    right_bvs = np.ones(N) * beta

    eig_vecs = np.vstack((left_bvs, eig_vecs))
    eig_vecs = np.vstack((eig_vecs, right_bvs))

    return eigs, eig_vecs


def sturm_lv_vis():
    # Plots error vs N for three first eigenvalues
    L = 1
    K = np.arange(2, 12)
    K = 2**K
    err = np.zeros((len(K), 3))

    n = 0
    # For each number of points, calculate the eigenvalues
    for N in K:
        eigs, _ = sv_solver(0, 0, L, N)

        eigs = np.flip(eigs[-3:])

        # Find the error for each eigenvalue
        for i in range(3):
            
            err[n, i] = norm(eigs[i] + ((i + 1) * pi)**2)
            
        n = n + 1

    for i in range(3):
        plt.figure(i)
        plt.loglog(K, err[:, i])
        plt.show()

    plt.figure(4)
    N = 499

    eigs, eigvecs = sv_solver(0,0,L,N)
    eigs = eigs[-3:]
    eigvecs = eigvecs[:, -3:]
    x = np.linspace(0, L, N+2)
    plt.plot(x, np.flip(eigvecs[:, 1]))

    print(eigs)

    plt.show()