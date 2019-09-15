from rknn.api import RKNN

def category_confirm(label):
    if label > 0 and label < 6:
        return '水果'

def load_model():
    rknn = RKNN()
    print('-->loading model')
    rknn.load_rknn('./mobilenet_v2.rknn')
    print('-->Init runtime environment')
    ret = rknn.init_runtime(target='rk3399pro')
    if ret != 0:
        print('Init runtime enviroment failed')
        exit(ret)
    return rknn
