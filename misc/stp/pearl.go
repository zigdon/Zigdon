package main

import (
  "fmt"
  "strings"
  "io/ioutil"
  "os"
)

type nodeType string
const (
  empty nodeType = " "
  white = "w"
  black = "b"
)

type edge struct {
  e bool  // exists
  p bool  // possible
}

type dir int
const (
  none dir = iota
  up
  down
  left
  right
)
var dirs = []dir{up, down, left, right}
func (d dir) rev() dir {
  if d == up {
    return down
  } else if d == down {
    return up
  } else if d == left {
    return right
  } else if d == right {
    return left
  }

  return none
}
func (d dir) orthogonal() []dir {
  if d == up || d == down {
    return []dir{right, left}
  } else if d == left || d == right {
    return []dir{up, down}
  }

  return []dir{}
}
func (d dir) name() string {
  switch d {
    case up:
      return "up"
    case down:
      return "down"
    case left:
      return "left"
    case right:
      return "right"
  }
  return "none"
}

type space struct {
  x, y int
  node nodeType
  c map[dir]edge
}

func (s *space) name() string{
  return fmt.Sprintf("(%d,%d = %v)", s.x+1, s.y+1, s.node)
}

func (s *space) CountConnections() []dir {
  cons := []dir{}
  for _, d := range dirs {
    if s.c[d].e {
      cons = append(cons, d)
    }
  }

  return cons
}

// Can we make a link starting from this node in direction d
func (s *space) CanLineFrom(d dir) bool {
  if !s.c[d].p { // not possible
    return false
  }
  if s.c[d].e { // already exists
    return true
  }

  // Can't have any more lines
  if len(s.CountConnections()) > 1 {
    return false
  }

  return true
}

// Can we make a line to this node from direction d
func (s *space) CanLineTo(d dir) bool {
  r := d.rev()
  if !s.c[r].p { // not possible
    return false
  }
  if s.c[r].e { // already exists
    return true
  }

  // Can't have any more lines
  if len(s.CountConnections()) > 1 {
    return false
  }

  return true
}

func (s *space) Print(simple bool) {
  if s.node != empty {
    fmt.Print(s.node)
  } else {
    if s.c[right].e && s.c[left].e {
      fmt.Print("-")
    } else if s.c[up].e && s.c[down].e {
      fmt.Print("|")
    } else if (s.c[up].e && s.c[right].e) || (s.c[down].e && s.c[left].e) {
      fmt.Print("\\")
    } else if (s.c[up].e && s.c[left].e) || (s.c[down].e && s.c[right].e) {
      fmt.Print("/")
    } else if s.c[up].e || s.c[down].e || s.c[left].e || s.c[right].e {
      fmt.Print("o")
    } else if !simple {
      fmt.Print(".")
    } else {
      fmt.Print(" ")
    }
  }
}

func (s *space) PrintRight(simple bool) {
  if s.c[right].e {
    fmt.Print("-")
  } else if !s.c[right].p && len(s.CountConnections()) != 2 && !simple {
    fmt.Print("x")
  } else {
    fmt.Print(" ")
  }
}

func (s *space) PrintBottom(simple bool) {
  if s.c[down].e {
    fmt.Print("| ")
  } else if !s.c[down].p && len(s.CountConnections()) != 2 && !simple {
    fmt.Print("x ")
  } else {
    fmt.Print("  ")
  }
}

func (s *space) NextTwo(b *board, d dir) *space {
  if d == up {
    n := s.Above(b)
    if n == nil {
      return nil
    }
    return n.Above(b)
  } else if d == down {
    n := s.Below(b)
    if n == nil {
      return nil
    }
    return n.Below(b)
  } else if d == left {
    n := s.Left(b)
    if n == nil {
      return nil
    }
    return n.Left(b)
  } else if d == right {
    n := s.Right(b)
    if n == nil {
      return nil
    }
    return n.Right(b)
  }

  return nil
}

func (s *space) Next(b *board, d dir) *space {
  if d == up {
    return s.Above(b)
  } else if d == down {
    return s.Below(b)
  } else if d == left {
    return s.Left(b)
  } else if d == right {
    return s.Right(b)
  }

  return nil
}

func (s *space) Above(b *board) *space {
  if s.y == 0 {
    return nil
  }
  return b.contents[s.y-1][s.x]
}

func (s *space) Below(b *board) *space {
  if s.y == b.height {
    return nil
  }
  return b.contents[s.y+1][s.x]
}

func (s *space) Left(b *board) *space {
  if s.x == 0 {
    return nil
  }
  return b.contents[s.y][s.x-1]
}

func (s *space) Right(b *board) *space {
  if s.x == b.width {
    return nil
  }
  return b.contents[s.y][s.x+1]
}

func (s *space) MakeMove(b *board) int {
  moves := 0
  if s.node == black {
    opt := []dir{}
    has := len(s.CountConnections())
    if has == 2 {
      return 0
    }
    // Check how many options exist for black nodes.
    //// fmt.Printf("looking at %s\n", s.name())
    for _, d := range dirs {
      if s.c[d].e {
        //// fmt.Printf("b1 reason0: already have %s\n", d.name())
        continue
      }
      n := s.Next(b, d)
      n2 := s.NextTwo(b, d)
      if n2 == nil {
        //// fmt.Printf("b1 reason nil: edge found to the %s\n", d.name())
        continue
      }
      if !s.CanLineFrom(d) {
        //// fmt.Printf("b1 reason1: can't go %s %s %s\n", s.name(), d.name(), n.name())
        continue
      }
      if !n.CanLineFrom(d) {
        //// fmt.Printf("b1 reason2: can't go %s %s %s\n", n.name(), d.name(), n2.name())
        continue
      }

      //// fmt.Printf("b1 can: %s\n", d.name())
      opt = append(opt, d)
    }

    // If there are exactly 2, take htem
    if len(opt) + has == 2 {
      for _, d := range opt {
        if err := s.Mark("b2", b, d); err != nil {
          break
        }
        moves++
        if err := s.Next(b, d).Mark("b2", b, d); err != nil {
          break
        }
        moves++
      }
    } else if len(opt) == 3 && has == 0 {
      // If there are 3, we know one of them is good
      dirmap := make(map[dir]bool)
      for _, d := range opt {
        dirmap[d] = true
      }
      for _, d := range dirs {
        if !dirmap[d] {
          r := d.rev()
          if err := s.Mark("b1", b, r); err == nil {
            s.Next(b, r).Mark("b1", b, r)
          }
          moves++
          break
        }
      }
    }
  } else if s.node == white {
    con := s.CountConnections()
    if len(con) == 1 {
      // White nodes, you must pass straight through.
      s.Mark("w1", b, con[0].rev())
      moves++
    } else if len(con) == 2 {
      // For white nodes, one side must be next to a corner.
      for _, d := range con {
        next := s.Next(b, d)
        opp := s.Next(b, d.rev())
        if next.c[d].e && opp.c[d.rev()].p {
          fmt.Printf("w2: disallowing %s from %s\n", d.rev().name(), opp.name())
          opp.Disallow(b, d.rev())
        }
      }
    } else {
      for _, d := range dirs {
        // If one direction is disallowed, we can make the two orthogonal ones
        if !s.c[d].p {
          for _, o := range d.orthogonal() {
            s.Mark("w+", b, o)
            moves++
          }
          break
        }
        // If the next node is white, only possible if we won't have a continuing line
        if s.Next(b, d).node == white {
          // does the node in the other direction already have a line going further?
          if s.Next(b, d.rev()).c[d.rev()].e {
            fmt.Printf("wx: disallowing %s from %s", d.name(), s.name())
            s.Disallow(b, d)
          }
        }
      }
    }
  }

  // If there's only one possible option, take it.
  if s.node != empty || len(s.CountConnections()) == 1 {
    moves += s.OnlyOption(b)
  }

  return moves
}

func (s *space) OnlyOption(b *board) int {
  moves := 0
  cons := s.CountConnections()
  if len(cons) == 2 {
    return 0
  }

  poss := []dir{}
  for _, d := range dirs {
    if s.c[d].p && !s.c[d].e {
      poss = append(poss, d)
    }
  }

  if len(poss) + len(cons) == 2 {
    for _, d := range poss {
      if err := s.Mark("oo", b, d); err != nil {
        break
      }
      moves++
    }
  }

  return moves
}

func (s *space) Disallow(b *board, d dir) string {
  edge := s.c[d]
  edge.p = false
  s.c[d] = edge

  if dest := s.Next(b, d); dest != nil {
    edge = dest.c[d.rev()]
    edge.p = false
    dest.c[d.rev()] = edge
  }

  return fmt.Sprintf("disallowed line from %s %s.", s.name(), d.name())
}

func (s *space) Mark(tag string, b *board, d dir) error {
  dest := s.Next(b, d)
  rev := d.rev()
  edge := s.c[d]
  if !edge.p {
    err := fmt.Sprintf("%s: ERROR: can't mark line from %s %s to %s.", tag, s.name(), d.name(), dest.name())
    fmt.Println(err)
    return fmt.Errorf(err)
  }

  // Don't mark into a dead end
  opt := []dir{}

  for _, nd := range dirs {
    if nd == rev {
      continue
    }
    if dest.c[nd].e || dest.c[nd].p {
      opt = append(opt, nd)
    }
  }
  if len(opt) == 0 {
    err := fmt.Sprintf("%s: ERROR: will mark into a dead end from %s %s to %s", tag, s.name(), d.name(), dest.name())
    fmt.Println(err)
    s.Disallow(b, d)
    return fmt.Errorf(err)
  }

  edge.e = true
  s.c[d] = edge

  edge = dest.c[rev]
  edge.e = true
  dest.c[rev] = edge

  for _, node := range []*space{s, dest} {
    cons := node.CountConnections()
    if len(cons) != 2 {
      continue
    }

    for _, di := range dirs {
      if node.c[di].e {
        continue
      }
      node.Disallow(b, di)
    }
  }

  fmt.Printf("%s: marked line from %s %s to %s.\n", tag, s.name(), d.name(), dest.name())
  return nil
}

type board struct {
  width, height int
  contents [][]*space
  cellTop string
  counts map[nodeType]int
}

func NewBoard() *board {
  return &board{cellTop: "--"}
}

func (b *board) Copy() *board {
  newBoard := &board{
    width: b.width,
    height: b.height,
    counts: b.counts,
    cellTop: b.cellTop,
    contents: [][]*space{},
  }

  for y, line := range b.contents {
    newBoard.contents = append(newBoard.contents, []*space{})
    for x, s := range line {
      newBoard.contents[y] = append(
        newBoard.contents[y],
        &space{
          node: s.node,
          x: x,
          y: y,
          c: map[dir]edge{
            up: s.c[up],
            down: s.c[down],
            left: s.c[left],
            right: s.c[right],
          }},
      )
    }
  }

  return newBoard
}

func (b *board) Load(path string) error {
  b.contents = [][]*space{}
  b.counts = make(map[nodeType]int)

  data, err := ioutil.ReadFile(path)
  if err != nil {
    return fmt.Errorf("error reading %s: %v", path, err)
  }

  b.width = 0
  b.height = 0
  for y, line := range strings.Split(string(data), "\n") {
    if len(line) == 0 {
      continue
    }
    b.contents = append(b.contents, []*space{})
    b.height++
    for x, char := range line {
      s := space{x:x,y:y, c: make(map[dir]edge)}
      for _, d := range dirs {
        s.c[d] = edge{p: true, e: false}
      }
      if char == 'b' {
        s.node = black
      } else if char == 'w' {
        s.node = white
      } else {
        s.node = empty
      }
      b.counts[s.node]++
      if y == 0 {
        s.c[up] = edge{p: false}
      }
      if x == 0 {
        s.c[left] = edge{p: false}
      }
      b.contents[y] = append(b.contents[y], &s)
    }
    if b.width == 0 {
      b.width = len(b.contents[y])-1
    } else if b.width != len(b.contents[y])-1 {
      return fmt.Errorf("line %d length mismatch. Expected %d, got %d.", y, b.width+1, len(b.contents[y]))
    }
    b.contents[y][b.width].c[right] = edge{p: false}
  }
  b.height--

  for _, s := range b.contents[b.height] {
    s.c[down] = edge{p: false}
  }

  b.PrintBoard(false)

  return nil
}

func (b *board) PrintBoard(simple bool) {
  fmt.Print("     ")
  for i := 1; i <= b.width+1; i++  {
    fmt.Printf("%-2d", i)
  }
  fmt.Println("")
  fmt.Println("")
  for y, line := range b.contents {
    fmt.Printf("%3d  ", y+1)
    for _, space := range line {
      space.Print(simple)
      space.PrintRight(simple)
    }
    fmt.Println("")
    fmt.Print("     ")
    for _, space := range line {
      space.PrintBottom(simple)
    }
    fmt.Println("")
  }
}

func (b *board) MakeMove() string {
  for _, line := range b.contents {
    for _, space := range line {
      if moves := space.MakeMove(b); moves > 0 {
        return fmt.Sprintf("Made %d moves.", moves)
      }
    }
  }

  return ""
}

func (b *board) FindStart() *space {
  var start *space
  for _, line := range b.contents {
    for _, space := range line {
      if len(space.CountConnections()) > 0 {
        start = space
        fmt.Printf("Found starting space: %s\n", space.name())
        break
      }
    }
    if start != nil {
      break
    }
  }

  return start
}

func (b *board) FindEnd(start *space) (*space, bool) {
  var mv dir
  counts := make(map[nodeType]int)

  // Follow the path, counting node types.
  space := start
  mv = start.CountConnections()[0]
  for {
    space = space.Next(b, mv)
    // fmt.Printf("%s -> %s\n", mv.name(), space.name())
    counts[space.node]++
    next := space.CountConnections()
    if len(next) != 2 {
      // fmt.Printf("Loop ends at %s.\n", space.name())
      return space, false
    }

    if space == start {
      fmt.Println("Loop complete.")

      if counts[black] == b.counts[black] && counts[white] == b.counts[white] {
        return nil, true
      } else {
        fmt.Printf("Bad loop - found counts %v, wanted %v\n", counts, b.counts)
        return nil, false
      }
    }

    if mv.rev() == next[0] {
      mv = next[1]
    } else {
      mv = next[0]
    }
  }
  
  return nil, false
}

func (b *board) FindEnds() []*space {
  var ends []*space
  for _, line := range b.contents {
    for _, space := range line {
      if len(space.CountConnections()) == 1 {
        ends = append(ends, space)
      }
    }
  }

  return ends
}

func (b *board) CheckWin() (bool, bool) {
  fmt.Println("Checking win...")

  start := b.FindStart()
  if start == nil {
    fmt.Println("No starting point.")
    return false, true
  }
  
  if len(start.CountConnections()) != 2 {
    fmt.Println("Dangling edge.")
    return false, false
  }
  
  edge, win := b.FindEnd(start)
  if edge != nil {
    fmt.Println("Found edge.")
    return false, false
  }

  return win, true
}

func solve(b *board, depth int) {
  for {
    if move := b.MakeMove(); move != "" {
      fmt.Printf("%d: %s\n", depth, move)
      b.PrintBoard(false)
      continue
    }

    if win, err := b.CheckWin(); win {
      fmt.Printf("%d: Win!\n", depth)
      b.PrintBoard(true)
      os.Exit(0)
    } else if err {
      fmt.Printf("%d: Err!\n", depth)
      return
    }

    // Save the current board, and all ends
    for _, guess := range b.FindEnds() {
      for _, d := range dirs {
        if !guess.c[d].e && guess.c[d].p {
          newBoard := b.Copy()

          mirror := newBoard.contents[guess.y][guess.x]
          tag := fmt.Sprintf("%d(guess)", depth)
          if err := mirror.Mark(tag, newBoard, d); err != nil {
            guess.Disallow(b, d)
            continue
          }

          newBoard.PrintBoard(false)
          solve(newBoard, depth+1)
          fmt.Printf("%d: %s.\n", depth, guess.Disallow(b, d))
          fmt.Printf("%d: So that didn't work out.\n", depth)
        }
      }
    }

    fmt.Printf("%d: No moves left!\n", depth)
    return
  }
}

func main() {
  b := NewBoard()
  if err := b.Load(os.Args[1]); err != nil {
    fmt.Printf("error loading board: %v\n", err)
    os.Exit(1)
  }

  solve(b, 0)

}
