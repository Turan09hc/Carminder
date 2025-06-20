# carminder/app/routes.py

from flask import Blueprint, request, render_template
from .models.oilcalc import OilChangeEstimator

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Welcome to CarMinder 🚗"

@main.route('/estimate')
def estimate():
    # For testing via URL: /estimate?distance=8500&gas=95&months=5&oil=premium
    try:
        distance = int(request.args.get('distance'))
        gas = int(request.args.get('gas'))
        months = int(request.args.get('months'))
        oil = request.args.get('oil')

        estimator = OilChangeEstimator(distance, gas, months, oil)
        result = estimator.calculate_oil_change_need()
        return result

    except Exception as e:
        return f"Error: {e}"
