package main

import (
	"errors"
	"math/rand"
	"sort"
	"time"

	"github.com/schollz/progressbar/v3"
)

func calculateReturn(startPrice float64, endPrice float64) float64 {
	return (endPrice - startPrice) / startPrice * 100
}

func findDate(date time.Time, stockData map[time.Time]float64, forward bool) (time.Time, error) {
	attempts := 0
	for {
		if _, ok := stockData[date]; ok {
			return date, nil
		}

		if forward {
			date = date.AddDate(0, 0, 1)
		} else {
			date = date.AddDate(0, 0, -1)
		}
		attempts += 1
		if attempts > 5 {
			return time.Time{}, errors.New("unable to find date")
		}
	}
}

type kv struct {
	Key   string
	Value float64
}

func PickStocks(clusterDef ClusterDefinition, data StockData, boundaries *[]Boundary, n int, randomFlag bool) {
	bar := progressbar.Default(int64(len(*boundaries)), "Boundaries Processed")
	for i, boundary := range *boundaries {
		sectors, ok := clusterDef[boundary.LookbackStart]

		for !ok {
			boundary.LookbackStart = boundary.LookbackStart.AddDate(0, 0, 1)
			sectors, ok = clusterDef[boundary.LookbackStart]
		}

		for _, stocks := range sectors {
			defer bar.Add(1)
			if len(stocks) <= 1 {
				continue
			}
			if randomFlag {
				randomBestStock := stocks[rand.Intn(len(stocks))]
				randomWorstStock := stocks[rand.Intn(len(stocks))]

				// for randomBestStock == "" {
				// 	randomBestStock = stocks[rand.Intn(len(stocks))]
				// }
				//
				// for randomWorstStock == "" {
				// 	randomWorstStock = stocks[rand.Intn(len(stocks))]
				// }
				//
				// for randomBestStock == randomWorstStock {
				// 	randomWorstStock = stocks[rand.Intn(len(stocks))]
				// }

				(*boundaries)[i].BestStocks = append((*boundaries)[i].BestStocks, randomBestStock)
				(*boundaries)[i].WorstStocks = append((*boundaries)[i].WorstStocks, randomWorstStock)

				continue

			}
			stock_returns := []kv{}

			for _, stock := range stocks {
				if _, ok := data[stock]; !ok {
					continue
				}

				start_date, err := findDate(boundary.LookbackStart, data[stock], true)
				if err != nil {
					continue
				}

				end_date, err := findDate(boundary.LookbackEnd, data[stock], false)
				if err != nil {
					continue
				}

				start_price := data[stock][start_date]
				end_price := data[stock][end_date]
				return_pct := calculateReturn(start_price, end_price)

				stock_returns = append(stock_returns, kv{Key: stock, Value: return_pct})
			}

			sort.Slice(stock_returns, func(i, j int) bool {
				return stock_returns[i].Value > stock_returns[j].Value
			})

			for j := range n {
				if j < len(stock_returns) {
					(*boundaries)[i].BestStocks = append((*boundaries)[i].BestStocks, stock_returns[j].Key)
				}
			}

			sort.Slice(stock_returns, func(i, j int) bool {
				return stock_returns[i].Value < stock_returns[j].Value
			})

			for j := range n {
				if j < len(stock_returns) {
					(*boundaries)[i].WorstStocks = append((*boundaries)[i].WorstStocks, stock_returns[j].Key)
				}
			}

		}

	}
}
