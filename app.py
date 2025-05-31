from flask import Flask, render_template
import plotly.express as px
import pandas as pd
import boto3
import os

app = Flask(__name__)

# Debug: verifică dacă AWS_ACCESS_KEY_ID este setat
print("DEBUG AWS_ACCESS_KEY_ID:", os.environ.get("AWS_ACCESS_KEY_ID"))

AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'eu-north-1')
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE', 'FaceRecognitionLogs')

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

@app.route('/')
def index():
    try:
        response = table.scan()
        items = response.get('Items', [])

        if not items:
            return "No data available from DynamoDB."

        df = pd.DataFrame(items)
        df.rename(columns={'person_name': 'nume', 'timestamp': 'ora'}, inplace=True)
        df['ora'] = pd.to_datetime(df['ora'])
        count_df = df.groupby('nume').size().reset_index(name='Apariții')

        fig = px.bar(count_df, x='nume', y='Apariții', title='Apariții pe zi')
        plot_html = fig.to_html(full_html=False)

        return render_template('index.html', plot=plot_html)

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
