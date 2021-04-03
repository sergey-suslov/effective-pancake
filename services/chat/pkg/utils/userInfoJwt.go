package utils

import (
	"context"
	"errors"

	"github.com/dgrijalva/jwt-go"
)

const SECRET = "secret"

type UserClaim struct {
	jwt.StandardClaims
	ID    string `json:"_id"`
	Email string `json:"email"`
}

func DecodeUserFromToken(token string) (*UserClaim, error) {
	claim, err := jwt.ParseWithClaims(token, &UserClaim{}, func(token *jwt.Token) (interface{}, error) {
		return []byte(SECRET), nil
	})
	if err != nil {
		return nil, err
	}
	return claim.Claims.(*UserClaim), nil
}

func GetUserClaimFromContext(ctx context.Context) (*UserClaim, error) {
	claim, ok := ctx.Value("userInfo").(*UserClaim)
	if !ok {
		return nil, errors.New("No userInfo in the context")
	}
	return claim, nil
}
