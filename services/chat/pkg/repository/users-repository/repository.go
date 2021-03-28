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
	GetUserProfileById(ctx context.Context, userId string) (UserProfile, error)
}

type UserRepositoryImpl struct {
	userServiceClient proto.UserServiceClient
}

func (r *UserRepositoryImpl) GetUserProfileById(ctx context.Context, userId string) (UserProfile, error) {
	userProfile, err := r.userServiceClient.GetUserInternal(ctx, &proto.ById{Id: userId})
	if err != nil {
		return UserProfile{}, err
	}
	return UserProfile{Id: userProfile.GetId(), Email: userProfile.GetEmail()}, nil
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
	return userProfiles, nil
}

func NewUserRepository(userServiceClient proto.UserServiceClient) UserRepository {
	return &UserRepositoryImpl{userServiceClient: userServiceClient}
}
