#!/bin/bash
echo "timestamp,pod_name,cpu,memory" > ~/assignment4/results/m4_raw/cpu_memory_metrics.csv
while true; do
    timestamp=$(date +%s)
    kubectl top pods -n emi --no-headers | grep emi-web | while read line; do
        pod=$(echo $line | awk '{print $1}')
        cpu=$(echo $line | awk '{print $2}')
        mem=$(echo $line | awk '{print $3}')
        echo "$timestamp,$pod,$cpu,$mem" >> ~/assignment4/results/m4_raw/cpu_memory_metrics.csv
    done
    sleep 15
done
