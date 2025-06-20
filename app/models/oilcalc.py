class OilChangeEstimator:
    def __init__(self, distance_km, gas_type, months_since_last, oil_brand):
        self.distance = distance_km
        self.gas_type = gas_type
        self.months = months_since_last
        self.oil_brand = oil_brand

    def calculate_oil_change_need(self):
        base_interval = 10000
        time_limit = 6

        gas_modifier = {
            92: 0.9,
            95: 1.0,
            98: 1.1
        }

        oil_modifier = {
            "generic": 1.0,
            "premium": 1.2,
            "synthetic": 1.4
        }

        gas_factor = gas_modifier.get(self.gas_type, 1.0)
        oil_factor = oil_modifier.get(self.oil_brand.lower(), 1.0)

        adjusted_km = base_interval * gas_factor * oil_factor

        if self.distance >= adjusted_km or self.months >= time_limit:
            return "Oil change needed 🚨"
        else:
            return f"Oil is still good for ~{int(adjusted_km - self.distance)} km or {time_limit - self.months} months ✅"
