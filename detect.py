import tensorflow as tf
import cv2

from model.yolo import YOLOv3
from utils.utils import load_class_names, draw_boxes_frame


def detect(path, iou_threshold, confidence_threshold):
    class_names, n_classes = load_class_names()
    model = YOLOv3(
        n_classes=n_classes,
        iou_threshold=iou_threshold,
        confidence_threshold=confidence_threshold
    )
    inputs = tf.placeholder(tf.float32, [1, *model.input_size, 3])
    detections = model(inputs)
    saver = tf.train.Saver(tf.global_variables(scope=model.scope))

    with tf.Session() as sess:
        saver.restore(sess, './weights/model.ckpt')
        # cv2.namedWindow('Detection')
        video = cv2.VideoCapture(path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        outfile_name = f'./results/detection_for_{path}.mp4'
        out = cv2.VideoWriter(outfile_name, fourcc, fps, frame_size)
        print(f'Video will be saved at {outfile_name}')
        print('Press q to quit')
        while True:
            retval, frame = video.read()
            if not retval:
                break
            resized_frame = cv2.resize(frame, dsize=tuple((x) for x in model.input_size[::-1]),
                                       interpolation=cv2.INTER_NEAREST)
            result = sess.run(detections, feed_dict={inputs: [resized_frame]})
            draw_boxes_frame(frame, frame_size, result, class_names, model.input_size)
            # cv2.imshow('Detections', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            out.write(frame)
        cv2.destroyAllWindows()
        video.release()
