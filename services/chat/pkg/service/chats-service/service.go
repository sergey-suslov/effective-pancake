package chats_service

import (
	"context"
	"errors"

	chats_repository "github.com/sergey-suslov/effective-pancake/pkg/repository/chats-repository"
	users_repository "github.com/sergey-suslov/effective-pancake/pkg/repository/users-repository"
)

var NoUserWithGivenId error = errors.New("No user with given id")

type ChatService interface {
	CreateChat(ctx context.Context, userOneId, userTwoId string) (chats_repository.UsersChat, error)
	GetUserChats(ctx context.Context, userId string, after int64, perPage int) ([]chats_repository.UsersChat, error)
}

type ChatServiceImpl struct {
	chatsRepository chats_repository.ChatsRepository
	userRepository  users_repository.UserRepository
}

func (s *ChatServiceImpl) getUserProfile(ctx context.Context, userId string) (chan users_repository.UserProfile, chan error) {
	userProfileC := make(chan users_repository.UserProfile, 1)
	errorC := make(chan error, 1)

	go func() {
		userProfile, err := s.userRepository.GetUserProfileById(ctx, userId)
		if err != nil {
			errorC <- err
			return
		}
		userProfileC <- userProfile
	}()
	return userProfileC, errorC
}

func (s *ChatServiceImpl) CreateChat(ctx context.Context, userOneId, userTwoId string) (chats_repository.UsersChat, error) {
	profileOneC, errorOneC := s.getUserProfile(ctx, userOneId)
	profileTwoC, errorTwoC := s.getUserProfile(ctx, userTwoId)

	var userProfileOne users_repository.UserProfile
	var userProfileTwo users_repository.UserProfile
	select {
	case userProfileOne = <-profileOneC:
	case err := <-errorOneC:
		return chats_repository.UsersChat{}, err
	case <-ctx.Done():
		return chats_repository.UsersChat{}, ctx.Err()
	}

	select {
	case userProfileTwo = <-profileTwoC:
	case err := <-errorTwoC:
		return chats_repository.UsersChat{}, err
	case <-ctx.Done():
		return chats_repository.UsersChat{}, ctx.Err()
	}

	if userProfileOne.Id == "" || userProfileTwo.Id == "" {
		return chats_repository.UsersChat{}, NoUserWithGivenId
	}

	chatId, err := s.chatsRepository.CreateChat(ctx, userOneId, userProfileOne.Email, userTwoId, userProfileTwo.Email)
	if err != nil {
		return chats_repository.UsersChat{}, err
	}
	usersChat, err := s.chatsRepository.GetChat(ctx, chatId)
	if err != nil {
		return chats_repository.UsersChat{}, err
	}
	return usersChat, nil
}

func NewChatService(chatsRepository chats_repository.ChatsRepository, usersRepository users_repository.UserRepository) ChatService {
	return &ChatServiceImpl{chatsRepository: chatsRepository, userRepository: usersRepository}
}

func (s *ChatServiceImpl) GetUserChats(ctx context.Context, userId string, after int64, perPage int) ([]chats_repository.UsersChat, error) {
	return s.chatsRepository.GetUserChats(ctx, userId, after, perPage)
}
