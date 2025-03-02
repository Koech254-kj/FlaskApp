from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import csv

app = Flask(__name__)

# MongoDB Connection
MONGO_URI = "mongodb+srv://kgeorgekoech:<password>@cluster0.u0ezy.mongodb.net/FlaskApp?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["user_data_db"]
collection = db["users"]

try:
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error: Unable to connect to MongoDB - {e}")

# User Class
class User:
    def __init__(self, age, gender, total_income, expenses):
        self.age = age
        self.gender = gender
        self.total_income = total_income
        self.expenses = expenses
    
    def to_dict(self):
        return {
            'age': self.age,
            'gender': self.gender,
            'total_income': self.total_income,
            **self.expenses
        }

# CSV Function
def save_to_csv():
    with open('user_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Age", "Gender", "Total Income", "Utilities", "Entertainment", "School Fees", "Shopping", "Healthcare"])
        for user in collection.find():
            writer.writerow([
                user['age'], user['gender'], user['total_income'],
                user['expenses'].get('utilities', 0), user['expenses'].get('entertainment', 0),
                user['expenses'].get('school_fees', 0), user['expenses'].get('shopping', 0),
                user['expenses'].get('healthcare', 0)
            ])

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        age = request.form.get('age')
        gender = request.form.get('gender')
        total_income = request.form.get('total_income')
        expenses = {
            'utilities': request.form.get('utilities', 0),
            'entertainment': request.form.get('entertainment', 0),
            'school_fees': request.form.get('school_fees', 0),
            'shopping': request.form.get('shopping', 0),
            'healthcare': request.form.get('healthcare', 0)
        }
        
        user = User(age, gender, total_income, expenses)
        collection.insert_one(user.to_dict())
        save_to_csv()
        return redirect(url_for('index'))
    
    return render_template('index.html')

if __name__ == "__main__":
    from waitress import serve  # Production-ready server
    serve(app, host="0.0.0.0", port=5000)
