# ⚡ CSV Plotter & Electricity Forecast App

A premium, interactive Flask-based web application and analytics console designed for uploading CSV data, visualizing columns, plotting custom charts, and running seasonal time-series forecasts using SARIMAX.

---

## 🚀 Features

### 📊 Data Visualization & CSV Parsing
- **CSV File Upload**: Instantly upload any tabular CSV file.
- **Dynamic Chart Plotting**: Generate interactive charts including:
  - **Line Plots** (default)
  - **Bar Charts**
  - **Scatter Plots**
- **Matplotlib Integration**: Automatic backend rendering (`Agg` mode) for thread-safe plot generation.

### 🔮 Time-Series SARIMAX Forecasting
- **Automatic Column Detection**: Intelligently identifies time/date columns and numerical target value columns (e.g., electricity load/consumption).
- **SARIMAX Model Training**: Fits a Seasonal AutoRegressive Integrated Moving Average model (`order=(1,1,1)`, `seasonal_order=(1,1,1, s)`) from `statsmodels`.
- **Forecast Comparison**: Automatically performs a train-test split, generates forecasts, and visualizes predictions against actual test data.
- **Evaluation Metrics**: Calculates Mean Absolute Error (MAE) and percentage errors for each predicted point, presented in a clean tabular view.

### 💻 Premium Interactive Dashboard
- **Modern UI/UX**: Built with an elegant light-mode dashboard aesthetic utilizing modern typography (`Inter` & `Outfit` fonts).
- **Asynchronous API Integration**: Employs AJAX calls to perform tasks seamlessly without full-page reloads.

---

## 🛠️ Technology Stack

- **Backend Framework**: [Flask](https://flask.palletsprojects.com/) (Python)
- **Data & Forecasting**:
  - [Pandas](https://pandas.pydata.org/) (Data manipulation)
  - [statsmodels](https://www.statsmodels.org/) (SARIMAX forecasting model)
  - [pmdarima](https://alkaline-ml.com/pmdarima/) (Time-series analysis utilities)
- **Visualization**: [Matplotlib](https://matplotlib.org/) (Plot generation)
- **Frontend**: Plain HTML5, Vanilla CSS, and JavaScript (Fetch API)

---

## ⚙️ Getting Started

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Install Dependencies
Clone the repository, navigate to the project directory, and install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Flask development server:
```bash
python app.py
```

Upon launching, the app will **automatically open your default web browser** to `http://127.0.0.1:5000`.

---

## 📂 Project Structure

```text
csv_plotter_app/
├── app.py                  # Main Flask backend application (routes & forecasting logic)
├── requirements.txt        # Python package dependencies
├── data.csv / sample_data.csv # Sample datasets for quick testing
├── templates/
│   ├── index.html          # Main interactive dashboard UI
│   └── graph.html          # Secondary graph visualization page
├── static/
│   ├── plot.png            # Statically generated plot image
│   └── forecast.png        # Statically generated forecast image
└── uploads/
    └── uploaded.csv        # Directory where uploaded CSVs are saved and processed
```
