import argparse
import sys
import os
import numpy as np

#############################
##### Parsing arguments #####
#############################
parser = argparse.ArgumentParser(description='Process inputs for n2p2.')
parser._action_groups.pop()
parser.set_defaults(feature=True)
autsym = parser.add_argument_group('Generation of symmetry functions')

autsym.add_argument('--ele', dest='ele', type=str, nargs='*', required=True,
                    help='Chemical symbol of elements (e.g. H O)')
autsym.add_argument('--rcen', dest='rcen', type=int, nargs='?', required=False, default=0,
                    help='Radial function are centered to 0 or/and shifted (0 = Centered, 1 = Shifted, 2 = Both; default = 0).')
autsym.add_argument('--acen', dest='acen', type=int, nargs='?', required=False, default=0,
                    help='Angular function are centered to 0 or/and shifted (0 = Centered, 1 = Shifted, 2 = Both; default = 0).')
autsym.add_argument('--nrra', dest='nrra', type=int, nargs='?', required=False, default=0,
                    help='Number of radial symmetry function (default: 1.0 spacing between rbeg and rend)')
autsym.add_argument('--nang', dest='nang', type=int, nargs='?', required=False, default=2,
                    help='Number of angular symmetry function (1, 2 or 4; default: 2)')
autsym.add_argument('--rbeg', dest='rbeg', type=float, nargs='?', required=False, default=1.0, 
                    help='The beggining of radius grid for radial symmetry functions (default = 1.0)')
autsym.add_argument('--rend', dest='rend', type=float, nargs='?', required=False, default=6.0, 
                    help='The last point of grid for radial symmetry functions (default = 6.0)')
autsym.add_argument('--abeg', dest='abeg', type=float, nargs='?', required=False, default=0.0, 
                    help='The beggining of radius grid for angluar symmetry functions (default: same as radial)')
autsym.add_argument('--aend', dest='aend', type=float, nargs='?', required=False, default=0.0, 
                    help='The last point of grid for angular symmetry functions (default: same as angular)')
autsym.add_argument('--nraa', dest='nraa', type=int, nargs='?', required=False, default=0,
                    help='Number of angular symmetry function (default: same as nrra)')
autsym.add_argument('--rwid', dest='rwid', type=float, nargs='?', required=False, default=4.0,
                    help='Polynomial function radial width (rcut-rlow) for shifted radial functions (default = 4.0)')
autsym.add_argument('--rpol', dest='rpol', type=str, nargs='?', required=False, default="p2",
                    help='Compact function specifier for radial functions (default = p2)')
autsym.add_argument('--apol', dest='apol', type=str, nargs='?', required=False, default="p2",
                    help='Compact function specifier for angular functions (default = p2)')
args = parser.parse_args()

if args.rcen < 0 or args.rcen >2:
    raise Exception("rcen is defined only for 0, 1, and 2")

if args.acen < 0 or args.acen >2:
    raise Exception("acen is defined only for 0, 1, and 2")

if args.nrra < 2 and args.nrra != 0:
    raise Exception("nrra has to be larger than 2")

if args.nraa < 2 and args.nraa != 0:
    raise Exception("nraa has to be larger than 2")

if args.nang < 1 or args.nang > 4:
    raise Exception("nang is defined only for 1, 2, and 4")

if args.rend < args.rbeg:
    raise Exception("rend has to be larger than rbeg")

if args.aend < args.abeg:
    raise Exception("aend has to be larger than rend")

if args.rwid < 1.0:
    raise Exception("rwid has to be large than 1.0")

if type(args.ele) is list:
    ele = args.ele
else:
    ele = [args.ele]

if args.nrra == 0:
    nrra = int(args.rend - args.rbeg)+1
else:
    nrra = args.nrra

if args.nraa == 0:
    nraa = nrra
else:
    nraa = args.nraa

if args.abeg == 0.0:
    args.abeg = args.rbeg

if args.aend == 0.0:
    args.aend = args.rend

input = open("sym.nn","w")
grid_r = np.linspace(args.rbeg, args.rend, nrra)
grid_a = np.linspace(args.abeg, args.aend, nraa)
#args.rend = grid_r[-1]

#################################################
##### Symmetry function generation - radial #####
#################################################
for e in ele:
    input.write("\n# Radial symmetry functions for element %s\n" %e)
    input.write("#\t\t\t Element G_i\t Neigh.\t rlow\t rcutoff subtype\t\n")
    for e1 in ele:
        if args.rcen != 1:
            for grid in grid_r:
                input.write("symfunction_short\t %s\t %i\t %s\t %5.2f\t %5.2f\t %s\t\n" %(e, 20, e1, -grid, grid, args.rpol))
            input.write("\n")
        if args.rcen != 0: 
            for grid in grid_r:
                input.write("symfunction_short\t %s\t %i\t %s\t %5.2f\t %5.2f\t %s\t\n" %(e, 20, e1, grid-args.rwid, grid, args.rpol))
            input.write("\n")

#################################################
##### Symmetry function generation - angular ####
#################################################
for e in ele:
    input.write("# Angular symmetry functions for element %s\n" %e)
    input.write("#\t\t\t Element G_i\t Neigh1 Neigh2\t rlow\t rcutoff   left\t right\t subtype\t\n")
    for e1 in ele:
        ele_reduced = ele[ele.index(e1):]
        for e2 in ele_reduced:
            if args.acen != 1:
                for grid in grid_a:
                    input.write("symfunction_short\t %s\t %i\t %s\t %s\t %5.2f\t %5.2f\t %6.1f\t %6.1f\t %s\t\n" %(e, 21, e1, e2, -grid, grid, -180, 180, args.apol))
                    if args.nang > 1:
                        input.write("symfunction_short\t %s\t %i\t %s\t %s\t %5.2f\t %5.2f\t %6.1f\t %6.1f\t %s\t\n" %(e, 21, e1, e2, -grid, grid, 0, 180, args.apol))
                    if args.nang > 3:
                        input.write("symfunction_short\t %s\t %i\t %s\t %s\t %5.2f\t %5.2f\t %6.1f\t %6.1f\t %s\t\n" %(e, 21, e1, e2, -grid, grid, 0, 90, args.apol))
                        input.write("symfunction_short\t %s\t %i\t %s\t %s\t %5.2f\t %5.2f\t %6.1f\t %6.1f\t %s\t\n" %(e, 21, e1, e2, -grid, grid, 90, 180, args.apol))
            if args.acen != 0: 
                for grid in grid_a:
                    input.write("symfunction_short\t %s\t %i\t %s\t %s\t %5.2f\t %5.2f\t %6.1f\t %6.1f\t %s\t\n" %(e, 21, e1, e2, grid-args.rwid, grid, -180, 180, args.apol))
                    if args.nang > 1:
                        input.write("symfunction_short\t %s\t %i\t %s\t %s\t %5.2f\t %5.2f\t %6.1f\t %6.1f\t %s\t\n" %(e, 21, e1, e2, grid-args.rwid, grid, 0, 180, args.apol))
                    if args.nang > 3:
                        input.write("symfunction_short\t %s\t %i\t %s\t %s\t %5.2f\t %5.2f\t %6.1f\t %6.1f\t %s\t\n" %(e, 21, e1, e2, grid-args.rwid, grid, 0, 90, args.apol))
                        input.write("symfunction_short\t %s\t %i\t %s\t %s\t %5.2f\t %5.2f\t %6.1f\t %6.1f\t %s\t\n" %(e, 21, e1, e2, grid-args.rwid, grid, 90, 180, args.apol))
input.close()
