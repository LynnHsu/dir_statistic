# dir_statistic
统计服务器文件夹的信息

## 介绍
统计服务器文件夹包含的内容，供文件分析使用

## 版本
#### v.2.0
版本 v.1.0 着重完成文件夹信息的统计，接着需要完成文件分析，完成后续的优化工作。
1. 指定类型文件（如日志）的压缩来缩小硬盘占用
2. 压缩后文件命名规则xxx.zip -> xxx.tar.gz, xxx.log -> xxx.gz
3. 文件范围：匹配到的所有文件，若为zip则解压重新压缩为gz

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

[control]
file_to_gz=True		True: 开启文件压缩
zip_to_gz=False		True: 开启zip转换为tar.gz
delete_zero_file=False	True: 开启删除空文件
recover=False		False: 正向压缩，True: 反向解压恢复
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
