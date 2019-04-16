#!/usr/bin/env python
# coding=utf-8

import logging


def get_logger(name):
    """
    生成输出特定日志格式的记录器
    :param name: 记录器名字
    :return: 记录器对象
    """
    # 日志记录格式：时间-模块[打印日志的行号]-日志级别-行号
    formatter = logging.Formatter('%(asctime)s - %(module)s[%(lineno)d] - %(levelname)s - %(message)s',
                                  '%Y/%m/%d %H:%M:%S')

    # 创建记录任何级别的记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 滚动记录日志到文件
    # fh = RotatingFileHandler("%s.log" % name, maxBytes=1024 * 1024 * 10, backupCount=10)
    # fh.setLevel(logging.INFO)
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)

    # 日志打印到控制台
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger
