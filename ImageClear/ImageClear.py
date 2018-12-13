#!/usr/bin/env python
# encoding: utf-8

"""
__author__ = 'zhengyuxin'

"""

import argparse
import time
import os
import re

imageType_png="png"
imageType_jpg="jpg"
imageType_gif="gif"
imageType_imageset="imageset"

# 承载遍历到的所有的图片资源
images=[]

code_file_extension = [".h", ".m", ".pch", ".mm"]

ignores_pattern_str = r'.*(hardPredict_level).*'

# 单个图片资源对象模型
class Image(object):
    def __init__(self, name, type=None, path=None):
        self.name = name
        self.type = type
        self.path = path

    def __str__(self):
        return "name: {}, type: {}, path: {}".format(self.name, self.type, self.path)

def parse_args():
    parse = argparse.ArgumentParser()
    parse.add_argument("-p", "--path", required=True, help="项目路径")
    return parse.parse_args()


# 当前时间戳
def current_time_stamp():
    return time.time()

# 处理文件
def handle_file(path):

    file_name = path.split("/")[-1]
    subs = file_name.split('.')
    if len(subs) <= 0:
        return

    file_extension = subs[-1]
    name = subs[0]

    if file_extension == imageType_gif:
        images.append(Image(name, imageType_gif, path))
    elif file_extension == imageType_imageset:
        images.append(Image(name, imageType_imageset, path))
    elif file_extension == imageType_png:
        images.append(Image(name, imageType_png, path))
    elif file_extension == imageType_jpg:
        images.append(Image(name, imageType_jpg, path))
    else:
        return


# 处理 xcassets 文件中的图片
def find_image_in_xcassets(path):
    for sub in os.listdir(path):
        p = os.path.join(path, sub)
        if sub.find(".imageset") >= 0: #imageset 文件夹
            handle_file(p)
        elif os.path.isdir(p): #普通文件
            find_image_in_xcassets(p)
        else:
            handle_file(p)

# 发现所有的图片资源
def find_all_image_resuorces(path):

    if os.path.isfile(path):
        handle_file(path)
        return

    for ele in os.listdir(path):
        p = os.path.join(path, ele)
        if ele.rfind(".xcassets") != -1:  #xcassets 文件夹
            find_image_in_xcassets(p)
        elif os.path.isdir(p):
            find_all_image_resuorces(p)
        else:
            handle_file(p)

def create_map_table():
    dict = {}
    for image in images:
        dict[image.name] = image
    return dict

def find_match_string_in_file(path, map_table):

    global number_of_line

    fp = open(path)

    for line in fp.readlines():
        if line.startswith("//") or line.startswith('\n'):
            continue

        ma = re.findall(r'@"(\w*)"', line)

        if ma:
            for ele in ma:
                if map_table.has_key(ele):
                    map_table.pop(ele)

    fp.close()
    pass

# 处理文件
def read_all_code_file(path, map_table):

    # 如果当前是文件
    if os.path.isfile(path):
        file_name = os.path.splitext(path)[-2]
        file_ex = os.path.splitext(path)[-1]
        if file_ex in code_file_extension:
            find_match_string_in_file(path, map_table)
        return

    # 如果当前是文件夹
    if os.path.isdir(path):
        for p in os.listdir(path):
            read_all_code_file(os.path.join(path, p), map_table)

        return


    print "it's not file or dir {}".format(path)
    # raise RuntimeError("Path Error")


def main():
    args = parse_args()
    path = args.path

    t1 = current_time_stamp()
    find_all_image_resuorces(path)
    t2 = current_time_stamp()
    print "find all image resource time: {}s".format(t2 - t1)

    dict = create_map_table()

    read_all_code_file(path, dict)

    t3 = current_time_stamp()

    print "read all file time: {}s".format(t3 - t2)

    print "unused image resources:"

    for key, value in dict.items():
        res = re.match(ignores_pattern_str, key)
        if res:
            continue
        print value


if __name__ == '__main__':
    main()



