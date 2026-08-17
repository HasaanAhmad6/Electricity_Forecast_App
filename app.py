import os
import shutil
import threading
import webbrowser
import pandas as pd

# Set matplotlib backend to 'Agg' before importing pyplot to ensure thread safety
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask, request, jsonify, render_template, redirect, url_for
from statsmodels.tsa.statespace.sarimax import SARIMAX

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Global variable to track the uploaded CSV filename
csv_filename = os.path.join(UPLOAD_FOLDER, 'uploaded.csv')


@app.route('/', methods=['GET', 'POST'])
def index():
    # Detect API/CLI checks like curl that don't request HTML and return health message
    accept_header = request.headers.get('Accept', '')
    user_agent = request.headers.get('User-Agent', '')
    if request.method == 'GET' and 'text/html' not in accept_header and 'Mozilla' not in user_agent:
        return "✅ Flask server is running!", 200

    graph_url = None
    selected_plot = 'line'
    
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            plot_type = request.form.get('plot_type', 'line')
            selected_plot = plot_type
            
            if file.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.csv')
                orig_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                
                # Save uploaded file
                file.save(filepath)
                
                # Create a copy with the original filename for backup/compatibility
                try:
                    shutil.copyfile(filepath, orig_filepath)
                except Exception as e:
                    print(f"Error copying file: {e}")
                
                global csv_filename
                csv_filename = filepath
                
                try:
                    df = pd.read_csv(filepath)
                    if df.shape[1] >= 2:
                        plt.clf()
                        plt.figure(figsize=(10, 6))
                        x_col, y_col = df.columns[0], df.columns[1]
                        
                        if plot_type == 'line':
                            plt.plot(df[x_col], df[y_col], marker='o')
                        elif plot_type == 'bar':
                            plt.bar(df[x_col], df[y_col])
                        elif plot_type == 'scatter':
                            plt.scatter(df[x_col], df[y_col])
                        else:
                            plt.plot(df[x_col], df[y_col], marker='o')
                            
                        plt.xlabel(x_col)
                        plt.ylabel(y_col)
                        plt.title(f'{plot_type.capitalize()} Plot of {y_col} vs {x_col}')
                        plt.tight_layout()
                        
                        graph_path = os.path.join(app.config['STATIC_FOLDER'], 'plot.png')
                        plt.savefig(graph_path)
                        plt.close()
                        graph_url = '/' + graph_path
                except Exception as e:
                    print(f"Error plotting inside index POST: {e}")

    return render_template('index.html', graph_url=graph_url, selected_plot=selected_plot)


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    global csv_filename
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save to standard path
    fixed_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.csv')
    file.save(fixed_path)
    
    # Also save to original filename path to satisfy both systems
    orig_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        shutil.copyfile(fixed_path, orig_filepath)
    except Exception as e:
        print(f"Error copying file in API upload: {e}")
        
    csv_filename = fixed_path
    return jsonify({'message': 'File uploaded successfully', 'filename': file.filename}), 200


@app.route('/get_columns', methods=['GET'])
def get_columns():
    global csv_filename
    target_path = csv_filename
    if not target_path or not os.path.exists(target_path):
        target_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.csv')
        
    if not os.path.exists(target_path):
        # Check if there are any other CSVs in the uploads directory
        csv_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.csv')]
        if csv_files:
            target_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_files[0])
        else:
            return jsonify({'error': 'No CSV file uploaded yet'}), 400
            
    try:
        df = pd.read_csv(target_path)
        return jsonify({'columns': list(df.columns)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/plot', methods=['POST'])
def plot_graph():
    global csv_filename
    target_path = csv_filename
    if not target_path or not os.path.exists(target_path):
        target_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.csv')
        
    if not os.path.exists(target_path):
        return jsonify({'error': 'No CSV file uploaded'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400

    # Support keys from both flask_csv_plot_project and FlaskGraphProject
    x_col = data.get('x') or data.get('x_column')
    y_col = data.get('y') or data.get('y_column')
    graph_type = data.get('type') or data.get('graph_type')

    if not x_col or not y_col or not graph_type:
        return jsonify({'error': 'Missing x, y, or type parameter'}), 400

    try:
        df = pd.read_csv(target_path)
        if x_col not in df.columns or y_col not in df.columns:
            return jsonify({'error': f'Invalid column name(s). Available columns: {list(df.columns)}'}), 400

        plt.clf()
        plt.figure(figsize=(10, 6))
        
        if graph_type == 'line':
            plt.plot(df[x_col], df[y_col], marker='o')
        elif graph_type == 'bar':
            plt.bar(df[x_col], df[y_col])
        elif graph_type == 'scatter':
            plt.scatter(df[x_col], df[y_col])
        else:
            return jsonify({'error': f'Unsupported graph type: {graph_type}'}), 400

        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f'{graph_type.capitalize()} Plot of {y_col} vs {x_col}')
        plt.tight_layout()
        
        plot_path = os.path.join(app.config['STATIC_FOLDER'], 'plot.png')
        plt.savefig(plot_path)
        plt.close()
        
        return jsonify({'message': 'Plot created', 'url': '/graph'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/graph', methods=['GET'])
def display_graph():
    return render_template('graph.html')


@app.route('/run_forecast', methods=['POST'])
def run_forecast():
    global csv_filename
    target_path = csv_filename
    if not target_path or not os.path.exists(target_path):
        target_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.csv')
        
    if not os.path.exists(target_path):
        return jsonify({'error': 'No CSV file uploaded yet'}), 400
        
    try:
        df = pd.read_csv(target_path)
        
        data_payload = request.get_json() if request.is_json else request.form
        
        date_col = data_payload.get('date_column')
        value_col = data_payload.get('value_column')
        steps_val = data_payload.get('forecast_steps', 7)
        
        try:
            steps = int(steps_val)
        except (ValueError, TypeError):
            steps = 7
            
        # Column auto-detection
        if not date_col or date_col not in df.columns:
            date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower() or 'year' in c.lower()]
            date_col = date_cols[0] if date_cols else df.columns[0]
            
        if not value_col or value_col not in df.columns:
            val_cols = [c for c in df.columns if c != date_col and (df[c].dtype == 'float64' or df[c].dtype == 'int64')]
            value_col = val_cols[0] if val_cols else (df.columns[1] if len(df.columns) > 1 else df.columns[0])
            
        # Create sorted datetime clean dataframe
        df_clean = df[[date_col, value_col]].copy()
        df_clean[date_col] = pd.to_datetime(df_clean[date_col])
        df_clean = df_clean.sort_values(date_col)
        df_clean.set_index(date_col, inplace=True)
        
        if len(df_clean) < steps + 2:
            return jsonify({'error': f'Dataset contains only {len(df_clean)} rows. Need at least {steps + 2} to split and forecast.'}), 400
            
        # Train-test split
        train = df_clean.iloc[:-steps]
        test = df_clean.iloc[-steps:]
        
        # Train seasonal SARIMAX
        # Order parameter (1,1,1) x Seasonal Order (1,1,1,steps or 7) matching the original project
        seasonal_period = steps if steps > 1 else 7
        model = SARIMAX(train[value_col], order=(1,1,1), seasonal_order=(1,1,1,seasonal_period))
        result = model.fit(disp=False)
        
        forecast = result.forecast(steps=steps)
        forecast.index = test.index
        
        # Plot styling for light-mode premium interface
        plt.clf()
        fig = plt.figure(figsize=(10, 5))
        fig.patch.set_facecolor('#ffffff')
        
        ax = plt.gca()
        ax.set_facecolor('#ffffff')
        
        # Draw curves
        plt.plot(train.index, train[value_col], label="Historical (Train)", color="#2563eb", linewidth=2.5)
        plt.plot(test.index, test[value_col], label="Actual (Test)", color="#10b981", linewidth=2.5)
        plt.plot(forecast.index, forecast, label="Predicted (Forecast)", color="#7c3aed", linestyle="--", linewidth=2.5)
        
        # Style layout
        ax.spines['bottom'].set_color('#cbd5e1')
        ax.spines['top'].set_color('#cbd5e1')
        ax.spines['left'].set_color('#cbd5e1')
        ax.spines['right'].set_color('#cbd5e1')
        ax.tick_params(colors='#475569')
        ax.xaxis.label.set_color('#0f172a')
        ax.yaxis.label.set_color('#0f172a')
        
        plt.xlabel("Date")
        plt.ylabel(str(value_col))
        plt.title(f"SARIMAX Forecast vs Actual for {value_col}", fontsize=14, color="#0f172a", pad=15)
        
        legend = plt.legend(facecolor='#ffffff', edgecolor='#e2e8f0')
        for text in legend.get_texts():
            text.set_color('#334155')
            
        plt.grid(True, linestyle=":", alpha=0.6, color="#cbd5e1")
        plt.tight_layout()
        
        forecast_path = os.path.join(app.config['STATIC_FOLDER'], 'forecast.png')
        plt.savefig(forecast_path, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        
        # Calculate comparison table metrics
        results_table = []
        for dt, act, fct in zip(test.index, test[value_col], forecast):
            err = abs(act - fct)
            pct = (err / act * 100) if act != 0 else 0
            results_table.append({
                'date': dt.strftime('%Y-%m-%d'),
                'actual': round(float(act), 2),
                'forecast': round(float(fct), 2),
                'error': round(float(err), 2),
                'error_percent': round(float(pct), 2)
            })
            
        mae = sum(r['error'] for r in results_table) / len(results_table)
        
        return jsonify({
            'message': 'Forecasting successfully completed',
            'url': '/static/forecast.png?' + os.urandom(4).hex(),  # append random string to bypass caching
            'results': results_table,
            'mae': round(mae, 2),
            'date_column': date_col,
            'value_column': value_col
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health_check', methods=['GET'])
def health_check():
    return jsonify({'status': 'running', 'message': 'Flask server is running!'}), 200


if __name__ == '__main__':
    port = 5000
    url = f"http://127.0.0.1:{port}"
    
    # Auto-open browser in a separate thread
    def open_browser():
        webbrowser.open(url)
        
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True, port=port)
