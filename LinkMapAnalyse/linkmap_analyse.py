#!/usr/bin/env python
# coding=utf-8

import argparse
import os
import time

def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", required=True, help="linkmap path")
    return parser.parse_args()

# 展示全部的依赖库
def out_all_lib_with_file(path):
    fp = open(path)
    libArr = {}

    for line in fp.readlines():
        # 到此结束
        if line.startswith('# Sections:'):
            break
        if line.startswith('#'):
            continue

        fileIndex = line.find(']')
        fileIndexText = line[0: fileIndex + 1]

        fileName = line[fileIndex + 2: -1]

        endIndex = fileName.rfind('(')

        if endIndex != -1:
            fileName = fileName[0:endIndex]
        else:
            if fileName.rfind('tbd') != -1:
                pass
            elif fileName.rfind('framework') != -1:
                endIndex = fileName.rfind('/')
                fileName = fileName[0: endIndex]
                pass
            else:
                endIndex = fileName.rfind('/')
                if endIndex != -1:
                    fileName = fileName[0: endIndex]

        libArr[fileIndexText] = fileName
    fp.close()
    return libArr

def out_all_lib_size_with_file(path, libDict):
    fp = open(path)
    lib_size_dict = {}

    index = 0

    for line in fp.readlines():

        lineArr = line.split('\t')

        if len(lineArr) < 2 or not lineArr[1].startswith('0x'):
            continue

        if line.startswith('<<dead>>'):
            continue

        size = int(lineArr[1], 16)
        name = lineArr[2]

        if size <= 0 or name.find(']') == -1:
            continue

        name = lineArr[2][0: name.find(']') + 1]
        lib_name = libDict.get(name)
        totalSize = lib_size_dict.get(lib_name)

        if not totalSize:
            totalSize = size
        else:
            totalSize += size

        lib_size_dict[lib_name] = totalSize

    fp.close()
    return lib_size_dict


def sotred_print_and_save(dict, save_path):

    sortedLists = sorted(dict.items(), key=lambda x: x[1], reverse=True)

    total = 0

    print "%s" % "=".ljust(80, "=")
    print "%s" % "各模块体积".center(85)
    print "%s" % "=".ljust(80, "=")

    write_file = open(save_path, 'w')
    write_file.write("%s \n" % "=".ljust(80, "="))
    write_file.write("%s \n" % "各模块体积".center(85))
    write_file.write("%s \n" % "=".ljust(80, "="))

    for key, value in sortedLists:
        total += value
        print('%s %s' % (key[key.rfind('/') + 1:].ljust(50), convert_show_str_for_number(value)))
        write_file.write('%s %s \n' % (key[key.rfind('/') + 1:].ljust(50), convert_show_str_for_number(value)))

    print("%s %s" % ("total size".ljust(50), convert_show_str_for_number(total)))
    write_file.write("%s %s \n" % ("total size".ljust(50), convert_show_str_for_number(total)))
    write_file.close()
    print("%s %s" % ("file save to ", save_path))

def print_all_title(path):
    fp = open(path)
    for line in fp.readlines():
        if line.startswith('#'):
            print line
    fp.close()

def convert_show_str_for_number(value):
    kv = value / 1024.0
    if kv < 1024:
        return str(round(kv, 2)) + "KB"
    kv = kv / 1024.0
    return str(round(kv, 2)) + "MB"


def main():
    args = parse_arg()
    path = args.path

    if not os.path.isfile(path):
        print "path is not a file"
        return
    print args.path

    libs = out_all_lib_with_file(path)

    lib_size_dict = out_all_lib_size_with_file(path, libs)

    save_path = os.path.dirname(path) + "/" + os.path.basename(path).split('.')[0] + "_analyse_" + str(int(time.time())) + ".txt"

    sotred_print_and_save(lib_size_dict, save_path)


if __name__ == '__main__':
    main()