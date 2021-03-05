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
        data = {'type': 'question', 'page': 1, 'kw': '开学'}
        data = json.dumps(data, ensure_ascii=False)
        response = stub.Zhihu(spider_pb2.Data(data=data))
        print("Sentiment client received: " + response.result)


if __name__ == '__main__':
    run()