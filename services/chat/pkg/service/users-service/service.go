package users_service

import (
	"context"

	users_repository "github.com/sergey-suslov/effective-pancake/pkg/repository/users-repository"
)

type UsersService interface {
	GetAvailableUsers(context.Context, int, int) ([]users_repository.UserProfile, error)
}

type UsersServiceImpl struct {
	userRepository users_repository.UserRepository
}

func (s *UsersServiceImpl) GetAvailableUsers(ctx context.Context, page, perPage int) ([]users_repository.UserProfile, error) {
	return s.userRepository.GetAvailableUsers(ctx, page, perPage)
}

func NewUserService(userRepository users_repository.UserRepository) UsersService {
	return &UsersServiceImpl{userRepository: userRepository}
}
