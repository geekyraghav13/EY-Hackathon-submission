"""
Trend Analysis Agent for Provider Validation System
Analyzes patterns and trends in provider data quality
"""
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import random


class TrendAnalysisAgent:
    """Analyzes geographic, temporal, and specialty-based trends in provider data"""
    
    def __init__(self):
        self.trend_data = {}
        self.patterns = []
    
    def analyze_geographic_patterns(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze data quality patterns by geographic region"""
        state_data = defaultdict(lambda: {
            'total': 0,
            'issues_count': 0,
            'quality_scores': [],
            'critical_count': 0,
            'specialties': defaultdict(int)
        })
        
        for result in results:
            provider = result.get('provider', {})
            report = result.get('report', {})
            
            state = provider.get('state', 'Unknown')
            state_data[state]['total'] += 1
            state_data[state]['issues_count'] += len(provider.get('issues_found', []))
            state_data[state]['quality_scores'].append(provider.get('data_quality_score', 0))
            
            if report.get('overall_status') == 'Critical':
                state_data[state]['critical_count'] += 1
            
            specialty = provider.get('specialty', 'Unknown')
            state_data[state]['specialties'][specialty] += 1
        
        # Calculate aggregated metrics
        geographic_analysis = {}
        for state, data in state_data.items():
            avg_quality = sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            geographic_analysis[state] = {
                'total_providers': data['total'],
                'average_quality_score': round(avg_quality, 1),
                'issues_per_provider': round(data['issues_count'] / data['total'], 2) if data['total'] > 0 else 0,
                'critical_percentage': round(data['critical_count'] / data['total'] * 100, 1) if data['total'] > 0 else 0,
                'top_specialty': max(data['specialties'].items(), key=lambda x: x[1])[0] if data['specialties'] else 'N/A',
                'risk_level': self._calculate_risk_level(avg_quality, data['critical_count'], data['total'])
            }
        
        return {
            'by_state': geographic_analysis,
            'highest_risk_states': self._get_top_risk_states(geographic_analysis, 5),
            'lowest_risk_states': self._get_lowest_risk_states(geographic_analysis, 5),
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_specialty_trends(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze trends by medical specialty"""
        specialty_data = defaultdict(lambda: {
            'total': 0,
            'quality_scores': [],
            'common_issues': defaultdict(int),
            'status_distribution': defaultdict(int)
        })
        
        for result in results:
            provider = result.get('provider', {})
            report = result.get('report', {})
            
            specialty = provider.get('specialty', 'Unknown')
            specialty_data[specialty]['total'] += 1
            specialty_data[specialty]['quality_scores'].append(provider.get('data_quality_score', 0))
            
            # Track issues
            for issue in provider.get('issues_found', []):
                specialty_data[specialty]['common_issues'][issue] += 1
            
            # Track status
            status = report.get('overall_status', 'Unknown')
            specialty_data[specialty]['status_distribution'][status] += 1
        
        # Analyze each specialty
        specialty_analysis = {}
        for specialty, data in specialty_data.items():
            avg_quality = sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            top_issues = sorted(data['common_issues'].items(), key=lambda x: x[1], reverse=True)[:3]
            
            specialty_analysis[specialty] = {
                'provider_count': data['total'],
                'average_quality_score': round(avg_quality, 1),
                'top_issues': [{'issue': i[0], 'count': i[1]} for i in top_issues],
                'status_distribution': dict(data['status_distribution']),
                'trend_indicator': self._calculate_trend_indicator(avg_quality)
            }
        
        return {
            'by_specialty': specialty_analysis,
            'best_performing': self._get_best_specialties(specialty_analysis, 3),
            'needs_attention': self._get_worst_specialties(specialty_analysis, 3),
            'timestamp': datetime.now().isoformat()
        }
    
    def identify_seasonal_patterns(self, historical_data: List[Dict] = None) -> Dict[str, Any]:
        """Identify seasonal or time-based patterns (simulated for demo)"""
        # Simulate seasonal trends for demo purposes
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Simulated quality trend data
        quality_trend = []
        base_score = 55
        for i, month in enumerate(months):
            # Add some seasonal variation
            seasonal_factor = 5 * (1 if i in [0, 1, 11] else -1 if i in [6, 7] else 0)
            score = base_score + random.uniform(-5, 5) + seasonal_factor
            quality_trend.append({
                'month': month,
                'average_quality': round(max(0, min(100, score)), 1),
                'providers_validated': random.randint(150, 250)
            })
        
        return {
            'monthly_trends': quality_trend,
            'peak_months': ['March', 'April', 'October'],
            'low_months': ['July', 'August'],
            'recommendation': 'Schedule additional validation resources for Q2 and Q4',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_trend_report(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive trend analysis report"""
        geographic = self.analyze_geographic_patterns(results)
        specialty = self.detect_specialty_trends(results)
        seasonal = self.identify_seasonal_patterns()
        
        # Generate insights
        insights = self._generate_insights(geographic, specialty)
        
        return {
            'report_title': 'Provider Data Quality Trend Analysis',
            'generated_at': datetime.now().isoformat(),
            'geographic_analysis': geographic,
            'specialty_analysis': specialty,
            'seasonal_patterns': seasonal,
            'key_insights': insights,
            'recommendations': self._generate_recommendations(geographic, specialty)
        }
    
    def _calculate_risk_level(self, avg_quality: float, critical_count: int, total: int) -> str:
        """Calculate risk level based on quality metrics"""
        critical_ratio = critical_count / total if total > 0 else 0
        
        if avg_quality < 40 or critical_ratio > 0.3:
            return 'High'
        elif avg_quality < 60 or critical_ratio > 0.15:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_trend_indicator(self, avg_quality: float) -> str:
        """Calculate trend indicator emoji"""
        if avg_quality >= 70:
            return '↑ Improving'
        elif avg_quality >= 50:
            return '→ Stable'
        else:
            return '↓ Declining'
    
    def _get_top_risk_states(self, analysis: Dict, count: int) -> List[Dict]:
        """Get states with highest risk"""
        risk_order = {'High': 3, 'Medium': 2, 'Low': 1}
        sorted_states = sorted(
            analysis.items(),
            key=lambda x: (risk_order.get(x[1]['risk_level'], 0), -x[1]['average_quality_score']),
            reverse=True
        )
        return [{'state': s[0], **s[1]} for s in sorted_states[:count]]
    
    def _get_lowest_risk_states(self, analysis: Dict, count: int) -> List[Dict]:
        """Get states with lowest risk"""
        sorted_states = sorted(
            analysis.items(),
            key=lambda x: x[1]['average_quality_score'],
            reverse=True
        )
        return [{'state': s[0], **s[1]} for s in sorted_states[:count]]
    
    def _get_best_specialties(self, analysis: Dict, count: int) -> List[Dict]:
        """Get best performing specialties"""
        sorted_specs = sorted(
            analysis.items(),
            key=lambda x: x[1]['average_quality_score'],
            reverse=True
        )
        return [{'specialty': s[0], **s[1]} for s in sorted_specs[:count]]
    
    def _get_worst_specialties(self, analysis: Dict, count: int) -> List[Dict]:
        """Get specialties needing attention"""
        sorted_specs = sorted(
            analysis.items(),
            key=lambda x: x[1]['average_quality_score']
        )
        return [{'specialty': s[0], **s[1]} for s in sorted_specs[:count]]
    
    def _generate_insights(self, geographic: Dict, specialty: Dict) -> List[str]:
        """Generate key insights from analysis"""
        insights = []
        
        high_risk = geographic.get('highest_risk_states', [])
        if high_risk:
            states = ', '.join([s['state'] for s in high_risk[:3]])
            insights.append(f"States with highest data quality risks: {states}")
        
        best_specs = specialty.get('best_performing', [])
        if best_specs:
            specs = ', '.join([s['specialty'] for s in best_specs[:2]])
            insights.append(f"Best performing specialties: {specs}")
        
        worst_specs = specialty.get('needs_attention', [])
        if worst_specs:
            specs = ', '.join([s['specialty'] for s in worst_specs[:2]])
            insights.append(f"Specialties requiring immediate attention: {specs}")
        
        return insights
    
    def _generate_recommendations(self, geographic: Dict, specialty: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        high_risk = geographic.get('highest_risk_states', [])
        for state in high_risk[:2]:
            recommendations.append({
                'priority': 'High',
                'category': 'Geographic',
                'action': f"Prioritize data validation for providers in {state['state']}",
                'impact': f"Potential improvement of {100 - state['average_quality_score']:.0f}% in quality scores"
            })
        
        worst_specs = specialty.get('needs_attention', [])
        for spec in worst_specs[:2]:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Specialty',
                'action': f"Review validation criteria for {spec['specialty']} providers",
                'impact': 'Address common issues specific to this specialty'
            })
        
        return recommendations
