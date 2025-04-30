# Simple Linear Regression Model User Manual

## Overview

This project implements a simple linear regression model to predict a target variable based on a single feature from a dataset. The project includes a Python script for training and evaluating the model, as well as instructions for running the script and interpreting the results.

## Prerequisites

Before running the project, ensure you have the following installed:

*   Python (3.6 or higher)
*   Pip (Python package installer)

## Installation

1.  Clone the repository to your local machine.
2.  Navigate to the project directory.
3.  Install the required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Dataset:** The script expects a CSV dataset named `house_prices.csv` in the `data` directory. If you don't have this dataset, you can download it from Kaggle (e.g., the "House Prices - Advanced Regression Techniques" dataset) or use any other CSV dataset with a numerical feature and target variable.
2.  **Running the Script:**

    To run the script, execute the following command from the project directory:

    ```bash
    npm start
    ```

    This will start the Streamlit application, which will:
        * Load the dataset.
        * Train a linear regression model.
        * Display the model's performance metrics (MSE and R2 score).
        * Show a visualization of the regression line.
        * Allow you to predict the price of a new house based on its size.

## Interpreting the Results

*   **Mean Squared Error (MSE):** The MSE measures the average squared difference between the predicted and actual values. A lower MSE indicates better model performance.
*   **R-squared (R2) Score:** The R2 score represents the proportion of variance in the target variable that can be explained by the feature variable. An R2 score closer to 1 indicates a better fit.

## Customization

You can customize the script by:

*   Changing the dataset file path.
*   Selecting different feature and target variables.
*   Modifying the data splitting ratio.
*   Experimenting with different imputation methods for missing values.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.