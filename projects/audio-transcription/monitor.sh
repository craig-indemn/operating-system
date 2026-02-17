#!/bin/bash
# Monitor memory usage for transcription workers
# Logs to monitor.log every 10 seconds

LOG="/Users/home/Repositories/operating-system/projects/audio-transcription/monitor.log"
INTERVAL=10

echo "timestamp,mem_pressure,workers,worker_rss_mb" > "$LOG"

while true; do
    ts=$(date '+%H:%M:%S')

    # Memory pressure (simple summary)
    pressure=$(memory_pressure 2>/dev/null | grep "System-wide memory free percentage" | awk '{print $NF}')

    # Per-process: find transcribe.py processes
    worker_count=$(ps aux | grep '[t]ranscribe.py' | wc -l | tr -d ' ')
    worker_rss=$(ps aux | grep '[t]ranscribe.py' | awk '{sum += $6} END {printf "%.0f", sum/1024}')
    worker_detail=$(ps aux | grep '[t]ranscribe.py' | awk '{printf "  PID %s: %.0fMB RSS\n", $2, $6/1024}')

    # Physical memory from sysctl
    total_bytes=$(sysctl -n hw.memsize)
    total_gb=$((total_bytes / 1073741824))

    echo "$ts,$pressure,$worker_count,$worker_rss" >> "$LOG"
    echo "$ts | RAM: ${total_gb}GB total, ${pressure} free | Workers: $worker_count (${worker_rss}MB total RSS)"
    if [ "$worker_count" -gt 0 ]; then
        echo "$worker_detail"
    fi

    sleep $INTERVAL
done
