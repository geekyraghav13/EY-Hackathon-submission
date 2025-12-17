"""
Directory Management Agent
Generates reports, manages workflows, and creates communication
"""
from typing import Dict, List, Any
from datetime import datetime

class DirectoryManagementAgent:
    def __init__(self):
        self.name = "Directory Management Agent"

    def generate_provider_report(self, provider: Dict[str, Any],
                                validation_results: Dict[str, Any],
                                enrichment_results: Dict[str, Any],
                                quality_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive provider validation report"""

        report = {
            "provider_id": provider["provider_id"],
            "provider_name": f"{provider['first_name']} {provider['last_name']}",
            "specialty": provider["specialty"],
            "validation_timestamp": datetime.now().isoformat(),
            "overall_status": self._determine_status(quality_results),
            "quality_metrics": {
                "quality_score": quality_results["quality_score"],
                "confidence_score": validation_results["overall_confidence"],
                "enrichment_score": enrichment_results["enrichment_confidence"]
            },
            "validation_summary": {
                "phone": "Valid" if validation_results["phone_validation"]["valid"] else "Invalid",
                "address": "Valid" if validation_results["address_validation"]["valid"] else "Invalid",
                "npi": "Valid" if validation_results["npi_validation"]["valid"] else "Invalid",
                "license": "Valid" if validation_results["license_validation"]["valid"] else "Invalid"
            },
            "issues_found": validation_results["issues_found"],
            "red_flags": quality_results["red_flags"],
            "discrepancies": quality_results["comparison_results"]["discrepancies"],
            "enrichment_summary": {
                "website_found": enrichment_results["website_data"]["website_found"],
                "online_profiles_found": enrichment_results["online_profiles"]["healthgrades_found"],
                "affiliations_verified": len(enrichment_results["hospital_data"]["verified_affiliations"])
            },
            "priority": quality_results["priority_info"]["priority"],
            "recommended_actions": quality_results["priority_info"]["recommended_actions"],
            "requires_manual_review": quality_results["requires_manual_review"]
        }

        return report

    def _determine_status(self, quality_results: Dict[str, Any]) -> str:
        """Determine overall validation status"""

        quality_score = quality_results["quality_score"]

        if quality_score >= 90:
            return "Excellent"
        elif quality_score >= 75:
            return "Good"
        elif quality_score >= 60:
            return "Fair"
        elif quality_score >= 40:
            return "Poor"
        else:
            return "Critical"

    def create_summary_report(self, all_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary report for all providers validated"""

        total_providers = len(all_reports)

        status_counts = {
            "Excellent": 0,
            "Good": 0,
            "Fair": 0,
            "Poor": 0,
            "Critical": 0
        }

        needs_review = 0
        critical_priority = 0
        high_priority = 0

        total_quality_score = 0
        total_confidence_score = 0

        for report in all_reports:
            status_counts[report["overall_status"]] += 1
            total_quality_score += report["quality_metrics"]["quality_score"]
            total_confidence_score += report["quality_metrics"]["confidence_score"]

            if report["requires_manual_review"]:
                needs_review += 1

            if report["priority"] == "Critical":
                critical_priority += 1
            elif report["priority"] == "High":
                high_priority += 1

        summary = {
            "total_providers_validated": total_providers,
            "validation_timestamp": datetime.now().isoformat(),
            "status_distribution": status_counts,
            "average_quality_score": round(total_quality_score / total_providers, 2) if total_providers > 0 else 0,
            "average_confidence_score": round(total_confidence_score / total_providers, 2) if total_providers > 0 else 0,
            "providers_needing_review": needs_review,
            "critical_priority_count": critical_priority,
            "high_priority_count": high_priority,
            "validation_success_rate": round((total_providers - needs_review) / total_providers * 100, 1) if total_providers > 0 else 0
        }

        return summary

    def generate_communication_email(self, provider: Dict[str, Any],
                                    report: Dict[str, Any]) -> str:
        """Generate email communication for provider data update requests"""

        email_template = f"""
Subject: Provider Directory Information Update Request

Dear Dr. {provider['last_name']},

We are updating our provider directory to ensure our members have accurate information when seeking care. As part of our routine data validation process, we would like to verify the following information for your practice:

Provider Information:
- Name: {provider['first_name']} {provider['last_name']}
- Specialty: {provider['specialty']}
- NPI: {provider['npi']}

Current Information on File:
- Phone: {provider['phone']}
- Address: {provider['address']}, {provider['city']}, {provider['state']} {provider['zip_code']}
- Accepting New Patients: {'Yes' if provider['accepting_new_patients'] else 'No'}

"""

        if report["issues_found"]:
            email_template += "\nWe have identified the following items that need verification:\n"
            for issue in report["issues_found"]:
                email_template += f"- {issue}\n"

        if report["recommended_actions"]:
            email_template += "\nRequired Actions:\n"
            for action in report["recommended_actions"]:
                email_template += f"- {action}\n"

        email_template += """
Please review the information above and respond with any updates or corrections at your earliest convenience. Accurate provider information helps our members access care efficiently.

To update your information, please reply to this email or call our Provider Relations team at (800) 555-0199.

Thank you for your continued participation in our network.

Best regards,
Provider Relations Team
Healthcare Network Services

---
This is an automated communication generated by our Provider Directory Management System.
"""

        return email_template

    def create_manual_review_queue(self, all_reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create prioritized queue for manual review"""

        # Filter providers needing review
        review_queue = [
            report for report in all_reports
            if report["requires_manual_review"]
        ]

        # Sort by priority and quality score
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

        review_queue.sort(
            key=lambda x: (
                priority_order.get(x["priority"], 4),
                x["quality_metrics"]["quality_score"]
            )
        )

        # Add queue position and estimated processing time
        for i, item in enumerate(review_queue):
            item["queue_position"] = i + 1
            item["estimated_wait_time"] = f"{i * 15} minutes"

        return review_queue

    def generate_dashboard_data(self, all_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data for web dashboard visualization"""

        summary = self.create_summary_report(all_reports)
        review_queue = self.create_manual_review_queue(all_reports)

        # Extract top issues
        all_issues = {}
        for report in all_reports:
            for issue in report["issues_found"]:
                all_issues[issue] = all_issues.get(issue, 0) + 1

        top_issues = sorted(all_issues.items(), key=lambda x: x[1], reverse=True)[:10]

        # Quality score distribution
        score_ranges = {
            "90-100": 0,
            "75-89": 0,
            "60-74": 0,
            "40-59": 0,
            "0-39": 0
        }

        for report in all_reports:
            score = report["quality_metrics"]["quality_score"]
            if score >= 90:
                score_ranges["90-100"] += 1
            elif score >= 75:
                score_ranges["75-89"] += 1
            elif score >= 60:
                score_ranges["60-74"] += 1
            elif score >= 40:
                score_ranges["40-59"] += 1
            else:
                score_ranges["0-39"] += 1

        dashboard_data = {
            "summary": summary,
            "review_queue": review_queue,
            "top_issues": top_issues,
            "quality_distribution": score_ranges,
            "charts": {
                "status_pie": summary["status_distribution"],
                "quality_histogram": score_ranges
            }
        }

        return dashboard_data
