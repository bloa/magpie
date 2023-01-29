#!/bin/sh

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
