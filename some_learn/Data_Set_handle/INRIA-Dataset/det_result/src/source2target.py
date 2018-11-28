# -*- coding: utf-8 -*-
# @Time    : 18-11-15 下午9:21
# @Author  : unicoe
# @Email   : unicoe@163.com
# @File    : source2target.py
# @Software: PyCharm
import copy
import numpy as np

# save img_shape to dict
def get_shape_dict():
    test_shape = open("/home/user/PycharmProjects/some_learn/Data_Set_handle"
              "/INRIA-Dataset/lst/test_img_shape.txt", "r")

    shape_dict = {}
    content = test_shape.readline()
    while content:


        im_info = content.strip("\n").split(" ")
        shape_dict[im_info[0]] = [int(im_info[1]), int(im_info[2])]           # h w

        content = test_shape.readline()

    return shape_dict

def get_source_dict(source_path):

    source_det = open(source_path, "r")

    content = source_det.readline()
    det_dict = {}
    while content:
        """
        set01_V000_I00280 0.266 256.2 84.5 394.1 417.3
        set01_V000_I00280 0.155 350.9 101.6 442.1 375.4
        
        0 set01_V000_I00280
        1 0.155
        2 3 4 5 bbox
        """
        det_info = content.strip("\n").split(" ")

        im_name = det_info[0]
        det_lst = []
        for idx in xrange(1,6):
            det_lst.append(float(det_info[idx]))

        if im_name in det_dict:
            det_dict[im_name].append(copy.copy(det_lst))
            pass
        else:

            det_dict[im_name] = [copy.copy(det_lst)]

        content = source_det.readline()
    return det_dict


def get_im_name_lst():
    r_test_shape = open("/home/user/PycharmProjects/some_learn/Data_Set_handle/"
              "INRIA-Dataset/lst/test_img_shape.txt", "r")

    content = r_test_shape.readline()
    im_name_lst = []
    while content:
        im_info = content.strip("\n").split(" ")
        im_name_lst.append(im_info[0])
        content = r_test_shape.readline()

    return im_name_lst

def handle_det(im_name_lst, det_dict, shape_dict):

    for im_idx in im_name_lst:
        if im_idx in det_dict:
            cur_shape = shape_dict[im_idx]
            im_w = cur_shape[1]
            im_h = cur_shape[0]

            min_size = min(im_w, im_h)
            max_size = max(im_w, im_h)

            """
            # Each scale is the pixel size of an image's shortest side
            __C.TEST.SCALES = (960,)
    
            # Max pixel size of the longest side of a scaled input image
            __C.TEST.MAX_SIZE = 1280
            """
            im_scale = float(960) / float(min_size)
            # Prevent the biggest axis from being more than MAX_SIZE
            if np.round(im_scale * max_size) > 1280:
                im_scale = float(1280) / float(max_size)

            sw = im_w * im_scale
            sh = im_h * im_scale

            r1 = 1280.0 / sw
            r2 = 960.0 / sh

            for bbox_item in det_dict[im_idx]:
                x1 = bbox_item[1]
                y1 = bbox_item[2]
                x2 = bbox_item[3]
                y2 = bbox_item[4]

                tw = bbox_item[3] - bbox_item[1]
                th = bbox_item[4] - bbox_item[2]
                #
                #
                #
                # b_w = min(tw, th)
                # b_h = max(tw, th)

                b_w = bbox_item[3] - bbox_item[1]
                b_h = bbox_item[4] - bbox_item[2]

                tmp_b_w = b_w/r1
                tmp_b_h = b_h/r2

                x_c = x1 + b_w/2.0
                y_c = y1 + b_h/2.0
                t_xc = x_c / r1
                t_yc = y_c / r2

                # t_x1 = t_xc - b_w/2.0
                # t_y1 = t_yc - b_h/2.0
                #
                # t_x2 = t_xc + b_w / 2.0
                # t_y2 = t_yc + b_h / 2.0

                t_x1 = t_xc - tmp_b_w / 2.0
                t_y1 = t_yc - tmp_b_h / 2.0

                t_x2 = t_xc + tmp_b_w / 2.0
                t_y2 = t_yc + tmp_b_h / 2.0

                bbox_item[1] = t_x1
                bbox_item[2] = t_y1
                bbox_item[3] = t_x2
                bbox_item[4] = t_y2
    return im_name_lst, det_dict

def save_target(im_name_lst, det_dict):

    save_name = "handle_" + target_idx.split("/")[-1]
    target_file = "/home/user/PycharmProjects/some_learn/Data_Set_handle/INRIA-Dataset/det_result/det/" + save_name

    save_target = open(target_file, "w")

    for im_idx in im_name_lst:
        if im_idx in det_dict:
            for bbox_idx in det_dict[im_idx]:
                save_target.write(im_idx)
                for xy_i in bbox_idx:
                    save_target.write(" ")
                    save_target.write(str(round(xy_i,4)))

                save_target.write("\n")
    save_target.close()


target_lst = [

'/home/user/PycharmProjects/some_learn/Data_Set_handle/INRIA-Dataset/det_result/det/1001-5.txt',

]

for target_idx in target_lst:
    shape_dict = get_shape_dict()
    source_dict = get_source_dict(target_idx)
    im_lst = get_im_name_lst()
    im_name_lst, det_dict = handle_det(im_name_lst=im_lst, det_dict=source_dict, shape_dict=shape_dict)
    save_target(im_name_lst, det_dict)
