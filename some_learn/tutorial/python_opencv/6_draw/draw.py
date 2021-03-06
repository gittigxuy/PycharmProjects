# -*- coding: utf-8 -*-
# @Time    : 18-6-6 上午11:40
# @Author  : unicoe
# @Email   : unicoe@163.com
# @File    : draw.py
# @Software: PyCharm Community Edition

import numpy as np
import cv2

img = np.zeros((512,512,3), np.uint8)
cv2.line(img, (0,0), (511,511), (255,0,0), 5)
cv2.rectangle(img, (384,0), (510,128),(0,255,0),3)
cv2.circle(img, (447,63), 63, (0,0,255), -1)
cv2.ellipse(img, (256,256), (100,500),0,0,180,255,-1)

cv2.imshow("example",img)
cv2.waitKey(0)
cv2.destroyAllWindows()