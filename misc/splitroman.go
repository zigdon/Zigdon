package main

import (
	"fmt"
	"os"
	"sort"
	"strings"
)

var r = map[string]int{
	"I":     1,
	"II":    2,
	"III":   3,
	"IV":    4,
	"V":     5,
	"VI":    6,
	"VII":   7,
	"VIII":  8,
	"IX":    9,
	"X":     10,
	"XI":    11,
	"XII":   12,
	"XIII":  13,
	"XIV":   14,
	"XV":    15,
	"XVI":   16,
	"XVII":  17,
	"XVIII": 18,
	"XIX":   19,
	"XX":    20,
	"XXI":   21,
	"XXII":  22,
	"XXIII": 23,
	"XXIV":  24,
	"XXV":   25,
	"XXVI":  26,
}

func keys(m map[string]int) []string {
	k := []string{}
	for i := range m {
		k = append(k, i)
	}

	return k
}

func getPossibleNums(rs []string, s string) []string {
	// find all the numbers that can be found at the beginning of the string.
	res := []string{}
	for _, n := range rs {
		if !strings.HasPrefix(s, n) {
			continue
		}

		res = append(res, n)
	}

	return res
}

// returns a list of numeral lists. VII -> {{V, I, I}, {V, II}, {VI, I}, {VII}}
func breakup(rs []string, s string) [][]string {
	// fmt.Printf("breaking %q\n", s)
	res := [][]string{}

	for _, opt := range getPossibleNums(rs, s) {
		if len(opt) == 0 {
			continue
		}

		next := strings.TrimPrefix(s, opt)
		if len(next) == 0 {
			res = append(res, []string{opt})
			continue
		}

		sub := breakup(rs, strings.TrimPrefix(s, opt))

		// fmt.Printf("got %v\n", sub)

		for _, sb := range sub {
			if len(sb) > 9 {
				continue
			}
			num := []string{opt}
			num = append(num, sb...)
			res = append(res, num)
		}
	}

	return res
}

func word(s []string) string {
	res := ""
	for _, l := range s {
		res = res + string('A'-1+r[l])
	}

	return res
}

func main() {
	str := os.Args[1]

	rs := keys(r)
	sort.Slice(rs, func(i, j int) bool {
		return len(rs[i]) > len(rs[j])
	})

	for _, s := range breakup(rs, str) {
		if len(s) != 9 {
			continue
		}
		fmt.Printf("%v -> %s\n", s, word(s))
	}
}
