#!/usr/bin/python
# -*- coding: UTF-8 -*-

# ********
# 文件夹分析
# 1. 包含的文件数
# 2. 文件夹大小
# 3. 输出到csv
# ********

import os
import logging

from bin.run import Run

# 开始执行
Run().__call__()

# 执行完成
input('Press Enter to exit...')
