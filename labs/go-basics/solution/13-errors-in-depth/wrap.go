//go:build ignore

// Chapter 13: an error wrapped twice, and still recognised.
package main

import (
	"errors"
	"fmt"
)

var ErrNoRoom = errors.New("van is full")

func load(van string, count int) error {
	if count >= 10 {
		return fmt.Errorf("load parcel onto %s: %w", van, ErrNoRoom)
	}
	return nil
}

func dispatch(van string, count int) error {
	if err := load(van, count); err != nil {
		return fmt.Errorf("dispatch failed: %w", err)
	}
	return nil
}

func main() {
	err := dispatch("Van 7", 10)
	fmt.Println(err)
	fmt.Println(errors.Is(err, ErrNoRoom), err == ErrNoRoom)
	fmt.Println(errors.Unwrap(errors.Unwrap(err)) == ErrNoRoom)
}
