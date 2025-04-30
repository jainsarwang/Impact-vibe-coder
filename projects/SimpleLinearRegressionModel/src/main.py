import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import streamlit as st
import base64
import io
import os
import zipfile

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Function to display project directory in sidebar
def display_project_directory(project_dir):
    st.sidebar.header("Project Directory")
    files = []
    for (dirpath, dirnames, filenames) in os.walk(project_dir):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))

    for file in files:
        st.sidebar.write(file)

# Function to generate a download link for the project as a zip file
def download_project(project_dir):
    zip_file = io.BytesIO()
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, project_dir))
    zip_file.seek(0)
    b64 = base64.b64encode(zip_file.read()).decode()
    href = f'<a href="data:file/zip;base64,{b64}" download="{os.path.basename(project_dir)}.zip">Download Project ZIP</a>'
    return href


# Load custom CSS
local_css("src/style.css")

# Set the project directory
project_dir = "SimpleLinearRegressionModel"

# Display project directory in sidebar
display_project_directory(project_dir)

# Main function
def main():
    st.title("Simple Linear Regression Model")

    # Load the dataset
    try:
        df = pd.read_csv("D:\langmanus\SimpleLinearRegressionModel\data\house_price.csv")
    except FileNotFoundError:
        st.error("Dataset 'house_prices.csv' not found in the 'data' directory. Please download it from Kaggle or provide a CSV file with a numerical feature and target variable.")
        return

    # Explore the dataset
    st.header("Dataset Overview")
    st.dataframe(df.head())
    st.write(df.describe())
    st.write(df.info())

    # Select feature and target variables
    st.header("Feature and Target Selection")
    feature_col = st.selectbox("Select feature variable", df.columns)
    target_col = st.selectbox("Select target variable", df.columns)

    # Handle missing values
    st.header("Handling Missing Values")
    if df[feature_col].isnull().any() or df[target_col].isnull().any():
        st.warning("Missing values found in the selected feature or target variable. Imputing with the mean.")
        df[feature_col].fillna(df[feature_col].mean(), inplace=True)
        df[target_col].fillna(df[target_col].mean(), inplace=True)
    else:
        st.success("No missing values found in the selected feature or target variable.")

    # Split the data into training and testing sets
    st.header("Data Splitting")
    X = df[[feature_col]]
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a linear regression model
    st.header("Model Training")
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions on the test data
    st.header("Model Prediction")
    y_pred = model.predict(X_test)

    # Evaluate the model's performance
    st.header("Model Evaluation")
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    st.write(f"Mean Squared Error: {mse:.2f}")
    st.write(f"R-squared Score: {r2:.2f}")

    # Visualize the results
    st.header("Visualization")
    fig, ax = plt.subplots()
    ax.scatter(X_test, y_test, label="Actual")
    ax.plot(X_test, y_pred, color='red', label="Predicted")
    ax.set_xlabel(feature_col)
    ax.set_ylabel(target_col)
    ax.legend()
    st.pyplot(fig)

    # Predict price of a new house
    st.header("Predict Price of a New Data")
    new_feature_value = st.number_input(f"Enter the value of {feature_col}")
    predicted_price = model.predict([[new_feature_value]])[0]
    st.write(f"Predicted {target_col}: {predicted_price:.2f}")

    # Download Project
    st.markdown(download_project(project_dir), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
