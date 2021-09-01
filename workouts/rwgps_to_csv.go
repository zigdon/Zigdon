package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	"github.com/zigdon/goride"
)

var (
	configFile = flag.String(
		"config",
		filepath.Join(os.Getenv("HOME"), ".config", "ridewithgps.ini"),
		"Path to ridewithgps ini file.")
	start = flag.String("start", "2000-01-01", "Only collect rides after this date.")
	count = flag.Int("count", 0, "How many rides to collect, 0 to get all.")
)

func rideToCSV(r *goride.RideSlim, gear map[int]string) []string {
	year, month, day := r.DepartedAt.Date()
	date := fmt.Sprintf("%04d-%02d-%02d", year, month, day)
	time := fmt.Sprintf("%02d:%02d:%02d", r.DepartedAt.Hour(), r.DepartedAt.Minute(), r.DepartedAt.Second())
	line := []string{
		// Date
		date,
		// Time
		time,
		// ID
		fmt.Sprintf("%d", r.ID),
		// Name
		r.Name,
		// Description
		r.Description,
		// Gear
		gear[r.GearID],
		// Duration
		fmt.Sprintf("%d", r.Duration),
		// Distance
		fmt.Sprintf("%.2f", r.Distance),
		// Elevation
		fmt.Sprintf("%.2f", r.ElevationGain),
		// sw lat/long
		fmt.Sprintf("%.2f", r.SwLat),
		fmt.Sprintf("%.2f", r.SwLng),
		// ne lat/long
		fmt.Sprintf("%.2f", r.NeLat),
		fmt.Sprintf("%.2f", r.NeLng),
	}

	return line
}

func writeCSV(path string, rides []*goride.RideSlim, gear map[int]string) error {
	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("can't open %q: %v", path, err)
	}
	defer f.Close()

	w := csv.NewWriter(f)
	defer w.Flush()

	// Write headers
	header := []string{
		"Date",
		"Time",
		"ID",
		"Name",
		"Description",
		"Gear",
		"Duration",
		"Distance",
		"Elevation",
		"sw latlong",
		"sw long",
		"ne lat",
		"ne long",
	}
	if err := w.Write(header); err != nil {
		return fmt.Errof("Error writing headers: %v", err)
	}

	for i, r := range rides {
		line := rideToCSV(r, gear)
		if err := w.Write(line); err != nil {
			return fmt.Errorf("error writing line %d: %v\n%v", i, err, line)
		}
	}

	return nil
}

func getRides(api *goride.RWGPS, user *goride.User) ([]*goride.RideSlim, error) {
	var res []*goride.RideSlim
	limit := 100
	offset := user.TotalTrips
	gotRides := 0
	startDate, err := time.Parse("2006-01-02", *start)
	if err != nil {
		return nil, fmt.Errorf("can't parse %q as date: %v", *start, err)
	}

	log.Printf("Total rides: %d", user.TotalTrips)
	for offset > 0 && (*count == 0 || gotRides <= *count) {
		offset -= limit
		if offset < 0 {
			offset = 0
		}
		log.Printf("Getting rides %d-%d (%d got)", offset, offset+limit, gotRides)
		rides, _, err := api.GetRides(user.ID, offset, limit)
		if err != nil {
			return nil, fmt.Errorf("can't get more rides at offset %d: %v", offset)
		}
		if rides[0].DepartedAt.Before(startDate) {
			log.Printf("Skipping set (%s)", rides[0].DepartedAt)
			continue
		}
		for i := range rides {
			ride := rides[len(rides)-i-1]
			if ride.DepartedAt.Before(startDate) {
				log.Printf("Skipping ride (%s)", ride.DepartedAt)
				continue
			}
			if *count > 0 && gotRides > *count {
				break
			}
			gotRides += 1
			res = append(res, ride)
		}
	}
	log.Printf("Got %d rides.", len(res))

	return res, nil
}

func main() {
	flag.Parse()
	outFile := flag.Arg(0)
	if outFile == "" {
		log.Fatal("Usage: rwgps_to_csv.go <outfile>")
	}

	api, err := goride.New(*configFile)
	if err != nil {
		log.Fatalf("Can't load config from %q: %v", *configFile, err)
	}

	if err := api.Auth(); err != nil {
		log.Fatalf("Can't auth to RWGPS: %v", err)
	}

	user, err := api.GetCurrentUser()
	if err != nil {
		log.Fatalf("Can't get logged in user: %v", err)
	}
	gear := map[int]string{0: "N/A"}
	for _, g := range user.Gear {
		gear[g.ID] = g.Name
	}

	rides, err := getRides(api, user)
	if err != nil {
		log.Fatalf("Can't get rides: %v", err)
	}

	if err := writeCSV(outFile, rides, gear); err != nil {
		log.Fatalf("Can't write CSV to %q: %v", outFile, err)
	}
}
