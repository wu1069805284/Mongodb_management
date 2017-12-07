#!/bin/bash
## Note:Stop mongo Instance

source /etc/profile
export LANG=en_US.UTF-8

function  usage()
{
    echo "usage: sh $0 -P port" 
}

if [[ "$#" -eq 0 ]]  
then
    usage
    exit 1
fi

while getopts P:h: OPTION
do
    case "$OPTION" in
        P)port=$OPTARG
            ;;
        h)
            usage
            exit 0
            ;;
        *)
            usage      
            exit 1
            ;;
    esac
done

MONGOD_BIN="/opt/soft/mongodb3210/bin/mongod"
CONF="/work/mongodb${port}/etc/mongodb${port}.conf"
if [ -d $MONGOD_BIN ]
then
    ${MONGOD_BIN} --config ${CONF} --shutdown
else
    echo "Can't find Mongo Server Directory,Do nothing and Exit!"
    exit 1
fi

exit 0
