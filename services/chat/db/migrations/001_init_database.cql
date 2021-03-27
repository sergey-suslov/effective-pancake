create keyspace chats with replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
create table chats.chats(id UUID, created timeuuid, PRIMARY KEY(id));
create table chats.chats_for_users(userId text, chatId UUID, userEmail text, PRIMARY KEY((userId), chatId));
