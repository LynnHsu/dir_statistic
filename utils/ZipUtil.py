import os
import re
import zipfile

# 解压到指定目录
from utils import FileUtil


def names_solve(folder_path):
    for dir_path, dir_names, file_names in os.walk(folder_path):  # 进入需要改正名字的文件夹
        for filename in file_names:
            try:
                new_filename = filename.encode('cp437').decode('gbk')  # 尝试对文件名字进行编码解码
                file_full_path = os.path.join(dir_path, filename)  # 如果成功，则将文件原始路径算出
                if os.path.exists(file_full_path):
                    new_file_full_path = os.path.join(dir_path, new_filename)
                    os.rename(file_full_path, new_file_full_path)  # 将名字进行替换
            except Exception as ex:
                print(ex)
                print('文件更名失败!')
        for dir_name in dir_names:
            try:
                new_dir_name = dir_name.encode('cp437').decode('gbk')
                dir_full_path = os.path.join(dir_path, dir_name)
                if os.path.exists(dir_full_path):
                    new_dir_full_path = os.path.join(dir_path, new_dir_name)
                    os.rename(dir_full_path, new_dir_full_path)  # 将名字进行替换
            except:
                print('文件夹更名失败!')


def un_zip(src_zip, des_dir=None):
    """
    解压zip
    :param src_zip: zip文件名
    :param des_dir: 指定目录
    :return:
    """
    if des_dir is None:
        des_dir = re.sub(r'\.zip$', "", src_zip, flags=re.IGNORECASE)
    if not os.path.isdir(des_dir):
        os.makedirs(des_dir)
    zip_file = zipfile.ZipFile(src_zip)
    for names in zip_file.namelist():
        zip_file.extract(names, des_dir)
    zip_file.close()
    names_solve(des_dir)  # 中文文件名转义


# zip压缩文件夹，将srcPath下的文件内容压缩到根目录下
def zip_dir(srcPath, targetZipFile):
    root_path = srcPath  # 要压缩的文件夹路径
    file_news = targetZipFile  # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)  # 参数一：文件夹名
    if os.path.isfile(root_path):
        parent_path = os.path.dirname(root_path)
        filename = os.path.basename(root_path)
        file_path = parent_path.replace(os.path.dirname(root_path), '')  # 这一句很重要，不replace的话，就从根目录开始复制
        file_path = file_path and file_path + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        z.write(os.path.join(parent_path, filename), file_path + filename)
    else:
        for dir_path, dir_names, file_names in os.walk(root_path):
            file_path = dir_path.replace(root_path, '')  # 这一句很重要，不replace的话，就从根目录开始复制
            file_path = file_path and file_path + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
            for filename in file_names:
                z.write(os.path.join(dir_path, filename), file_path + filename)
    z.close()


# zip_dir(r"D:\dir_statistic_work1\dir_statistic_work\dev-portal-hub-NO_20200918101105.csv", "D:\\3335.zip")
un_zip("D:\\1\\22.zip", "d:\\1\\22_zip")
# un_zip("D:\\1\\22.zip")
zip_dir("d:\\1\\22_zip", "D:\\1\\221.zip")
