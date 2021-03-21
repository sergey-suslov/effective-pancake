from concurrent import futures
import logging
import os

from pymongo.mongo_client import MongoClient
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.grpc_transport.user_service import UserServiceGrpc
from src.api.user_pb2_grpc import add_UserServiceServicer_to_server
import grpc


def serve():
    client = MongoClient('mongodb://%s:%s@127.0.0.1' %
                         (os.getenv("MONGODB_USER"), os.getenv("MONGODB_PASSWORD")))
    logging.info('Connected to DB')
    user_repository = UserRepository(client=client)
    auth_service = AuthService(user_repository=user_repository)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_UserServiceServicer_to_server(
        UserServiceGrpc(auth_service=auth_service), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info('Starting...')
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=0)
    serve()
