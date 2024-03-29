#!/bin/bash
###
 # @Author: Athrun
 # @Email: erythron@outlook.com
 # @Date: 2022-12-12 18:21:29
 # @LastEditTime: 2023-04-07 14:54:22
 # @description: bash init-disk.sh 1 "sdb" "/app"
 #               bash init-disk.sh 2 "sda,sdb,sdc" "/app"
 #               bash init-disk.sh 3 "lvm模式未完成"
###

function disk {
  #$1 磁盘
  #$2 路径
  echo "sudo mkfs.xfs /dev/$1"
  sudo mkfs.xfs /dev/$1
  judge=$?
  sleep 5
  list=`sudo blkid | grep $1 | awk -F: '{print $2}' | awk -F\" '{print $2}'`
  if [[ -n "$list" && $judge == 0 ]] ;then
    echo "sudo mkdir $2"
    sudo mkdir $2
    #echo "UUID="$list " $2 xfs defaults 0 0"
    echo "UUID=$list $2 xfs defaults 0 0" | sudo tee -a  /etc/fstab
    sudo mount -a
    sleep 1
    sudo chmod 777 $2
  else
    echo "ERROR: cant find $1 UUID or init failed"
    exit 1
  fi
}


#check folder
function check {
  if [ -d "$1" ]; then
    echo "$1 exist! init exit"
    exit 1
  fi
}

#$1 单磁盘模式
if [ $1 == 1 ];
then
  check $3
  if [ $? == 0 ];
  then
    disk $2 $3
  fi
fi

count=0 #用于计算多磁盘模式的顺序
if [ $1 == 2 ];
#$1 多磁盘模式
#$2 盘名, 字符串: 以逗号分割, 依次挂载到/app0 /app1下
then
  #string=$2
  array=(`echo $2 | tr ',' ' '` )
  for var in ${array[@]}
  do
    echo "check $3$count"
    check $3$count
    if [ $? == 0 ];
    then
      disk "$var" $3$count
      count=`expr $count + 1`
    fi
  done
fi

if [ $1 == 3 ];
then
  echo 'lvm 模式未想好咋搞'
fi