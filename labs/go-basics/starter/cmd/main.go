package main

import (
	"fmt"

	"labbox/lab"
)

func main() {
	fmt.Println(lab.Total([]int{1500, 2000}))               // 3500
	fmt.Println(lab.ParseAmount("12.50"))                   // 1250 <nil>
	orders := []lab.Order{{"coffee", 2}, {"vada pav", 1}, {"coffee", 1}}
	fmt.Println(lab.CountByItem(orders), lab.Busiest(orders)) // map[coffee:3 vada pav:1] coffee
}
