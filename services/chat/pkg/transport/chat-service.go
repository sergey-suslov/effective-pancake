package transport

import (
	"context"

	"github.com/sergey-suslov/effective-pancake/api/proto"
	users_service "github.com/sergey-suslov/effective-pancake/pkg/service/users-service"
)

type ChatServiceGrpc struct {
	usersService users_service.UsersService
	proto.UnimplementedChatServiceServer
}

func NewChatServiceGrpc(usersService users_service.UsersService) *ChatServiceGrpc {
	return &ChatServiceGrpc{usersService: usersService}
}

func (s *ChatServiceGrpc) GetAvailableUsers(ctx context.Context, request *proto.GetAvailableUsersRequest) (*proto.GetAvailableUsersResponse, error) {
	availableUsers, err := s.usersService.GetAvailableUsers(ctx, int(request.GetPagination().GetPage()), int(request.GetPagination().GetPerPage()))
	if err != nil {
		return nil, err
	}
	response := &proto.GetAvailableUsersResponse{}
	response.AvailableUsers = []*proto.UserProfile{}
	for i := range availableUsers {
		response.AvailableUsers = append(response.AvailableUsers, &proto.UserProfile{Id: availableUsers[i].Id, Email: availableUsers[i].Email})
	}
	return response, nil
}

func (s *ChatServiceGrpc) mustEmbedUnimplementedChatServiceServer() {}
