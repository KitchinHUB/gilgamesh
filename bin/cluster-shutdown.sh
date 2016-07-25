#!/bin/bash

for i in $(bpstat -n allup ) ; do echo $i; bpctl -S $i -P ; sleep 2s; done

#end