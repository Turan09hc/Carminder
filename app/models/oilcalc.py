class OilChangeEstimator:
    """
    Professional Oil Change Estimator with advanced calculations
    """
    
    def __init__(self, distance_km, gas_type, months_since_last, oil_brand):
        self.distance = distance_km
        self.gas_type = gas_type
        self.months = months_since_last
        self.oil_brand = oil_brand.lower() if oil_brand else 'generic'
        
        # Configuration constants
        self.BASE_INTERVAL_KM = 10000  # Base interval in kilometers
        self.BASE_TIME_MONTHS = 6      # Base time interval in months
        
        # Gas type modifiers (higher octane = better for engine = longer intervals)
        self.GAS_MODIFIERS = {
            92: 0.9,   # Regular gas - shorter interval
            95: 1.0,   # Standard gas - normal interval
            98: 1.1,   # Premium gas - longer interval
            'diesel': 1.3  # Diesel - much longer interval
        }
        
        # Oil brand/type modifiers (better oil = longer intervals)
        self.OIL_MODIFIERS = {
            'generic': 1.0,      # Basic oil
            'standard': 1.0,     # Standard oil
            'premium': 1.2,      # Premium conventional oil
            'semi-synthetic': 1.3, # Semi-synthetic oil
            'synthetic': 1.5,    # Full synthetic oil
            'high-mileage': 1.1, # High-mileage formula
            'racing': 0.8        # Racing oil (shorter intervals due to performance)
        }

    def get_gas_modifier(self):
        """Get the gas type modifier"""
        return self.GAS_MODIFIERS.get(self.gas_type, 1.0)
    
    def get_oil_modifier(self):
        """Get the oil type modifier"""
        # Try exact match first, then partial matches
        if self.oil_brand in self.OIL_MODIFIERS:
            return self.OIL_MODIFIERS[self.oil_brand]
        
        # Check for partial matches
        for oil_type, modifier in self.OIL_MODIFIERS.items():
            if oil_type in self.oil_brand:
                return modifier
        
        return 1.0  # Default modifier

    def calculate_adjusted_intervals(self):
        """Calculate adjusted intervals based on gas and oil type"""
        gas_factor = self.get_gas_modifier()
        oil_factor = self.get_oil_modifier()
        
        adjusted_km = int(self.BASE_INTERVAL_KM * gas_factor * oil_factor)
        adjusted_months = int(self.BASE_TIME_MONTHS * oil_factor)
        
        return adjusted_km, adjusted_months

    def calculate_oil_change_need(self):
        """Main calculation method"""
        adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
        
        km_exceeded = self.distance >= adjusted_km
        time_exceeded = self.months >= adjusted_months
        
        if km_exceeded or time_exceeded:
            urgency = self.calculate_urgency(adjusted_km, adjusted_months)
            return f"Oil change needed {urgency} 🚨"
        else:
            km_remaining = adjusted_km - self.distance
            months_remaining = adjusted_months - self.months
            return f"Oil is good for ~{km_remaining} km or {months_remaining} months ✅"

    def calculate_urgency(self, adjusted_km, adjusted_months):
        """Calculate urgency level"""
        km_overdue = max(0, self.distance - adjusted_km)
        months_overdue = max(0, self.months - adjusted_months)
        
        # Calculate overdue percentages
        km_overdue_pct = (km_overdue / adjusted_km) * 100 if adjusted_km > 0 else 0
        months_overdue_pct = (months_overdue / adjusted_months) * 100 if adjusted_months > 0 else 0
        
        max_overdue_pct = max(km_overdue_pct, months_overdue_pct)
        
        if max_overdue_pct >= 50:
            return "URGENTLY"
        elif max_overdue_pct >= 20:
            return "SOON"
        else:
            return "NOW"

    def get_calculation_details(self):
        """Get detailed calculation information"""
        adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
        gas_factor = self.get_gas_modifier()
        oil_factor = self.get_oil_modifier()
        
        return {
            'base_interval_km': self.BASE_INTERVAL_KM,
            'base_time_months': self.BASE_TIME_MONTHS,
            'gas_type': self.gas_type,
            'gas_modifier': gas_factor,
            'oil_brand': self.oil_brand,
            'oil_modifier': oil_factor,
            'adjusted_km_interval': adjusted_km,
            'adjusted_month_interval': adjusted_months,
            'current_distance': self.distance,
            'current_months': self.months,
            'km_remaining': max(0, adjusted_km - self.distance),
            'months_remaining': max(0, adjusted_months - self.months),
            'km_overdue': max(0, self.distance - adjusted_km),
            'months_overdue': max(0, self.months - adjusted_months)
        }

    def get_recommendations(self):
        """Get maintenance recommendations"""
        details = self.get_calculation_details()
        recommendations = []
        
        if details['km_overdue'] > 0 or details['months_overdue'] > 0:
            recommendations.append("⚠️ Schedule oil change immediately")
            
            if details['km_overdue'] > details['adjusted_km_interval'] * 0.2:
                recommendations.append("🔧 Consider full engine inspection")
            
            if details['months_overdue'] > 3:
                recommendations.append("🧪 Check oil quality and viscosity")
        
        elif details['km_remaining'] < 1000 or details['months_remaining'] <= 1:
            recommendations.append("📅 Schedule oil change within next month")
        
        elif details['km_remaining'] < 2000 or details['months_remaining'] <= 2:
            recommendations.append("📋 Start planning next oil change")
        
        # Oil-specific recommendations
        if 'synthetic' not in self.oil_brand and details['adjusted_km_interval'] > 8000:
            recommendations.append("💡 Consider upgrading to synthetic oil for longer intervals")
        
        if self.gas_type == 92 and details['gas_modifier'] <= 0.9:
            recommendations.append("⛽ Consider using higher octane fuel for better engine protection")
        
        return recommendations

    def get_service_history_analysis(self, service_intervals):
        """Analyze service history to provide insights"""
        if not service_intervals or len(service_intervals) < 2:
            return "Not enough service history for analysis"
        
        avg_interval = sum(service_intervals) / len(service_intervals)
        recommended_interval = self.calculate_adjusted_intervals()[0]
        
        if avg_interval > recommended_interval * 1.2:
            return "⚠️ Service intervals are longer than recommended - consider more frequent changes"
        elif avg_interval < recommended_interval * 0.8:
            return "✅ Service intervals are more frequent than needed - current schedule is excellent"
        else:
            return "✅ Service intervals are appropriate for your vehicle"

    @staticmethod
    def get_oil_types():
        """Get available oil types for UI"""
        return [
            {'value': 'generic', 'label': 'Generic/Standard Oil'},
            {'value': 'premium', 'label': 'Premium Conventional Oil'},
            {'value': 'semi-synthetic', 'label': 'Semi-Synthetic Oil'},
            {'value': 'synthetic', 'label': 'Full Synthetic Oil'},
            {'value': 'high-mileage', 'label': 'High-Mileage Oil'},
            {'value': 'racing', 'label': 'Racing/Performance Oil'}
        ]

    @staticmethod
    def get_gas_types():
        """Get available gas types for UI"""
        return [
            {'value': 92, 'label': '92 Octane (Regular)'},
            {'value': 95, 'label': '95 Octane (Standard)'},
            {'value': 98, 'label': '98 Octane (Premium)'},
            {'value': 'diesel', 'label': 'Diesel'}
        ]