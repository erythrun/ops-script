#!/python_vir/mysql/bin/python
'''
@Author: Athrun
@Email: erythron@qq.com
@Date: 2020-06-02 16:27:21
LastEditTime: 2021-04-26 10:43:49
@description: mysql 执行导出csv并邮件发送, 需要虚拟环境;
    foxmail看不到附件, 需要修改yagmail源码
    20200707: 修改失败订单sql
'''

from datetime import datetime, date, timedelta
import pymysql, csv, sys, os, time
import smtplib
import yagmail
import keyring


# sql语句, 使用嵌套列表
SQLQueryStrings = [
    [
        # 截止5月28日
        "截止"+yesterday+"(包含该日期)",
        '''select a.cmcopchannelid,b.channelname,
            CASE a.status
                    WHEN 3 THEN '开通中'
                    WHEN 5 THEN '成功'
            ELSE '失败' END as status,a.count from
            (select cmcopchannelid,status,count(*) as count from order_main where channelcode='67042'
            and createtime < '{SQL_today}' group by cmcopchannelid,status) a
            left join cmcop_channel b on a.cmcopchannelid=b.channelid order by b.channelid asc;'''.format(SQL_today=SQL_today)
    ],
    [
        # 5月28日当天
        yesterday+"当天",
        '''
            select a.cmcopchannelid,b.channelname,
            CASE a.status
                    WHEN 3 THEN '开通中'
                    WHEN 5 THEN '成功'
            ELSE '失败' END as status,a.count from
            (select cmcopchannelid,status,count(*) as count from order_main
            where channelcode='67042'
            and createtime>= '{SQL_yesterday}'
            and createtime < '{SQL_today}'
            group by cmcopchannelid,status) a
            left join cmcop_channel b on a.cmcopchannelid=b.channelid order by b.channelid asc;
        '''.format(SQL_yesterday=SQL_yesterday,SQL_today=SQL_today)
    ]
]


def MySQLQuery(file_name, SQL_query):
    db = pymysql.connect(**db_opts)
    cur = db.cursor()


    try:
        cur.execute(SQL_query)
        rows = cur.fetchall()
    finally:
        db.close()
        time.sleep(5)

    # Continue only if there are rows returned.
    if rows:
        # New empty list called 'result'. This will be written to a file.
        result = list()

        # The row name is the first entry for each entity in the description tuple.
        column_names = list()
        for i in cur.description:
            column_names.append(i[0])

        result.append(column_names)
        for row in rows:
            result.append(row)

        # csv 文件路径
        csv_file_path = "./mysql_report/"+today+"/"+file_name+".csv"
        with open(csv_file_path, 'w', encoding="utf_8_sig", newline='',) as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in result:
                csvwriter.writerow(row)
    else:
        pass


if __name__ == "__main__":
    mysql_pd = keyring.get_password("mysql","mysql_user")
    db_opts = {
        'user': 'yw_rights_market',
        'password': mysql_pd,
        'host': '10.3.22.71',
        'database': 'rights_market'
    }

    yesterday = (date.today() + timedelta(days=-1)).strftime("%Y%m%d")
    today = time.strftime("%Y%m%d")
    SQL_today = today + "000000"
    SQL_yesterday = yesterday + "000000"

    if os.path.exists("./mysql_report"):
        os.mkdir("./mysql_report/"+today)
    else:
        os.makedirs("./mysql_report/"+today)
    for file_name, SQL_query in SQLQueryStrings:
        MySQLQuery(file_name, SQL_query)

    #压缩, 这里使用绝对路径
    os.system(
        "cd /data/mysql/mysql_report/"+today+" && zip -qr /data/mysql/zip/"+today+".zip *")
    time.sleep(3)
    email_user = keyring.get_password("user","email_88")
    email_pd = keyring.get_password("passwd","email_88")
    email_stmp = keyring.get_password("smtp","email_88")
    email_args = {
        "user": email_user,
        "password": email_pd,
        "host": email_stmp,
        "port": "465"
    }
    yag = yagmail.SMTP(**email_args)
    # 邮箱正文
    contents = ['你好, 详细见附件', '    请勿回复, 此为自动程序发送']
    # 标题
    title = "mysql 自动执行日志--"+today
    # 接收邮箱
    address = ['email@qq.com']
    # 发送邮件
    file_path = "/data/mysql/zip/"+today+".zip"
    yag.send(address, title, contents, file_path)

