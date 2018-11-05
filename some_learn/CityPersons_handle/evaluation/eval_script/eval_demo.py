from coco import COCO
from eval_MR_multisetup import COCOeval

annType = 'bbox'      #specify type here
print 'Running demo for *%s* results.'%(annType)

#initialize COCO ground truth api
annFile = '/home/user/PycharmProjects/some_learn/CityPersons_handle/evaluation/val_gt.json'
# initialize COCO detections api
resFile = '/home/user/PycharmProjects/some_learn/CityPersons_handle/evaluation/val_dt.json'

## running evaluation
res_file = open("/home/user/PycharmProjects/some_learn/CityPersons_handle/evaluation/results.txt", "w")
for id_setup in range(0,4):
    cocoGt = COCO(annFile)
    cocoDt = cocoGt.loadRes(resFile)
    imgIds = sorted(cocoGt.getImgIds())
    cocoEval = COCOeval(cocoGt,cocoDt,annType)
    cocoEval.params.imgIds  = imgIds
    cocoEval.evaluate(id_setup)
    cocoEval.accumulate()
    cocoEval.summarize(id_setup,res_file)

res_file.close()
