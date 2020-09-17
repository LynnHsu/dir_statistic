#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
@author lynn_hsu@yeah.net
@desc
# 文件夹分析
# 1. 包含的文件数
# 2. 文件夹大小
# 3. 输出到csv
@date 2020.09.10
"""

import configparser
import os
import logging
import sys
from datetime import datetime

from utils import ConfigUtil, CsvUtil, FileUtil

curr_package = "bin.run"


class Run(object):

    def __init__(self, logger=None):
        """ 参数声明 """
        # 脚本中使用到的参数 [[
        self.total_num = 0
        self.trace_num = 0
        self.config = configparser.ConfigParser()
        self.now: datetime
        self.batch_no: str
        self.root_path = '统计的根目录'
        self.max_level = 0
        self.work_path = '输出目录'
        self.work_path_log = '日志目录'
        self.work_csv = '统计输出的文件'
        self.logger = None
        self.csv_header = []
        # self.bin_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        # self.project_path = os.path.dirname(self.bin_path)
        self.project_path = os.getcwd()
        # 脚本中使用到的参数 ]]

        self.now = datetime.now()
        self.batch_no = str('NO_%s' % self.now.strftime('%Y%m%d%H%M%S'))

        """ 日志初始化 """
        # if logger is None:
        # logging.basicConfig(level=logging.DEBUG, format='%(lineno)d %(asctime)s - %(name)s - %(levelname)s - %(
        # message)s', filename=os.path.abspath(os.path.join(self.project_path, 'logs', (self.batch_no + '.log'))))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        log_path = os.path.abspath(os.path.join(self.project_path, 'logs'))
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        self.formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(name)s - %('
                                           'levelname)s: %(message)s')
        self.fh = logging.FileHandler(
            r'' + os.path.abspath(os.path.join(self.project_path, 'logs',
                                               (self.batch_no + '.log'))),
            encoding='utf-8')  # 日志文件路径文件名称，编码格式
        self.fh.setLevel(logging.INFO)
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)

        # console log 控制台输出控制
        self.ch = logging.StreamHandler(sys.stdout)
        self.ch.setLevel(logging.INFO)
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)
        # else:
        #     self.logger = logger.getChild(curr_package)

        """ 配置初始化 """
        # 实例化configParser对象
        # read读取ini文件
        self.config.read(os.path.abspath(os.path.join(self.project_path, "config\\config.ini")), encoding='UTF-8')

        """ 打印脚本说明 """
        self.logger.info("current time: %s" % self.now.strftime('%Y-%m-%d %H:%M:%S'))
        self.logger.info("batch_no: %s" % self.batch_no)
        self.logger.info("***************************************")
        self.logger.info("** 文件夹分析 **")
        self.logger.info("** 1. 包含的文件数 **")
        self.logger.info("** 2. 文件夹大小 **")
        self.logger.info("** 3. 输出到csv **")
        self.logger.info("**************************************")
        self.logger.info("------")

        """ 变量初始化 """
        # 检查配置文件
        # -sections得到所有的section，并以列表的形式返回
        self.root_path = ConfigUtil.get(self.config, 'TARGET', 'root_path', self.logger)
        self.max_level = ConfigUtil.getint(self.config, 'TARGET', 'max_level', self.logger)
        self.pc = ConfigUtil.get(self.config, 'TARGET', 'pc', self.logger)
        self.description = ConfigUtil.get(self.config, 'TARGET', 'description', self.logger)
        self.work_path = ConfigUtil.get(self.config, 'WORK_SPACE', 'work_path', self.logger)

        self.work_csv = os.path.join(os.path.abspath(self.work_path),
                                     (self.pc + '-' + self.description + '-' + self.batch_no + ".csv"))

        self.csv_header = ['pc', 'description', 'batch_no',
                           'dir_name', 'dir_path',
                           'parent_path', 'root_path',
                           'dir_level',
                           'child_file_num', 'child_file_num_all',
                           'child_dir_num', 'child_dir_num_all',
                           'child_file_size(MB)', 'child_file_size_all(MB)',
                           'child_zero_num', 'child_zero_num_all',
                           'statistic_time']

    def __call__(self, *args, **kwargs):
        self.run()

    def run(self):
        try:
            CsvUtil.write(self.work_csv, self.csv_header, [])
            rows = []
            self.get_statistic_row(rows, self.pc, self.description, self.batch_no, self.root_path, self.root_path, 0,
                                   self.logger)
            CsvUtil.write(self.work_csv, [], rows)

        except Exception as ex:
            self.logger.error(ex, exc_info=1)
            # logging.error("出现如下异常%s" % ex)
        finally:
            self.logger.info("task finish... total_num: %d, trace_num: %d " % (self.total_num, self.trace_num))

    # 递归获取文件夹子文件夹的信息，并返回curr文件夹的文件数、文件夹数
    def get_statistic_row(self, _rows, _pc, _description, _batch_no, _curr_path, _root_path, _level, logger):
        """
        递归获取文件夹子文件夹的信息
        @author xu.liyin@lifecycle.cn
        :param _rows:
        :param _pc: pc mark
        :param _description: root dir mark
        :param _batch_no:
        :param _curr_path:
        :param _root_path:
        :param _level:
        :param logger:
        :return:
        """
        _logger = logger.getChild('get_statistic_row')
        file_num = 0
        dir_num = 0
        file_size = 0
        zero_num = 0
        _file_num = 0  # 文件数
        _dir_num = 0  # 文件夹数
        _file_size = 0  # 文件大小和
        _zero_num = 0  # 空文件数
        _row = []
        _logger.debug("start - %s" % _curr_path)
        for loop_dir_path, loop_dir_names, loop_file_names in os.walk(_curr_path, followlinks=False):
            # _file_num = loop_file_names.__len__() #会统计快捷方式
            # _dir_num = loop_dir_names.__len__() #会统计快捷方式
            if len(loop_file_names) > 0:
                for child_file_name in loop_file_names:
                    temp_path = os.path.join(loop_dir_path, child_file_name)
                    ext = os.path.splitext(temp_path)[1][1:].lower()
                    if ext != 'lnk' and os.path.isfile(temp_path):
                        _file_num += 1
                        _temp_size = os.path.getsize(temp_path)
                        _file_size += _temp_size
                        if _temp_size == 0:
                            _zero_num += 1
            if len(loop_dir_names) > 0:
                for child_dir_name in loop_dir_names:
                    temp_path = os.path.join(loop_dir_path, child_dir_name)
                    real_path = os.path.realpath(temp_path)
                    if temp_path == real_path:
                        arr = self.get_statistic_row(_rows, _pc, _description,
                                                     _batch_no, temp_path,
                                                     _root_path,
                                                     _level + 1,
                                                     logger)
                        file_num += arr[0]
                        dir_num += arr[1]
                        file_size += arr[2]
                        zero_num += arr[3]
                        _dir_num += 1
            file_num += _file_num
            dir_num += _dir_num
            file_size += _file_size
            zero_num += _zero_num
            break
        if _level <= self.max_level:
            _dir_name = os.path.basename(_curr_path)
            _dir_path = os.path.abspath(_curr_path)
            _parent_path = os.path.abspath(os.path.dirname(_curr_path) + os.path.sep + ".")

            _row.append(_pc)
            _row.append(_description)
            _row.append(_batch_no)
            _row.append(_dir_name)
            _row.append(_dir_path)
            _row.append(_parent_path)
            _row.append(_root_path)
            _row.append(_level)
            _row.append(_file_num)
            _row.append(file_num)
            _row.append(_dir_num)
            _row.append(dir_num)
            _row.append(FileUtil.format2MB(_file_size))
            _row.append(FileUtil.format2MB(file_size))
            _row.append(_zero_num)
            _row.append(zero_num)
            _row.append((datetime.now()).strftime('%Y-%m-%d %H:%M:%S'))
            _rows.append(_row)
            self.total_num += 1
            if _rows.__len__() == 500:
                temp_rows = _rows.copy()
                CsvUtil.write(self.work_csv, [], temp_rows)
                self.logger.info("csv export 500.")
                _rows.clear()
        arr = [file_num, dir_num, file_size, zero_num]
        _logger.debug("end - %s ,%s" % (_curr_path, _row))
        self.trace_num += 1
        if self.trace_num % 10000 == 0:
            _logger.info("current trace num: %d %s" % (self.trace_num, _curr_path))
        return arr
