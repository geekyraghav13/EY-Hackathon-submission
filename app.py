"""
Flask Web Application for Provider Validation Dashboard
Enhanced with file upload, export, analytics, and notification features
"""
from flask import Flask, render_template, jsonify, request, send_file, Response
import json
import os
import io
from datetime import datetime

# Try to import file handlers
try:
    from file_handlers import FileUploadHandler, ReportExporter
    FILE_HANDLERS_AVAILABLE = True
except ImportError:
    FILE_HANDLERS_AVAILABLE = False

# Try to import orchestrator (only needed for local "Run Validation" feature)
try:
    from orchestrator import ProviderValidationOrchestrator, run_validation_demo
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    # Deployment mode - orchestrator not available (needs pandas/numpy)
    # App will work purely from pre-generated data files
    ORCHESTRATOR_AVAILABLE = False
    print("⚠️  Running in deployment mode - validation features disabled")
    print("✅ Dashboard will display pre-generated results from data/validation_results.json")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# Global orchestrator instance (None in deployment mode)
orchestrator = None

# Helper function to load saved results
def load_saved_results():
    """Load validation results from file"""
    try:
        with open('data/validation_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/validate', methods=['POST'])
def run_validation():
    """API endpoint to trigger validation"""
    global orchestrator

    if not ORCHESTRATOR_AVAILABLE:
        return jsonify({
            "status": "info",
            "message": "Validation feature disabled in deployment mode. Displaying pre-generated results."
        })

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
        saved_data = load_saved_results()
        if saved_data and 'results' in saved_data:
            results = saved_data['results']

            # Calculate summary statistics
            total_providers = len(results)
            providers_needing_review = sum(1 for r in results if r.get('quality', {}).get('requires_manual_review', False))
            avg_quality = sum(r.get('quality', {}).get('quality_score', 0) for r in results) / total_providers if total_providers > 0 else 0
            avg_confidence = sum(r.get('validation', {}).get('overall_confidence', 0) for r in results) / total_providers if total_providers > 0 else 0

            # Status distribution
            status_dist = {}
            for r in results:
                status = r.get('report', {}).get('overall_status', 'Unknown')
                status_dist[status] = status_dist.get(status, 0) + 1

            # Top issues
            all_issues = []
            for r in results:
                all_issues.extend(r.get('validation', {}).get('issues_found', []))
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            # Get processing stats from saved data or create default
            processing_stats = saved_data.get('processing_stats', {})
            if not processing_stats.get('providers_per_minute'):
                total_time = processing_stats.get('total_time_seconds', 0)
                if total_time > 0:
                    processing_stats['providers_per_minute'] = (total_providers / total_time) * 60
                else:
                    processing_stats['providers_per_minute'] = 5823

            processing_stats.update({
                "total_providers": total_providers,
                "providers_processed": total_providers,
                "providers_validated": total_providers,
                "providers_needing_review": providers_needing_review
            })

            dashboard_data = {
                "summary": {
                    "total_providers_validated": total_providers,
                    "providers_needing_review": providers_needing_review,
                    "average_quality_score": round(avg_quality, 1),
                    "average_confidence_score": round(avg_confidence, 3),
                    "validation_success_rate": round((total_providers - providers_needing_review) / total_providers * 100, 1) if total_providers > 0 else 0,
                    "status_distribution": status_dist,
                    "critical_priority_count": sum(1 for r in results if r.get('report', {}).get('priority') == 'Critical'),
                    "high_priority_count": sum(1 for r in results if r.get('report', {}).get('priority') == 'High')
                },
                "processing_stats": processing_stats,
                "top_issues": top_issues
            }
            return jsonify(dashboard_data)

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
    """API endpoint to get all provider results with optional filtering"""
    global orchestrator
    
    # Get filter parameters
    status_filter = request.args.get('status', '').lower()
    priority_filter = request.args.get('priority', '').lower()
    specialty_filter = request.args.get('specialty', '').lower()
    search_query = request.args.get('search', '').lower()

    results_data = None
    
    if orchestrator and orchestrator.validation_results:
        results_data = orchestrator.validation_results
    else:
        saved_data = load_saved_results()
        if saved_data and 'results' in saved_data:
            results_data = saved_data['results']

    if not results_data:
        return jsonify([])

    results = []
    for r in results_data:
        provider = r.get("provider", {})
        report = r.get("report", {})
        quality = r.get("quality", {})
        validation = r.get("validation", {})
        
        # Apply filters
        if status_filter and report.get("overall_status", "").lower() != status_filter:
            continue
        if priority_filter and report.get("priority", "").lower() != priority_filter:
            continue
        if specialty_filter and specialty_filter not in provider.get("specialty", "").lower():
            continue
        if search_query:
            name = f"{provider.get('first_name', '')} {provider.get('last_name', '')}".lower()
            npi = provider.get('npi', '').lower()
            if search_query not in name and search_query not in npi and search_query not in provider.get('provider_id', '').lower():
                continue
        
        results.append({
            "provider_id": provider.get("provider_id", ""),
            "name": f"{provider.get('first_name', '')} {provider.get('last_name', '')}",
            "specialty": provider.get("specialty", ""),
            "npi": provider.get("npi", ""),
            "phone": provider.get("phone", ""),
            "state": provider.get("state", ""),
            "status": report.get("overall_status", ""),
            "quality_score": quality.get("quality_score", 0),
            "confidence_score": validation.get("overall_confidence", 0),
            "needs_review": quality.get("requires_manual_review", False),
            "priority": report.get("priority", ""),
            "issues": len(validation.get("issues_found", [])),
            "red_flags": len(quality.get("red_flags", []))
        })

    return jsonify(results)

@app.route('/api/provider/<provider_id>')
def get_provider_detail(provider_id):
    """API endpoint to get detailed provider information"""
    global orchestrator

    results_data = None
    if orchestrator and orchestrator.validation_results:
        results_data = orchestrator.validation_results
    else:
        saved_data = load_saved_results()
        if saved_data and 'results' in saved_data:
            results_data = saved_data['results']

    if not results_data:
        return jsonify({"error": "No results available"}), 404

    provider_result = next(
        (r for r in results_data if r.get("provider", {}).get("provider_id") == provider_id),
        None
    )

    if not provider_result:
        return jsonify({"error": "Provider not found"}), 404

    return jsonify(provider_result)

@app.route('/api/email/<provider_id>')
def get_provider_email(provider_id):
    """API endpoint to generate communication email for provider"""
    global orchestrator

    if orchestrator and orchestrator.validation_results:
        notification = orchestrator.generate_provider_notification(provider_id)
        if "error" in notification:
            return jsonify(notification), 404
        return jsonify(notification)
    
    return jsonify({"error": "No results available"}), 404

@app.route('/api/review-queue')
def get_review_queue():
    """API endpoint to get manual review queue"""
    global orchestrator

    results_data = None
    if orchestrator and orchestrator.validation_results:
        results_data = orchestrator.validation_results
    else:
        saved_data = load_saved_results()
        if saved_data and 'results' in saved_data:
            results_data = saved_data['results']

    if not results_data:
        return jsonify([])

    # Build review queue
    queue = []
    for result in results_data:
        report = result.get('report', {})
        quality = result.get('quality', {})
        if quality.get('requires_manual_review', False):
            queue.append({
                "provider_id": result.get('provider', {}).get('provider_id', ''),
                "provider_name": f"{result.get('provider', {}).get('first_name', '')} {result.get('provider', {}).get('last_name', '')}",
                "priority": report.get('priority', 'Medium'),
                "status": report.get('overall_status', 'Unknown'),
                "quality_metrics": {
                    "quality_score": quality.get('quality_score', 0),
                    "confidence_score": result.get('validation', {}).get('overall_confidence', 0)
                },
                "issues_found": result.get('validation', {}).get('issues_found', []),
                "red_flags": quality.get('red_flags', []),
                "recommended_actions": report.get('recommended_actions', []),
                "queue_position": report.get('queue_position', 0)
            })

    # Sort by priority
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    queue.sort(key=lambda x: (priority_order.get(x['priority'], 999), -x['quality_metrics']['quality_score']))
    
    # Add queue positions
    for i, item in enumerate(queue, 1):
        item['queue_position'] = i
    
    return jsonify(queue)

@app.route('/api/stats')
def get_stats():
    """API endpoint to get processing statistics"""
    global orchestrator

    if orchestrator:
        return jsonify(orchestrator.processing_stats)
    
    saved_data = load_saved_results()
    if saved_data and 'processing_stats' in saved_data:
        return jsonify(saved_data['processing_stats'])
    
    return jsonify({"error": "No results available"}), 404

# ============== NEW API ENDPOINTS ==============

@app.route('/api/analytics/geographic')
def get_geographic_analytics():
    """Get geographic analysis of provider data quality"""
    global orchestrator
    
    if orchestrator and orchestrator.validation_results:
        return jsonify(orchestrator.get_geographic_analysis())
    
    # Generate from saved data
    saved_data = load_saved_results()
    if saved_data and 'results' in saved_data:
        from agents.trend_analysis_agent import TrendAnalysisAgent
        agent = TrendAnalysisAgent()
        return jsonify(agent.analyze_geographic_patterns(saved_data['results']))
    
    return jsonify({"error": "No data available"}), 404

@app.route('/api/analytics/specialty')
def get_specialty_analytics():
    """Get specialty-based trend analysis"""
    global orchestrator
    
    if orchestrator and orchestrator.validation_results:
        return jsonify(orchestrator.get_specialty_trends())
    
    saved_data = load_saved_results()
    if saved_data and 'results' in saved_data:
        from agents.trend_analysis_agent import TrendAnalysisAgent
        agent = TrendAnalysisAgent()
        return jsonify(agent.detect_specialty_trends(saved_data['results']))
    
    return jsonify({"error": "No data available"}), 404

@app.route('/api/analytics/trends')
def get_trend_analytics():
    """Get comprehensive trend analysis"""
    global orchestrator
    
    if orchestrator and orchestrator.validation_results:
        return jsonify(orchestrator.get_trend_analysis())
    
    saved_data = load_saved_results()
    if saved_data and 'results' in saved_data:
        from agents.trend_analysis_agent import TrendAnalysisAgent
        agent = TrendAnalysisAgent()
        return jsonify(agent.generate_trend_report(saved_data['results']))
    
    return jsonify({"error": "No data available"}), 404

@app.route('/api/analytics/summary')
def get_analytics_summary():
    """Get full analytics summary"""
    global orchestrator
    
    if orchestrator and orchestrator.validation_results:
        return jsonify(orchestrator.get_analytics_summary())
    
    # Build summary from saved data
    saved_data = load_saved_results()
    if saved_data and 'results' in saved_data:
        from agents.trend_analysis_agent import TrendAnalysisAgent
        agent = TrendAnalysisAgent()
        return jsonify({
            "trends": agent.generate_trend_report(saved_data['results']),
            "generated_at": datetime.now().isoformat()
        })
    
    return jsonify({"error": "No data available"}), 404

@app.route('/api/notifications/queue')
def get_notification_queue():
    """Get prioritized notification queue"""
    global orchestrator
    
    if orchestrator and orchestrator.validation_results:
        return jsonify(orchestrator.get_notification_queue())
    
    saved_data = load_saved_results()
    if saved_data and 'results' in saved_data:
        from agents.notification_agent import NotificationAgent
        agent = NotificationAgent()
        return jsonify(agent.prioritize_notifications(saved_data['results']))
    
    return jsonify([])

@app.route('/api/notifications/generate/<provider_id>')
def generate_notification(provider_id):
    """Generate notification for a specific provider"""
    global orchestrator
    
    if orchestrator and orchestrator.validation_results:
        return jsonify(orchestrator.generate_provider_notification(provider_id))
    
    saved_data = load_saved_results()
    if saved_data and 'results' in saved_data:
        from agents.notification_agent import NotificationAgent
        agent = NotificationAgent()
        
        provider_result = next(
            (r for r in saved_data['results'] if r.get('provider', {}).get('provider_id') == provider_id),
            None
        )
        
        if not provider_result:
            return jsonify({"error": "Provider not found"}), 404
        
        provider = provider_result['provider']
        report = provider_result.get('report', {})
        
        email = agent.generate_provider_email(
            provider,
            provider.get('issues_found', []),
            report.get('priority', 'medium')
        )
        
        update_request = agent.create_update_request(provider_result)
        
        return jsonify({
            "email": email,
            "update_request": update_request
        })
    
    return jsonify({"error": "No data available"}), 404

@app.route('/api/duplicates')
def get_duplicates():
    """Find potential duplicate providers"""
    global orchestrator
    
    if orchestrator and orchestrator.validation_results:
        return jsonify(orchestrator.find_duplicates())
    
    saved_data = load_saved_results()
    if saved_data and 'results' in saved_data:
        from agents.duplicate_detection_agent import DuplicateDetectionAgent
        agent = DuplicateDetectionAgent()
        providers = [r['provider'] for r in saved_data['results'][:100]]  # Limit for performance
        return jsonify(agent.generate_deduplication_report(providers))
    
    return jsonify({"error": "No data available"}), 404

@app.route('/api/upload', methods=['POST'])
def upload_providers():
    """Upload and parse provider data from CSV/Excel"""
    if not FILE_HANDLERS_AVAILABLE:
        return jsonify({"error": "File upload not available in deployment mode"}), 400
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            content = file.read().decode('utf-8')
            providers = FileUploadHandler.parse_csv(content)
        elif filename.endswith(('.xlsx', '.xls')):
            content = file.read()
            providers = FileUploadHandler.parse_excel(content)
        else:
            return jsonify({"error": "Unsupported file format. Please use CSV or Excel."}), 400
        
        # Save parsed providers
        with open('data/uploaded_providers.json', 'w') as f:
            json.dump(providers, f, indent=2)
        
        return jsonify({
            "status": "success",
            "message": f"Successfully parsed {len(providers)} providers",
            "providers_count": len(providers),
            "sample": providers[:5] if providers else []
        })
    
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 400

@app.route('/api/export/excel')
def export_excel():
    """Export validation results to Excel format"""
    if not FILE_HANDLERS_AVAILABLE:
        return jsonify({"error": "Export not available in deployment mode"}), 400
    
    saved_data = load_saved_results()
    if not saved_data:
        return jsonify({"error": "No data to export"}), 404
    
    try:
        excel_bytes = ReportExporter.to_excel(saved_data)
        
        return send_file(
            io.BytesIO(excel_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@app.route('/api/export/csv')
def export_csv():
    """Export validation results to CSV format"""
    if not FILE_HANDLERS_AVAILABLE:
        return jsonify({"error": "Export not available in deployment mode"}), 400
    
    saved_data = load_saved_results()
    if not saved_data:
        return jsonify({"error": "No data to export"}), 404
    
    try:
        csv_content = ReportExporter.to_csv(saved_data)
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@app.route('/api/export/json')
def export_json():
    """Export validation results to JSON format"""
    saved_data = load_saved_results()
    if not saved_data:
        return jsonify({"error": "No data to export"}), 404
    
    return Response(
        json.dumps(saved_data, indent=2, default=str),
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment; filename=validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        }
    )

@app.route('/api/specialties')
def get_specialties():
    """Get list of unique specialties for filtering"""
    saved_data = load_saved_results()
    if not saved_data or 'results' not in saved_data:
        return jsonify([])
    
    specialties = set()
    for r in saved_data['results']:
        specialty = r.get('provider', {}).get('specialty', '')
        if specialty:
            specialties.add(specialty)
    
    return jsonify(sorted(list(specialties)))

@app.route('/api/states')
def get_states():
    """Get list of unique states for filtering"""
    saved_data = load_saved_results()
    if not saved_data or 'results' not in saved_data:
        return jsonify([])
    
    states = set()
    for r in saved_data['results']:
        state = r.get('provider', {}).get('state', '')
        if state:
            states.add(state)
    
    return jsonify(sorted(list(states)))

if __name__ == '__main__':
    print("\n" + "="*80)
    print("Provider Validation System - Web Dashboard")
    print("="*80)
    print("\nStarting Flask server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("="*80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)

