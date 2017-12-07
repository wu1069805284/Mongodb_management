#!/bin/sh
ps aux | grep -i worker | grep -iv grep | awk '{print $2}' | xargs  kill -9
