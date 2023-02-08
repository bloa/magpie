#!/bin/sh

# handle the two artificial parameters of minisat_advanced.params
for arg in "$@"; do
    shift
    case "$arg" in
        # if positive, then use -1 for the original parameter
        "-sub-lim-unbounded") shift ; set -- "$@" "-sub-lim" "-1" ;;
        "-cl-lim-unbounded") shift ; set -- "$@" "-cl-lim" "-1" ;;
        # if negative, delete
        "-no-sub-lim-unbounded") shift ;;
        "-no-cl-lim-unbounded") shift ;;
        # don't touch other parameters
        *)
    esac
done

./simp/minisat data/uf50-01.cnf $@
./simp/minisat data/uf50-02.cnf $@
./simp/minisat data/uf100-01.cnf $@
./simp/minisat data/uf100-02.cnf $@
./simp/minisat data/uf150-01.cnf $@
./simp/minisat data/uf150-02.cnf $@
./simp/minisat data/uf200-01.cnf $@
./simp/minisat data/uf200-02.cnf $@
./simp/minisat data/uf250-01.cnf $@
./simp/minisat data/uf250-02.cnf $@

./simp/minisat data/uuf50-01.cnf $@
./simp/minisat data/uuf50-02.cnf $@
./simp/minisat data/uuf100-01.cnf $@
./simp/minisat data/uuf100-02.cnf $@
./simp/minisat data/uuf150-01.cnf $@
./simp/minisat data/uuf150-02.cnf $@
./simp/minisat data/uuf200-01.cnf $@
./simp/minisat data/uuf200-02.cnf $@
./simp/minisat data/uuf250-01.cnf $@
./simp/minisat data/uuf250-02.cnf $@

exit 0
