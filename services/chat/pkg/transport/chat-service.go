package transport

import (
	"context"
	"log"

	"github.com/sergey-suslov/effective-pancake/api/proto"
	chats_service "github.com/sergey-suslov/effective-pancake/pkg/service/chats-service"
	users_service "github.com/sergey-suslov/effective-pancake/pkg/service/users-service"
	"github.com/sergey-suslov/effective-pancake/pkg/utils"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/protobuf/types/known/timestamppb"
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
	if err == chats_service.NoUserWithGivenId {
		return nil, grpc.Errorf(codes.InvalidArgument, err.Error())
	}
	if err != nil {
		return nil, err
	}
	return &proto.CreateChatResponse{
		Chat: &proto.Chat{
			Id:      usersChat.Id,
			UserOne: &proto.UserProfile{Id: usersChat.ChatsForUsers[0].UserId, Email: usersChat.ChatsForUsers[0].UserEmail},
			UserTwo: &proto.UserProfile{Id: usersChat.ChatsForUsers[1].UserId, Email: usersChat.ChatsForUsers[1].UserEmail},
			Created: timestamppb.New(usersChat.Created),
		},
	}, nil
}

func (s *ChatServiceGrpc) GetChatsByUserId(ctx context.Context, request *proto.GetChatsByUserRequest) (*proto.GetChatsByUserResponse, error) {
	chats, err := s.chatsService.GetUserChats(ctx, request.GetId().GetId(), request.GetPagination().GetAfter(), int(request.GetPagination().GetPerPage()))
	if err != nil {
		return nil, err
	}
	chatsResponse := make([]*proto.Chat, 0, len(chats))
	for i := range chats {
		chatsResponse = append(chatsResponse, &proto.Chat{
			Id:      chats[i].Id,
			UserOne: &proto.UserProfile{Id: chats[i].ChatsForUsers[0].UserId, Email: chats[i].ChatsForUsers[0].UserEmail},
			UserTwo: &proto.UserProfile{Id: chats[i].ChatsForUsers[1].UserId, Email: chats[i].ChatsForUsers[1].UserEmail},
			Created: timestamppb.New(chats[i].Created),
		})
	}
	return &proto.GetChatsByUserResponse{Chats: chatsResponse}, nil
}
