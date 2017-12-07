#!/bin/bash
## Note:Create a new mongod node
##
## Created by jihaodong@58ganji.com
## 2017/05/19[Init]
##
## Change log
##
source /etc/profile
export LANG=en_US.UTF-8


function usage()
{                                                                                                                                
        echo "Usage: sh $0 -p port -m CacheSize -o OplogSize -v mongoVersion"
        echo "-p [Port] default: 27017"
        echo "-m [CacheSize] default: 8"
        echo "-o [oplogSize] default: 10240"
        echo "-v [version]   default: 32 (26,32)"
}
                                                                                                                                
if [[ "$#" -eq 0 ]]
then
        usage
        exit 1                                                                                                                 
fi

while getopts p:m:o:v:h OPTION
do
        case "$OPTION" in
                p)port=$OPTARG
                ;;
                m)mem=$OPTARG
                ;;
                o)oplog=$OPTARG
                ;;
                v)version=$OPTARG
                ;;
                h)usage
                exit 0
                ;;
                *)
                usage
                exit 1
                ;;
        esac
done

chkPort=$(echo $port | sed "s/[0-9]//g")"OK"
if [ -z "$port" ]
then
        usage
        echo "You must specify a port!"
        exit 1

elif [ "$chkPort" == "OK" ]
then
        if [ $port -lt 7000 ] || [ $port -gt 60000 ]
        then
                echo "Mongo Port must be between 7000 and 8000!"
                exit 1
        fi
else
        echo "Mongo Port must be a number!"
        exit 1

fi

availMem=`free -g | grep ^- | awk '{print $4}'`
if [ -z "$mem" ]
then
        mem=8
fi

if [ -z "$version" ]
then
        version=32
fi

dbTools=/opt/dbtools
mongo26BaseDir=/opt/soft/mongodb26
mongo32BaseDir=/opt/soft/mongodb3210
initEtcFile=$dbTools/mongo/mongo32.conf

function getMongoLatestEtcFile()
{
    if [ ! -f $initFile ]
        echo "push conf file"
    then
        echo "Can't find $initFile,Check it!"
        exit 1                                                                
    fi
}

function install_Mongo26()
{
    if [ ! -d $mongo26BaseDir ]
    then
        yum -y install mongodb26
        echo "yum -y install mongodb26.x86_64"
    fi
}

function install_Mongo32()
{
    if [ ! -d $mongo32BaseDir ]
    then
        yum -y install 58mongodb32.x86_64
        echo "yum -y install 58mongodb32.x86_64"
    fi
}

if [ $version -eq 26 ]
then
    install_Mongo26
elif [ $version -eq 32 ]
then
    install_Mongo32
else
    echo "Unsupport Mongo Version!"
    exit 1
fi


####Init New Instance
instanceDir=/work/mongodb$port
portExists=`netstat -lnp | grep :$port | wc -l`
if [ $portExists -gt 0 ]
then
    echo "Mongo $port already exists,Exit!"
    exit 1
fi

if [ -d $instanceDir ]
then
    echo "The new Instance Directory $instanceDir already exists,Check it!"
    exit 1
else
    mkdir -p $instanceDir/{etc,var,key,log,tmp}
fi


#checkUserGroup
#getLatestInitFile
if [ ! -d "$instanceDir/etc" ] || [ ! -d "$instanceDir/var" ]
then
    echo "Can't find etc or var,Check it!"
else
    cnfFile=$instanceDir/etc/mongo$port.cnf
    
    if [ -f "$initEtcFile" ]
    then
        cp -f $initEtcFile  $cnfFile
    else
        echo "Can't find init configuration file:mongo32.conf, Check it!"
    fi
fi


sed -i -e "s/23333/${port}/g" $cnfFile
sed -i -e "s/IamCache/${mem}/g" $cnfFile
sed -i -e "s/IamOplog/${oplog}/g" $cnfFile

exit 0

