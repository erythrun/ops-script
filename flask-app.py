# -*- coding: utf8 -*-
'''
Author: Athrun
Email: erythron@qq.com
Date: 2021-08-23 09:07:39
LastEditTime: 2021-09-15 11:29:00
description: 测试flask_apscheduler以及flask-api的使用
'''
from flask import Flask
from flask_restful import Resource, Api
import time
from flask_apscheduler import APScheduler
import requests
import json


app = Flask(__name__)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
api = Api(app)
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

#定时任务调用的方法需要放在class外部
def hi():
    return ('hi')

class Data(Resource):

    def get(self):
        return {'time': now_time}

    @scheduler.task('interval', id='do_job_1', seconds=3, misfire_grace_time=900)
    def Time():
        global now_time
        print (hi())
        now_time = time.strftime("%Y-%m-%d,%H:%M:%S")




api.add_resource(Data, '/')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)


