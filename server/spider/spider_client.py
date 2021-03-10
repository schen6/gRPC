import grpc
import os
import sys
import json

current_path = os.path.realpath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
sys.path.append(root_path)
import server.spider.spider_pb2 as spider_pb2
import server.spider.spider_pb2_grpc as spider_pd2_grpc


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('127.0.0.1:50052') as channel:
        stub = spider_pd2_grpc.SpiderStub(channel)

        # data = {'type': 'question', 'page': 1, 'kw': '开学'}
        # data = json.dumps(data, ensure_ascii=False)
        # response = stub.Zhihu(spider_pb2.Data(data=data))
        # print("Spider client received: " + response.result)

        cookie = 'did=web_343e77b758eb4c6298ca21c42338d7eb; didv=1609143454710; kpf=PC_WEB; kpn=KUAISHOU_VISION; clientid=3; userId=1529640684; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABVWrnLvAI96rYS3nup5ZKDXzZTzKw1xH2I3bOblSpgoQI93-j-yOG24CQ5lvoxb1os4FG9bN_-D_-iIIpu8x5zDonR-cihO9g63MhW7e4NuM5K3HFVvlXBd_-PnWy5SfIvwGwMHkOP6ufyajaMSzxr7XKMrFkEl0R2Bb0QfgSKPGeFS17Ret1YfCUlcWLkibO4k2DKMNprNalBcE-nMbLIhoSWXnZQFypWC8Fi7687FtZGgfDIiD6U64VZIDYS7-LTIKg4O-Iz24i9G17kZLwV-8GlkCzOCgFMAE; kuaishou.server.web_ph=8e211e489aac6053b5d64c3b3ddc02b78b52'
        data = {
            'type': 'video',
            'user_id': '3xydeseejbfdtwe',
            'cookie': cookie,
        }
        # data = {
        #     'type': 'search',
        #     'kw': '电竞',
        #     'cookie': cookie,
        # }
        data = json.dumps(data, ensure_ascii=False)
        response = stub.Kuaishou(spider_pb2.Data(data=data))
        print("Spider client received: " + response.result)


if __name__ == '__main__':
    run()