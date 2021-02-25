import grpc
import os
import sys
import sentiment_pb2
import sentiment_pb2_grpc

current_path = os.path.realpath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
sys.path.append(root_path)
from Logger import log


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = sentiment_pb2_grpc.SentimentStub(channel)
        response = stub.GetSentiment(sentiment_pb2.TextInput(text='你妈死了'))
        print("Sentiment client received: " + response.result)


if __name__ == '__main__':
    run()