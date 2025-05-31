from flask import Flask, render_template
import plotly.express as px
import pandas as pd
import boto3

app = Flask(__name__)

# Configure your DynamoDB table and region
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')  # e.g., 'us-east-1'
table = dynamodb.Table('FaceRecognitionLogs')  # Replace with your table name

@app.route('/')
def index():
    # Fetch all data
    response = table.scan()
    items = response.get('Items', [])

    # Check if data exists
    if not items:
        return "No data available from DynamoDB."

    # Convert to DataFrame
    df = pd.DataFrame(items)

    # Rename to match the expected columns
    df.rename(columns={'person_name': 'nume', 'timestamp': 'ora'}, inplace=True)

    # Optional: convert timestamp to datetime (if needed for filtering/plotting by time)
    df['ora'] = pd.to_datetime(df['ora'])

    # Count number of appearances by person
    count_df = df.groupby('nume').size().reset_index(name='Apariții')

    # Generate bar chart
    fig = px.bar(count_df, x='nume', y='Apariții', title='Apariții pe zi')
    plot_html = fig.to_html(full_html=False)

    return render_template('index.html', plot=plot_html)

if __name__ == '__main__':
    app.run(debug=True)
