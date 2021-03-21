#!/bin/bash
work_path=$(dirname $0)

cat ${work_path}/../log/sentiment_pid.txt | while read line
do
    echo $line
    kill $line
done

source ~/venv/bin/activate

nohup python ${work_path}/../server/sentiment/sentiment_server.py > ${work_path}/../log/sentiment.log 2>&1 &
echo $! > ${work_path}/../log/sentiment_pid.txt

deactivate