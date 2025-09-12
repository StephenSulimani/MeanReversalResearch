package main

import (
	"encoding/csv"
	"errors"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
	"time"
)

type ClusterDefinition map[time.Time]map[string][]string

type DateRange struct {
	Start time.Time
	End   time.Time
}

type StockData map[string]map[time.Time]float64

func ProcessClusterCSV(filename string) (ClusterDefinition, DateRange, []string, error) {
	clusterDef := ClusterDefinition{}
	dateRange := DateRange{}

	file, err := os.Open(filename)
	if err != nil {
		return clusterDef, dateRange, []string{}, err
	}
	defer file.Close()

	reader := csv.NewReader(file)

	header, err := reader.Read()
	if err != nil {
		return clusterDef, dateRange, []string{}, err
	}

	dateCol := -1

	identifierCols := map[int]string{}
	allIdentifiers := []string{}

	for i, col := range header {
		if strings.ToLower(col) == "date" {
			dateCol = i
		} else {
			identifierCols[i] = col
			allIdentifiers = append(allIdentifiers, col)
		}
	}

	if dateCol == -1 {
		return clusterDef, dateRange, []string{}, errors.New("date column not found")
	}

	for {
		record, err := reader.Read()
		if err != nil {
			if err == io.EOF {
				break
			}
			return clusterDef, dateRange, []string{}, err
		}

		var date time.Time

		for i, col := range record {
			if i == dateCol {
				date, err = time.Parse("2006-01-02", col)
				if err != nil {
					return clusterDef, dateRange, []string{}, errors.New("unable to parse date")
				}
				break
			}
		}

		for i, col := range record {
			if i != dateCol && len(col) > 0 {
				if _, ok := clusterDef[date]; !ok {
					clusterDef[date] = map[string][]string{}
				}
				clusterDef[date][col] = append(clusterDef[date][col], identifierCols[i])
			}
			if date.Before(dateRange.Start) || dateRange.Start.IsZero() {
				dateRange.Start = date
			}
			if date.After(dateRange.End) || dateRange.End.IsZero() {
				dateRange.End = date
			}
		}
	}

	return clusterDef, dateRange, allIdentifiers, nil
}

func PreLoadStocks(allStocks []string) (StockData, error) {
	stocks := StockData{}
	for _, stock := range allStocks {
		file, err := os.Open(fmt.Sprintf("data/%s.csv", stock))
		if err != nil {
			continue
		}

		reader := csv.NewReader(file)

		header, err := reader.Read()
		if err != nil {
			return StockData{}, err
		}

		dateCol := -1
		priceCol := -1

		for i, col := range header {
			if dateCol != -1 && priceCol != -1 {
				break
			}
			if strings.ToLower(col) == "date" {
				dateCol = i
			}
			if strings.ToLower(col) == "close" || strings.ToLower(col) == "price" || strings.ToLower(col) == "adj_prc" {
				priceCol = i
			}
		}

		if dateCol == -1 {
			return StockData{}, errors.New("date column not found")
		}

		for {
			record, err := reader.Read()
			if err != nil {
				if err == io.EOF {
					break
				}
				return StockData{}, err
			}

			date, err := time.Parse("2006-01-02", record[dateCol])
			if err != nil {
				return StockData{}, errors.New("unable to parse date")
			}

			if _, ok := stocks[stock]; !ok {
				stocks[stock] = map[time.Time]float64{}
			}
			price, err := strconv.ParseFloat(record[priceCol], 64)
			if err != nil {
				return StockData{}, err
			}
			stocks[stock][date] = price
		}
	}
	return stocks, nil
}

type Boundary struct {
	LookbackStart time.Time
	LookbackEnd   time.Time
	TestStart     time.Time
	TestEnd       time.Time
	BestStocks    []string
	WorstStocks   []string
}

func (clusterDef *ClusterDefinition) findDate(date time.Time) (time.Time, error) {
	attempts := 0
	for {
		if _, ok := (*clusterDef)[date]; ok {
			return date, nil
		}
		date = date.AddDate(0, 1, 0)
		attempts += 1
		if attempts > 5 {
			return time.Time{}, errors.New("unable to find date")
		}
	}
}

func getLastDayOfMonth(t time.Time) time.Time {
	// Check the day of the month
	day := t.Day()

	if day <= 15 {
		// If in the first half of the month, return the last day of the previous month
		return time.Date(t.Year(), t.Month(), 1, 0, 0, 0, 0, t.Location()).AddDate(0, 0, -1)
	}

	// If in the second half of the month, return the last day of the current month
	nextMonth := t.AddDate(0, 1, 0)
	return time.Date(nextMonth.Year(), nextMonth.Month(), 1, 0, 0, 0, 0, t.Location()).AddDate(0, 0, -1)
}

func setToFirstDayOfMonth(t time.Time) time.Time {
	// Check the day of the month
	day := t.Day()

	if day <= 15 {
		// If in the first half of the month, set to the first day of the current month
		return time.Date(t.Year(), t.Month(), 1, 0, 0, 0, 0, t.Location())
	}

	// If in the second half of the month, set to the first day of the next month
	return time.Date(t.Year(), t.Month()+1, 1, 0, 0, 0, 0, t.Location())
}

func DefineBoundaries(clusterDef ClusterDefinition, dateRange DateRange, lookbackMonths int) ([]Boundary, error) {
	boundaries := []Boundary{}

	lookback_start := setToFirstDayOfMonth(dateRange.Start)
	lookback_end := getLastDayOfMonth(dateRange.Start.AddDate(0, lookbackMonths, 0))
	test_start := setToFirstDayOfMonth(lookback_end.AddDate(0, 0, 1))
	test_end := getLastDayOfMonth(test_start.AddDate(0, 0, 30))

	boundaries = append(boundaries, Boundary{LookbackStart: dateRange.Start, LookbackEnd: lookback_end, TestStart: test_start, TestEnd: test_end, BestStocks: []string{}, WorstStocks: []string{}})

	for {
		if test_end.AddDate(0, 0, 1).After(dateRange.End) {
			return boundaries, nil
		}

		lookback_start = setToFirstDayOfMonth(lookback_start.AddDate(0, 1, 0))
		lookback_end = getLastDayOfMonth(lookback_start.AddDate(0, lookbackMonths, 0))
		test_start = setToFirstDayOfMonth(lookback_end.AddDate(0, 0, 1))
		test_end = getLastDayOfMonth(test_start.AddDate(0, 1, 0))

		if lookback_start.Before(dateRange.End) && lookback_end.Before(dateRange.End) && test_start.Before(dateRange.End) && test_end.After(dateRange.End) {
			test_end = dateRange.End
		}

		boundaries = append(boundaries, Boundary{LookbackStart: lookback_start, LookbackEnd: lookback_end, TestStart: test_start, TestEnd: test_end, BestStocks: []string{}, WorstStocks: []string{}})
		if lookback_start.After(dateRange.End) || lookback_end.After(dateRange.End) || test_start.After(dateRange.End) || test_end.After(dateRange.End) {
			return boundaries, nil
		}

	}
}
