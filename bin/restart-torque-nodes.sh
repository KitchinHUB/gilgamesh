#!/bin/bash
# Run as root
for i in $(seq 0 30); do 
    echo $i;
    NODE=$i /etc/beowulf/init.d/90torque stop
    sleep 2s
done

#end
