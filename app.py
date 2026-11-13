from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import requests

app = Flask(__name__)

DATABASE = "mealplanner.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database
def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_name TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            meal_date TEXT NOT NULL,
            ingredients TEXT
        )
    """)

    conn.commit()
    conn.close()

# Automatic Ingredient Finder
@app.route("/find-ingredients", methods=["POST"])
def find_ingredients():

    dish_name = request.json.get("dish", "").strip()

    if not dish_name:
        return jsonify({"error": "Please enter a dish name"}), 400

    try:
        api_url = "https://www.themealdb.com/api/json/v1/1/search.php"

        response = requests.get(
            api_url,
            params={"s": dish_name},
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("meals"):
            return jsonify({
                "error": "No matching recipe found. Try another dish."
            }), 404

        results = []

        for meal in data["meals"][:5]:

            ingredients = []

            for i in range(1, 21):

                ingredient = meal.get(f"strIngredient{i}", "").strip()
                measure = meal.get(f"strMeasure{i}", "").strip()

                if ingredient:
                    ingredients.append({
                        "name": ingredient,
                        "measure": measure
                    })

            results.append({
                "id": meal["idMeal"],
                "name": meal["strMeal"],
                "image": meal["strMealThumb"],
                "ingredients": ingredients
            })

        return jsonify({"meals": results})

    except requests.RequestException:
        return jsonify({
            "error": "Could not connect to the recipe database. Try again."
        }), 502

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    conn = get_db()
    meals = conn.execute("SELECT * FROM meals").fetchall()
    conn.close()

    return render_template("dashboard.html", meals=meals)


# Meal management
@app.route("/meals", methods=["GET", "POST"])
def meals():

    conn = get_db()

    if request.method == "POST":

        meal_name = request.form["meal_name"]
        meal_type = request.form["meal_type"]
        meal_date = request.form["meal_date"]
        ingredients = request.form["ingredients"]

        conn.execute("""
            INSERT INTO meals
            (meal_name, meal_type, meal_date, ingredients)
            VALUES (?, ?, ?, ?)
        """, (meal_name, meal_type, meal_date, ingredients))

        conn.commit()

    all_meals = conn.execute(
        "SELECT * FROM meals"
    ).fetchall()

    conn.close()

    return render_template("meals.html", meals=all_meals)


# Delete meal
@app.route("/delete/<int:meal_id>")
def delete_meal(meal_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM meals WHERE id = ?",
        (meal_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("meals"))

# Nutrition Guide
@app.route("/nutrition", methods=["GET", "POST"])
def nutrition():

    profile = None

    if request.method == "POST":

        age = request.form["age"]
        height = request.form["height"]
        weight = request.form["weight"]

        profile = {
            "age": age,
            "height": height,
            "weight": weight
        }

    return render_template("nutrition.html", profile=profile)

# Shopping list
@app.route("/shopping")
def shopping():

    conn = get_db()

    meals = conn.execute(
        "SELECT * FROM meals"
    ).fetchall()

    conn.close()

    return render_template("shopping.html", meals=meals)


# Run application
if __name__ == "__main__":

    create_table()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )