# dir_statistic
统计服务器文件夹的信息

## 介绍
统计服务器文件夹包含的内容，供文件分析使用

## 版本
#### v.1.0
> 诉求

最近服务器中磁盘占用过了预警线，文件夹深度及文件琐碎，常规的统计工具（如everything, treeSize.）也能分析出文件情况。考虑到后续可能要对这些文件做处理（如压缩、清理、迁移等），编写了个脚本来达到自己预期的结果。
1. 能知道文件夹情况
2. 能知道文件夹有多少的空文件
3. 能用sql在数据库中操作统计信息

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
2. csv文件头：
```
"pc","description","batch_no","dir_name","dir_path","parent_path","root_path","dir_level","child_file_num","child_file_num_all","child_dir_num","child_dir_num_all","child_file_size","child_file_size_all","child_zero_num","child_zero_num_all","statistic_time"
```

> 数据库
1. config/dir_statistic.sql
2. sql对应的oracle数据库，可根据自己的需要更改sql

## 脚本执行
1. 修改配置 config/config.ini
2. 可源码执行 **start.py**:  python ./start.py
