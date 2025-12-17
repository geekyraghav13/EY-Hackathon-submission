"""
Flask Web Application for Provider Validation Dashboard
"""
from flask import Flask, render_template, jsonify, request
import json
import os
from orchestrator import ProviderValidationOrchestrator, run_validation_demo

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# Global orchestrator instance
orchestrator = None

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/validate', methods=['POST'])
def run_validation():
    """API endpoint to trigger validation"""
    global orchestrator

    data = request.get_json()
    num_providers = data.get('num_providers', 200)

    # Run validation
    orchestrator = run_validation_demo(num_providers)

    if orchestrator:
        return jsonify({
            "status": "success",
            "message": f"Validated {num_providers} providers successfully"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Validation failed. Please ensure data is generated."
        }), 500

@app.route('/api/dashboard')
def get_dashboard_data():
    """API endpoint to get dashboard data"""
    global orchestrator

    if not orchestrator or not orchestrator.validation_results:
        # Try to load from saved results
        try:
            with open('data/validation_results.json', 'r') as f:
                saved_data = json.load(f)

                # If saved data has the full structure, return it
                if 'processing_stats' in saved_data and 'results' in saved_data:
                    # Generate dashboard from saved results
                    from agents.directory_management_agent import DirectoryManagementAgent
                    directory_agent = DirectoryManagementAgent()
                    reports = [result["report"] for result in saved_data['results']]
                    dashboard_data = directory_agent.generate_dashboard_data(reports)
                    dashboard_data["processing_stats"] = saved_data.get('processing_stats', {})
                    return jsonify(dashboard_data)

                return jsonify(saved_data)
        except FileNotFoundError:
            return jsonify({
                "error": "No validation results available. Please run validation first.",
                "summary": {
                    "total_providers_validated": 0,
                    "providers_needing_review": 0,
                    "average_quality_score": 0,
                    "average_confidence_score": 0
                }
            })

    dashboard_data = orchestrator.generate_summary_dashboard()
    return jsonify(dashboard_data)

@app.route('/api/providers')
def get_providers():
    """API endpoint to get all provider results"""
    global orchestrator

    if not orchestrator or not orchestrator.validation_results:
        # Try to load from saved results
        try:
            with open('data/validation_results.json', 'r') as f:
                saved_data = json.load(f)
                if 'results' in saved_data:
                    results = [{
                        "provider_id": r["provider"]["provider_id"],
                        "name": f"{r['provider']['first_name']} {r['provider']['last_name']}",
                        "specialty": r["provider"]["specialty"],
                        "status": r["report"]["overall_status"],
                        "quality_score": r["quality"]["quality_score"],
                        "confidence_score": r["validation"]["overall_confidence"],
                        "needs_review": r["quality"]["requires_manual_review"],
                        "priority": r["report"]["priority"],
                        "issues": len(r["validation"]["issues_found"]),
                        "red_flags": len(r["quality"]["red_flags"])
                    } for r in saved_data['results']]
                    return jsonify(results)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

        return jsonify([])  # Return empty array instead of 404

    results = [{
        "provider_id": r["provider"]["provider_id"],
        "name": f"{r['provider']['first_name']} {r['provider']['last_name']}",
        "specialty": r["provider"]["specialty"],
        "status": r["report"]["overall_status"],
        "quality_score": r["quality"]["quality_score"],
        "confidence_score": r["validation"]["overall_confidence"],
        "needs_review": r["quality"]["requires_manual_review"],
        "priority": r["report"]["priority"],
        "issues": len(r["validation"]["issues_found"]),
        "red_flags": len(r["quality"]["red_flags"])
    } for r in orchestrator.validation_results]

    return jsonify(results)

@app.route('/api/provider/<provider_id>')
def get_provider_detail(provider_id):
    """API endpoint to get detailed provider information"""
    global orchestrator

    if not orchestrator or not orchestrator.validation_results:
        return jsonify({"error": "No results available"}), 404

    provider_result = next(
        (r for r in orchestrator.validation_results if r["provider"]["provider_id"] == provider_id),
        None
    )

    if not provider_result:
        return jsonify({"error": "Provider not found"}), 404

    return jsonify(provider_result)

@app.route('/api/email/<provider_id>')
def get_provider_email(provider_id):
    """API endpoint to generate communication email for provider"""
    global orchestrator

    if not orchestrator or not orchestrator.validation_results:
        return jsonify({"error": "No results available"}), 404

    email = orchestrator.generate_email_for_provider(provider_id)

    return jsonify({"email": email})

@app.route('/api/review-queue')
def get_review_queue():
    """API endpoint to get manual review queue"""
    global orchestrator

    if not orchestrator or not orchestrator.validation_results:
        # Try to load from saved results
        try:
            with open('data/validation_results.json', 'r') as f:
                saved_data = json.load(f)
                if 'results' in saved_data:
                    from agents.directory_management_agent import DirectoryManagementAgent
                    directory_agent = DirectoryManagementAgent()
                    reports = [result["report"] for result in saved_data['results']]
                    queue = directory_agent.create_manual_review_queue(reports)
                    return jsonify(queue)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

        return jsonify([])  # Return empty array instead of 404

    reports = [result["report"] for result in orchestrator.validation_results]
    queue = orchestrator.directory_agent.create_manual_review_queue(reports)

    return jsonify(queue)

@app.route('/api/stats')
def get_stats():
    """API endpoint to get processing statistics"""
    global orchestrator

    if not orchestrator:
        return jsonify({"error": "No results available"}), 404

    return jsonify(orchestrator.processing_stats)

if __name__ == '__main__':
    print("\n" + "="*80)
    print("Provider Validation System - Web Dashboard")
    print("="*80)
    print("\nStarting Flask server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("="*80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
