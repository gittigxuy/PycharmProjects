#!/bin/bash
# Usage:
# ./experiments/scripts/rfcn_end2end_ohem.sh GPU NET DATASET [options args to {train,test}_net.py]
# DATASET is either pascal_voc or coco.
#
# Example:
# ./experiments/scripts/rfcn_end2end_ohem.sh 0 ResNet50 pascal_voc \
#   --set EXP_DIR foobar RNG_SEED 42 TRAIN.SCALES "[400, 500, 600, 700]"

set -x
set -e

export PYTHONUNBUFFERED="True"

GPU_ID=$1
NET=$2
NET_lc=${NET,,}
DATASET=$3

array=( $@ )
len=${#array[@]}
EXTRA_ARGS=${array[@]:3:$len}
EXTRA_ARGS_SLUG=${EXTRA_ARGS// /_}

case $DATASET in
  pascal_voc)
    TRAIN_IMDB="voc_0712_trainval"
    TEST_IMDB="voc_0712_test"
    PT_DIR="pascal_voc"
    ITERS=32000
    ;;
  coco)
    # This is a very long and slow training schedule
    # You can probably use fewer iterations and reduce the
    # time to the LR drop (set in the solver to 350,000 iterations).
    TRAIN_IMDB="coco_2014_train"
    TEST_IMDB="coco_2014_val"
    PT_DIR="coco"
    ITERS=1920000
    ;;
  *)
    echo "No dataset given"
    exit
    ;;
esac

LOG="experiments/11_13_dataset/logs/test_rfcn_end2end_${NET}_${EXTRA_ARGS_SLUG}.txt.`date +'%Y-%m-%d_%H-%M-%S'`"
exec &> >(tee -a "$LOG")
echo Logging output to "$LOG"

set +x
NET_FINAL=`tail -n 100 ${LOG} | grep -B 1 "done solving" | grep "Wrote snapshot" | awk '{print $4}'`
set -x

time ./tools/test_net.py --gpu ${GPU_ID} \
  --def experiments/11_13_dataset/model_ohem/multi_test.prototxt \
  --net output/11_13_dataset/model/voc_0712_trainval/fpn_rfcn_ohem_iter_8000.caffemodel \
  --imdb ${TEST_IMDB} \
  --cfg experiments/11_13_dataset/rfcn_end2end_ohem.yml \
  --set TEST.SOFT_NMS 0
  ${EXTRA_ARGS}
