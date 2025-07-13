package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
)

// [
//     {
//         "lookback": {
//             "start": "2020-01-01",
//             "end": "2020-03-31"
//         },
//         "test": {
//             "start": "2020-04-01",
//             "end": "2020-04-30"
//         },
//         "best_stocks": [
//             "DLR",
//             "SBAC",
//             "NEM",
//             "MSCI",
//             "DPZ",
//             "MPWR",
//             "TSLA",
//             "ROL",
//             "DXCM",
//             "NFLX",
//             "MRNA"
//         ],
//         "worst_stocks": [
//             "BA",
//             "SPG",
//             "APA",
//             "DFS",
//             "TPR",
//             "HAL",
//             "CNP",
//             "NCLH",
//             "ALGN",
//             "PARA",
//             "CTVA"
//         ]
//     },

type Period struct {
	Start string `json:"start"`
	End   string `json:"end"`
}

type BoundaryJSON struct {
	Lookback    Period   `json:"lookback"`
	Test        Period   `json:"test"`
	BestStocks  []string `json:"best_stocks"`
	WorstStocks []string `json:"worst_stocks"`
}

func (b *Boundary) ConvertToJSON() BoundaryJSON {
	return BoundaryJSON{
		Lookback: Period{
			Start: b.LookbackStart.Format("2006-01-02"),
			End:   b.LookbackEnd.Format("2006-01-02"),
		},
		Test: Period{
			Start: b.TestStart.Format("2006-01-02"),
			End:   b.TestEnd.Format("2006-01-02"),
		},
		BestStocks:  b.BestStocks,
		WorstStocks: b.WorstStocks,
	}
}

func main() {
	// Accept commandline arguments
	//Usage: python StockPicker.py <cluster_csv> <n> <lookback_months> <output_json>

	if len(os.Args) != 5 {
		fmt.Println("Usage: ./StockPicker <cluster_csv> <n> <lookback_months> <output_json>")
		return
	}

	clusterCSV := os.Args[1]
	n, _ := strconv.ParseInt(os.Args[2], 10, 64)
	lookbackMonths, _ := strconv.ParseInt(os.Args[3], 10, 64)
	outputJSON := os.Args[4]

	clusterDef, dateRange, allStocks, err := ProcessClusterCSV(clusterCSV)

	if err != nil {
		fmt.Println(err)
		return
	}

	// fmt.Println(clusterDef)
	// fmt.Println(allStocks)
	// fmt.Println(dateRange)

	stocks, err := PreLoadStocks(allStocks)

	if err != nil {
		fmt.Println(err)
		return
	}

	boundaries, err := DefineBoundaries(clusterDef, dateRange, int(lookbackMonths))

	// fmt.Println(boundaries)

	PickStocks(clusterDef, stocks, &boundaries, int(n))

	jsonBoundaries := []BoundaryJSON{}

	for _, boundary := range boundaries {
		jsonBoundaries = append(jsonBoundaries, boundary.ConvertToJSON())
	}

	json_bytes, err := json.MarshalIndent(jsonBoundaries, "", "    ")

	if err != nil {
		fmt.Println(err)
		return
	}

	os.WriteFile(outputJSON, json_bytes, 0644)

}
