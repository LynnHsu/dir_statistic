#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author lynn_hsu@yeah.net
@desc csv 处理工具
@date 2020.09.10.142900
"""

import csv
import os


def write(file, header, rows):
    """
    导出csv到文件， 自动创建文件， append方式
    :param file: 导出的csv文件
    :param header: csv header
    :param rows: csv rows
    :return: void
    """
    if file == '':
        raise ValueError("params: file_name, path could not be null")
    parent_path = os.path.dirname(file)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)
    csv_file = open(file, 'a+', newline='', encoding="utf-8")  # 打开方式还可以使用file对象
    writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_ALL, lineterminator='\r\n')
    if header and len(header) > 0:
        writer.writerow(header)
    if rows and len(rows) > 0:
        writer.writerows(rows)
    csv_file.close()
    pass
