#!/usr/bin/python
# -*- coding: UTF-8 -*-

# gz： 即gzip。通常仅仅能压缩一个文件。与tar结合起来就能够实现先打包，再压缩。
#
# tar： linux系统下的打包工具。仅仅打包。不压缩
#
# tgz：即tar.gz。先用tar打包，然后再用gz压缩得到的文件
#
# zip： 不同于gzip。尽管使用相似的算法，能够打包压缩多个文件。只是分别压缩文件。压缩率低于tar。
#
# rar：打包压缩文件。最初用于DOS，基于window操作系统。

# 当前类使用前提：tar.gz本质上是文件夹的压缩包，.gz是单个文件的压缩包

import gzip
import os
import re
import tarfile

from utils import FileUtil


# 压缩tar.gz包
def make_tar_gz(source_dir, output_filename):
    """
    一次性打包整个根目录。空子目录会被打包。
    如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。

    :param source_dir: 源文件夹
    :param output_filename: 最终结果文件名
    :return:
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    tar.close()


def make_tar_gz_unEmptyDir(source_dir, output_filename):
    """
    逐个添加文件打包，未打包空子目录。可过滤文件。
    如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。

    :param source_dir:
    :param output_filename:
    :return:
    """
    tar = tarfile.open(output_filename, "w:gz")
    for root, dir_names, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            tar.add(file_path, arcname=file)
    tar.close()


def unzip_tar_gz(src_dir, des_dir=None, src_root=None, isDelete=False):
    """
    递归解压文件夹内的tar.gz
    解压tar gz文件
    全部解压，不为tar.gz的直接迁移

    :param src_dir: dir - 则解压所有dir的
    :param des_dir: 目标文件夹
    :param src_root: 源文件的根目录，用于确认当前文件的深度
    :param isDelete: 解压之后删除源文件
    :return:
    """
    if not os.path.exists(src_dir):
        raise ValueError("src dir not exists.")
    if src_root is None:
        src_root = src_dir
    if not os.path.isdir(src_dir):  # 是文件，非文件夹
        # 解压特定文件
        if src_dir.lower().endswith(".tar.gz"):
            temp_dir_file = re.sub(r'\.tar\.gz$', "", src_dir, flags=re.IGNORECASE)
            if des_dir is not None:
                temp_dir_file = os.path.join(des_dir)   # 解压到指定目录
            f = tarfile.open(src_dir)
            names = f.getnames()
            for name in names:
                f.extract(name, path=temp_dir_file)
            f.close()
        else:
            # 不为空，文件则迁移
            if des_dir is not None:
                FileUtil.copy_children_cover(src_dir, des_dir)
    else:
        files = os.listdir(src_dir)
        for file in files:
            dir_tmp = os.path.join(src_dir, file)
            new_path = dir_tmp.replace(src_root, des_dir)
            parent_path = os.path.dirname(new_path)
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
            unzip_tar_gz(dir_tmp, parent_path, src_root)

    if isDelete:
        FileUtil.remove_file(src_dir)
    return temp_dir_file


# 单文件压缩
def file_to_gz(source_file, gz_file=None):
    if gz_file is None:
        gz_file = source_file + '.gz'
    if gz_file is not None and gz_file.lower().endswith(".gz") and not gz_file.lower().endswith(".tar.gz"):
        f_in = open(source_file, "rb")  # 打开文件
        f_out = gzip.open(gz_file, "w")  # 创建压缩文件对象
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
    else:
        raise ValueError("out file name: " + source_file + ". is endswith '.gz'")


def gz_to_file(source_file, output_file=None):
    if source_file is not None and source_file.lower().endswith(".gz") and not source_file.lower().endswith(".tar.gz"):
        f = gzip.open(source_file, 'rb')  # 打开压缩文件对象
        if output_file is None:
            # output_file = os.path.splitext(source_file)[0]    # 获取文件名
            output_file = re.sub(r'\.gz$', "", source_file, flags=re.IGNORECASE)
        f_out = open(output_file, "w")  # 打开解压后内容保存的文件
        file_content = f.read()  # 读取解压后文件内容
        f_out.write(file_content.decode("utf-8"))  # 写入新文件当中
        f.close()  # 关闭文件流
        f_out.close()
    else:
        raise ValueError("source file name: " + source_file + ". is endswith '.gz'")
