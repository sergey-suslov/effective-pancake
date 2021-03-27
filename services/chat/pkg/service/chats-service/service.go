package chats_service

import (
	"context"
	"errors"
	"sync"

	"github.com/sergey-suslov/effective-pancake/api/proto"
	chats_repository "github.com/sergey-suslov/effective-pancake/pkg/repository/chats-repository"
)

var NoUserWithGivenId error = errors.New("No user with given id")

type ChatService interface {
	CreateChat(ctx context.Context, userOneId, userTwoId string) (chats_repository.UsersChat, error)
}

type ChatServiceImpl struct {
	chatsRepository   chats_repository.ChatsRepository
	userServiceClient proto.UserServiceClient
}

func (s *ChatServiceImpl) CreateChat(ctx context.Context, userOneId, userTwoId string) (chats_repository.UsersChat, error) {
	wg := sync.WaitGroup{}

	var userProfileTwo *proto.UserProfile
	var err error
	go func() {
		userProfileTwo, err = s.userServiceClient.GetUserInternal(ctx, &proto.ById{Id: userTwoId})
		wg.Done()
	}()
	wg.Add(1)
	userProfileOne, err := s.userServiceClient.GetUserInternal(ctx, &proto.ById{Id: userOneId})
	wg.Done()

	wg.Wait()
	if userProfileOne.GetId() == "" || userProfileTwo.GetId() == "" {
		err = NoUserWithGivenId
	}
	if err != nil {
		return chats_repository.UsersChat{}, err
	}

	chatId, err := s.chatsRepository.CreateChat(ctx, userOneId, userTwoId)
	if err != nil {
		return chats_repository.UsersChat{}, err
	}
	usersChat, err := s.chatsRepository.GetChat(ctx, chatId)
	if err != nil {
		return chats_repository.UsersChat{}, err
	}
	return usersChat, nil
}

func NewChatService(chatsRepository chats_repository.ChatsRepository, userServiceClient proto.UserServiceClient) ChatService {
	return &ChatServiceImpl{chatsRepository: chatsRepository, userServiceClient: userServiceClient}
}
