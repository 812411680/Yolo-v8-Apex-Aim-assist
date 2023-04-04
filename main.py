import argparse
from screenshots import *
import time
from pynput import mouse, keyboard
from MyListener import listen_key, listen_mouse, get_S_L, Mouse_redirection, Move_Mouse
from predict import *
from args_ import *
from threading import Thread
from multiprocessing import Process, Pipe, Value
from show_target import Show_target
import numpy as np

global Start_detection, Listen
# Start listen the right mouse button and the esc
def listeners():
    # key_listener = keyboard.Listener(on_press=listen_key)
    # key_listener.start()

    mouse_listener = mouse.Listener(on_click=listen_mouse)
    mouse_listener.start()
    print("listener start")
    mouse_listener.join()

count=0
interval=0.03
if __name__ == "__main__":
    # create a arg set
    Listen=True

    args = argparse.ArgumentParser()
    args = arg_init(args)

    process1 = Thread(
        target=listeners,
        args=(),
    )
    process1.start()

    Mouse_mover = Thread(target=Move_Mouse, args=(args,), name="Mouse_mover")
    Mouse_mover.start()

    predict_init(args)
    print("Main start")
    time_start = time.time()
    while Listen:
        
        Start_detection, Listen = get_S_L()
        # take a screenshot
        img=take_shots(args)
        #print("shots time: ", time.time() - time_start)
        # predict the image
        predict_res = predict(args,img)
        #print("shot+predict time: ", time.time() - time_start)
        time.sleep(args.wait)
        boxes = predict_res.boxes
        boxes = boxes[boxes[:].cls == args.target_index]
        boxes = boxes.cpu()
        boxes = boxes[:].xyxy
        boxes = boxes.numpy()
        if boxes.shape[0] == 0:
            boxes = np.array([[-1, -1, -1, -1]])
        if Start_detection :
            if boxes.shape[0] > 0:
                Mouse_redirection(boxes, args, interval)
        #print("total time: ", time.time() - time_start)
        count+=1

        if(count%100==0):        
            time_per_100frame = time.time() - time_start
            time_start = time.time()
            print("fps: ", count/time_per_100frame)
            interval=time_per_100frame/count
            print(interval)
            count=0
        

    print("main over")
