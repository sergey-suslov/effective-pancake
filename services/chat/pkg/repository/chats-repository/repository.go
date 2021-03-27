package chats_repository

import (
	"context"

	"github.com/gocql/gocql"
	"github.com/sergey-suslov/effective-pancake/api/proto"
)

type Chat struct {
	Id      string
	Created string
}

type ChatForUser struct {
	UserId    string
	ChatId    string
	UserEmail string
}

type UsersChat struct {
	Chat
	ChatsForUsers []ChatForUser
}

type ChatsRepository interface {
	CreateChat(ctx context.Context, userOneId, userTwoId string) (chatId string, err error)
	GetChat(ctx context.Context, chatId string) (usersChat UsersChat, err error)
}

type ChatRepositoryImpl struct {
	chatsSession      *gocql.Session
	userServiceClient proto.UserServiceClient
}

func (r *ChatRepositoryImpl) CreateChat(ctx context.Context, userOneId, userTwoId string) (chatId string, err error) {
	batch := r.chatsSession.NewBatch(gocql.LoggedBatch)

	generatedChatId, err := gocql.RandomUUID()
	if err != nil {
		return "", err
	}

	batch.Query("insert into chats.chats (id, created) VALUES (?, now())", generatedChatId)
	batch.Query("insert into chats.chats_for_users (userid, chatid) VALUES (?, ?)", userOneId, generatedChatId)
	batch.Query("insert into chats.chats_for_users (userid, chatid) VALUES (?, ?)", userTwoId, generatedChatId)

	err = r.chatsSession.ExecuteBatch(batch)
	if err != nil {
		return "", err
	}

	return generatedChatId.String(), nil
}

func (r *ChatRepositoryImpl) GetChat(ctx context.Context, chatId string) (usersChat UsersChat, err error) {
	return UsersChat{}, nil
}

func NewChatsRepository(userServiceClient proto.UserServiceClient, chatsSession *gocql.Session) ChatsRepository {
	return &ChatRepositoryImpl{userServiceClient: userServiceClient, chatsSession: chatsSession}
}
