package interceptors

import (
	"context"

	"github.com/sergey-suslov/effective-pancake/pkg/utils"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

func AuthInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (resp interface{}, err error) {
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return nil, status.Errorf(codes.Unauthenticated, "Error while retrieving metadata")
	}
	authToken, ok := md["auth-token"]
	if !ok {
		return nil, status.Errorf(codes.Unauthenticated, "Authorization token is not supplied")
	}
	userClaim, err := utils.DecodeUserFromToken(authToken[0])
	if err != nil {
		return nil, status.Errorf(codes.Unauthenticated, err.Error())
	}
	newCtx := context.WithValue(ctx, "userInfo", userClaim)
	return handler(newCtx, req)
}
