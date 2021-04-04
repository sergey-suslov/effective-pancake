create keyspace chats with replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
create table chats.chats(id UUID, created timestamp, PRIMARY KEY(id, created));
create table chats.chats_for_users(userId text, chatId UUID, userEmail text, created timestamp, PRIMARY KEY((userId), created, chatId)) with clustering order by (created desc, chatId desc);
create table chats.users_for_chats(userId text, chatId UUID, userEmail text, created timestamp, PRIMARY KEY((chatId), created, userId)) with clustering order by (created desc, userId desc);
create table chats.messages_for_chats(userId text, chatId UUID, message text, created timestamp, PRIMARY KEY((chatId), created)) with clustering order by (created desc);
