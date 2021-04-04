package chats_repository

import (
	"context"
	"time"
)

type MessageForChat struct {
	ChatId  string
	UserId  string
	Message string
	Created time.Time
}

func (r *ChatRepositoryImpl) GetMessagesByChat(ctx context.Context, chatId string, afterTimestamp int64, perPage int) ([]MessageForChat, error) {
	iter := r.chatsSession.Query("select chatid, userid, message, created from chats.messages_for_chats where chatid = ? and created < ? limit ?", chatId, afterTimestamp, perPage).Iter().Scanner()

	messages := make([]MessageForChat, 0, perPage)
	var messageForChat MessageForChat
	for iter.Next() {
		err := iter.Scan(&messageForChat.ChatId, &messageForChat.UserId, &messageForChat.Message, &messageForChat.Created)
		if err != nil {
			return nil, err
		}
		messages = append(messages, messageForChat)
	}
	return messages, nil
}
