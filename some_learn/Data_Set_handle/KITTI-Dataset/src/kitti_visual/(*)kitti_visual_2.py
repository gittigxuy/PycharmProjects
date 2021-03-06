#--coding:utf-8--
import os
import cv2
import matplotlib.pyplot as plt

def mkdir(path):
    import os

    path = path.strip()
    path = path.rstrip("\\")

    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print path + 'ok'
        return True
    else:

        print path + 'failed!'
        return False

def generate_result(resource_path):
    """
    :param path:
    :return:
    """
    rf = open(resource_path)

    content = rf.readline()
    cnt = 0
    tmp_dict = {}

    while content:
        #print content

        res = content.replace("\n", "").split(" ")
        cls  = str(res[0:1][0])
        bbox = res[1:6]

        if cls in tmp_dict:
            tmp_dict[cls].append(bbox)
        else:
            tmp_dict[cls] = [bbox]
            cnt += 1

        content = rf.readline()
    rf.close()
    return tmp_dict

def draw_bbox(tmp_dict):

    bbox_cnt = 0
    img_cnt = 0
    undet_img = []


    cur_path = "/home/user/Disk1.8T/data_set/KITTI/testing/image_2"
    dirList = []
    files = os.listdir(cur_path)

    for file in files:
        tmp_path = cur_path + "/" + file
        dirList.append(tmp_path)

    #获取当前图片的绝对路径，然后进行处理
    for idx_im in dirList:
        all_str = idx_im
        inDict = all_str.split("/")
        bot = inDict[-1][:-4]
        inDict_name = bot

        if inDict_name in tmp_dict :

            bboxList = tmp_dict[inDict_name]
            im = cv2.imread(all_str)

            flag = 0

            for idx_bbox in bboxList:

                x1 = int(float(idx_bbox[1]))
                y1 = int(float(idx_bbox[2]))
                x2 = int(float(idx_bbox[3]))
                y2 = int(float(idx_bbox[4]))

                if float(idx_bbox[0]) >= 0.1:
                    flag = 1
                    bbox_cnt = bbox_cnt + 1
                    cv2.rectangle(im, (x1, y1), (x2, y2), (0, 255, 0), 1)
                    cv2.rectangle(im, (x1, y1), (x1 + 20, y1 - 10), (0, 255, 0), -1)
                    cv2.putText(im, str(float(idx_bbox[0]))[:4], (x1, y1), 0, 0.3, (0, 0, 0), 1)

            if flag == 1:
                img_cnt = img_cnt + 1
                mkdir('/home/user/Disk1.8T/draw_result/kitti/test_11_23_Fri_04_27./' + str(inDict[-3] + '/' + inDict[-2]))
                cv2.imwrite('/home/user/Disk1.8T/draw_result/kitti/test_./' +
                            str(inDict[-3] + '/' + inDict[-2]) + '/' + bot + ".png",
                            im)
            else:
                undet_img.append(bot)

    #print str(undet_img)
    w_undet = open("/home/user/PycharmProjects/some_learn/Data_Set_handle/KITTI-Dataset/src/visual_test/un_det_test_11_23_Fri_04_27.txt", "w")

    for idx in undet_img:
        w_undet.write(idx)
        w_undet.write("\n")

    w_undet.write("un_det " + str(len(undet_img)))
    w_undet.write("bbox: " + str(bbox_cnt))
    w_undet.write("img " + str(img_cnt))
    w_undet.close()

    print "un_det " + str(len(undet_img))
    print "bbox: " + str(bbox_cnt)
    print "img " + str(img_cnt)


def str2float_in_list(str_list):
    import re
    float_reg = re.compile(r'^\d+\.\d+$')
    float_list = [float(f) for f in str_list if float_reg.match(f)]

    return float_list


file_path = "/home/user/Disk1.8T/KITTI-experiments/det_result/11_23/5_part_psroi_915_trainval/2018_11_23_Fri_04_27_09_det_test_person.txt"
dec_result = generate_result(file_path)

draw_bbox(dec_result)