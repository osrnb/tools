#!/usr/bin/env python
# coding=utf-8

"""
监控日报是否填写，发现未填写时，以邮件通知
1、需要设置控制参数：
username：统一认证用户名
password：统一认证密码
workday：监控周几的日报
2、只支持内网和邮箱账号密码一致的账号
"""

import re

import requests
from bs4 import BeautifulSoup

from utils.constants import username, password, workday
from utils.logger import get_logger
from utils.mail import daily_mailto

logger = get_logger(__name__)

# 登录-接收post请求
login_url = r"http://passport.kdgcsoft.com/login?service=http%3A%2F%2Foffice.kdgcsoft.com%2F"

# 填写日报-查看-发起get请求
rep_daily_url = "http://60.174.249.206:9999/in/modules/prj/rep_daily.php?rep_time="

# 查看是否有日报未填写
report_list_url = "http://60.174.249.206:9999/in/modules/xoa/mytask.php"


def login():
    """
    登录到内网，完成认证
    :return: 登录成功后到session
    """
    # 创建会话
    with requests.session() as session:
        # 第一次连接获取执行串，进行后续登录认证
        first_response = session.get(login_url, timeout=10)
        soup = BeautifulSoup(first_response.text, 'lxml')
        execution = soup.findAll("input", {"name": "execution"})
        if len(execution) >= 1:
            execution = execution[0].attrs
            execution = execution["value"]
        else:
            return -1

        # 登录，使会话生效
        data = {"username": username, "password": password, "vcode": "",
                "service": r"http%3A%2F%2Foffice.kdgcsoft.com%2F",
                "execution": execution, "_eventId": "submit", "geolocation": ""}
        session.post(login_url, data=data, timeout=10)

        return session


def find_lose_report(session):
    """
    查找缺失日报
    :param session: 需要登录成功后的Session
    :return: 缺失日报字典，格式'星期四':'http://60.174.249.206:9999/in/modules/prj/rep_daily.php?rep_time=1553126400'
    """
    # 查看是否存在未填写日报的情况
    params = {'mode': 'a'}
    report_response = session.get(report_list_url, params=params, timeout=10)
    soup = BeautifulSoup(bytes.decode(report_response.content, 'utf-8'), 'lxml')

    # 找出可写日报的a标签对象<a onclick="...rep_daily..."></a>
    # 使用re.search()搜索是否存在onclick属性包含rep_daily的a标签
    a_rep_daily = soup.find_all('a', onclick=re.compile('rep_daily'))

    # 提取时间戳
    re_time_stamp = re.compile(r".*(\d{10}).*")

    # 提取星期几
    set_day = set()
    for day in workday:
        if day in ['一', '二', '三', '四', '五', '六', '日']:
            set_day.add(day)

    re_workday = '|'.join(set_day)
    re_week = re.compile(rf".*([{re_workday}]).*")

    report_lost = {}
    # 从a标签中找出没有填写日报的星期几和对应的时间戳
    for a in a_rep_daily:
        # 含有内容为无的a标签
        if a.has_attr('onclick') and re.search(r"无", a.text):
            # 能够搜索到时间戳且能搜索到星期几
            if re_time_stamp.search(a.get("onclick")) and re_week.search(a.text):
                time_stamp = rep_daily_url + str(re_time_stamp.search(a.get("onclick")).group(1))
                week = "星期%s" % re_week.search(a.text).group(1)

                report_lost[week] = time_stamp

    return report_lost


def monitor_rep_daily():
    """
    检查是否写日报，如未写则发邮件提醒
    :return: None
    """
    session = login()
    report_lost = find_lose_report(session)

    # 发邮件提醒
    if len(report_lost):
        logger.info("未填写%s日报" % list(report_lost.keys()))
        links = ""
        for k, v in report_lost.items():
            links = links + "<a href='%s'>%s</a>\n" % (v, k)

        msg = "个人日报有缺失，请注意填写：\n%s" % links
        daily_mailto(msg)
    else:
        logger.info("个人日报已全部填写。")


if __name__ == "__main__":
    monitor_rep_daily()
