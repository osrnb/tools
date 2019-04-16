# 编码
UTF-8

# 换行
LF，即（\n）

# 准备工作
本工具使用python开发，需具备基础知识

## 版本
Python 3.7.3

## 第三方库
```
pip3 install requests
pip3 install lxml
pip3 install BeautifulSoup4
```

## 设置环境
将PYTHONPATH变量绑定到{存放脚本的父目录}/python/目录上（自行百度如何设置变量）

# 部署
## 目录层级
$PYTHONPATH 目录下放置的文件结构：
```
python
├── README.md
├── job
│   ├── __init__.py
│   └── daily
│       ├── __init__.py
│       ├── auto_rep_daily.py
│       └── rep_daily.py
└── utils
    ├── __init__.py
    ├── constants.py
    ├── logger.py
    └── mail.py
```

## 脚本说明
1. constants.py：根据说明修改本脚本中的username, password, workday, log, which_task, place等参数，部分参数有默认值。
2. rep_daily.py：监控是否有日报缺失，如有缺失则邮件通知；
3. auto_rep_daily.py：自动填写缺失日报，自动填写失败则邮件通知。

## 其他说明
1. 自动填写日报，只支持一份8小时日报；
2. 登录内网和邮箱的密码需一致。