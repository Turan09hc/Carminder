from app.models.oilcalc import OilChangeEstimator

estimator = OilChangeEstimator(8500, 95, 5, "premium")
print(estimator.calculate_oil_change_need())
