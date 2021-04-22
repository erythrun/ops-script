'''
Author: Athrun
Email: erythron@qq.com
Date: 2020-11-05 11:03:32
LastEditTime: 2021-04-22 10:41:04
description:
    对Grafana定时截图并提取数据, 自动化日报;
    Authorization value 到期需到/etc/nginx/nginx.conf中修改
    账号密码使用keyring储存
'''


from selenium import webdriver
import time
from datetime import datetime, date, timedelta
from lxml import etree
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email import encoders
from email.mime.application import MIMEApplication
import keyring


def GrafanaHTMLCode(size,png_path,url):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')           # 解决DevToolsActivePort文件不存在的报错
    options.add_argument('window-size=1920x'+size)  # 指定浏览器分辨率
    options.add_argument('--start-maximized')      # 最大化运行（全屏窗口）
    options.add_argument('--headless')             # 浏览器不提供可视化页面.
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(executable_path='./chromedriver',chrome_options=options)
    browser.get(url)
    time.sleep(15)
    browser.save_screenshot(png_path)
    html_code = browser.find_element_by_xpath("//*").get_attribute("outerHTML")
    browser.quit()
    return html_code


def Basic(html_data):
    selector = etree.HTML(html_data)
    nginx_60 = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div[1]/div/div[2]/div/div[1]/div/div[1]/span')[0].text
    nginx_61 = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div[1]/div/div[2]/div/div[2]/div/div[1]/span')[0].text
    max_network = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/text()')[0]
    max_io = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div[2]/div[4]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/text()')[0]
    max_cpu = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div[2]/div[6]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/text()')[0]
    max_memory = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div[2]/div[7]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/text()')[0]
    nginx_sum = int(nginx_60)+int(nginx_61)
    nginx_min = nginx_sum // 60
    basic_data = [nginx_sum, nginx_min, max_cpu, max_io, max_network, max_memory]
    return basic_data



def Order(html_data):
    selector = etree.HTML(html_data)
    #下单接口
    api_order = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[3]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr/td[2]/text()')[0]
    #回调接口
    api_callback = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[6]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr/td[2]/text()')[0]
    #查询接口
    api_query = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[9]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr/td[2]/text()')[0]
    #总订单量
    order_success = int(selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/div[2]/div/div[3]/div/div[1]/span')[0].text)
    #最高并发
    order_max = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/div/div/text()')[0]
    #失败订单
    order_fail = int(selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/div[2]/div/div[1]/div/div[1]/span')[0].text)
    #开通订单
    order_open = int(selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/div[2]/div/div[5]/div/div[1]/span')[0].text)
    #超时
    order_timeout = int(selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/div[2]/div/div[4]/div/div[1]/span')[0].text)
    #成功率
    order_success_percent = "{:.2%}".format(order_success/(order_success+order_fail+order_open+order_timeout))
    order_data = [order_success,order_fail,order_timeout,order_success_percent,order_max,api_order,api_callback,api_query]
    return order_data


def Redis(html_data):
    selector = etree.HTML(html_data)
    #执行
    redis_exec = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/text()')[0]
    #内存
    redis_memory = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[3]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[3]/text()')[0]
    #key
    redis_key = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[4]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/text()')[0]
    redis_data = [redis_exec,redis_memory,redis_key]
    return redis_data


def MySQL(html_data):
    selector = etree.HTML(html_data)
    mysql_sync_time = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[9]/div/div[1]/div/div[2]/div/plugin-component/panel-plugin-graph/grafana-panel/ng-transclude/div/div[2]/div/div[1]/div/table/tbody/tr[1]/td[2]/text()')[0]
    TPS = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/div[2]/div/div[1]/div/div[1]/span[5]')[0].text
    QPS = selector.xpath('/html/body/grafana-app/div/div/react-container/div/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/div[2]/div/div[4]/div/div[1]/span[5]')[0].text
    mysql_data = [mysql_sync_time,TPS, QPS]
    return mysql_data


def RabbitMQ(png_path):
    MQ_user = keyring.get_password('MQ', 'user')
    MQ_passwd = keyring.get_password('MQ', 'passwd')
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')           # 解决DevToolsActivePort文件不存在的报错
    options.add_argument('window-size=1920x1000')  # 指定浏览器分辨率
    options.add_argument('--start-maximized')      # 最大化运行（全屏窗口）
    options.add_argument('--headless')             # 浏览器不提供可视化页面.
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(executable_path='./chromedriver',chrome_options=options)
    browser.get('http://10.3.22.66:15672/')
    time.sleep(3)
    name = browser.find_element_by_name("username")
    passwd = browser.find_element_by_name("password")
    name.send_keys(MQ_user)
    passwd.send_keys(MQ_passwd)
    button = browser.find_element_by_xpath('/html/body/div[1]/div/form/table/tbody/tr[3]/td/input')
    button.click()
    time.sleep(3)
    browser.save_screenshot(png_path)
    browser.quit()


def PngPath(name):
    png_path = "./png/{day}/{run_time}-{name}.png".format(day=day,name=name,run_time=run_time)
    return png_path


def SlowLog():
    sendlog_passwd = keyring.get_password('user', 'sendlog')
    log_time = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
    count_log = 'mysqlslog-count-{log_time}.log'.format(log_time=log_time)
    log = 'mysqlslog-{log_time}'.format(log_time=log_time)
    os.system("sshpass -p '{passwd}' scp sendlog@10.3.22.71:/data/check/slow_log/{count_log} /opt/report_day/slow_log/".format(passwd=sendlog_passwd,count_log=count_log))
    os.system("sshpass -p '{passwd}' scp sendlog@10.3.22.71:/data/check/slow_log/{log} /opt/report_day/slow_log/".format(passwd=sendlog_passwd,log=log))
    time.sleep(2)
    attachments = [
        ['./slow_log/'+log,log],
        ['./slow_log/'+count_log,count_log],
    ]
    return attachments


def SendEmail(contents,png_paths,receivers,attachments):
    user = keyring.get_password('email', 'user')
    passwd = keyring.get_password('email', 'passwd')
    smtp = keyring.get_password('email', 'smtp')
    msg = MIMEMultipart('related')
    msg.attach(MIMEText(contents, 'html', 'utf-8'))
    for png_path in png_paths:
        with open(png_path[0],'rb') as f:
            pic = MIMEImage(f.read())
            pic.add_header('Content-ID',png_path[1])
            msg.attach(pic)
    for attachment in attachments:
        with open(attachment[0],'rb') as f:
            attachfile = MIMEApplication(f.read())
            attachfile.add_header('Content-Disposition', 'attachment', filename=attachment[1])
            msg.attach(attachfile)

    msg['From'] = user
    msg['To'] = ','.join(receivers)
    msg['Subject'] = Header('运维日报' + day,'utf-8').encode()
    smtp = smtplib.SMTP_SSL(smtp)
    message = smtp.login(user,passwd)
    smtp.sendmail(user, receivers, msg.as_string())
    smtp.quit()


contents = '''
<body style="font-size:14px">
<h1>性能日报</h1>
<h2>一、综述</h2>
<h3>故障0起，告警异常0起，</h3>
<h3>部署0起:  </h3>
<h3>操作系统：正常   数据库：正常 </h3>
<h3>同步延迟{mysql_sync_time}S </h3>
<h3>无安全事件 </h3>

<h2>二、基础系统性能</h2>
<img src="cid:102" width=100%>
<hr>
结论：<br/>
1. nginx请求最多并发：{nginx_sum}/60={nginx_min}tps，系统设计nginx最大并发10000tps <br/>
2. CPU最高使用率{max_cpu}，正常 <br/>
3. 磁盘最大{max_io}，正常 <br/>
4. 网络流传最大{max_network}，正常 <br/>
5. 内存使用率最大使用{max_memory}，正常 <br/>

<h2>三、平台业务指标</h2>
<img src="cid:105" width=100%>
<hr>
结论：<br/>
1. 订单最高并发 {order_max} 笔/分钟 <br/>
2，成功订单数{order_success}，失败订单数{order_fail}, 超时订单数{order_timeout} <br/>
3，收单、查询、回调接口平均响应时间分别为：{api_order}、{api_query}、{api_callback} <br/>

<h2>四、第三方插件性能</h2>
<h2>3.1 、redis </h2>
<img src="cid:201" width=100%>
<hr>
结论： <br/>
1，redis无慢查询 <br/>
2，每秒执行命令最高{redis_exec}，正常 <br/>
3，内存最高使用{redis_memory}，正常 <br/>
4，Keys的键值数最大{redis_key},正常 <br/>
5，连接数无明显徒增，正常 <br/>

<h2>3.2、数据库</h2>
<img src="cid:205" width=100%>
<hr>
结论： <br/>
1，最高{TPS}TPS, {QPS} QPS, 正常 <br/>
2，命中率100%,正常 <br/>
3，没有等待琐情况 <br/>
4，过去一天的mysql慢查询日志，请见附件。 <br/>

<h2>3.3、rabbitmq </h2>
<img src="cid:303" width=100%>
<hr>
结论： <br/>
1，publish 负载正常 <br/>
2，未见阻塞，正常 <br/>
</body>
'''


if __name__ == '__main__':
    day = time.strftime("%Y%m%d")
    run_time = time.strftime("%Y%m%d%H")
    if os.path.exists("./png/{day}".format(day=day)):
        pass
    else:
        os.mkdir("./png/{day}".format(day=day))
    #路径
    basic_png = PngPath('basic')
    order_png = PngPath('order')
    mysql_png = PngPath('mysql')
    redis_png = PngPath('redis')
    rabbit_png = PngPath('rabbit')
    #数据返回
    basic_data = Basic(GrafanaHTMLCode('1200',basic_png,'http://127.0.0.1:10086/osaProxy/grafana/d/VXNTiQWQYPT/19_quan-yi-zhong-xin-quan-wang-quan-yi-ping-tai-ji-chu-jian-kong?orgId=1&var-datasource=Zabbix%20LG&var-group=All&var-host=All'))
    order_data = Order(GrafanaHTMLCode('1500',order_png,'http://127.0.0.1:10086/osaProxy/grafana/d/RcQIWNzGz/19_quan-yi-zhong-xin-quan-wang-quan-yi-ping-tai-ye-wu-jian-kong?orgId=1&from=now-24h&to=now'))
    redis_data = Redis(GrafanaHTMLCode('1200',redis_png,'http://127.0.0.1:10086/osaProxy/grafana/d/fT7o_16Wz/19_quan-yi-zhong-xin-quan-wang-quan-yi-ping-tai-redis?orgId=1&from=now-24h&to=now'))
    mysql_data = MySQL(GrafanaHTMLCode('1200',mysql_png,'http://127.0.0.1:10086/osaProxy/grafana/d/-M49Yy6Zz/19_quan-yi-zhong-xin-quan-wang-quan-yi-ping-tai-mysql?orgId=1'))
    RabbitMQ(rabbit_png)
    #填充
    contents = contents.format(mysql_sync_time=mysql_data[0],nginx_sum=basic_data[0],nginx_min=basic_data[1],max_cpu=basic_data[2],max_io=basic_data[3], max_network=basic_data[4], max_memory=basic_data[5],order_success=order_data[0],order_fail=order_data[1],order_timeout=order_data[2],order_success_percent=order_data[3],order_max=order_data[4],api_order=order_data[5],api_callback=order_data[6],api_query=order_data[7],redis_exec=redis_data[0],redis_memory=redis_data[1],redis_key=redis_data[2],TPS=mysql_data[1], QPS=mysql_data[2])

    png_paths = [
        [basic_png, '<102>'],
        [order_png, '<105>'],
        [redis_png, '<201>'],
        [mysql_png, '<205>'],
        [rabbit_png, '<303>']
    ]
    attachments = SlowLog()
    receivers = ['email@qq.com']
    SendEmail(contents,png_paths,receivers,attachments)
    print (contents)





