#!/bin/sh

ARGV=$@

my_test() {
    FILENAME=$1
    EXPECTED=$2
    ./simp/minisat $FILENAME $ARGV > /dev/null
    RETURN=$?
    if [ $RETURN -ne $((EXPECTED)) ]
    then
        echo "FAILED ON FILE:" $FILENAME
        echo "GOT:" $RETURN
        echo "EXPECTED:" $EXPECTED
        exit -1
    fi
}

my_test data/uf50-01.cnf 10
my_test data/uf50-02.cnf 10
my_test data/uf100-01.cnf 10
my_test data/uf100-02.cnf 10
my_test data/uf150-01.cnf 10
my_test data/uf150-02.cnf 10

my_test data/uuf50-01.cnf 20
my_test data/uuf50-02.cnf 20
my_test data/uuf100-01.cnf 20
my_test data/uuf100-02.cnf 20
my_test data/uuf150-01.cnf 20
my_test data/uuf150-02.cnf 20
