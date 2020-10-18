#!/bin/bash

if [ x$1 != x ]
then
s1=$1
s0="stap -v fnperf.stp 'process("
s2=")'  -o fptfnperf.log &"

echo $s0\"$s1\"$s2
eval  $s0\"$s1\"$s2
sleep 5
echo "Run your app..."
sleep 1	
date +%s_%N >fptperfprofiling.t1 &&  $*  &&date +%s_%N >fptperfprofiling.t2

sleep 3 
echo "stop systemtap..."
#using > /dev/null 2>&1 will redirect all your command output (both stdout and stderr ) to /dev/null 
ps -efww|grep -w 'stapio'|grep -v grep|cut -c 9-15|xargs kill -9 > /dev/null 2>&1
sleep 2

echo 'Result is saved in fptfnperf.log. now process Perf data in fptfnperf.log'

DIR=$(cd $(dirname $0) && pwd )
echo python $DIR\/tools/processPerfdata2kexue.py fptfnperf.log
eval python $DIR\/tools/processPerfdata2kexue.py fptfnperf.log

else
    #no args...
    echo "usesage: sh yourpath/perfProfiling.sh" "runyourapp"
    echo "note: use the absolute pathname or full path."
    echo "eg: sh /root/fpowertool/perfProfiling.sh" "/home/gwei/parsec-3.0/pkgs/apps/bodytrack/inst/amd64-linux.gcc/bin/bodytrack sequenceB_2 4 2 2000 5 0 1 "
fi
