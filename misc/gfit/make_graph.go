package main

import (
    "encoding/csv"
    "os"
    "io"
    "fmt"
    "log"
    "io/ioutil"
    "html/template"
    "strings"
    "strconv"
)

type gfitLine struct {
  Year, Month, Day uint
  Data []int
}

type col struct {
  name string
  idx int
  factor uint
}

type data struct {
  Cols []string
  Rows []gfitLine
}

const (
  msToMin = 60*1000
)

func mustAtoi(s string) uint {
  if s == "" { return 0 }
  n, err := strconv.ParseUint(s, 10, 64)
  if err != nil {
    log.Fatalf("Can't convert %q to int: %v", s, err)
  }
  return uint(n)
}

func parseLines(cols []col, f io.Reader) ([]gfitLine, error) {
  res := []gfitLine{}
  r := csv.NewReader(f)

  // Skip the headers
  _, err := r.Read()
  if err != nil {
    return nil, fmt.Errorf("error parsing header: %v", err)
  }

  var lastMonth, lastYear uint
  var totals []int
  lastMonth = 13
  for {
    l, err := r.Read()
    if err == io.EOF {
      rec := gfitLine{Year: lastYear, Month: lastMonth, Day: 1, Data: totals}
      res = append(res, rec)
      break
    }
    if err != nil {
      return nil, fmt.Errorf("error parsing line: %v", err)
    }
    date := strings.Split(l[0], "-")
    year := mustAtoi(date[0])
    month := mustAtoi(date[1]) - 1
    // day := mustAtoi(date[2])
    if mustAtoi(l[28]) > 40000000 {
      m := mustAtoi(l[28]) / 60000
      log.Printf("discarding value for cycling in %s: %d", date, m)
      l[28] = "0"
    }

    if month != lastMonth {
      if lastMonth != 13 {
        rec := gfitLine{Year: lastYear, Month: lastMonth, Day: 1, Data: totals}
        res = append(res, rec)
        totals = nil
      }
      lastMonth = month
      lastYear = year
    }

    if len(totals) > 0 {
      for i, c := range cols {
        totals[i] += int(mustAtoi(l[c.idx]) / c.factor)
      }
    } else {
      for _, c := range cols {
        totals = append(totals, int(mustAtoi(l[c.idx]) / c.factor))
      }
    }
  }

  return res, nil
}

func main() {
  if len(os.Args) != 4 {
    fmt.Println("Usage: input.csv template.html out.html")
    os.Exit(1)
  }
  fname := os.Args[1]
  tmplName := os.Args[2]
  htmlName := os.Args[3]
  f, err := os.Open(fname)
  if err != nil {
    log.Fatalf("Can't open %q: %v", fname, err)
  }

  fm := map[string]interface{}{
    "join": strings.Join,
  }

  tmplData, err := ioutil.ReadFile(tmplName)
  if err != nil {
    log.Fatalf("Can't read template from %q: %v", tmplName, err)
  }

  tmpl, err := template.New("t").Funcs(fm).Parse(string(tmplData))
  if err != nil {
    log.Fatalf("Error parsing template %q: %v", tmplName, err)
  }

  cols := []col{
    {
      name: "Biking",
      idx: 28,
      factor: msToMin,
    },
    {
      name: "Spinning",
      idx: 33,
      factor: msToMin,
    },
    {
      name: "Stationary",
      idx: 34,
      factor: msToMin,
    },
    {
      name: "Climbing",
      idx: 40,
      factor: msToMin,
    },
    {
      name: "Strength",
      idx: 42,
      factor: msToMin,
    },
  }
  colTitles := []string{}
  for _, c := range cols {
    colTitles = append(colTitles, c.name)
  }

  lines, err := parseLines(cols, f)
  if err != nil {
    log.Fatalf("Error parsing csv: %v",  err)
  }

  tmp, err := ioutil.TempFile("", ".html")
  if err != nil {
    log.Fatalf("Error creating tmpfile: %v", err)
  }
  tmpName := tmp.Name()

  if err := tmpl.Execute(tmp, data{Cols: colTitles, Rows: lines}); err != nil {
    log.Fatalf("Error executing template: %v",  err)
  }

  tmp.Close()
  if err := os.Rename(tmpName, htmlName); err != nil {
    log.Fatalf("Error renaming %q to %q: %v", tmpName, htmlName)
  }

  if err := os.Chmod(htmlName, 0644); err != nil {
    log.Fatalf("Can't chmod %q: %v", htmlName, err)
  }
}
