# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# Modified by yszhu
# --------------------------------------------------------

"""Train a Fast R-CNN network."""

import caffe
from fast_rcnn.config import cfg
import roi_data_layer.roidb as rdl_roidb
from utils.timer import Timer
import numpy as np
import os

from caffe.proto import caffe_pb2
import google.protobuf as pb2

import google.protobuf.text_format

class SolverWrapper(object):
    """A simple wrapper around Caffe's solver.
    This wrapper gives us control over he snapshotting process, which we
    use to unnormalize the learned bounding-box regression weights.
    """

    def __init__(self, solver_prototxt, roidb, output_dir,
                 pretrained_model=None):
        """Initialize the SolverWrapper."""
        self.output_dir = output_dir

        if (cfg.TRAIN.HAS_RPN and cfg.TRAIN.BBOX_REG and
            cfg.TRAIN.BBOX_NORMALIZE_TARGETS):
            # RPN can only use precomputed normalization because there are no
            # fixed statistics to compute a priori
            assert cfg.TRAIN.BBOX_NORMALIZE_TARGETS_PRECOMPUTED

        if cfg.TRAIN.BBOX_REG:
            print 'Computing bounding-box regression targets...'
            self.bbox_means, self.bbox_stds = \
                    rdl_roidb.add_bbox_regression_targets(roidb)
            print 'done'

        self.solver = caffe.SGDSolver(solver_prototxt)
        if pretrained_model is not None:
            print ('Loading pretrained model '
                   'weights from {:s}').format(pretrained_model)
            self.solver.net.copy_from(pretrained_model)

        self.solver_param = caffe_pb2.SolverParameter()
        with open(solver_prototxt, 'rt') as f:
            pb2.text_format.Merge(f.read(), self.solver_param)

        self.solver.net.layers[0].set_roidb(roidb)

    def snapshot(self):
        """Take a snapshot of the network after unnormalizing the learned
        bounding-box regression weights. This enables easy use at test-time.
        """
        net = self.solver.net

	# faster_rcnn
        scale_bbox_params_faster_rcnn = (cfg.TRAIN.BBOX_REG and
                             cfg.TRAIN.BBOX_NORMALIZE_TARGETS and
                             net.params.has_key('bbox_pred'))

	# rfcn
        #scale_bbox_params_rfcn = (cfg.TRAIN.BBOX_REG and
        #                     cfg.TRAIN.BBOX_NORMALIZE_TARGETS and
        #                     net.params.has_key('rfcn_bbox'))

	# rfcn multi_branch
        scale_bbox_params_rfcn = (cfg.TRAIN.BBOX_REG and
                             cfg.TRAIN.BBOX_NORMALIZE_TARGETS and
                             net.params.has_key('rfcn_bbox_p3'))

	# rpn
        #scale_bbox_params_rpn = (cfg.TRAIN.RPN_NORMALIZE_TARGETS and
        #                         net.params.has_key('rpn_bbox_pred'))

	# rpn for multi_branch
        scale_bbox_params_rpn = (cfg.TRAIN.RPN_NORMALIZE_TARGETS and
                                 net.params.has_key('rpn_bbox_pred_p3'))

	# coupleNet
        scale_bbox_params_couplenet = (cfg.TRAIN.BBOX_REG and
                                  cfg.TRAIN.BBOX_NORMALIZE_TARGETS and
                                  net.params.has_key('global_bbox_pred') and
                                  net.params.has_key('local_bbox'))

        if scale_bbox_params_faster_rcnn: # faster_rcnn
            # save original values
            orig_0 = net.params['bbox_pred'][0].data.copy()
            orig_1 = net.params['bbox_pred'][1].data.copy()

            # scale and shift with bbox reg unnormalization; then save snapshot
            net.params['bbox_pred'][0].data[...] = \
                    (net.params['bbox_pred'][0].data *
                     self.bbox_stds[:, np.newaxis])
            net.params['bbox_pred'][1].data[...] = \
                    (net.params['bbox_pred'][1].data *
                     self.bbox_stds + self.bbox_means)

        #if scale_bbox_params_rpn: # rpn
        #    rpn_orig_0 = net.params['rpn_bbox_pred'][0].data.copy()
        #    rpn_orig_1 = net.params['rpn_bbox_pred'][1].data.copy()
        #    num_anchor = rpn_orig_0.shape[0] / 4
        #    # scale and shift with bbox reg unnormalization; then save snapshot
        #    self.rpn_means = np.tile(np.asarray(cfg.TRAIN.RPN_NORMALIZE_MEANS),
        #                              num_anchor)
        #    self.rpn_stds = np.tile(np.asarray(cfg.TRAIN.RPN_NORMALIZE_STDS),
        #                             num_anchor)
        #    net.params['rpn_bbox_pred'][0].data[...] = \
        #        (net.params['rpn_bbox_pred'][0].data *
        #         self.rpn_stds[:, np.newaxis, np.newaxis, np.newaxis])
        #    net.params['rpn_bbox_pred'][1].data[...] = \
        #        (net.params['rpn_bbox_pred'][1].data *
        #         self.rpn_stds + self.rpn_means)

        if scale_bbox_params_rpn: # rpn
            rpn_orig_0_p2 = net.params['rpn_bbox_pred_p2'][0].data.copy()
            rpn_orig_1_p2 = net.params['rpn_bbox_pred_p2'][1].data.copy()
            num_anchor = rpn_orig_0_p2.shape[0] / 4
            # scale and shift with bbox reg unnormalization; then save snapshot
            self.rpn_means = np.tile(np.asarray(cfg.TRAIN.RPN_NORMALIZE_MEANS),
                                      num_anchor)
            self.rpn_stds = np.tile(np.asarray(cfg.TRAIN.RPN_NORMALIZE_STDS),
                                     num_anchor)
            net.params['rpn_bbox_pred_p2'][0].data[...] = \
                (net.params['rpn_bbox_pred_p2'][0].data *
                 self.rpn_stds[:, np.newaxis, np.newaxis, np.newaxis])
            net.params['rpn_bbox_pred_p2'][1].data[...] = \
                (net.params['rpn_bbox_pred_p2'][1].data *
                 self.rpn_stds + self.rpn_means)


            rpn_orig_0_p3 = net.params['rpn_bbox_pred_p3'][0].data.copy()
            rpn_orig_1_p3 = net.params['rpn_bbox_pred_p3'][1].data.copy()
            num_anchor = rpn_orig_0_p3.shape[0] / 4
            # scale and shift with bbox reg unnormalization; then save snapshot
            self.rpn_means = np.tile(np.asarray(cfg.TRAIN.RPN_NORMALIZE_MEANS),
                                      num_anchor)
            self.rpn_stds = np.tile(np.asarray(cfg.TRAIN.RPN_NORMALIZE_STDS),
                                     num_anchor)
            net.params['rpn_bbox_pred_p3'][0].data[...] = \
                (net.params['rpn_bbox_pred_p3'][0].data *
                 self.rpn_stds[:, np.newaxis, np.newaxis, np.newaxis])
            net.params['rpn_bbox_pred_p3'][1].data[...] = \
                (net.params['rpn_bbox_pred_p3'][1].data *
                 self.rpn_stds + self.rpn_means)



	    print 'bbbb'


        #if scale_bbox_params_rfcn: # rfcn
            # save original values
        #    orig_0 = net.params['rfcn_bbox'][0].data.copy()
        #    orig_1 = net.params['rfcn_bbox'][1].data.copy()
        #    repeat = orig_1.shape[0] / self.bbox_means.shape[0]

            # scale and shift with bbox reg unnormalization; then save snapshot
        #    net.params['rfcn_bbox'][0].data[...] = \
        #            (net.params['rfcn_bbox'][0].data *
        #             np.repeat(self.bbox_stds, repeat).reshape((orig_1.shape[0], 1, 1, 1)))
        #    net.params['rfcn_bbox'][1].data[...] = \
        #            (net.params['rfcn_bbox'][1].data *
        #             np.repeat(self.bbox_stds, repeat) + np.repeat(self.bbox_means, repeat))

        if scale_bbox_params_rfcn: # rfcn multi_branch

            # save original values
            orig_0_p2 = net.params['rfcn_bbox_p2'][0].data.copy()
            orig_1_p2 = net.params['rfcn_bbox_p2'][1].data.copy()
            repeat = orig_1_p2.shape[0] / self.bbox_means.shape[0]

            # scale and shift with bbox reg unnormalization; then save snapshot
            net.params['rfcn_bbox_p2'][0].data[...] = \
                    (net.params['rfcn_bbox_p2'][0].data *
                     np.repeat(self.bbox_stds, repeat).reshape((orig_1_p2.shape[0], 1, 1, 1)))
            net.params['rfcn_bbox_p2'][1].data[...] = \
                    (net.params['rfcn_bbox_p2'][1].data *
                     np.repeat(self.bbox_stds, repeat) + np.repeat(self.bbox_means, repeat))


            # save original values
            orig_0_p3 = net.params['rfcn_bbox_p3'][0].data.copy()
            orig_1_p3 = net.params['rfcn_bbox_p3'][1].data.copy()
            repeat = orig_1_p3.shape[0] / self.bbox_means.shape[0]

            # scale and shift with bbox reg unnormalization; then save snapshot
            net.params['rfcn_bbox_p3'][0].data[...] = \
                    (net.params['rfcn_bbox_p3'][0].data *
                     np.repeat(self.bbox_stds, repeat).reshape((orig_1_p3.shape[0], 1, 1, 1)))
            net.params['rfcn_bbox_p3'][1].data[...] = \
                    (net.params['rfcn_bbox_p3'][1].data *
                     np.repeat(self.bbox_stds, repeat) + np.repeat(self.bbox_means, repeat))


            # save original values

	    print 'aaaa'



        if scale_bbox_params_couplenet: # couplenet
            # save original values
            orig_0_7 = net.params['local_bbox'][0].data.copy()
            orig_1_7 = net.params['local_bbox'][1].data.copy()
            repeat_7 = orig_1_7.shape[0] / self.bbox_means.shape[0]

            # scale and shift with bbox reg unnormalization; then save snapshot
            net.params['local_bbox'][0].data[...] = \
                (net.params['local_bbox'][0].data *
                 np.repeat(self.bbox_stds, repeat_7).reshape((orig_1_7.shape[0], 1, 1, 1)))
            net.params['local_bbox'][1].data[...] = \
                (net.params['local_bbox'][1].data *
                 np.repeat(self.bbox_stds, repeat_7)) #+ np.repeat(self.bbox_means, repeat_7))

            # save original values
            orig_0_1 = net.params['global_bbox_pred'][0].data.copy()
            orig_1_1 = net.params['global_bbox_pred'][1].data.copy()
            repeat_1 = orig_1_1.shape[0] / self.bbox_means.shape[0]

            # scale and shift with bbox reg unnormalization; then save snapshot
            net.params['global_bbox_pred'][0].data[...] = \
                (net.params['global_bbox_pred'][0].data *
                 np.repeat(self.bbox_stds, repeat_1).reshape((orig_1_1.shape[0], 1, 1, 1)))
            net.params['global_bbox_pred'][1].data[...] = \
                (net.params['global_bbox_pred'][1].data *
                 np.repeat(self.bbox_stds, repeat_1) + np.repeat(self.bbox_means, repeat_1))

        infix = ('_' + cfg.TRAIN.SNAPSHOT_INFIX
                 if cfg.TRAIN.SNAPSHOT_INFIX != '' else '')
        filename = (self.solver_param.snapshot_prefix + infix +
                    '_iter_{:d}'.format(self.solver.iter) + '.caffemodel')
        filename = os.path.join(self.output_dir, filename)
        net.save(str(filename))
        print 'Wrote snapshot to: {:s}'.format(filename)

        if scale_bbox_params_faster_rcnn:
            # restore net to original state
            net.params['bbox_pred'][0].data[...] = orig_0
            net.params['bbox_pred'][1].data[...] = orig_1
        #if scale_bbox_params_rfcn:
            # restore net to original state
        #    net.params['rfcn_bbox'][0].data[...] = orig_0
        #    net.params['rfcn_bbox'][1].data[...] = orig_1
        if scale_bbox_params_rfcn:
            # restore net to original state
	    # ***********

            net.params['rfcn_bbox_p2'][0].data[...] = orig_0_p2
            net.params['rfcn_bbox_p2'][1].data[...] = orig_1_p2

            net.params['rfcn_bbox_p3'][0].data[...] = orig_0_p3
            net.params['rfcn_bbox_p3'][1].data[...] = orig_1_p3

        if scale_bbox_params_couplenet:
            # restore net to original state
            net.params['local_bbox'][0].data[...] = orig_0_7
            net.params['local_bbox'][1].data[...] = orig_1_7
            net.params['global_bbox_pred'][0].data[...] = orig_0_1
            net.params['global_bbox_pred'][1].data[...] = orig_1_1
        #if scale_bbox_params_rpn:
        #    # restore net to original state
        #    net.params['rpn_bbox_pred'][0].data[...] = rpn_orig_0
        #    net.params['rpn_bbox_pred'][1].data[...] = rpn_orig_1

        if scale_bbox_params_rpn:
            # restore net to original state
	    # ***********

            net.params['rpn_bbox_pred_p2'][0].data[...] = rpn_orig_0_p2
            net.params['rpn_bbox_pred_p2'][1].data[...] = rpn_orig_1_p2

            net.params['rpn_bbox_pred_p3'][0].data[...] = rpn_orig_0_p3
            net.params['rpn_bbox_pred_p3'][1].data[...] = rpn_orig_1_p3

        return filename

    def train_model(self, max_iters):
        """Network training loop."""
        last_snapshot_iter = -1
        timer = Timer()
        model_paths = []
        while self.solver.iter < max_iters:
            # Make one SGD update
            timer.tic()
            self.solver.step(1)
            timer.toc()
            if self.solver.iter % (10 * self.solver_param.display) == 0:
                print 'speed: {:.3f}s / iter'.format(timer.average_time)

            if self.solver.iter % cfg.TRAIN.SNAPSHOT_ITERS == 0:
                last_snapshot_iter = self.solver.iter
                model_paths.append(self.snapshot())

        if last_snapshot_iter != self.solver.iter:
            model_paths.append(self.snapshot())
        return model_paths

def get_training_roidb(imdb):
    """Returns a roidb (Region of Interest database) for use in training."""
    if cfg.TRAIN.USE_FLIPPED:
        print 'Appending horizontally-flipped training examples...'
        imdb.append_flipped_images()
        print 'done'

    print 'Preparing training data...'
    rdl_roidb.prepare_roidb(imdb)
    print 'done'

    return imdb.roidb

def filter_roidb(roidb):
    """Remove roidb entries that have no usable RoIs."""

    def is_valid(entry):
        # Valid images have:
        #   (1) At least one foreground RoI OR
        #   (2) At least one background RoI
        overlaps = entry['max_overlaps']
        # find boxes with sufficient overlap
        fg_inds = np.where(overlaps >= cfg.TRAIN.FG_THRESH)[0]
        # Select background RoIs as those within [BG_THRESH_LO, BG_THRESH_HI)
        bg_inds = np.where((overlaps < cfg.TRAIN.BG_THRESH_HI) &
                           (overlaps >= cfg.TRAIN.BG_THRESH_LO))[0]
        # image is only valid if such boxes exist
        valid = len(fg_inds) > 0 or len(bg_inds) > 0
        return valid

    num = len(roidb)
    filtered_roidb = [entry for entry in roidb if is_valid(entry)]
    num_after = len(filtered_roidb)
    print 'Filtered {} roidb entries: {} -> {}'.format(num - num_after,
                                                       num, num_after)
    return filtered_roidb

def train_net(solver_prototxt, roidb, output_dir,
              pretrained_model=None, max_iters=40000):
    """Train a Fast R-CNN network."""

    roidb = filter_roidb(roidb)
    sw = SolverWrapper(solver_prototxt, roidb, output_dir,
                       pretrained_model=pretrained_model)

    print 'Solving...'
    model_paths = sw.train_model(max_iters)
    print 'done solving'
    return model_paths
