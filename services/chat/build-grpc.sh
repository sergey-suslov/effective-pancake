protoc --proto_path=../../proto --go_out=api --go_opt=paths=import \
    --go-grpc_out=api --go-grpc_opt=paths=import \
    ../../proto/api/*.proto
