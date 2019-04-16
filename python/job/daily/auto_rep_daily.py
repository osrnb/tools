#!/usr/bin/env python
# coding=utf-8

"""
预填写缺失日报：
1、需要设置控制参数：
log：工作日志内容
which_task：选择第几个项目任务
place：出勤地点
2、只支持填写一份8小时日报
3、支持多日日报同时填写
"""

import re

from bs4 import BeautifulSoup

from job.daily.rep_daily import login, find_lose_report
from utils.constants import log, which_task, place
from utils.logger import get_logger
from utils.mail import daily_mailto

logger = get_logger(__name__)

# 填写日报-接收post请求
rep_daily_post_url = "http://60.174.249.206:9999/in/modules/prj/rep_daily_post.php"


def auto_write_rep_daily():
    """
    自动填写个人日报
    """
    session = login()  # 登录内网
    report_lost = find_lose_report(session)  # 查看是否有缺失日报

    # 日报无缺失
    if len(report_lost) == 0:
        logger.info("个人日报已全部填写。")
        return 0

    # 有缺失日报，开启自动写日报
    logger.info("准备自动填写%s日报。" % list(report_lost.keys()))

    # ------------------------------批量写日报开始------------------------------
    # 支持写多日日报
    # '星期四':'http://60.174.249.206:9999/in/modules/prj/rep_daily.php?rep_time=1553126400'
    for week, url in report_lost.items():
        r = session.post(url, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')

        task_list = soup.find("select", id="taskid[1]").findAll("option")
        task_nums = len(task_list)
        # 无可选任务（只有默认的"请选择"时，表示无可选项目任务）
        if task_nums <= 1 or task_nums <= which_task:
            logger.error("自动填写日报异常-->无效的项目任务供选择。")
            return -1
        # 选择指定的第几个任务，自动填写日报
        task_id = task_list[which_task - 1].attrs["value"]

        # 出勤记录，cq：公司出勤，gc：本地公出，cc：外地出差，jb：本地加班，jc：出差加班，qj：请假缺勤
        # 如果为设置出勤地点，则自动判断。但只支持jb：本地加班，工作日为cq，周末为加班
        place_ = place
        if not place_:
            if week in {'星期六', '星期日'}:
                place_ = "jb"
            else:
                place_ = "cq"

        # 获取需要填写日报的时间戳
        target_date = re.search(r".*(\d{10}).*", url).group(1)

        # 注意，post时需要提交所有表单变量
        daily_data = {"smile[1]": "1", "arch[1]": "", "busy[1]": "2", "taskid[1]": task_id,
                      "log[1]": log, "plan[1]": "", "question[1]": "",
                      "task_type[1]": "13", "progress[1]": "0", "place[1]": place_, "wtime[1]": "8.00",
                      "date1[1]": target_date, "worktdesc[1]": "", "repid[1]": "-1", "amount[1]": "",
                      "unit_type[1]": "0",
                      "save": "保存", "time1[1]": "540"}
        session.post(rep_daily_post_url, data=daily_data, timeout=10)
    # ------------------------------批量写日报结束------------------------------

    # 再次查看是否自动填写成功
    report_lost = find_lose_report(session)
    # 有缺失日报
    if len(report_lost):
        href = ""
        for week, url in report_lost.items():
            href = href + f"<a href='{url}'>{week}</a>    "

        msg = f"自动填写{href}日报失败，需手动填写。"
        daily_mailto(msg)
        logger.error("自动填写日报-->失败，已邮件通知")
    # 没有缺失日报
    else:
        logger.info("自动填写日报-->成功。")


if __name__ == "__main__":
    auto_write_rep_daily()
