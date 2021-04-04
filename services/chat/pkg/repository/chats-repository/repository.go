package chats_repository

import (
	"context"
	"time"

	"github.com/gocql/gocql"
	"github.com/sergey-suslov/effective-pancake/api/proto"
)

type TracerLog struct{}

func (t TracerLog) Trace(traceId []byte) {
}

type Chat struct {
	Id      string
	Created time.Time
}

type ChatForUser struct {
	UserId    string
	ChatId    string
	Created   time.Time
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
	GetMessagesByChat(ctx context.Context, chatId string, afterTimestamp int64, perPage int) ([]MessageForChat, error)
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
	err = r.chatsSession.Query("select id, created from chats.chats where id = ?", chatId).Scan(&usersChat.Chat.Id, &usersChat.Chat.Created)
	iter := r.chatsSession.Query("select chatid, userid, useremail, created from chats.users_for_chats where chatid = ? limit 2", chatId).Iter().Scanner()

	usersChat.ChatsForUsers = make([]ChatForUser, 0, 2)
	var chatForUser ChatForUser
	for iter.Next() {
		err := iter.Scan(&chatForUser.ChatId, &chatForUser.UserId, &chatForUser.UserEmail, &chatForUser.Created)
		if err != nil {
			return UsersChat{}, err
		}
		usersChat.ChatsForUsers = append(usersChat.ChatsForUsers, chatForUser)
	}
	return
}

func (r *ChatRepositoryImpl) getChatsForUserByUserId(ctx context.Context, userId string, afterTimestamp int64, perPage int) ([]ChatForUser, error) {
	chatsIter := r.chatsSession.Query("select chatid, userid, useremail, created from chats.chats_for_users where userid = ? and created < ? limit ?", userId, afterTimestamp, perPage).Iter().Scanner()
	chatsForUser := make([]ChatForUser, 0, perPage)
	var chatForUser ChatForUser
	for chatsIter.Next() {
		err := chatsIter.Scan(&chatForUser.ChatId, &chatForUser.UserId, &chatForUser.UserEmail, &chatForUser.Created)
		if err != nil {
			return nil, err
		}
		chatsForUser = append(chatsForUser, chatForUser)
	}
	return chatsForUser, nil
}

func (r *ChatRepositoryImpl) getChatsForUserByChatIds(ctx context.Context, chatIds []string) ([]ChatForUser, error) {
	chatsIter := r.chatsSession.Query("select chatid, userid, useremail from chats.users_for_chats where chatid in ?", chatIds).Iter()
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
