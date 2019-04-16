#!/usr/bin/env python
# coding=utf-8

import smtplib
from email.header import Header
from email.mime.text import MIMEText

from utils.constants import password, sender, receiver
from utils.logger import get_logger

logger = get_logger(__name__)


class Mail:
    """
    通过邮件将文本内容发送给指定人
    """

    def __init__(self, server, port, address_from, password, address_to, subject, msg):
        self.server = server  # 发件服务器
        self.port = port  # 发件服务器端口
        self.address_from = address_from  # 发件人邮箱
        self.password = password  # 发件人邮箱密码
        self.address_to = address_to  # 收件人邮箱
        self.sub = subject  # 邮件主题
        self.msg = msg  # 邮件内容

    def send(self):
        # msg = MIMEText(self.msg, 'plain', 'utf-8')  # 封装文本内容
        msg = MIMEText(self.msg, 'html', 'utf-8')  # 封装文本内容
        msg['Subject'] = Header(self.sub, 'utf-8')  # 封装邮件主题
        msg['From'] = Header(self.address_from)  # 封装发件人
        msg['To'] = Header(self.address_to)  # 封装收件人

        try:
            server_smtp = smtplib.SMTP(self.server, self.port, timeout=1)  # 第二个参数为默认端口为25，有些邮件有特殊端口
            server_smtp.login(self.address_from, self.password)  # 登录邮箱
            server_smtp.sendmail(self.address_from, self.address_to, msg.as_string())  # 将msg转化成string发出
            logger.info("邮件发送成功")
            server_smtp.quit()
        except Exception as e:
            logger.error("邮件发送失败")
            raise e


# 发邮件
def daily_mailto(msg):
    """
    自己给自己发邮件
    :param msg: 邮件内容
    :return: None
    """
    host = "smtp.ustcinfo.com"
    port = 25
    subject = "【重要】个人日报"

    mail = Mail(host, port, sender, password, receiver, subject, msg)
    mail.send()
