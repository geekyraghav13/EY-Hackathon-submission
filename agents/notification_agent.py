"""
Notification Agent for Provider Validation System
Handles generation and management of provider notifications
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class NotificationAgent:
    """Generates and manages notifications for provider data updates"""
    
    EMAIL_TEMPLATES = {
        'critical': {
            'subject': 'URGENT: Critical Data Issues Require Immediate Attention',
            'priority': 'Critical',
            'tone': 'urgent'
        },
        'high': {
            'subject': 'Important: Provider Data Updates Required',
            'priority': 'High',
            'tone': 'professional'
        },
        'medium': {
            'subject': 'Provider Directory Update Request',
            'priority': 'Medium',
            'tone': 'friendly'
        },
        'low': {
            'subject': 'Routine Provider Information Verification',
            'priority': 'Low',
            'tone': 'casual'
        }
    }
    
    def __init__(self):
        self.notification_queue = []
        self.sent_notifications = []
    
    def generate_provider_email(self, provider: Dict, issues: List[str], priority: str = 'medium') -> Dict[str, Any]:
        """Generate personalized email content for a provider"""
        template = self.EMAIL_TEMPLATES.get(priority.lower(), self.EMAIL_TEMPLATES['medium'])
        
        provider_name = f"Dr. {provider.get('first_name', '')} {provider.get('last_name', '')}"
        specialty = provider.get('specialty', 'Healthcare Provider')
        
        # Generate email body based on issues
        issue_list = self._format_issues(issues)
        
        email_body = self._generate_email_body(
            provider_name=provider_name,
            specialty=specialty,
            issues=issue_list,
            tone=template['tone'],
            provider=provider
        )
        
        return {
            'recipient': {
                'name': provider_name,
                'email': provider.get('email', ''),
                'provider_id': provider.get('provider_id', '')
            },
            'subject': template['subject'],
            'body': email_body,
            'priority': template['priority'],
            'generated_at': datetime.now().isoformat(),
            'issues_addressed': issues,
            'response_deadline': (datetime.now() + timedelta(days=self._get_deadline_days(priority))).isoformat()
        }
    
    def create_update_request(self, result: Dict) -> Dict[str, Any]:
        """Create a structured update request for a provider"""
        provider = result.get('provider', {})
        report = result.get('report', {})
        validation = result.get('validation', {})
        
        # Identify fields that need updates
        fields_to_update = []
        
        if not validation.get('phone_validation', {}).get('valid', True):
            fields_to_update.append({
                'field': 'phone',
                'current_value': provider.get('phone', ''),
                'issue': validation.get('phone_validation', {}).get('issue', 'Invalid'),
                'required': True
            })
        
        if not validation.get('address_validation', {}).get('valid', True):
            fields_to_update.append({
                'field': 'address',
                'current_value': f"{provider.get('address', '')}, {provider.get('city', '')}, {provider.get('state', '')} {provider.get('zip_code', '')}",
                'issue': validation.get('address_validation', {}).get('issue', 'Invalid'),
                'required': True
            })
        
        if not validation.get('license_validation', {}).get('valid', True):
            fields_to_update.append({
                'field': 'license',
                'current_value': provider.get('license_number', ''),
                'issue': validation.get('license_validation', {}).get('issue', 'Invalid'),
                'required': True
            })
        
        return {
            'request_id': f"REQ-{provider.get('provider_id', '')}-{datetime.now().strftime('%Y%m%d')}",
            'provider_id': provider.get('provider_id', ''),
            'provider_name': f"{provider.get('first_name', '')} {provider.get('last_name', '')}",
            'priority': report.get('priority', 'Medium'),
            'fields_to_update': fields_to_update,
            'current_quality_score': provider.get('data_quality_score', 0),
            'created_at': datetime.now().isoformat(),
            'status': 'Pending',
            'reminder_schedule': self._generate_reminder_schedule(report.get('priority', 'Medium'))
        }
    
    def prioritize_notifications(self, results: List[Dict]) -> List[Dict]:
        """Prioritize notifications based on urgency and impact"""
        notifications = []
        
        for result in results:
            provider = result.get('provider', {})
            report = result.get('report', {})
            
            if not report.get('requires_manual_review', False):
                continue
            
            priority = report.get('priority', 'Low')
            priority_score = self._calculate_priority_score(result)
            
            notification = {
                'provider_id': provider.get('provider_id', ''),
                'provider_name': f"{provider.get('first_name', '')} {provider.get('last_name', '')}",
                'priority': priority,
                'priority_score': priority_score,
                'issues_count': len(provider.get('issues_found', [])),
                'quality_score': provider.get('data_quality_score', 0),
                'notification_type': self._determine_notification_type(result),
                'recommended_action': self._get_recommended_action(priority)
            }
            notifications.append(notification)
        
        # Sort by priority score (highest first)
        notifications.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Add queue position
        for idx, notification in enumerate(notifications, 1):
            notification['queue_position'] = idx
        
        return notifications
    
    def track_notification_status(self, notification_id: str) -> Dict[str, Any]:
        """Track the status of a sent notification"""
        # Simulated tracking for demo
        return {
            'notification_id': notification_id,
            'status': 'Sent',
            'sent_at': datetime.now().isoformat(),
            'opened': True,
            'opened_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'response_received': False,
            'follow_up_scheduled': True
        }
    
    def generate_batch_summary(self, notifications: List[Dict]) -> Dict[str, Any]:
        """Generate summary of notification batch"""
        priority_counts = defaultdict(int)
        for n in notifications:
            priority_counts[n.get('priority', 'Unknown')] += 1
        
        return {
            'total_notifications': len(notifications),
            'by_priority': dict(priority_counts),
            'estimated_response_rate': '65%',
            'batch_id': f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.now().isoformat()
        }
    
    def _format_issues(self, issues: List[str]) -> str:
        """Format issues list for email"""
        if not issues:
            return "No specific issues identified."
        
        formatted = "\n".join([f"  • {issue}" for issue in issues])
        return formatted
    
    def _generate_email_body(self, provider_name: str, specialty: str, 
                            issues: str, tone: str, provider: Dict) -> str:
        """Generate email body based on template and tone"""
        
        if tone == 'urgent':
            greeting = f"Dear {provider_name},"
            intro = "We are contacting you regarding critical discrepancies found in your provider directory listing that require immediate attention."
            action = "Please update your information within 48 hours to maintain your active status in our network."
        elif tone == 'professional':
            greeting = f"Dear {provider_name},"
            intro = "During our routine directory validation process, we identified some updates needed for your provider profile."
            action = "We kindly request that you review and update your information within the next 7 days."
        else:
            greeting = f"Hello {provider_name},"
            intro = "We're reaching out to verify your current practice information in our healthcare provider directory."
            action = "When you have a moment, please review your listing and confirm or update your information."
        
        body = f"""{greeting}

{intro}

The following items require your attention:
{issues}

{action}

Your Current Information on File:
  • Practice: {specialty}
  • Address: {provider.get('address', 'N/A')}, {provider.get('city', '')}, {provider.get('state', '')} {provider.get('zip_code', '')}
  • Phone: {provider.get('phone', 'N/A')}
  • NPI: {provider.get('npi', 'N/A')}

To update your information:
  1. Log in to the provider portal
  2. Navigate to "My Profile"
  3. Update the flagged fields
  4. Submit for verification

If you have any questions, please contact our Provider Relations team.

Thank you for your prompt attention to this matter.

Best regards,
Provider Directory Management Team
Healthcare Payer Network
"""
        return body
    
    def _get_deadline_days(self, priority: str) -> int:
        """Get response deadline based on priority"""
        deadlines = {
            'critical': 2,
            'high': 7,
            'medium': 14,
            'low': 30
        }
        return deadlines.get(priority.lower(), 14)
    
    def _generate_reminder_schedule(self, priority: str) -> List[Dict]:
        """Generate reminder schedule based on priority"""
        schedules = {
            'Critical': [
                {'day': 1, 'type': 'email'},
                {'day': 2, 'type': 'phone'}
            ],
            'High': [
                {'day': 3, 'type': 'email'},
                {'day': 5, 'type': 'email'},
                {'day': 7, 'type': 'phone'}
            ],
            'Medium': [
                {'day': 7, 'type': 'email'},
                {'day': 14, 'type': 'email'}
            ],
            'Low': [
                {'day': 14, 'type': 'email'}
            ]
        }
        return schedules.get(priority, schedules['Medium'])
    
    def _calculate_priority_score(self, result: Dict) -> int:
        """Calculate numerical priority score"""
        score = 0
        provider = result.get('provider', {})
        report = result.get('report', {})
        
        # Priority level
        priority_scores = {'Critical': 100, 'High': 75, 'Medium': 50, 'Low': 25}
        score += priority_scores.get(report.get('priority', 'Low'), 25)
        
        # Issues count
        score += len(provider.get('issues_found', [])) * 5
        
        # Inverse quality score (lower quality = higher priority)
        quality = provider.get('data_quality_score', 50)
        score += (100 - quality) * 0.5
        
        return int(score)
    
    def _determine_notification_type(self, result: Dict) -> str:
        """Determine the type of notification needed"""
        report = result.get('report', {})
        red_flags = report.get('red_flags', [])
        
        for flag in red_flags:
            if flag.get('severity') == 'Critical':
                return 'Urgent Update Required'
        
        if report.get('priority') in ['Critical', 'High']:
            return 'Priority Update Request'
        
        return 'Routine Verification'
    
    def _get_recommended_action(self, priority: str) -> str:
        """Get recommended action based on priority"""
        actions = {
            'Critical': 'Immediate phone outreach recommended',
            'High': 'Email with phone follow-up',
            'Medium': 'Standard email notification',
            'Low': 'Batch email notification'
        }
        return actions.get(priority, 'Standard email notification')
