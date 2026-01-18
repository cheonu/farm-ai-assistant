"""
Farm Data Processor
Processes and validates farm data for AI analysis
"""

from typing import List, Dict, Optional
from datetime import datetime


class FarmDataProcessor:
    def __init__(self):
        """Initialize the Data Processor"""
        self.gestation_days = 114
        self.heat_cycle_days = 21

    def process_farm_data(self, raw_data: Optional[Dict]) -> Dict:
        """
        Process raw farm data into structured format for AI analysis
        
        Args:
            raw_data: Raw farm data from React Native app

        Returns:
            Processed and validated farm data
        """
        if not raw_data:
            return {"pigs": [], "summary": {"total_pigs": 0}}

        # Handle both direct pig list and nested structure
        pigs = raw_data.get("pigs", raw_data if isinstance(raw_data, list) else [])

        processed_data = {
            "pigs": pigs,
            "summary": self._generate_summary(pigs),
            "breeding_status": self._analyze_breeding_status(pigs),
            "health_status": self._analyze_health_status(pigs),
            "alerts": self._generate_alerts(pigs)
        }
        
        return processed_data
    
    def _generate_summary(self, pigs: List[Dict]) -> Dict:
        """Generate basic farm summary"""
        if not pigs:
            return {"total": 0}
        
        summary = {
            "total": len(pigs),
            "by_gender": {},
            "pregnant": 0,
            "available_for_breeding": 0
        }
        
        for pig in pigs:
            # Count the gender
            gender = pig.get("gender", "unknown")
            summary["by_gender"][gender] = summary["by_gender"].get(gender, 0) + 1

            # Count pregnant
            if pig.get("crossedDate") and pig.get("expectedDeliveryDate"):
                summary["pregnant"] += 1
            elif gender in ["Sow", "Gilt"]:
                summary["available_for_breeding"] += 1
        
        return summary

    def _analyze_breeding_status(self, pigs: List[Dict]) -> Dict:
        """Analyze breeding status across the farm"""
        breeding_status = {
            "pregnant_pigs": [],
            "due_for_heat": [],
            "overdue_farrowing": [],
            "recently_farrowed": []
        }
        today = datetime.now()
        
        for pig in pigs:
            pig_id = pig.get("tagNumber", pig.get("tag_number", "Unknown"))

            # Check pregnancy status
            if pig.get("crossedDate") and pig.get("expectedDeliveryDate"):
                try:
                    expected_date = datetime.fromisoformat(
                        pig["expectedDeliveryDate"].replace("Z", "")
                    )
                    days_until = (expected_date - today).days
                    pig_breeding_info = {
                        "pig_id": pig_id,
                        "expected_delivery": expected_date.strftime("%Y-%m-%d"),
                        "days_until": days_until,
                    }

                    if days_until < 0:  # Overdue
                        pig_breeding_info["days_overdue"] = abs(days_until)
                        breeding_status["overdue_farrowing"].append(pig_breeding_info)
                    else:
                        breeding_status["pregnant_pigs"].append(pig_breeding_info)
                except ValueError:
                    pass  # Skip invalid dates
            
            elif pig.get("gender") in ["Sow", "Gilt"] and pig.get("expectedHeatDate"):
                try:
                    heat_date = datetime.fromisoformat(
                        pig["expectedHeatDate"].replace("Z", "")
                    )
                    days_until_heat = (heat_date - today).days

                    if -2 <= days_until_heat <= 7:
                        breeding_status["due_for_heat"].append({
                            "pig_id": pig_id,
                            "heat_date": pig["expectedHeatDate"],
                            "days_until": days_until_heat
                        })
                except ValueError:
                    pass  # Skip invalid dates
        
        return breeding_status

    def _analyze_health_status(self, pigs: List[Dict]) -> Dict:
        """Analyze health status across the farm"""
        health_status = {
            "recently_medicated": [],
            "medication_patterns": {},
            "health_alerts": []
        }
        today = datetime.now()

        for pig in pigs:
            pig_id = pig.get("tagNumber", pig.get("tag_number", "Unknown"))
            medications = pig.get("medications", [])

            if medications:
                recent_meds = []
                for med in medications:
                    try:
                        med_date = datetime.fromisoformat(med.get("date", ""))
                        days_ago = (today - med_date).days

                        if days_ago <= 30:
                            recent_meds.append({
                                "medication": med.get("name", "Unknown"),
                                "date": med.get("date"),
                                "days_ago": days_ago
                            })

                            # Track medication patterns
                            med_name = med.get("name", "Unknown")
                            health_status["medication_patterns"][med_name] = \
                                health_status["medication_patterns"].get(med_name, 0) + 1
                    
                    except (ValueError, TypeError):
                        pass
                
                if recent_meds:
                    health_status["recently_medicated"].append({
                        "pig_id": pig_id,
                        "recent_medications": recent_meds
                    })

                # Check for frequent medication (potential chronic issues)
                if len(medications) > 3:
                    health_status["health_alerts"].append(
                        f"Pig {pig_id} has {len(medications)} medication records - monitor for chronic issues"
                    )
        
        return health_status

    def _generate_alerts(self, pigs: List[Dict]) -> List[str]:
        """Generate actionable alerts based on farm data"""
        alerts = []
        today = datetime.now()

        overdue_count = 0
        heat_due_count = 0

        for pig in pigs:
            pig_id = pig.get("tagNumber", pig.get("tag_number", "Unknown"))

            # Check for overdue farrowings
            if pig.get("expectedDeliveryDate"):
                try:
                    expected_date = datetime.fromisoformat(
                        pig["expectedDeliveryDate"].replace("Z", "")
                    )
                    
                    if today > expected_date:
                        day_overdue = (today - expected_date).days
                        overdue_count += 1
                        if day_overdue > 7: 
                            alerts.append(
                                f"Pig {pig_id} overdue for farrowing by {day_overdue} days"
                            )
                        
                except (ValueError, TypeError):
                    pass  # Skip invalid dates
            
            # Check for upcoming heat cycles
            if pig.get("expectedHeatDate"):
                try:
                    heat_date = datetime.fromisoformat(
                        pig["expectedHeatDate"].replace("Z", "")
                    )
                    days_until = (heat_date - today).days

                    if 0 <= days_until <= 7:
                        heat_due_count += 1
                        alerts.append(
                            f"Pig {pig_id} due for heat cycle in {days_until} days"
                        )
                except (ValueError, TypeError):
                    pass  # Skip invalid dates

        if overdue_count > 0:
            alerts.append(f"You have {overdue_count} pig(s) overdue for farrowing")
        
        if heat_due_count > 0:
            alerts.append(f"You have {heat_due_count} pig(s) due for heat cycle")
        
        return alerts

    def validate_pig_data(self, pig_data: Dict) -> Dict:
        """Validate individual pig data

        Args:
            pig_data: Single pig data dictionary

        Returns:
            Validation results with errors if any
        """
        errors = []
        warnings = []

        # Required fields
        required_fields = ["tagNumber", "gender"]
        for field in required_fields:
            if not pig_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate gender
        valid_genders = ["Boar", "Sow", "Gilt", "Grower", "Piglet"]
        gender = pig_data.get("gender")
        if gender and gender not in valid_genders:
            warnings.append(f"Unusual gender value: {gender}")

        # validate dates
        date_fields = ["birthDate", "crossedDate", "expectedDeliveryDate", "expectedHeatDate"]
        for field in date_fields:
            if pig_data.get(field):
                try: 
                    datetime.fromisoformat(pig_data[field].replace("Z", ""))
                except (ValueError, TypeError):
                    errors.append(f"Invalid date format for {field}: {pig_data.get(field)}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
