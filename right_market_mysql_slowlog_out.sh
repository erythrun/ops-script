date_format=`date -d '1 days ago' +%Y-%m-%d`
mysqlslog='/data/mysql/I06-LGJF-PA-ZYC-SV241-R4700G3-YY-slow.log'


head -3 $mysqlslog > ./slow_log/mysqlslog-$date_format

#导出昨日的慢查询
sed -n "/^# Time: $date_format/,$ p" $mysqlslog >> ./slow_log/mysqlslog-$date_format

#统计慢查询
mysqldumpslow -s c ./slow_log/mysqlslog-$date_format >> ./slow_log/mysqlslog-count-$date_format.log