from sector import Sector, sp500_sectors

if __name__ == "__main__":
    sectors = sp500_sectors()

    START_DATE = "2022-10-12"
    MIDPOINT_DATE = "2023-10-12"
    END_DATE = "2024-01-12"

    for sector_name, sector_stocks in sectors.items():
        sector = Sector(sector_name, sector_stocks)

        sector.run_calculations(START_DATE, MIDPOINT_DATE, END_DATE)
