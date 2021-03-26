package cmd

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"text/tabwriter"

	"github.com/sergey-suslov/effective-pancake/api/proto"
	users_repository "github.com/sergey-suslov/effective-pancake/pkg/repository/users-repository"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

func main() {
	fs := flag.NewFlagSet("apartmentscli", flag.ExitOnError)
	var (
		port               = fs.String("port", "50052", "Port of Chat service")
		userServicePort    = fs.String("userServicePort", "50051", "Address of User service")
		userServiceAddress = fs.String("userServiceAddress", "localhost", "Port of User service")
		help               = fs.Bool("h", false, "Show help")
		logDebug           = fs.Bool("debug", false, "Log debug info")
	)
	fs.Usage = usageFor(fs, os.Args[0]+" [flags] <a> <b>")
	_ = fs.Parse(os.Args[1:])
	if *help {
		fs.Usage()
		os.Exit(1)
	}

	// Service clients initialisation
	userServiceConnection := getGrpcConnectionUserService(*userServiceAddress, *userServicePort)
	userServiceClient := proto.NewUserServiceClient(userServiceConnection)

	userRepository := users_repository.NewUserRepository(userServiceClient)
}

func getGrpcConnectionUserService(addr, port string) *grpc.ClientConn {
	conn, err := grpc.Dial(net.JoinHostPort(addr, port))
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
