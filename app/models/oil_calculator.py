class MaintenanceEstimator:
    """
    Professional maintenance estimator supporting all vehicle types including electric cars
    """
    
    def __init__(self, distance_km, fuel_type, months_since_last, oil_brand='standard', vehicle_type='gasoline'):
        self.distance = distance_km
        self.fuel_type = fuel_type.lower() if fuel_type else 'gasoline'
        self.months = months_since_last
        self.oil_brand = oil_brand.lower() if oil_brand else 'standard'
        self.vehicle_type = vehicle_type.lower()
        
        # Service intervals by vehicle type
        self.SERVICE_INTERVALS = {
            'gasoline': {
                'base_km': 10000,
                'base_months': 6,
                'service_type': 'oil_change'
            },
            'diesel': {
                'base_km': 12000,
                'base_months': 8,
                'service_type': 'oil_change'
            },
            'hybrid': {
                'base_km': 12000,
                'base_months': 8,
                'service_type': 'oil_change'
            },
            'electric': {
                'base_km': 20000,  # Battery coolant/brake fluid service
                'base_months': 12,
                'service_type': 'maintenance_check'
            }
        }
        
        # Fuel type modifiers for gasoline/diesel vehicles
        self.FUEL_MODIFIERS = {
            '92': 0.85,
            '95': 1.0,
            '98': 1.15,
            'diesel': 1.3,
            'electric': 1.0,  # No fuel modifier for electric
            'hybrid': 1.1
        }
        
        # Oil type modifiers (only applies to combustion engines)
        self.OIL_MODIFIERS = {
            'standard': 1.0,
            'premium': 1.2,
            'semi-synthetic': 1.3,
            'synthetic': 1.5
        }

    def get_vehicle_config(self):
        """Get vehicle-specific configuration"""
        return self.SERVICE_INTERVALS.get(self.vehicle_type, self.SERVICE_INTERVALS['gasoline'])

    def get_fuel_modifier(self):
        """Get fuel type modifier"""
        if self.vehicle_type == 'electric':
            return 1.0
        
        try:
            # Handle numeric fuel types (octane ratings)
            if isinstance(self.fuel_type, str) and self.fuel_type.isdigit():
                return self.FUEL_MODIFIERS.get(self.fuel_type, 1.0)
            return self.FUEL_MODIFIERS.get(self.fuel_type, 1.0)
        except (ValueError, TypeError):
            return 1.0

    def get_oil_modifier(self):
        """Get oil type modifier (only for combustion engines)"""
        if self.vehicle_type == 'electric':
            return 1.0
        return self.OIL_MODIFIERS.get(self.oil_brand, 1.0)

    def calculate_adjusted_intervals(self):
        """Calculate adjusted maintenance intervals"""
        config = self.get_vehicle_config()
        fuel_factor = self.get_fuel_modifier()
        oil_factor = self.get_oil_modifier()
        
        adjusted_km = int(config['base_km'] * fuel_factor * oil_factor)
        adjusted_months = int(config['base_months'] * oil_factor)
        
        return adjusted_km, adjusted_months

    def calculate_maintenance_need(self):
        """
        Calculate maintenance needs based on vehicle type
        """
        try:
            config = self.get_vehicle_config()
            adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
            
            # Check if maintenance is needed
            km_exceeded = self.distance >= adjusted_km
            time_exceeded = self.months >= adjusted_months
            
            service_name = "Battery/brake service" if self.vehicle_type == 'electric' else "Oil change"
            
            if km_exceeded or time_exceeded:
                # Calculate how overdue
                km_overdue = max(0, self.distance - adjusted_km)
                months_overdue = max(0, self.months - adjusted_months)
                
                if km_overdue > (adjusted_km * 0.2) or months_overdue > 2:
                    return f"{service_name} needed URGENTLY 🚨"
                else:
                    return f"{service_name} needed NOW 🚨"
            else:
                # Calculate remaining distance/time
                km_remaining = adjusted_km - self.distance
                months_remaining = adjusted_months - self.months
                
                # Warning if close to limit
                if km_remaining <= 1000 or months_remaining <= 1:
                    return f"{service_name} soon - {km_remaining} km or {months_remaining} months remaining ⚠️"
                else:
                    return f"Maintenance good for {km_remaining} km or {months_remaining} months ✅"
                    
        except Exception as e:
            return "Error calculating maintenance status - check vehicle data"

    def get_calculation_details(self):
        """Get detailed calculation breakdown"""
        try:
            config = self.get_vehicle_config()
            adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
            fuel_factor = self.get_fuel_modifier()
            oil_factor = self.get_oil_modifier()
            
            return {
                'vehicle_type': self.vehicle_type,
                'service_type': config['service_type'],
                'base_interval_km': config['base_km'],
                'base_time_months': config['base_months'],
                'fuel_type': self.fuel_type,
                'fuel_modifier': fuel_factor,
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
        """Check if vehicle needs immediate service"""
        adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
        return self.distance >= adjusted_km or self.months >= adjusted_months

    @staticmethod
    def get_recommended_intervals():
        """Get recommended intervals for different vehicle types"""
        return {
            # Gasoline vehicles
            'gasoline_standard_92': 8500,
            'gasoline_standard_95': 10000,
            'gasoline_standard_98': 11500,
            'gasoline_synthetic_92': 12750,
            'gasoline_synthetic_95': 15000,
            'gasoline_synthetic_98': 17250,
            
            # Diesel vehicles
            'diesel_standard': 13000,
            'diesel_synthetic': 19500,
            
            # Hybrid vehicles
            'hybrid_standard': 11000,
            'hybrid_synthetic': 16500,
            
            # Electric vehicles (battery coolant/brake service)
            'electric_maintenance': 20000
        }


class TireChangeEstimator:
    """
    Professional tire change estimator
    """
    
    def __init__(self, distance_km, months_since_last, tire_brand='standard', driving_conditions='normal'):
        self.distance = distance_km
        self.months = months_since_last
        self.tire_brand = tire_brand.lower() if tire_brand else 'standard'
        self.driving_conditions = driving_conditions.lower()
        
        # Base tire intervals
        self.BASE_INTERVAL_KM = 60000  # 60,000 km base interval
        self.BASE_TIME_MONTHS = 48     # 4 years base interval
        
        # Tire quality modifiers
        self.TIRE_MODIFIERS = {
            'budget': 0.8,     # Budget tires - 48,000 km
            'standard': 1.0,   # Standard tires - 60,000 km
            'premium': 1.3,    # Premium tires - 78,000 km
            'performance': 0.9, # Performance tires - 54,000 km
            'winter': 0.85     # Winter tires - 51,000 km
        }
        
        # Driving condition modifiers
        self.CONDITION_MODIFIERS = {
            'city': 0.85,      # City driving - more wear
            'highway': 1.15,   # Highway driving - less wear
            'mixed': 1.0,      # Mixed driving - standard
            'aggressive': 0.7, # Aggressive driving - much more wear
            'normal': 1.0      # Normal driving - standard
        }

    def get_tire_modifier(self):
        """Get tire quality modifier"""
        return self.TIRE_MODIFIERS.get(self.tire_brand, 1.0)

    def get_condition_modifier(self):
        """Get driving condition modifier"""
        return self.CONDITION_MODIFIERS.get(self.driving_conditions, 1.0)

    def calculate_adjusted_intervals(self):
        """Calculate adjusted tire change intervals"""
        tire_factor = self.get_tire_modifier()
        condition_factor = self.get_condition_modifier()
        
        adjusted_km = int(self.BASE_INTERVAL_KM * tire_factor * condition_factor)
        adjusted_months = self.BASE_TIME_MONTHS  # Time doesn't change much for tires
        
        return adjusted_km, adjusted_months

    def calculate_tire_change_need(self):
        """Calculate tire change needs"""
        try:
            adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
            
            km_exceeded = self.distance >= adjusted_km
            time_exceeded = self.months >= adjusted_months
            
            if km_exceeded or time_exceeded:
                km_overdue = max(0, self.distance - adjusted_km)
                months_overdue = max(0, self.months - adjusted_months)
                
                if km_overdue > (adjusted_km * 0.1) or months_overdue > 6:
                    return "Tire change needed URGENTLY 🚨"
                else:
                    return "Tire change needed NOW 🚨"
            else:
                km_remaining = adjusted_km - self.distance
                months_remaining = adjusted_months - self.months
                
                if km_remaining <= 5000 or months_remaining <= 6:
                    return f"Tire change soon - {km_remaining} km or {months_remaining} months remaining ⚠️"
                else:
                    return f"Tires good for {km_remaining} km or {months_remaining} months ✅"
                    
        except Exception as e:
            return "Error calculating tire status - check vehicle data"

    def is_critical(self):
        """Check if tires need immediate replacement"""
        adjusted_km, adjusted_months = self.calculate_adjusted_intervals()
        return self.distance >= adjusted_km or self.months >= adjusted_months


# Original OilChangeEstimator class for backward compatibility
class OilChangeEstimator:
    """
    Original oil change estimator - maintained for backward compatibility
    """
    
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