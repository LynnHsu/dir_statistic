# dir_statistic
统计服务器文件夹的信息

## 介绍
统计服务器文件夹包含的内容，供文件分析使用

## 依赖
python3.8

## 配置说明
> config/config.ini
```
[TARGET]
pc=local-pc		主机标识，会打印在统计结果文件名
description=hub	
root_path=D:\Lynn	统计的根目录，对应的dir_level=0，子文件夹的dir_level依次递增
max_level=2		统计的最大level

[WORK_SPACE]
work_path=d:\\dir_statistic_work	统计csv结果输出的目录
```

> 生成的结果
1. 格式：csv
2. csv文件头："pc","description","batch_no","dir_name","dir_path","parent_path","root_path","dir_level","child_file_num","child_file_num_all","child_dir_num","child_dir_num_all","child_file_size","child_file_size_all","child_zero_num","child_zero_num_all","statistic_time"

> 数据库
1. config/dir_statistic.sql
2. sql对应的oracle数据库，可根据自己的需要更改sql

## 脚本执行
1. 修改配置 config/config.ini
2. 可源码执行 **start.py**:  python ./start.py
