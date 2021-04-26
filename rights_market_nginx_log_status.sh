#!/bin/bash
###
 # @Author: 小成
 # @Date: 2021-04-26 10:26:55
 # @LastEditTime: 2021-04-26 10:29:01
 # @description: 权益超市nginx状态码检查
###


source /etc/profile

mail_list=""
date_format=`date -d "0 days ago" +%Y:%H`
filename="qwqy_nginx_ip.txt"
echo "#######最近一个小时访问情况，次数 ip，错误码：######"  >./$filename
grep "$date_format" /data/nginx/logs/access.log|awk '{if($9~"^4")print $1 " " $9}' |sort -n|uniq -c|sort -nr |head >> ./$filename
echo -e "\n" >> ./$filename


echo "######今天访问情况，次数 ip，错误码######" >>./$filename
awk '{if($9~"^4")print $1 " " $9}' /data/nginx/logs/access.log|sort -n|uniq -c|sort -nr |head >> ./$filename
echo -e "\n" >> ./$filename


content=`cat $filename`
/usr/bin/python send_mail.py $mail_list "全网权益平台nginx异常访问" """$content""" $filename
