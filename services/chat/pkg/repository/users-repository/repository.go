package users_repository

import (
	"context"

	"github.com/sergey-suslov/effective-pancake/api/proto"
)

type UserProfile struct {
	Id    string
	Email string
}

type UserRepository interface {
	GetAvailableUsers(context.Context, int, int) ([]UserProfile, error)
}

type UserRepositoryImpl struct {
	userServiceClient proto.UserServiceClient
}

func (r *UserRepositoryImpl) GetAvailableUsers(ctx context.Context, page, perPage int) ([]UserProfile, error) {
	usersInternalResponse, err := r.userServiceClient.UsersInternal(ctx, &proto.UsersInternalRequest{Pagination: &proto.Pagination{Page: int32(page), PerPage: int32(perPage)}})
	if err != nil {
		return nil, err
	}
	userProfiles := []UserProfile{}
	availableUsers := usersInternalResponse.GetAvailableUsers()
	for i := range availableUsers {
		userProfiles = append(userProfiles, UserProfile{Id: availableUsers[i].Id, Email: availableUsers[i].Email})
	}
	return []UserProfile{}, nil
}

func NewUserRepository(userServiceClient proto.UserServiceClient) UserRepository {
	return &UserRepositoryImpl{userServiceClient: userServiceClient}
}
