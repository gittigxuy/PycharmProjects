# -*- coding: utf-8 -*-
# @Time    : 18-6-18 下午4:12
# @Author  : unicoe
# @Email   : unicoe@163.com
# @File    : merge_txt.py
# @Software: PyCharm Community Edition


rf = open("/home/user/PycharmProjects/handle_result/6_25/handle_result/5_28_original_det_test_person.txt")
wf = open("/home/user/PycharmProjects/handle_result/6_25/handle_result/merge_result_upper_528person.txt","a+")

content = rf.readline()

while content:

    info = content.strip("\n").split(" ")

    for idx in info:
        wf.write(str(idx))
        wf.write(" ")
    wf.write("\n")
    content = rf.readline()

print "merge done~"