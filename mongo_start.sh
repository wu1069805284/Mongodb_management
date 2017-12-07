#!/bin/bash
## Note:Start mongo Instance

source /etc/profile
export LANG=en_US.UTF-8

function  usage()
{
        echo "usage: sh $0 -P port" 
}

if [[ "$#" -ne 2 ]]  
then
     usage
     exit 1
fi

while getopts P:h: OPTION
do
    case "$OPTION" in
        P)port=$OPTARG
            ;;
        h)usage
            exit 0
            ;;
        *)usage      
            exit 1
            ;;
    esac
done

MONGOD_BIN="/opt/soft/mongodb3210/bin/mongod"
CONF="/work/mongodb${port}/etc/mongodb${port}.conf"
portExists=`netstat -an | grep LISTEN | grep tcp | grep $port | wc -l`

if [ $portExists -eq 1 ]
then
    echo "Port $port is already exists!"
    exit 1
fi
if [ ! -d $MONGOD_BIN ]
then 
    echo "Can't find Mongo Server Directory!"
    exit 1
else
    ${MONGOD_BIN} --config ${CONF}
    echo "Start mongodb,waiting~~~~"
fi


exit 0
