#!/bin/sh

my_test() {
    FILENAME=$1
    EXPECTED=$2
    ./simp/minisat $FILENAME $ARGV > /dev/null
    RETURN=$?
    if [ $RETURN -ne $((EXPECTED)) ]; then
        echo "FAILED ON FILE:" $FILENAME
        echo "GOT:" $RETURN
        echo "EXPECTED:" $EXPECTED
        exit -1
    fi
}

if [ $2 = "SAT" ]; then
    my_test $1 10
elif [ $2 = "UNSAT" ]; then
    my_test $1 20
else
    echo "BAD USAGE"
    exit -1
fi

exit 0
