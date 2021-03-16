# Messaging System

This app allows to communicate via chat.

## Requirements

- The app should be scalable and should be able to start and run on diffrent clusters
- The app should have a simple REST API

## Features

- Registration and authorisation
- Obtaining of available users
- Chat creation
- Getting the list chat's messages
- Message posting

## Technological Stack

- Go
- Cassandra
- Linkerd
- Kafka

## Services Specification

- Users - handles user's registration, auth, and profile manipulations
- Chatting - handles the connection establishment and message transferring
- Chats - handles messages' and chats' storage and provision
- ChatCLI - cli app to interact with the services

## Transport Layers

All between-service communication should be implemented using gRPC.
Public intefrace should be implemented using REST.

### Users

This service should be able to register a user by email/password, authenticate,
and authorize the user by a JWT.

**Routes**

- [ ] sign-up (gRCP)
- [ ] sign-in (gRPC)
- [ ] profile (gRPC) - returns a user's profile with the number of chats

### Chatting

This service handles socket connections of users, receiving and routing their
messages, and sends messages to queues to write them in a DB.

### Chats

This service handles the chat's CRUD, and messages CRUD including syncing newly
created messages from queues.

**Routes**

- [ ] chats (gRPC)
- [ ] chats/:chatId/messages (gRPC)

### ChatCLI

This cli app should allow to interact with the system. The app should use gRPC
to communicate with the services and send/receive messages over http2 connection
weather it is gRPC or a custom implementation.
