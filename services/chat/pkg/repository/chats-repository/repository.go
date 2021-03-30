package chats_repository

import (
	"context"
	"log"
	"time"

	"github.com/gocql/gocql"
	"github.com/sergey-suslov/effective-pancake/api/proto"
	"github.com/sergey-suslov/effective-pancake/pkg/utils"
)

type Chat struct {
	Id      string
	Created string
}

type ChatForUser struct {
	UserId    string
	ChatId    string
	Created   string
	UserEmail string
}

type UsersChat struct {
	Chat
	ChatsForUsers []ChatForUser
}

type ChatsRepository interface {
	CreateChat(ctx context.Context, userOneId, userOneEmail, userTwoId, userTwoEmail string) (chatId string, err error)
	GetChat(ctx context.Context, chatId string) (usersChat UsersChat, err error)
	GetUserChats(ctx context.Context, userId string, afterTimestamp int64, perPage int) ([]UsersChat, error)
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
	batch.Query("insert into chats.chats_for_users (userid, chatid, userEmail, created) VALUES (?, ?, ?, toTimestamp(now()))", userOneId, generatedChatId, userOneEmail)
	batch.Query("insert into chats.chats_for_users (userid, chatid, userEmail, created) VALUES (?, ?, ?, toTimestamp(now()))", userTwoId, generatedChatId, userTwoEmail)
	batch.Query("insert into chats.users_for_chats (userid, chatid, userEmail, created) VALUES (?, ?, ?, toTimestamp(now()))", userOneId, generatedChatId, userOneEmail)
	batch.Query("insert into chats.users_for_chats (userid, chatid, userEmail, created) VALUES (?, ?, ?, toTimestamp(now()))", userTwoId, generatedChatId, userTwoEmail)

	err = r.chatsSession.ExecuteBatch(batch)
	if err != nil {
		return "", err
	}

	return generatedChatId.String(), nil
}

func (r *ChatRepositoryImpl) GetChat(ctx context.Context, chatId string) (usersChat UsersChat, err error) {
	var timestamp int64
	err = r.chatsSession.Query("select * from chats.chats where id = ?", chatId).Scan(&usersChat.Chat.Id, &timestamp)
	usersChat.Chat.Created = utils.ParseTimestamp(timestamp)
	iter := r.chatsSession.Query("select * from chats.users_for_chats where chatid = ? limit 2", chatId).Iter()

	usersChat.ChatsForUsers = make([]ChatForUser, 0, 2)
	var chatForUser ChatForUser
	for iter.Scan(&chatForUser.ChatId, &chatForUser.UserId, &chatForUser.UserEmail, &timestamp) {
		chatForUser.Created = utils.ParseTimestamp(timestamp)
		usersChat.ChatsForUsers = append(usersChat.ChatsForUsers, chatForUser)
	}
	return
}

func (r *ChatRepositoryImpl) getChatsForUserByUserId(ctx context.Context, userId string, afterTimestamp int64, perPage int) ([]ChatForUser, error) {
	chatsIter := r.chatsSession.Query("select * from chats.chats_for_users where userid = ? and created < ? limit ?", userId, utils.ParseTimestamp(afterTimestamp), perPage).Iter()
	chatsForUser := make([]ChatForUser, 0, perPage)
	var timestamp int64
	var chatForUser ChatForUser
	for chatsIter.Scan(&chatForUser.ChatId, &chatForUser.UserId, &chatForUser.UserEmail, chatForUser.Created) {
		chatForUser.Created = time.Unix(timestamp, 0).Format(time.RFC3339)
		chatsForUser = append(chatsForUser, chatForUser)
	}
	return chatsForUser, nil
}

func (r *ChatRepositoryImpl) getChatsForUserByChatIds(ctx context.Context, chatIds []string) ([]ChatForUser, error) {
	chatsIter := r.chatsSession.Query("select * from chats.users_for_chats where chatid in ?", chatIds).Iter()
	chatsForUser := make([]ChatForUser, 0, len(chatIds))
	var chatForUser ChatForUser
	for chatsIter.Scan(&chatForUser.ChatId, &chatForUser.UserId, &chatForUser.UserEmail) {
		chatsForUser = append(chatsForUser, chatForUser)
	}
	return chatsForUser, nil
}

func (r *ChatRepositoryImpl) getChatsByIds(ctx context.Context, chatIds []string) ([]Chat, error) {
	chatsIter := r.chatsSession.Query("select * from chats.chats where id in ?", chatIds).Iter()
	var chat Chat
	var timestamp int64
	chats := make([]Chat, 0, len(chatIds))
	for chatsIter.Scan(&chat.Id, &timestamp) {
		chats = append(chats, chat)
	}
	return chats, nil
}

func (r *ChatRepositoryImpl) GetUserChats(ctx context.Context, userId string, afterTimestamp int64, perPage int) ([]UsersChat, error) {
	chatsForUser, err := r.getChatsForUserByUserId(ctx, userId, afterTimestamp, perPage)
	if err != nil {
		return nil, err
	}

	chatsIds := make([]string, 0, len(chatsForUser))
	for i := range chatsForUser {
		chatsIds = append(chatsIds, chatsForUser[i].ChatId)
	}
	chats, err := r.getChatsByIds(ctx, chatsIds)
	if err != nil {
		return nil, err
	}

	allChatsForUser, err := r.getChatsForUserByChatIds(ctx, chatsIds)
	if err != nil {
		return nil, err
	}

	usersChats := make([]UsersChat, 0, len(chats))
	for chatI := range chats {
		usersChat := UsersChat{Chat: chats[chatI], ChatsForUsers: make([]ChatForUser, 0, 2)}
		for chatsForUserI := range allChatsForUser {
			if allChatsForUser[chatsForUserI].ChatId == usersChat.Id {
				usersChat.ChatsForUsers = append(usersChat.ChatsForUsers, allChatsForUser[chatsForUserI])
			}
		}
		usersChats = append(usersChats, usersChat)
	}
	return usersChats, nil
}

func NewChatsRepository(userServiceClient proto.UserServiceClient, chatsSession *gocql.Session) ChatsRepository {
	return &ChatRepositoryImpl{userServiceClient: userServiceClient, chatsSession: chatsSession}
}
