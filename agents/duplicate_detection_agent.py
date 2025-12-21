"""
Duplicate Detection Agent for Provider Validation System
Identifies potential duplicate provider entries using fuzzy matching
"""
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import defaultdict
import re


class DuplicateDetectionAgent:
    """Detects and manages potential duplicate provider entries"""
    
    # Weights for similarity scoring
    FIELD_WEIGHTS = {
        'npi': 0.30,           # NPI is highly unique
        'name': 0.25,          # Name matching
        'phone': 0.15,         # Phone number
        'address': 0.15,       # Address
        'license': 0.10,       # License number
        'specialty': 0.05     # Specialty
    }
    
    SIMILARITY_THRESHOLD = 0.75  # 75% similarity to flag as potential duplicate
    
    def __init__(self):
        self.duplicate_pairs = []
        self.merge_candidates = []
    
    def find_potential_duplicates(self, providers: List[Dict]) -> List[Dict]:
        """Find potential duplicate providers in the dataset"""
        duplicates = []
        processed_pairs = set()
        
        for i, provider1 in enumerate(providers):
            for j, provider2 in enumerate(providers[i+1:], start=i+1):
                pair_key = tuple(sorted([provider1.get('provider_id', ''), provider2.get('provider_id', '')]))
                
                if pair_key in processed_pairs:
                    continue
                
                similarity = self.calculate_similarity_score(provider1, provider2)
                
                if similarity >= self.SIMILARITY_THRESHOLD:
                    duplicate_record = {
                        'pair_id': f"DUP-{i:04d}-{j:04d}",
                        'provider_1': {
                            'id': provider1.get('provider_id', ''),
                            'name': f"{provider1.get('first_name', '')} {provider1.get('last_name', '')}",
                            'npi': provider1.get('npi', ''),
                            'specialty': provider1.get('specialty', ''),
                            'phone': provider1.get('phone', ''),
                            'address': self._format_address(provider1)
                        },
                        'provider_2': {
                            'id': provider2.get('provider_id', ''),
                            'name': f"{provider2.get('first_name', '')} {provider2.get('last_name', '')}",
                            'npi': provider2.get('npi', ''),
                            'specialty': provider2.get('specialty', ''),
                            'phone': provider2.get('phone', ''),
                            'address': self._format_address(provider2)
                        },
                        'similarity_score': round(similarity * 100, 1),
                        'matching_fields': self._get_matching_fields(provider1, provider2),
                        'confidence': self._get_confidence_level(similarity),
                        'recommended_action': self._get_recommended_action(similarity),
                        'detected_at': datetime.now().isoformat()
                    }
                    duplicates.append(duplicate_record)
                    processed_pairs.add(pair_key)
        
        # Sort by similarity score
        duplicates.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return duplicates
    
    def calculate_similarity_score(self, provider1: Dict, provider2: Dict) -> float:
        """Calculate weighted similarity score between two providers"""
        total_score = 0.0
        
        # NPI comparison (exact match only)
        npi1 = str(provider1.get('npi', '')).strip()
        npi2 = str(provider2.get('npi', '')).strip()
        if npi1 and npi2:
            npi_score = 1.0 if npi1 == npi2 else 0.0
            total_score += npi_score * self.FIELD_WEIGHTS['npi']
        
        # Name comparison (fuzzy)
        name1 = f"{provider1.get('first_name', '')} {provider1.get('last_name', '')}".lower().strip()
        name2 = f"{provider2.get('first_name', '')} {provider2.get('last_name', '')}".lower().strip()
        name_score = self._string_similarity(name1, name2)
        total_score += name_score * self.FIELD_WEIGHTS['name']
        
        # Phone comparison (normalized)
        phone1 = self._normalize_phone(provider1.get('phone', ''))
        phone2 = self._normalize_phone(provider2.get('phone', ''))
        if phone1 and phone2:
            phone_score = 1.0 if phone1 == phone2 else self._string_similarity(phone1, phone2)
            total_score += phone_score * self.FIELD_WEIGHTS['phone']
        
        # Address comparison (fuzzy)
        addr1 = self._normalize_address(provider1)
        addr2 = self._normalize_address(provider2)
        addr_score = self._string_similarity(addr1, addr2)
        total_score += addr_score * self.FIELD_WEIGHTS['address']
        
        # License comparison
        lic1 = str(provider1.get('license_number', '')).upper().strip()
        lic2 = str(provider2.get('license_number', '')).upper().strip()
        if lic1 and lic2:
            lic_score = 1.0 if lic1 == lic2 else self._string_similarity(lic1, lic2)
            total_score += lic_score * self.FIELD_WEIGHTS['license']
        
        # Specialty comparison
        spec1 = provider1.get('specialty', '').lower().strip()
        spec2 = provider2.get('specialty', '').lower().strip()
        spec_score = 1.0 if spec1 == spec2 else 0.5 if self._specialties_related(spec1, spec2) else 0.0
        total_score += spec_score * self.FIELD_WEIGHTS['specialty']
        
        return total_score
    
    def suggest_merge_candidates(self, duplicates: List[Dict]) -> List[Dict]:
        """Suggest which provider records should be merged"""
        merge_candidates = []
        
        for dup in duplicates:
            if dup['similarity_score'] >= 85:  # High confidence duplicates
                merge_candidate = {
                    'pair_id': dup['pair_id'],
                    'providers': [dup['provider_1'], dup['provider_2']],
                    'similarity': dup['similarity_score'],
                    'merge_recommendation': self._generate_merge_recommendation(dup),
                    'primary_record': self._determine_primary_record(dup),
                    'fields_to_merge': self._identify_merge_fields(dup),
                    'auto_merge_eligible': dup['similarity_score'] >= 95
                }
                merge_candidates.append(merge_candidate)
        
        return merge_candidates
    
    def generate_deduplication_report(self, providers: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive deduplication report"""
        duplicates = self.find_potential_duplicates(providers)
        merge_candidates = self.suggest_merge_candidates(duplicates)
        
        # Statistics
        by_confidence = defaultdict(int)
        for dup in duplicates:
            by_confidence[dup['confidence']] += 1
        
        return {
            'report_title': 'Provider Duplicate Detection Report',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_providers_analyzed': len(providers),
                'potential_duplicates_found': len(duplicates),
                'merge_candidates': len(merge_candidates),
                'auto_merge_eligible': sum(1 for m in merge_candidates if m.get('auto_merge_eligible', False))
            },
            'by_confidence': dict(by_confidence),
            'duplicates': duplicates[:50],  # Limit for display
            'merge_candidates': merge_candidates[:20],
            'recommendations': self._generate_report_recommendations(duplicates)
        }
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using Levenshtein-like approach"""
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0
        
        # Simple token-based similarity for performance
        tokens1 = set(s1.lower().split())
        tokens2 = set(s2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to digits only"""
        if not phone:
            return ''
        digits = re.sub(r'\D', '', str(phone))
        # Remove country code if present
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        return digits[-10:] if len(digits) >= 10 else digits
    
    def _normalize_address(self, provider: Dict) -> str:
        """Normalize address for comparison"""
        parts = [
            str(provider.get('address', '')),
            str(provider.get('city', '')),
            str(provider.get('state', '')),
            str(provider.get('zip_code', ''))[:5]
        ]
        normalized = ' '.join(p.lower().strip() for p in parts if p)
        # Remove common abbreviations
        normalized = normalized.replace('street', 'st').replace('avenue', 'ave')
        normalized = normalized.replace('boulevard', 'blvd').replace('drive', 'dr')
        return normalized
    
    def _format_address(self, provider: Dict) -> str:
        """Format address for display"""
        return f"{provider.get('address', '')}, {provider.get('city', '')}, {provider.get('state', '')} {provider.get('zip_code', '')}"
    
    def _specialties_related(self, spec1: str, spec2: str) -> bool:
        """Check if two specialties are related"""
        related_groups = [
            {'internal medicine', 'family medicine', 'primary care'},
            {'cardiology', 'cardiovascular', 'heart'},
            {'orthopedic', 'orthopedics', 'orthopedic surgery'},
            {'psychiatry', 'psychology', 'mental health'},
            {'pediatrics', 'pediatric', 'child health'}
        ]
        
        for group in related_groups:
            if any(s in spec1 for s in group) and any(s in spec2 for s in group):
                return True
        return False
    
    def _get_matching_fields(self, provider1: Dict, provider2: Dict) -> List[str]:
        """Identify which fields match between providers"""
        matching = []
        
        if provider1.get('npi') == provider2.get('npi'):
            matching.append('NPI')
        
        name1 = f"{provider1.get('first_name', '')} {provider1.get('last_name', '')}".lower()
        name2 = f"{provider2.get('first_name', '')} {provider2.get('last_name', '')}".lower()
        if name1 == name2:
            matching.append('Full Name')
        elif provider1.get('last_name', '').lower() == provider2.get('last_name', '').lower():
            matching.append('Last Name')
        
        if self._normalize_phone(provider1.get('phone', '')) == self._normalize_phone(provider2.get('phone', '')):
            matching.append('Phone')
        
        if provider1.get('specialty', '').lower() == provider2.get('specialty', '').lower():
            matching.append('Specialty')
        
        if provider1.get('state', '').upper() == provider2.get('state', '').upper():
            matching.append('State')
        
        return matching
    
    def _get_confidence_level(self, similarity: float) -> str:
        """Get confidence level label"""
        if similarity >= 0.95:
            return 'Very High'
        elif similarity >= 0.85:
            return 'High'
        elif similarity >= 0.75:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_recommended_action(self, similarity: float) -> str:
        """Get recommended action based on similarity"""
        if similarity >= 0.95:
            return 'Auto-merge recommended'
        elif similarity >= 0.85:
            return 'Manual review and merge'
        elif similarity >= 0.75:
            return 'Review for potential merge'
        else:
            return 'Monitor - likely different providers'
    
    def _generate_merge_recommendation(self, duplicate: Dict) -> str:
        """Generate merge recommendation text"""
        score = duplicate['similarity_score']
        if score >= 95:
            return "These records appear to be exact duplicates. Auto-merge is recommended."
        elif score >= 85:
            return "High similarity detected. Manual review recommended before merging."
        else:
            return "Moderate similarity. Careful review required to confirm duplicate status."
    
    def _determine_primary_record(self, duplicate: Dict) -> str:
        """Determine which record should be the primary (surviving) record"""
        # In a real system, this would use more sophisticated logic
        # For demo, we just pick provider_1
        return duplicate['provider_1']['id']
    
    def _identify_merge_fields(self, duplicate: Dict) -> List[Dict]:
        """Identify which fields should be merged and how"""
        fields = []
        p1 = duplicate['provider_1']
        p2 = duplicate['provider_2']
        
        if p1.get('phone') != p2.get('phone'):
            fields.append({
                'field': 'phone',
                'value_1': p1.get('phone', ''),
                'value_2': p2.get('phone', ''),
                'recommendation': 'Keep most recently verified'
            })
        
        if p1.get('address') != p2.get('address'):
            fields.append({
                'field': 'address',
                'value_1': p1.get('address', ''),
                'value_2': p2.get('address', ''),
                'recommendation': 'Keep most complete address'
            })
        
        return fields
    
    def _generate_report_recommendations(self, duplicates: List[Dict]) -> List[str]:
        """Generate recommendations for the deduplication report"""
        recommendations = []
        
        high_confidence = sum(1 for d in duplicates if d['similarity_score'] >= 85)
        if high_confidence > 0:
            recommendations.append(f"Review and merge {high_confidence} high-confidence duplicate pairs")
        
        auto_merge = sum(1 for d in duplicates if d['similarity_score'] >= 95)
        if auto_merge > 0:
            recommendations.append(f"{auto_merge} pairs are eligible for automatic merging")
        
        if len(duplicates) > 0:
            recommendations.append("Implement duplicate prevention at data entry point")
            recommendations.append("Consider standardizing data formats to reduce false duplicates")
        
        return recommendations
