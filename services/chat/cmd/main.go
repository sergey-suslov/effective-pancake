package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"text/tabwriter"

	"github.com/gocql/gocql"
	"github.com/sergey-suslov/effective-pancake/api/proto"
	chats_repository "github.com/sergey-suslov/effective-pancake/pkg/repository/chats-repository"
	users_repository "github.com/sergey-suslov/effective-pancake/pkg/repository/users-repository"
	chats_service "github.com/sergey-suslov/effective-pancake/pkg/service/chats-service"
	users_service "github.com/sergey-suslov/effective-pancake/pkg/service/users-service"
	transport "github.com/sergey-suslov/effective-pancake/pkg/transport"
	"google.golang.org/grpc"
)

func main() {
	fs := flag.NewFlagSet("apartmentscli", flag.ExitOnError)
	var (
		port               = fs.String("port", "50052", "Port of Chat service")
		userServicePort    = fs.String("userServicePort", "50051", "Address of User service")
		userServiceAddress = fs.String("userServiceAddress", "localhost", "Port of User service")
		cassandraHost      = fs.String("cassandraHost", "localhost", "Address of Cassandra DB")
		help               = fs.Bool("h", false, "Show help")
	)
	fs.Usage = usageFor(fs, os.Args[0]+" [flags] <a> <b>")
	_ = fs.Parse(os.Args[1:])
	if *help {
		fs.Usage()
		os.Exit(1)
	}

	chatsCluster := getCassandraClusterConfig("chats", *cassandraHost)
	chatsSession, err := chatsCluster.CreateSession()
	if err != nil {
		log.Fatalln("Could not create cassandra session")
	}

	// Service clients initialisation
	userServiceConnection := getGrpcConnectionUserService(*userServiceAddress, *userServicePort)
	userServiceClient := proto.NewUserServiceClient(userServiceConnection)

	userRepository := users_repository.NewUserRepository(userServiceClient)
	userService := users_service.NewUserService(userRepository)

	chatsRepository := chats_repository.NewChatsRepository(userServiceClient, chatsSession)
	chatsService := chats_service.NewChatService(chatsRepository, userServiceClient)

	chatServiceGrpc := transport.NewChatServiceGrpc(userService, chatsService)

	lis, err := net.Listen("tcp", net.JoinHostPort("localhost", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	var opts []grpc.ServerOption
	grpcServer := grpc.NewServer(opts...)
	proto.RegisterChatServiceServer(grpcServer, chatServiceGrpc)
	grpcServer.Serve(lis)
}

func getGrpcConnectionUserService(addr, port string) *grpc.ClientConn {
	conn, err := grpc.Dial(net.JoinHostPort(addr, port), grpc.WithInsecure())
	if err != nil {
		log.Fatalln("Failed to dial server:", err)
	}
	return conn
}

func usageFor(fs *flag.FlagSet, short string) func() {
	return func() {
		fmt.Fprintf(os.Stderr, "USAGE\n")
		fmt.Fprintf(os.Stderr, "  %s\n", short)
		fmt.Fprintf(os.Stderr, "\n")
		fmt.Fprintf(os.Stderr, "FLAGS\n")
		w := tabwriter.NewWriter(os.Stderr, 0, 2, 2, ' ', 0)
		fs.VisitAll(func(f *flag.Flag) {
			fmt.Fprintf(w, "\t-%s %s\t%s\n", f.Name, f.DefValue, f.Usage)
		})
		_ = w.Flush()
		fmt.Fprintf(os.Stderr, "\n")
	}
}

func getCassandraClusterConfig(keyspace, host string) *gocql.ClusterConfig {
	cluster := gocql.NewCluster(host)
	cluster.Keyspace = keyspace
	cluster.Consistency = gocql.Quorum

	return cluster
}
