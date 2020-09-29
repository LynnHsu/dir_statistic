#!/usr/bin/python
# -*- coding: UTF-8 -*-


# 文件大小格式化， M
import os
import shutil


def format2MB(byte_size):
    return round(byte_size / float(1024 * 1024), 2)


def copy_children_cover(src, dist):
    if src is None or src == "":
        print("src is None, can`t copy.")
    else:
        if not os.path.isdir(src):
            child_path = src
            if not os.path.exists(dist):
                os.makedirs(dist)
            shutil.copyfile(child_path, os.path.join(dist, os.path.basename(child_path)))
        else:
            for dirPath, dirNames, fileNames in os.walk(src):
                if len(fileNames) > 0:
                    for fileName in fileNames:
                        child_path = os.path.join(dirPath, fileName)
                        new_path = child_path.replace(src, dist)
                        parent_path = os.path.dirname(new_path)
                        if not os.path.exists(parent_path):
                            os.makedirs(parent_path)
                        if os.path.isfile(child_path):
                            copy_children_cover(child_path, parent_path)
                        else:
                            shutil.copytree(child_path, new_path)


# 删除文件/文件夹
def remove_file(path):
    if path is None or path == "":
        return 0
    else:
        if not os.path.exists(path):
            return -1
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.removedirs(path)
