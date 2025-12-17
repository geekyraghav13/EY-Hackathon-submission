"""
Quality Assurance Agent
Compares provider information across sources and identifies inconsistencies
"""
import random
from typing import Dict, List, Any

class QualityAssuranceAgent:
    def __init__(self):
        self.name = "Quality Assurance Agent"

    def compare_data_sources(self, provider: Dict[str, Any],
                            validation_results: Dict[str, Any],
                            enrichment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare information across multiple sources for consistency"""

        discrepancies = []

        # Check phone number consistency
        if validation_results["phone_validation"]["valid"]:
            if enrichment_results["website_data"].get("additional_phone"):
                discrepancies.append({
                    "field": "phone",
                    "issue": "Multiple phone numbers found",
                    "severity": "Low",
                    "action": "Verify primary contact number"
                })

        # Check specialty consistency
        if enrichment_results["website_data"].get("updated_specialties"):
            if len(enrichment_results["website_data"]["updated_specialties"]) > 1:
                discrepancies.append({
                    "field": "specialty",
                    "issue": "Additional specialties found online",
                    "severity": "Medium",
                    "action": "Update provider specialty list"
                })

        # Check affiliation consistency
        verified_count = len(enrichment_results["hospital_data"]["verified_affiliations"])
        original_count = len(provider.get("hospital_affiliations", []))

        if verified_count < original_count:
            discrepancies.append({
                "field": "hospital_affiliations",
                "issue": f"Only {verified_count} of {original_count} affiliations verified",
                "severity": "High",
                "action": "Manual verification required"
            })

        return {
            "discrepancies_found": len(discrepancies),
            "discrepancies": discrepancies
        }

    def flag_suspicious_data(self, provider: Dict[str, Any],
                            validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potentially fraudulent or suspicious information"""

        red_flags = []

        # Check for placeholder data
        if provider["phone"] == "(000) 000-0000":
            red_flags.append({
                "type": "Placeholder Data",
                "field": "phone",
                "severity": "High",
                "description": "Phone number appears to be placeholder"
            })

        if "Old Address" in provider["address"]:
            red_flags.append({
                "type": "Outdated Data",
                "field": "address",
                "severity": "High",
                "description": "Address appears outdated"
            })

        # Check license issues
        if provider["license_status"] == "Unknown":
            red_flags.append({
                "type": "Credential Issue",
                "field": "license_status",
                "severity": "Critical",
                "description": "License status cannot be verified"
            })

        # Check for very old last verification
        from datetime import datetime, timedelta
        last_verified = datetime.strptime(provider["last_verified"], "%Y-%m-%d")
        days_since_verified = (datetime.now() - last_verified).days

        if days_since_verified > 180:
            red_flags.append({
                "type": "Stale Data",
                "field": "last_verified",
                "severity": "Medium",
                "description": f"Provider data not verified in {days_since_verified} days"
            })

        # Check NPI name mismatch
        if not validation_results["npi_validation"].get("npi_data", {}).get("name_match", True):
            red_flags.append({
                "type": "Identity Mismatch",
                "field": "npi",
                "severity": "Critical",
                "description": "NPI name does not match provider record"
            })

        return red_flags

    def calculate_data_quality_score(self, provider: Dict[str, Any],
                                     validation_results: Dict[str, Any],
                                     enrichment_results: Dict[str, Any],
                                     discrepancies: Dict[str, Any],
                                     red_flags: List[Dict[str, Any]]) -> float:
        """Calculate overall data quality score (0-100)"""

        base_score = 100.0

        # Deduct for validation issues
        if not validation_results["phone_validation"]["valid"]:
            base_score -= 15

        if not validation_results["address_validation"]["valid"]:
            base_score -= 15

        if not validation_results["npi_validation"]["valid"]:
            base_score -= 20

        if not validation_results["license_validation"]["valid"]:
            base_score -= 25

        # Deduct for discrepancies
        base_score -= discrepancies["discrepancies_found"] * 5

        # Deduct for red flags
        for flag in red_flags:
            if flag["severity"] == "Critical":
                base_score -= 15
            elif flag["severity"] == "High":
                base_score -= 10
            elif flag["severity"] == "Medium":
                base_score -= 5
            else:
                base_score -= 2

        # Bonus for enrichment success
        if enrichment_results["enrichment_confidence"] > 0.80:
            base_score += 5

        return max(0.0, min(100.0, base_score))

    def prioritize_for_review(self, quality_score: float,
                             red_flags: List[Dict[str, Any]],
                             provider: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize providers for manual review based on multiple factors"""

        priority = "Low"
        priority_score = 0

        # Quality score factor
        if quality_score < 50:
            priority_score += 40
        elif quality_score < 70:
            priority_score += 20

        # Red flags factor
        critical_flags = sum(1 for flag in red_flags if flag["severity"] == "Critical")
        priority_score += critical_flags * 25

        high_flags = sum(1 for flag in red_flags if flag["severity"] == "High")
        priority_score += high_flags * 10

        # Member impact factor (simulate based on specialty demand)
        high_demand_specialties = ["Family Medicine", "Pediatrics", "Internal Medicine"]
        if provider["specialty"] in high_demand_specialties:
            priority_score += 10

        # Determine priority level
        if priority_score >= 60:
            priority = "Critical"
        elif priority_score >= 35:
            priority = "High"
        elif priority_score >= 15:
            priority = "Medium"

        return {
            "priority": priority,
            "priority_score": priority_score,
            "estimated_review_time": f"{random.randint(5, 30)} minutes",
            "recommended_actions": self._generate_recommended_actions(red_flags, quality_score)
        }

    def _generate_recommended_actions(self, red_flags: List[Dict[str, Any]],
                                     quality_score: float) -> List[str]:
        """Generate recommended actions for manual reviewers"""

        actions = []

        for flag in red_flags:
            if flag["severity"] in ["Critical", "High"]:
                actions.append(f"Verify {flag['field']}: {flag['description']}")

        if quality_score < 70:
            actions.append("Complete comprehensive data verification")

        if not actions:
            actions.append("Routine review - no critical issues found")

        return actions

    def assess_provider_quality(self, provider: Dict[str, Any],
                               validation_results: Dict[str, Any],
                               enrichment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive quality assessment"""

        # Compare data sources
        comparison_results = self.compare_data_sources(
            provider, validation_results, enrichment_results
        )

        # Flag suspicious data
        red_flags = self.flag_suspicious_data(provider, validation_results)

        # Calculate quality score
        quality_score = self.calculate_data_quality_score(
            provider, validation_results, enrichment_results,
            comparison_results, red_flags
        )

        # Prioritize for review
        priority_info = self.prioritize_for_review(quality_score, red_flags, provider)

        return {
            "provider_id": provider["provider_id"],
            "quality_score": quality_score,
            "comparison_results": comparison_results,
            "red_flags": red_flags,
            "priority_info": priority_info,
            "requires_manual_review": quality_score < 70 or len(red_flags) > 0
        }
