# Sales Data Analyzer

## Overview

This project provides a simple application to analyze sales data from a CSV file. It calculates total sales, average transaction value, and identifies the best-selling product.

## Requirements

- Python 3.11.0
- pandas library

## Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd SalesDataAnalyzer
    ```

2.  Install the dependencies:

    ```bash
    pip install pandas
    ```

## Usage

1.  Place your sales data CSV file in the same directory as `main.py`. The CSV file should have columns like 'Product', 'Quantity', and 'Price'.

2.  Run the application:

    ```bash
    python main.py <sales_data.csv>
    ```

    Replace `<sales_data.csv>` with the actual name of your sales data file.

## main.py Functions

-   `load_data(file_path)`: Loads the sales data from the specified CSV file into a pandas DataFrame.
-   `calculate_total_sales(data)`: Calculates the total sales from the DataFrame.
-   `calculate_average_transaction(data)`: Calculates the average transaction value from the DataFrame.
-   `find_best_selling_product(data)`: Identifies the best-selling product based on the quantity sold.
-   `main()`: The main function that orchestrates the data loading, analysis, and output.

## Example

```bash
python main.py sales_data.csv
```

## Notes

-   Ensure that the CSV file has the correct column names ('Product', 'Quantity', 'Price') for the analysis to work correctly.
