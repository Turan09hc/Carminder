class OilChangeEstimator:
  
    
    def __init__(self, distance_km, gas_type, months_since_last, oil_brand):
        self.distance = distance_km
        self.gas_type = gas_type
        self.months = months_since_last
        self.oil_brand = oil_brand.lower() if oil_brand else 'standard'
        
        # Base intervals - professional standards
        self.BASE_INTERVAL_KM = 10000  # 10,000 km base interval
        self.BASE_TIME_MONTHS = 6      # 6 months base interval
        
        # Gas type modifiers (higher octane = longer intervals)
        self.GAS_MODIFIERS = {
            92: 0.85,       # Regular gas - shorter interval (8,500 km)
            95: 1.0,        # Standard gas - normal interval (10,000 km) 
            98: 1.15,       # Premium gas - longer interval (11,500 km)
            'diesel': 1.3   # Diesel - much longer interval (13,000 km)
        }
        
        # Oil type modifiers (better oil = longer intervals)
        self.OIL_MODIFIERS = {
            'standard': 1.0,        # Standard oil - 10,000 km
            'premium': 1.2,         # Premium oil - 12,000 km  
            'semi-synthetic': 1.3,  # Semi-synthetic - 13,000 km
            'synthetic': 1.5        # Full synthetic - 15,000 km
        }

    def get_gas_modifier(self):
        """Get gas type modifier for calculations"""
        try:
            if isinstance(self.gas_type, str):
                if self.gas_type.lower() == 'diesel':
                    return self.GAS_MODIFIERS['diesel']
                else:
                    return self.GAS_MODIFIERS.get(int(self.gas_type), 1.0)
            return self.GAS_MODIFIERS.get(self.gas_type, 1.0)
        except (ValueError, TypeError):
            return 1.0
    
    def get_oil_modifier(self):
        """Get oil type modifier for calculations"""
        return self.OIL_MODIFIERS.get(self.oil_brand, 1.0)

    def calculate_adjusted_intervals(self):
        """Calculate adjusted intervals based on gas and oil type"""
        gas_factor = self.get_gas_modifier()
        oil_factor = self.get_oil_modifier()
        
        adjusted_km = int(self.BASE_INTERVAL_KM * gas_factor * oil_factor)
        adjusted_months = int(self.BASE_TIME_MONTHS * oil_factor)
        
        return adjusted_km, adjusted_months

    def calculate_oil_change_need(self):
        """
        Main calculation method - determines if oil change is needed
        Returns status message with recommendations
        """
        try:
            adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
            
            # Check if either distance or time limit exceeded
            km_exceeded = self.distance >= adjusted_km
            time_exceeded = self.months >= adjusted_months
            
            if km_exceeded or time_exceeded:
                # Calculate how overdue the vehicle is
                km_overdue = max(0, self.distance - adjusted_km)
                months_overdue = max(0, self.months - adjusted_months)
                
                if km_overdue > (adjusted_km * 0.2) or months_overdue > 2:
                    return "Oil change needed URGENTLY 🚨"
                else:
                    return "Oil change needed NOW 🚨"
            else:
                # Calculate remaining distance/time
                km_remaining = adjusted_km - self.distance
                months_remaining = adjusted_months - self.months
                
                # Warning if close to limit
                if km_remaining <= 1000 or months_remaining <= 1:
                    return f"Oil change soon - {km_remaining} km or {months_remaining} months remaining ⚠️"
                else:
                    return f"Oil good for {km_remaining} km or {months_remaining} months ✅"
                    
        except Exception as e:
            return "Error calculating oil status - check vehicle data"

    def get_calculation_details(self):
        """Get detailed calculation breakdown for analysis"""
        try:
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
        except Exception:
            return {}

    def is_critical(self):
        """Simple boolean check if vehicle needs immediate service"""
        adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
        return self.distance >= adjusted_km or self.months >= adjusted_months

    @staticmethod
    def get_recommended_intervals():
        """Get recommended intervals for different oil/gas combinations"""
        return {
            'standard_92': 8500,   # Standard oil + 92 octane
            'standard_95': 10000,  # Standard oil + 95 octane  
            'standard_98': 11500,  # Standard oil + 98 octane
            'premium_92': 10200,   # Premium oil + 92 octane
            'premium_95': 12000,   # Premium oil + 95 octane
            'premium_98': 13800,   # Premium oil + 98 octane
            'synthetic_92': 12750, # Synthetic oil + 92 octane
            'synthetic_95': 15000, # Synthetic oil + 95 octane
            'synthetic_98': 17250, # Synthetic oil + 98 octane
            'diesel_standard': 13000,  # Diesel + standard oil
            'diesel_synthetic': 19500  # Diesel + synthetic oil
        }