"""
Main Orchestrator for Provider Validation System
Coordinates all agents and manages workflow
"""
import json
import time
from typing import Dict, List, Any
from datetime import datetime

from agents.data_validation_agent import DataValidationAgent
from agents.information_enrichment_agent import InformationEnrichmentAgent
from agents.quality_assurance_agent import QualityAssuranceAgent
from agents.directory_management_agent import DirectoryManagementAgent

class ProviderValidationOrchestrator:
    def __init__(self):
        self.validation_agent = DataValidationAgent()
        self.enrichment_agent = InformationEnrichmentAgent()
        self.qa_agent = QualityAssuranceAgent()
        self.directory_agent = DirectoryManagementAgent()

        self.validation_results = []
        self.processing_stats = {
            "start_time": None,
            "end_time": None,
            "total_providers": 0,
            "providers_processed": 0,
            "providers_validated": 0,
            "providers_needing_review": 0
        }

    def load_providers(self, filepath: str = "data/providers.json") -> List[Dict[str, Any]]:
        """Load provider data from JSON file"""
        try:
            with open(filepath, 'r') as f:
                providers = json.load(f)
            return providers
        except FileNotFoundError:
            print(f"Error: Provider data file not found at {filepath}")
            return []

    def validate_single_provider(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single provider through all validation stages"""

        print(f"Processing provider: {provider['provider_id']} - {provider['first_name']} {provider['last_name']}")

        # Stage 1: Data Validation
        validation_results = self.validation_agent.validate_provider(provider)

        # Stage 2: Information Enrichment
        enrichment_results = self.enrichment_agent.enrich_provider(provider)

        # Stage 3: Quality Assurance
        quality_results = self.qa_agent.assess_provider_quality(
            provider, validation_results, enrichment_results
        )

        # Stage 4: Report Generation
        report = self.directory_agent.generate_provider_report(
            provider, validation_results, enrichment_results, quality_results
        )

        # Update provider record with results
        provider.update({
            "validation_status": report["overall_status"],
            "confidence_score": validation_results["overall_confidence"],
            "data_quality_score": quality_results["quality_score"],
            "needs_manual_review": quality_results["requires_manual_review"],
            "issues_found": validation_results["issues_found"],
            "last_verified": datetime.now().strftime("%Y-%m-%d")
        })

        return {
            "provider": provider,
            "report": report,
            "validation": validation_results,
            "enrichment": enrichment_results,
            "quality": quality_results
        }

    def validate_batch(self, providers: List[Dict[str, Any]],
                      batch_size: int = None) -> List[Dict[str, Any]]:
        """Validate a batch of providers"""

        self.processing_stats["start_time"] = datetime.now()
        self.processing_stats["total_providers"] = len(providers)

        if batch_size:
            providers = providers[:batch_size]

        results = []

        for i, provider in enumerate(providers):
            try:
                result = self.validate_single_provider(provider)
                results.append(result)

                self.processing_stats["providers_processed"] += 1

                if not result["quality"]["requires_manual_review"]:
                    self.processing_stats["providers_validated"] += 1
                else:
                    self.processing_stats["providers_needing_review"] += 1

                # Simulate realistic processing time
                time.sleep(0.01)  # Small delay for demo purposes

                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"Progress: {i + 1}/{len(providers)} providers processed")

            except Exception as e:
                print(f"Error processing provider {provider['provider_id']}: {str(e)}")
                continue

        self.processing_stats["end_time"] = datetime.now()
        self.validation_results = results

        return results

    def generate_summary_dashboard(self) -> Dict[str, Any]:
        """Generate complete dashboard data"""

        if not self.validation_results:
            return {"error": "No validation results available"}

        reports = [result["report"] for result in self.validation_results]
        dashboard_data = self.directory_agent.generate_dashboard_data(reports)

        # Add processing stats
        if self.processing_stats["start_time"] and self.processing_stats["end_time"]:
            processing_time = (
                self.processing_stats["end_time"] - self.processing_stats["start_time"]
            ).total_seconds()

            dashboard_data["processing_stats"] = {
                "total_time_seconds": round(processing_time, 2),
                "total_time_minutes": round(processing_time / 60, 2),
                "providers_per_minute": round(
                    self.processing_stats["providers_processed"] / (processing_time / 60), 2
                ) if processing_time > 0 else 0,
                **self.processing_stats
            }

        return dashboard_data

    def save_results(self, filepath: str = "data/validation_results.json"):
        """Save validation results to file"""

        output_data = {
            "validation_timestamp": datetime.now().isoformat(),
            "processing_stats": self.processing_stats,
            "results": self.validation_results
        }

        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)

        print(f"\nResults saved to: {filepath}")

    def generate_email_for_provider(self, provider_id: str) -> str:
        """Generate communication email for specific provider"""

        # Find provider results
        provider_result = next(
            (r for r in self.validation_results if r["provider"]["provider_id"] == provider_id),
            None
        )

        if not provider_result:
            return "Provider not found"

        return self.directory_agent.generate_communication_email(
            provider_result["provider"],
            provider_result["report"]
        )

def run_validation_demo(num_providers: int = 200):
    """Run complete validation demonstration"""

    print("=" * 80)
    print("HEALTHCARE PROVIDER DIRECTORY VALIDATION SYSTEM")
    print("Agentic AI Demonstration - EY Hackathon")
    print("=" * 80)

    orchestrator = ProviderValidationOrchestrator()

    print("\n[1/4] Loading provider data...")
    providers = orchestrator.load_providers()

    if not providers:
        print("No provider data found. Please run generate_data.py first.")
        return None

    print(f"Loaded {len(providers)} provider records")

    print(f"\n[2/4] Validating {min(num_providers, len(providers))} providers...")
    print("Processing through AI agents:")
    print("  - Data Validation Agent")
    print("  - Information Enrichment Agent")
    print("  - Quality Assurance Agent")
    print("  - Directory Management Agent")
    print()

    results = orchestrator.validate_batch(providers, num_providers)

    print(f"\n[3/4] Generating dashboard and reports...")
    dashboard = orchestrator.generate_summary_dashboard()

    print(f"\n[4/4] Saving results...")
    orchestrator.save_results()

    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    stats = dashboard["processing_stats"]
    summary = dashboard["summary"]

    print(f"\nProcessing Performance:")
    print(f"  - Total Providers: {stats['providers_processed']}")
    print(f"  - Processing Time: {stats['total_time_minutes']:.2f} minutes")
    print(f"  - Throughput: {stats['providers_per_minute']:.0f} providers/minute")

    print(f"\nValidation Results:")
    print(f"  - Average Quality Score: {summary['average_quality_score']:.1f}/100")
    print(f"  - Average Confidence: {summary['average_confidence_score']:.1%}")
    print(f"  - Validation Success Rate: {summary['validation_success_rate']:.1f}%")

    print(f"\nStatus Distribution:")
    for status, count in summary['status_distribution'].items():
        print(f"  - {status}: {count}")

    print(f"\nManual Review Queue:")
    print(f"  - Total Needing Review: {summary['providers_needing_review']}")
    print(f"  - Critical Priority: {summary['critical_priority_count']}")
    print(f"  - High Priority: {summary['high_priority_count']}")

    print(f"\nTop Issues Found:")
    for issue, count in dashboard['top_issues'][:5]:
        print(f"  - {issue}: {count} providers")

    print("\n" + "=" * 80)
    print("Validation complete! Dashboard available at http://localhost:5000")
    print("=" * 80)

    return orchestrator

if __name__ == "__main__":
    run_validation_demo(200)
