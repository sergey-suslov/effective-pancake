package chats_repository

import (
	"context"
	"time"

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
	CreateChat(ctx context.Context, userOneId, userOneEmail, userTwoId, userTwoEmail string) (chatId string, err error)
	GetChat(ctx context.Context, chatId string) (usersChat UsersChat, err error)
}

type ChatRepositoryImpl struct {
	chatsSession      *gocql.Session
	userServiceClient proto.UserServiceClient
}

func (r *ChatRepositoryImpl) CreateChat(ctx context.Context, userOneId, userOneEmail, userTwoId, userTwoEmail string) (chatId string, err error) {
	batch := r.chatsSession.NewBatch(gocql.LoggedBatch)

	generatedChatId, err := gocql.RandomUUID()
	if err != nil {
		return "", err
	}

	batch.Query("insert into chats.chats (id, created) VALUES (?, dateOf(now()))", generatedChatId)
	batch.Query("insert into chats.chats_for_users (userid, chatid, userEmail) VALUES (?, ?, ?)", userOneId, generatedChatId, userOneEmail)
	batch.Query("insert into chats.chats_for_users (userid, chatid, userEmail) VALUES (?, ?, ?)", userTwoId, generatedChatId, userTwoEmail)
	batch.Query("insert into chats.users_for_chats (userid, chatid, userEmail) VALUES (?, ?, ?)", userOneId, generatedChatId, userOneEmail)
	batch.Query("insert into chats.users_for_chats (userid, chatid, userEmail) VALUES (?, ?, ?)", userTwoId, generatedChatId, userTwoEmail)

	err = r.chatsSession.ExecuteBatch(batch)
	if err != nil {
		return "", err
	}

	return generatedChatId.String(), nil
}

func (r *ChatRepositoryImpl) GetChat(ctx context.Context, chatId string) (usersChat UsersChat, err error) {
	var timestamp int64
	err = r.chatsSession.Query("select * from chats.chats where id = ?", chatId).Scan(&usersChat.Chat.Id, &timestamp)
	usersChat.Chat.Created = time.Unix(timestamp, 0).Format(time.RFC3339)
	iter := r.chatsSession.Query("select * from chats.users_for_chats where chatid = ? limit 2", chatId).Iter()

	usersChat.ChatsForUsers = make([]ChatForUser, 0, 2)
	var chatForUser ChatForUser
	for iter.Scan(&chatForUser.ChatId, &chatForUser.UserId, &chatForUser.UserEmail) {
		usersChat.ChatsForUsers = append(usersChat.ChatsForUsers, chatForUser)
	}
	return
}

func NewChatsRepository(userServiceClient proto.UserServiceClient, chatsSession *gocql.Session) ChatsRepository {
	return &ChatRepositoryImpl{userServiceClient: userServiceClient, chatsSession: chatsSession}
}
