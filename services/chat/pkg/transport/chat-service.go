package transport

import (
	"context"

	"github.com/sergey-suslov/effective-pancake/api/proto"
	chats_service "github.com/sergey-suslov/effective-pancake/pkg/service/chats-service"
	users_service "github.com/sergey-suslov/effective-pancake/pkg/service/users-service"
)

type ChatServiceGrpc struct {
	usersService users_service.UsersService
	chatsService chats_service.ChatService
	proto.UnimplementedChatServiceServer
}

func NewChatServiceGrpc(usersService users_service.UsersService, chatsService chats_service.ChatService) *ChatServiceGrpc {
	return &ChatServiceGrpc{usersService: usersService, chatsService: chatsService}
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

func (s *ChatServiceGrpc) CreateChat(ctx context.Context, request *proto.CreateChatRequest) (*proto.CreateChatResponse, error) {
	usersChat, err := s.chatsService.CreateChat(ctx, request.GetUserOneId(), request.GetUserTwoId())
	if err != nil {
		return nil, err
	}
	return &proto.CreateChatResponse{
		Chat: &proto.Chat{
			Id:      usersChat.Id,
			UserOne: &proto.UserProfile{Id: usersChat.ChatsForUsers[0].UserId, Email: usersChat.ChatsForUsers[0].UserEmail},
			UserTwo: &proto.UserProfile{Id: usersChat.ChatsForUsers[1].UserId, Email: usersChat.ChatsForUsers[1].UserEmail},
		},
	}, nil
}
