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
import re
import sys
from datetime import datetime

from utils import ConfigUtil, CsvUtil, FileUtil, ZipUtil, GzUtil

curr_package = "bin.run"


class Run(object):

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

    def __init__(self, logger=None):

        """ 参数声明 """
        # 脚本中使用到的参数 [[
        self.total_num = 0
        self.trace_num = 0
        self.config = configparser.ConfigParser()
        self.now: datetime
        self.batch_no: str
        self.pc: str = None
        self.description: str = None
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

        self.file_to_gz = False  # 文件做gz压缩
        self.zip_to_gz = False  # zip转换成gz
        self.delete_zero_file = False  # 删除空文件
        self.recover = False  # True: 正向压缩， False: 反向恢复（tar.gz -> zip, gz -> file, 空文件无法恢复）
        # 脚本中使用到的参数 ]]

        self.now = datetime.now()  # 全局变量，最先初始化
        self.batch_no = str('NO_%s' % self.now.strftime('%Y%m%d%H%M%S'))  # 日志中会用到

        ''' 初始化日志配置 '''
        self.init_log()

        """ 配置初始化 """
        self.init_config()

        """ 打印脚本说明 """
        self.init_intro()

        """ 变量初始化 """
        self.init_variate()
        pass

    def func_loop_file_names(self, arr_analysis, loop_dir_path, loop_file_names):
        """
        遍历文件
        :param arr_analysis: 统计内容数组
        :param loop_dir_path: 根路径
        :param loop_file_names: 遍历中文件夹下的文件
        """
        for child_file_name in loop_file_names:
            temp_path = os.path.join(loop_dir_path, child_file_name)
            ext = os.path.splitext(temp_path)[1][1:].lower()
            if ext != 'lnk' and os.path.isfile(temp_path):
                # _file_num += 1
                arr_analysis[4] += 1
                _temp_size = os.path.getsize(temp_path)
                # _file_size += _temp_size
                arr_analysis[6] += _temp_size
                if _temp_size == 0:
                    # _zero_num += 1
                    arr_analysis[7] += 1
                    if self.delete_zero_file:
                        FileUtil.remove_file(temp_path)
                        self.logger.info("deleted empty file: " + temp_path)
                    pass
                else:
                    # 逆向开始 [[ 将 tar.gz -> zip, gz -> file
                    if self.recover and ext == 'gz':
                        if temp_path.endswith(".tar.gz"):
                            if self.zip_to_gz:
                                _temp_parent_dir = GzUtil.unzip_tar_gz(temp_path, os.path.dirname(temp_path))
                                _temp_zip_dir = os.path.join(_temp_parent_dir,
                                                             re.sub(r'\.tar\.gz$', "", os.path.basename(temp_path),
                                                                    flags=re.IGNORECASE))
                                if _temp_zip_dir.endswith("_zip") and os.path.exists(_temp_zip_dir):
                                    # TODO 反向转换zip包内的zip压缩文件（递归解决）
                                    # 压缩成zip
                                    _temp_zip_file = re.sub(r'_zip$', "", _temp_zip_dir, flags=re.IGNORECASE) + ".zip"
                                    ZipUtil.zip_dir(_temp_zip_dir, _temp_zip_file)
                                    FileUtil.remove_file(_temp_zip_dir)
                                FileUtil.remove_file(temp_path)
                        else:
                            if self.file_to_gz:
                                # gz 直接解压为文件
                                GzUtil.gz_to_file(temp_path)
                                FileUtil.remove_file(temp_path)
                    # 逆向结束 ]]

                    # 如果为 zip 文件，解压后，压缩为 gz
                    # 正向压缩 [[
                    if (not self.recover) and self.zip_to_gz and ext == "zip":
                        self.logger.info("zip to gz: " + temp_path)
                        """
                        1. 解压
                        2. tar.gz压缩
                        3. 删除zip
                        """
                        temp_zip_dir = re.sub(r'\.zip$', "", temp_path, flags=re.IGNORECASE) + "_zip"
                        ZipUtil.un_zip(temp_path, temp_zip_dir)
                        # TODO 转换zip包内的zip压缩文件（递归解决）
                        temp_gz_file = temp_zip_dir + ".tar.gz"
                        GzUtil.make_tar_gz(temp_zip_dir, temp_gz_file)
                        FileUtil.remove_file(temp_zip_dir)
                        FileUtil.remove_file(temp_path)
                    if (not self.recover) and self.file_to_gz and ext != "zip" and ext != 'gz':
                        GzUtil.file_to_gz(temp_path, temp_path + ".gz")
                        FileUtil.remove_file(temp_path)
                    # 正向压缩 ]]
            pass
        pass

    def func_loop_dir_names(self, arr_analysis, loop_dir_path, loop_dir_names,
                            _rows, _pc, _description, _batch_no, _curr_path, _root_path, _level, logger):
        for child_dir_name in loop_dir_names:
            temp_path = os.path.join(loop_dir_path, child_dir_name)
            real_path = os.path.realpath(temp_path)
            if temp_path == real_path:
                arr = self.get_statistic_row(_rows, _pc, _description,
                                             _batch_no, temp_path,
                                             _root_path,
                                             _level + 1,
                                             logger)
                # file_num += arr[0]
                arr_analysis[0] += arr[0]
                # dir_num += arr[1]
                arr_analysis[1] += arr[1]
                # file_size += arr[2]
                arr_analysis[2] += arr[2]
                # zero_num += arr[3]
                arr_analysis[3] += arr[3]
                # _dir_num += 1
                arr_analysis[5] += 1

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
        '''
        file_num = 0    # all
        dir_num = 0     # all
        file_size = 0   # all
        zero_num = 0    # all
        _file_num = 0  # 文件数
        _dir_num = 0  # 文件夹数
        _file_size = 0  # 文件大小和
        _zero_num = 0  # 空文件数
        
        arr_analysis = 
            [file_num_all, dir_num_all, file_size_all, zero_num_all, _file_num, _dir_num, _file_size, _zero_num] 
        '''
        arr_analysis = [0, 0, 0, 0, 0, 0, 0, 0]
        _logger.debug("start - %s" % _curr_path)
        for loop_dir_path, loop_dir_names, loop_file_names in os.walk(_curr_path, followlinks=False):
            # _file_num = loop_file_names.__len__() #会统计快捷方式
            # _dir_num = loop_dir_names.__len__() #会统计快捷方式
            if len(loop_file_names) > 0:
                # 遍历文件
                self.func_loop_file_names(arr_analysis, loop_dir_path, loop_file_names)
            if len(loop_dir_names) > 0:
                self.func_loop_dir_names(arr_analysis, loop_dir_path, loop_dir_names,
                                         _rows, _pc, _description, _batch_no, _curr_path, _root_path, _level, logger)
            # file_num += _file_num
            arr_analysis[0] += arr_analysis[4]
            # dir_num += _dir_num
            arr_analysis[1] += arr_analysis[5]
            # file_size += _file_size
            arr_analysis[2] += arr_analysis[6]
            # zero_num += _zero_num
            arr_analysis[3] += arr_analysis[7]
            break  # 只用遍历一层，子层递归会解决
        if _level <= self.max_level:
            _dir_name = os.path.basename(_curr_path)
            _dir_path = os.path.abspath(_curr_path)
            _parent_path = os.path.abspath(os.path.dirname(_curr_path) + os.path.sep + ".")
            # 单行记录
            _row = [_pc, _description, _batch_no, _dir_name, _dir_path, _parent_path, _root_path, _level,
                    arr_analysis[4],
                    arr_analysis[0], arr_analysis[5], arr_analysis[1], FileUtil.format2MB(arr_analysis[6]),
                    FileUtil.format2MB(arr_analysis[2]), arr_analysis[7], arr_analysis[3],
                    (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')]
            _rows.append(_row)
            self.total_num += 1
            if _rows.__len__() == 500:
                temp_rows = _rows.copy()
                CsvUtil.write(self.work_csv, [], temp_rows)
                self.logger.info("csv export 500.")
                _rows.clear()
        arr = [arr_analysis[0], arr_analysis[1], arr_analysis[2], arr_analysis[3]]
        _logger.debug("end - %s ,%s" % (_curr_path, _row))
        self.trace_num += 1
        if self.trace_num % 10000 == 0:
            _logger.info("current trace num: %d %s" % (self.trace_num, _curr_path))
        return arr

    '''
    对象初始化   [[
    '''

    def init_log(self):
        """ 日志初始化 """
        # if logger is None:
        # logging.basicConfig(level=logging.DEBUG, format='%(lineno)d %(asctime)s - %(name)s - %(levelname)s - %(
        # message)s', filename=os.path.abspath(os.path.join(self.project_path, 'logs', (self.batch_no + '.log'))))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        log_path = os.path.abspath(os.path.join(self.project_path, 'logs'))
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(name)s - %('
                                      'levelname)s: %(message)s')
        fh = logging.FileHandler(
            r'' + os.path.abspath(os.path.join(self.project_path, 'logs',
                                               (self.batch_no + '.log'))),
            encoding='utf-8')  # 日志文件路径文件名称，编码格式
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # console log 控制台输出控制
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        # else:
        #     self.logger = logger.getChild(curr_package)
        pass

    def init_config(self):
        """ 配置初始化 """
        # 实例化configParser对象
        # read读取ini文件
        self.config.read(os.path.abspath(os.path.join(self.project_path, "config\\config.ini")), encoding='UTF-8')
        pass

    def init_intro(self):
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
        pass

    def init_variate(self):
        """ 变量初始化 """
        # 检查配置文件
        # -sections得到所有的section，并以列表的形式返回
        self.root_path = ConfigUtil.get(self.config, 'TARGET', 'root_path', self.logger)
        self.max_level = ConfigUtil.getint(self.config, 'TARGET', 'max_level', self.logger)
        self.pc = ConfigUtil.get(self.config, 'TARGET', 'pc', self.logger)
        self.description = ConfigUtil.get(self.config, 'TARGET', 'description', self.logger)
        self.work_path = ConfigUtil.get(self.config, 'WORK_SPACE', 'work_path', self.logger)

        self.file_to_gz = ConfigUtil.getboolean(self.config, 'control', 'file_to_gz', self.logger)
        self.zip_to_gz = ConfigUtil.getboolean(self.config, 'control', 'zip_to_gz', self.logger)
        self.delete_zero_file = ConfigUtil.getboolean(self.config, 'control', 'delete_zero_file', self.logger)
        self.recover = ConfigUtil.getboolean(self.config, 'control', 'recover', self.logger)

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
        pass

    '''
    对象初始化   ]]
    '''
