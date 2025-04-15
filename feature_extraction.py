"""
Feature Extraction Module for SaaS Case Analysis Application

This module implements structured feature extraction techniques for legal cases
to enhance the accuracy of settlement predictions. It extracts features across
multiple dimensions including case characteristics, party-specific factors,
evidence-based factors, and procedural/strategic factors.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class FeatureExtractor:
    """
    Main class for extracting structured features from legal case data.
    Implements various feature extraction techniques based on case type and available data.
    """
    
    def __init__(self):
        """Initialize the feature extractor with necessary resources."""
        # Jurisdiction data for regional analysis
        self.jurisdiction_data = {
            # Sample jurisdiction data - would be expanded in production
            "california": {
                "avg_settlement": 75000,
                "jury_favorability": 0.65,
                "damage_caps": {"medical_malpractice": 250000}
            },
            "new york": {
                "avg_settlement": 85000,
                "jury_favorability": 0.60,
                "damage_caps": {}
            },
            "texas": {
                "avg_settlement": 65000,
                "jury_favorability": 0.45,
                "damage_caps": {"non_economic": 750000}
            }
        }
        
        # Case type classification data
        self.case_type_data = {
            "personal_injury": {
                "subtypes": ["motor_vehicle", "slip_fall", "medical_malpractice", "product_liability", "workplace"],
                "avg_duration": 18,  # months
                "settlement_rate": 0.85
            },
            "contract_dispute": {
                "subtypes": ["breach", "performance", "payment", "warranty"],
                "avg_duration": 14,  # months
                "settlement_rate": 0.78
            },
            "employment": {
                "subtypes": ["discrimination", "harassment", "wrongful_termination", "wage_dispute"],
                "avg_duration": 22,  # months
                "settlement_rate": 0.72
            }
        }
        
        # Common injury types and severity scales
        self.injury_severity = {
            "whiplash": {"min": 2, "max": 6, "chronic_risk": 0.3},
            "fracture": {"min": 4, "max": 8, "chronic_risk": 0.25},
            "concussion": {"min": 3, "max": 7, "chronic_risk": 0.4},
            "soft_tissue": {"min": 1, "max": 5, "chronic_risk": 0.2},
            "spinal": {"min": 6, "max": 10, "chronic_risk": 0.7},
            "traumatic_brain_injury": {"min": 7, "max": 10, "chronic_risk": 0.8},
            "amputation": {"min": 8, "max": 10, "chronic_risk": 0.9},
            "psychological": {"min": 3, "max": 9, "chronic_risk": 0.5}
        }
    
    def extract_all_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all relevant features from the case data.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Extract case characteristic features
        features.update(self.extract_case_characteristic_features(case_data))
        
        # Extract party-specific features
        features.update(self.extract_party_specific_features(case_data))
        
        # Extract evidence-based features
        features.update(self.extract_evidence_based_features(case_data))
        
        # Extract procedural and strategic features
        features.update(self.extract_procedural_strategic_features(case_data))
        
        # Create composite features
        features.update(self.create_composite_features(features, case_data))
        
        return features
    
    def extract_case_characteristic_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features related to case characteristics.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Dictionary of case characteristic features
        """
        features = {}
        
        # Jurisdiction-based features
        features.update(self.extract_jurisdiction_features(case_data))
        
        # Case type classification features
        features.update(self.extract_case_type_features(case_data))
        
        # Temporal features
        features.update(self.extract_temporal_features(case_data))
        
        # Damage quantification features
        features.update(self.extract_damage_features(case_data))
        
        return {"case_characteristics": features}
    
    def extract_jurisdiction_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract jurisdiction-based features."""
        features = {
            "jurisdiction": "unknown",
            "jurisdiction_data": {},
            "venue_type": "unknown"
        }
        
        # Extract jurisdiction from court name
        court = case_data.get("court", "")
        if court:
            # Extract state from court name
            state_pattern = r"(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)"
            state_match = re.search(state_pattern, court, re.IGNORECASE)
            
            if state_match:
                state = state_match.group(1).lower()
                features["jurisdiction"] = state
                features["jurisdiction_data"] = self.jurisdiction_data.get(state, {})
            
            # Determine venue type
            if "federal" in court.lower():
                features["venue_type"] = "federal"
            elif "supreme" in court.lower():
                features["venue_type"] = "state_supreme"
            elif "appeal" in court.lower():
                features["venue_type"] = "appellate"
            elif "district" in court.lower() or "circuit" in court.lower():
                features["venue_type"] = "trial"
            elif "county" in court.lower() or "municipal" in court.lower():
                features["venue_type"] = "local"
        
        return {"jurisdiction": features}
    
    def extract_case_type_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract case type classification features."""
        features = {
            "primary_type": "unknown",
            "subtype": "unknown",
            "complexity": "standard",
            "type_data": {}
        }
        
        # Extract primary case type
        claim_type = case_data.get("claim_type", "").lower()
        
        # Map claim type to known case types
        if "personal injury" in claim_type or "injury" in claim_type:
            features["primary_type"] = "personal_injury"
            
            # Determine subtype
            if "vehicle" in claim_type or "car" in claim_type or "auto" in claim_type:
                features["subtype"] = "motor_vehicle"
            elif "slip" in claim_type or "fall" in claim_type:
                features["subtype"] = "slip_fall"
            elif "medical" in claim_type or "malpractice" in claim_type:
                features["subtype"] = "medical_malpractice"
            elif "product" in claim_type:
                features["subtype"] = "product_liability"
            elif "work" in claim_type or "employment" in claim_type:
                features["subtype"] = "workplace"
                
        elif "contract" in claim_type or "agreement" in claim_type:
            features["primary_type"] = "contract_dispute"
            
            # Determine subtype
            if "breach" in claim_type:
                features["subtype"] = "breach"
            elif "performance" in claim_type:
                features["subtype"] = "performance"
            elif "payment" in claim_type:
                features["subtype"] = "payment"
            elif "warranty" in claim_type:
                features["subtype"] = "warranty"
                
        elif "employment" in claim_type or "worker" in claim_type:
            features["primary_type"] = "employment"
            
            # Determine subtype
            if "discrimination" in claim_type:
                features["subtype"] = "discrimination"
            elif "harassment" in claim_type:
                features["subtype"] = "harassment"
            elif "termination" in claim_type or "fired" in claim_type:
                features["subtype"] = "wrongful_termination"
            elif "wage" in claim_type or "pay" in claim_type:
                features["subtype"] = "wage_dispute"
        
        # Get case type data
        features["type_data"] = self.case_type_data.get(features["primary_type"], {})
        
        # Determine complexity
        facts = case_data.get("facts", "")
        if facts:
            word_count = len(facts.split())
            if word_count > 500:
                features["complexity"] = "complex"
            elif word_count > 1000:
                features["complexity"] = "novel"
        
        return {"case_type": features}
    
    def extract_temporal_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal features."""
        features = {
            "days_since_filing": None,
            "time_to_trial_estimate": None,
            "statute_of_limitations_risk": "unknown"
        }
        
        # Calculate days since filing
        date_filed = case_data.get("date_filed", "")
        if date_filed:
            try:
                # Try different date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%B %d, %Y"]:
                    try:
                        filed_date = datetime.strptime(date_filed, fmt)
                        days_since = (datetime.now() - filed_date).days
                        features["days_since_filing"] = days_since
                        break
                    except ValueError:
                        continue
            except Exception:
                pass
        
        # Estimate time to trial based on case type
        case_type_features = self.extract_case_type_features(case_data)
        primary_type = case_type_features["case_type"]["primary_type"]
        type_data = self.case_type_data.get(primary_type, {})
        avg_duration = type_data.get("avg_duration", 18)  # Default to 18 months
        
        if features["days_since_filing"] is not None:
            months_since_filing = features["days_since_filing"] / 30.44  # Average days per month
            features["time_to_trial_estimate"] = max(0, avg_duration - months_since_filing)
        
        # Statute of limitations risk
        if primary_type == "personal_injury":
            # Most states have 2-3 year SOL for personal injury
            if features["days_since_filing"] is not None:
                years_since_filing = features["days_since_filing"] / 365.25
                if years_since_filing > 2.5:
                    features["statute_of_limitations_risk"] = "high"
                elif years_since_filing > 1.5:
                    features["statute_of_limitations_risk"] = "medium"
                else:
                    features["statute_of_limitations_risk"] = "low"
        
        return {"temporal": features}
    
    def extract_damage_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract damage quantification features."""
        features = {
            "economic_damages": 0.0,
            "estimated_non_economic_damages": 0.0,
            "total_estimated_damages": 0.0,
            "damage_multiplier": 1.0
        }
        
        # Extract economic damages
        economic_damages = case_data.get("damages", 0.0)
        features["economic_damages"] = float(economic_damages)
        
        # Estimate non-economic damages based on case type and injury
        case_type_features = self.extract_case_type_features(case_data)
        primary_type = case_type_features["case_type"]["primary_type"]
        
        if primary_type == "personal_injury":
            # Calculate multiplier based on injury severity
            multiplier = 1.5  # Default multiplier
            
            injury_types = case_data.get("injury_types", [])
            injury_details = case_data.get("injury_details", "")
            
            severity_score = self._calculate_injury_severity(injury_types, injury_details)
            
            # Adjust multiplier based on severity
            if severity_score > 7:
                multiplier = 4.0
            elif severity_score > 5:
                multiplier = 3.0
            elif severity_score > 3:
                multiplier = 2.0
            
            features["damage_multiplier"] = multiplier
            features["estimated_non_economic_damages"] = features["economic_damages"] * multiplier
            
        elif primary_type == "contract_dispute":
            # Contract disputes typically have limited non-economic damages
            features["damage_multiplier"] = 0.25
            features["estimated_non_economic_damages"] = features["economic_damages"] * 0.25
            
        elif primary_type == "employment":
            # Employment cases often have emotional distress damages
            features["damage_multiplier"] = 1.0
            features["estimated_non_economic_damages"] = features["economic_damages"] * 1.0
        
        # Calculate total estimated damages
        features["total_estimated_damages"] = features["economic_damages"] + features["estimated_non_economic_damages"]
        
        return {"damages": features}
    
    def _calculate_injury_severity(self, injury_types: List[str], injury_details: str) -> float:
        """
        Calculate injury severity score based on injury types and details.
        
        Args:
            injury_types: List of injury type strings
            injury_details: Detailed description of injuries
            
        Returns:
            Severity score from 1-10
        """
        severity_score = 0
        count = 0
        
        # Check for known injury types
        for injury in injury_types:
            injury_lower = injury.lower()
            for known_injury, data in self.injury_severity.items():
                if known_injury in injury_lower:
                    severity_score += (data["min"] + data["max"]) / 2
                    count += 1
                    break
        
        # If no matches found, use text analysis
        if count == 0:
            # Check for severity indicators in the details
            severity_indicators = {
                "severe": 3,
                "significant": 2.5,
                "serious": 2.5,
                "moderate": 1.5,
                "mild": 0.5,
                "minor": 0.5,
                "permanent": 3,
                "temporary": 1,
                "chronic": 2,
                "acute": 1.5,
                "surgery": 2.5,
                "hospitalization": 2,
                "therapy": 1,
                "pain": 1,
                "disability": 2.5,
                "impairment": 2
            }
            
            detail_score = 0
            detail_count = 0
            
            for indicator, value in severity_indicators.items():
                if indicator in injury_details.lower():
                    detail_score += value
                    detail_count += 1
            
            if detail_count > 0:
                severity_score = min(10, detail_score / detail_count * 2)
            else:
                severity_score = 3  # Default moderate severity
        else:
            severity_score /= count
        
        return min(10, severity_score)
    
    def extract_party_specific_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features related to parties involved in the case.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Dictionary of party-specific features
        """
        features = {}
        
        # Extract plaintiff characteristics
        features.update(self.extract_plaintiff_features(case_data))
        
        # Extract defendant characteristics
        features.update(self.extract_defendant_features(case_data))
        
        # Extract attorney representation features
        features.update(self.extract_attorney_features(case_data))
        
        # Extract relationship features
        features.update(self.extract_relationship_features(case_data))
        
        return {"party_specific": features}
    
    def extract_plaintiff_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract plaintiff characteristic features."""
        features = {
            "type": "individual",  # Default assumption
            "sympathetic_factors": 0.0,
            "credibility_factors": 0.0
        }
        
        # Analyze facts and injury details for plaintiff information
        facts = case_data.get("facts", "").lower()
        injury_details = case_data.get("injury_details", "").lower()
        
        # Determine plaintiff type
        if "company" in facts or "corporation" in facts or "business" in facts:
            features["type"] = "business"
        elif "government" in facts or "agency" in facts or "department" in facts:
            features["type"] = "government"
        
        # Analyze sympathetic factors
        sympathetic_indicators = [
            "child", "elderly", "pregnant", "disability", "veteran", 
            "pre-existing", "family", "emotional", "trauma", "victim"
        ]
        
        sympathetic_score = 0
        for indicator in sympathetic_indicators:
            if indicator in facts or indicator in injury_details:
                sympathetic_score += 1
        
        features["sympathetic_factors"] = min(1.0, sympathetic_score / 5)
        
        # Analyze credibility factors
        credibility_positive = ["consistent", "documented", "evidence", "witness", "record"]
        credibility_negative = ["inconsistent", "contradiction", "prior claim", "criminal", "misleading"]
        
        credibility_score = 0.5  # Start at neutral
        for indicator in credibility_positive:
            if indicator in facts:
                credibility_score += 0.1
        
        for indicator in credibility_negative:
            if indicator in facts:
                credibility_score -= 0.1
        
        features["credibility_factors"] = max(0.0, min(1.0, credibility_score))
        
        return {"plaintiff": features}
    
    def extract_defendant_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract defendant characteristic features."""
        features = {
            "type": "individual",  # Default assumption
            "insurance_involved": False,
            "deep_pockets": 0.0,
            "public_relations_risk": 0.0
        }
        
        # Check for insurance company involvement
        insurance_company = case_data.get("insurance_company", "")
        if insurance_company:
            features["insurance_involved"] = True
        
        # Analyze facts for defendant information
        facts = case_data.get("facts", "").lower()
        
        # Determine defendant type
        if "company" in facts or "corporation" in facts or "business" in facts:
            features["type"] = "business"
            
            # Estimate deep pockets factor
            if "large" in facts or "corporation" in facts or "multinational" in facts:
                features["deep_pockets"] = 0.8
            elif "medium" in facts or "regional" in facts:
                features["deep_pockets"] = 0.5
            else:
                features["deep_pockets"] = 0.3
                
            # Estimate PR risk
            pr_indicators = ["public", "reputation", "media", "news", "press", "scandal", "attention"]
            pr_score = 0
            for indicator in pr_indicators:
                if indicator in facts:
                    pr_score += 1
            
            features["public_relations_risk"] = min(1.0, pr_score / 3)
            
        elif "government" in facts or "agency" in facts or "department" in facts:
            features["type"] = "government"
            features["deep_pockets"] = 0.7
            features["public_relations_risk"] = 0.6
        
        return {"defendant": features}
    
    def extract_attorney_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract attorney representation features."""
        # This is a simplified implementation - in a real system, you would
        # have a database of attorneys and firms with historical performance data
        features = {
            "plaintiff_representation_strength": 0.5,  # Default to average
            "defendant_representation_strength": 0.5,  # Default to average
            "representation_asymmetry": 0.0
        }
        
        # Check for expert witnesses as a proxy for representation quality
        plaintiff_medical_expert = case_data.get("plaintiff_medical_expert", "")
        defendant_medical_expert = case_data.get("defendant_medical_expert", "")
        plaintiff_non_medical_expert = case_data.get("plaintiff_non_medical_expert", "")
        defendant_non_medical_expert = case_data.get("defendant_non_medical_expert", "")
        
        # Adjust representation strength based on expert witnesses
        if plaintiff_medical_expert or plaintiff_non_medical_expert:
            features["plaintiff_representation_strength"] += 0.2
        
        if defendant_medical_expert or defendant_non_medical_expert:
            features["defendant_representation_strength"] += 0.2
        
        # Calculate representation asymmetry
        features["representation_asymmetry"] = features["plaintiff_representation_strength"] - features["defendant_representation_strength"]
        
        return {"attorney": features}
    
    def extract_relationship_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relationship features between parties."""
        features = {
            "relationship_type": "none",  # Default assumption
            "ongoing_relationship": False,
            "power_dynamic": 0.0  # 0 = equal, positive = plaintiff advantage, negative = defendant advantage
        }
        
        # Analyze facts for relationship information
        facts = case_data.get("facts", "").lower()
        
        # Determine relationship type
        relationship_indicators = {
            "contractual": ["contract", "agreement", "business relationship", "client", "customer"],
            "employment": ["employee", "employer", "workplace", "job", "work"],
            "professional": ["doctor", "patient", "lawyer", "client", "professional"],
            "personal": ["family", "friend", "neighbor", "personal", "relative"]
        }
        
        for rel_type, indicators in relationship_indicators.items():
            for indicator in indicators:
                if indicator in facts:
                    features["relationship_type"] = rel_type
                    break
            if features["relationship_type"] != "none":
                break
        
        # Check for ongoing relationship
        ongoing_indicators = ["ongoing", "current", "continuing", "still", "remains"]
        for indicator in ongoing_indicators:
            if indicator in facts:
                features["ongoing_relationship"] = True
                break
        
        # Analyze power dynamic
        if features["relationship_type"] == "employment":
            features["power_dynamic"] = -0.5  # Employer typically has advantage
        elif features["relationship_type"] == "professional":
            features["power_dynamic"] = -0.3  # Professional typically has advantage
        
        # Adjust based on defendant type
        defendant_features = self.extract_defendant_features(case_data)
        if defendant_features["defendant"]["type"] == "business" and features["relationship_type"] != "employment":
            features["power_dynamic"] -= 0.2
        elif defendant_features["defendant"]["type"] == "government":
            features["power_dynamic"] -= 0.4
        
        return {"relationship": features}
    
    def extract_evidence_based_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features related to evidence in the case.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Dictionary of evidence-based features
        """
        features = {}
        
        # Extract evidence strength assessment
        features.update(self.extract_evidence_strength(case_data))
        
        # Extract expert opinion features
        features.update(self.extract_expert_opinion_features(case_data))
        
        # Extract documentary evidence classification
        features.update(self.extract_documentary_evidence(case_data))
        
        # Extract witness credibility features
        features.update(self.extract_witness_features(case_data))
        
        return {"evidence_based": features}
    
    def extract_evidence_strength(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract evidence strength assessment."""
        features = {
            "overall_strength": 0.5,  # Default to average
            "key_evidence_types": [],
            "evidence_gaps": []
        }
        
        # Analyze facts for evidence information
        facts = case_data.get("facts", "").lower()
        
        # Check for evidence types
        evidence_types = {
            "documentary": ["document", "record", "report", "file", "written"],
            "testimonial": ["witness", "testimony", "statement", "interview"],
            "physical": ["physical", "object", "item", "exhibit"],
            "digital": ["video", "recording", "email", "message", "digital", "electronic"],
            "expert": ["expert", "specialist", "professional opinion"]
        }
        
        # Count evidence types
        evidence_counts = {}
        for ev_type, indicators in evidence_types.items():
            count = 0
            for indicator in indicators:
                if indicator in facts:
                    count += 1
            if count > 0:
                evidence_counts[ev_type] = count
                features["key_evidence_types"].append(ev_type)
        
        # Calculate overall strength based on diversity and quantity of evidence
        if evidence_counts:
            diversity_factor = min(1.0, len(evidence_counts) / 5)
            quantity_factor = min(1.0, sum(evidence_counts.values()) / 10)
            features["overall_strength"] = (diversity_factor + quantity_factor) / 2
        
        # Check for evidence gaps
        gap_indicators = {
            "no_witnesses": ["no witness", "lack of witness", "without witness"],
            "no_documentation": ["no document", "lack of document", "without document"],
            "no_physical_evidence": ["no physical", "lack of physical", "without physical"],
            "conflicting_evidence": ["conflict", "contradict", "inconsistent"]
        }
        
        for gap_type, indicators in gap_indicators.items():
            for indicator in indicators:
                if indicator in facts:
                    features["evidence_gaps"].append(gap_type)
                    features["overall_strength"] -= 0.1  # Reduce strength for each gap
                    break
        
        # Ensure overall strength is within bounds
        features["overall_strength"] = max(0.1, min(1.0, features["overall_strength"]))
        
        return {"evidence_strength": features}
    
    def extract_expert_opinion_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract expert opinion features."""
        features = {
            "plaintiff_expert_strength": 0.0,
            "defendant_expert_strength": 0.0,
            "expert_advantage": 0.0
        }
        
        # Check for expert witnesses
        plaintiff_medical_expert = case_data.get("plaintiff_medical_expert", "")
        defendant_medical_expert = case_data.get("defendant_medical_expert", "")
        plaintiff_non_medical_expert = case_data.get("plaintiff_non_medical_expert", "")
        defendant_non_medical_expert = case_data.get("defendant_non_medical_expert", "")
        
        # Calculate plaintiff expert strength
        if plaintiff_medical_expert:
            features["plaintiff_expert_strength"] += 0.4
        if plaintiff_non_medical_expert:
            features["plaintiff_expert_strength"] += 0.3
        
        # Calculate defendant expert strength
        if defendant_medical_expert:
            features["defendant_expert_strength"] += 0.4
        if defendant_non_medical_expert:
            features["defendant_expert_strength"] += 0.3
        
        # Calculate expert advantage
        features["expert_advantage"] = features["plaintiff_expert_strength"] - features["defendant_expert_strength"]
        
        return {"expert_opinion": features}
    
    def extract_documentary_evidence(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract documentary evidence classification."""
        features = {
            "documentary_evidence_strength": 0.5,  # Default to average
            "key_document_types": []
        }
        
        # Analyze facts for documentary evidence
        facts = case_data.get("facts", "").lower()
        
        # Check for document types
        document_types = {
            "medical_records": ["medical record", "health record", "hospital record", "doctor record"],
            "contracts": ["contract", "agreement", "terms", "signed document"],
            "correspondence": ["email", "letter", "message", "correspondence", "communication"],
            "financial_records": ["financial", "accounting", "bank", "transaction", "payment"],
            "official_reports": ["police report", "incident report", "official report", "investigation"]
        }
        
        # Identify document types
        for doc_type, indicators in document_types.items():
            for indicator in indicators:
                if indicator in facts:
                    features["key_document_types"].append(doc_type)
                    features["documentary_evidence_strength"] += 0.1
                    break
        
        # Check for smoking gun documents
        smoking_gun_indicators = ["smoking gun", "conclusive", "definitive", "undeniable", "admission"]
        for indicator in smoking_gun_indicators:
            if indicator in facts:
                features["documentary_evidence_strength"] += 0.3
                break
        
        # Ensure documentary evidence strength is within bounds
        features["documentary_evidence_strength"] = max(0.1, min(1.0, features["documentary_evidence_strength"]))
        
        return {"documentary_evidence": features}
    
    def extract_witness_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract witness credibility features."""
        features = {
            "witness_credibility": 0.5,  # Default to average
            "witness_types": []
        }
        
        # Analyze facts for witness information
        facts = case_data.get("facts", "").lower()
        
        # Check for witness types
        witness_types = {
            "eyewitness": ["eyewitness", "saw", "observed", "witnessed"],
            "character_witness": ["character", "reputation", "vouched"],
            "expert_witness": ["expert witness", "expert testimony", "professional opinion"],
            "fact_witness": ["fact witness", "factual testimony"]
        }
        
        # Identify witness types
        for wit_type, indicators in witness_types.items():
            for indicator in indicators:
                if indicator in facts:
                    features["witness_types"].append(wit_type)
                    if wit_type == "eyewitness" or wit_type == "expert_witness":
                        features["witness_credibility"] += 0.1
                    break
        
        # Check for credibility factors
        credibility_positive = ["consistent", "reliable", "credible", "trustworthy", "unbiased"]
        credibility_negative = ["inconsistent", "unreliable", "biased", "contradictory", "impeached"]
        
        for indicator in credibility_positive:
            if indicator in facts:
                features["witness_credibility"] += 0.1
        
        for indicator in credibility_negative:
            if indicator in facts:
                features["witness_credibility"] -= 0.1
        
        # Ensure witness credibility is within bounds
        features["witness_credibility"] = max(0.1, min(1.0, features["witness_credibility"]))
        
        return {"witness": features}
    
    def extract_procedural_strategic_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features related to procedural and strategic aspects of the case.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Dictionary of procedural and strategic features
        """
        features = {}
        
        # Extract procedural posture features
        features.update(self.extract_procedural_posture(case_data))
        
        # Extract motion practice features
        features.update(self.extract_motion_practice(case_data))
        
        # Extract settlement history features
        features.update(self.extract_settlement_history(case_data))
        
        # Extract alternative dispute resolution features
        features.update(self.extract_adr_features(case_data))
        
        return {"procedural_strategic": features}
    
    def extract_procedural_posture(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract procedural posture features."""
        features = {
            "stage": "pre_filing",  # Default assumption
            "trial_readiness": 0.0,
            "procedural_advantage": 0.0  # 0 = neutral, positive = plaintiff advantage, negative = defendant advantage
        }
        
        # Determine case stage based on available information
        if case_data.get("date_filed"):
            features["stage"] = "post_filing"
            
            # Analyze facts for procedural information
            facts = case_data.get("facts", "").lower()
            
            # Check for stage indicators
            if "discovery" in facts:
                features["stage"] = "discovery"
                features["trial_readiness"] = 0.3
            elif "deposition" in facts:
                features["stage"] = "discovery"
                features["trial_readiness"] = 0.4
            elif "motion" in facts and "summary judgment" in facts:
                features["stage"] = "dispositive_motions"
                features["trial_readiness"] = 0.6
            elif "pretrial" in facts:
                features["stage"] = "pretrial"
                features["trial_readiness"] = 0.8
            elif "trial" in facts:
                features["stage"] = "trial"
                features["trial_readiness"] = 1.0
            
            # Calculate procedural advantage
            if features["stage"] == "discovery":
                # Check for discovery advantages
                if "plaintiff favorable" in facts or "defendant unfavorable" in facts:
                    features["procedural_advantage"] += 0.2
                if "plaintiff unfavorable" in facts or "defendant favorable" in facts:
                    features["procedural_advantage"] -= 0.2
            
            if features["stage"] == "dispositive_motions":
                # Check for motion advantages
                if "motion denied" in facts and "defendant" in facts:
                    features["procedural_advantage"] += 0.3
                if "motion granted" in facts and "defendant" in facts:
                    features["procedural_advantage"] -= 0.3
        
        return {"procedural_posture": features}
    
    def extract_motion_practice(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract motion practice features."""
        features = {
            "pending_motions": False,
            "dispositive_motion_risk": 0.0,
            "motion_outcome_prediction": 0.0  # 0-1 scale, higher means more favorable to plaintiff
        }
        
        # Analyze facts for motion information
        facts = case_data.get("facts", "").lower()
        
        # Check for pending motions
        if "pending motion" in facts or "filed motion" in facts:
            features["pending_motions"] = True
        
        # Check for dispositive motion risk
        dispositive_indicators = ["summary judgment", "dismiss", "judgment on the pleadings"]
        for indicator in dispositive_indicators:
            if indicator in facts:
                features["dispositive_motion_risk"] = 0.7
                break
        
        # Predict motion outcome if motions are pending
        if features["pending_motions"]:
            # Default to neutral prediction
            features["motion_outcome_prediction"] = 0.5
            
            # Adjust based on case strength
            evidence_features = self.extract_evidence_based_features(case_data)
            evidence_strength = evidence_features["evidence_based"]["evidence_strength"]["overall_strength"]
            
            # Strong evidence favors the party with the burden
            if "plaintiff motion" in facts:
                features["motion_outcome_prediction"] = evidence_strength
            elif "defendant motion" in facts:
                features["motion_outcome_prediction"] = 1.0 - evidence_strength
        
        return {"motion_practice": features}
    
    def extract_settlement_history(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract settlement history features."""
        features = {
            "prior_negotiations": False,
            "last_demand": None,
            "last_offer": None,
            "negotiation_gap": None
        }
        
        # Analyze facts for settlement information
        facts = case_data.get("facts", "").lower()
        
        # Check for prior negotiations
        if "settlement" in facts or "negotiation" in facts or "demand" in facts or "offer" in facts:
            features["prior_negotiations"] = True
        
        # Extract last demand and offer if available
        demand_pattern = r"demand.*?\$([0-9,]+)"
        offer_pattern = r"offer.*?\$([0-9,]+)"
        
        demand_match = re.search(demand_pattern, facts)
        if demand_match:
            try:
                features["last_demand"] = float(demand_match.group(1).replace(",", ""))
            except ValueError:
                pass
        
        offer_match = re.search(offer_pattern, facts)
        if offer_match:
            try:
                features["last_offer"] = float(offer_match.group(1).replace(",", ""))
            except ValueError:
                pass
        
        # Calculate negotiation gap if both values are available
        if features["last_demand"] is not None and features["last_offer"] is not None:
            features["negotiation_gap"] = features["last_demand"] - features["last_offer"]
        
        return {"settlement_history": features}
    
    def extract_adr_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract alternative dispute resolution features."""
        features = {
            "adr_suitability": 0.5,  # Default to average
            "mediation_attempted": False,
            "arbitration_clause": False
        }
        
        # Analyze facts for ADR information
        facts = case_data.get("facts", "").lower()
        
        # Check for ADR indicators
        if "mediation" in facts:
            features["mediation_attempted"] = True
        
        if "arbitration clause" in facts or "arbitration agreement" in facts:
            features["arbitration_clause"] = True
            features["adr_suitability"] = 0.9
        
        # Calculate ADR suitability
        case_type_features = self.extract_case_type_features(case_data)
        primary_type = case_type_features["case_type"]["primary_type"]
        
        # Adjust suitability based on case type
        if primary_type == "contract_dispute":
            features["adr_suitability"] += 0.2
        elif primary_type == "employment":
            features["adr_suitability"] += 0.1
        
        # Adjust based on relationship features
        relationship_features = self.extract_relationship_features(case_data)
        if relationship_features["relationship"]["ongoing_relationship"]:
            features["adr_suitability"] += 0.2
        
        # Ensure ADR suitability is within bounds
        features["adr_suitability"] = max(0.1, min(1.0, features["adr_suitability"]))
        
        return {"adr": features}
    
    def create_composite_features(self, features: Dict[str, Any], case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create composite features by combining individual features.
        
        Args:
            features: Dictionary of already extracted features
            case_data: Dictionary containing case information
            
        Returns:
            Dictionary of composite features
        """
        composite = {}
        
        # Create settlement pressure index
        composite.update(self.create_settlement_pressure_index(features, case_data))
        
        # Create case strength ratio
        composite.update(self.create_case_strength_ratio(features, case_data))
        
        # Create litigation risk profile
        composite.update(self.create_litigation_risk_profile(features, case_data))
        
        return {"composite": composite}
    
    def create_settlement_pressure_index(self, features: Dict[str, Any], case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create settlement pressure index composite feature."""
        # Initialize with default values
        pressure_index = 5.0  # Default to medium pressure
        pressure_factors = {}
        
        try:
            # Time pressure factors
            time_pressure = 5.0
            
            # Check temporal features
            if "case_characteristics" in features and "temporal" in features["case_characteristics"]:
                temporal = features["case_characteristics"]["temporal"]
                
                # Trial proximity pressure
                if temporal.get("time_to_trial_estimate") is not None:
                    if temporal["time_to_trial_estimate"] < 1:
                        time_pressure += 3.0
                    elif temporal["time_to_trial_estimate"] < 3:
                        time_pressure += 2.0
                    elif temporal["time_to_trial_estimate"] < 6:
                        time_pressure += 1.0
                
                # Statute of limitations pressure
                if temporal.get("statute_of_limitations_risk") == "high":
                    time_pressure += 3.0
                elif temporal.get("statute_of_limitations_risk") == "medium":
                    time_pressure += 1.5
            
            pressure_factors["time_pressure"] = min(10.0, time_pressure) / 10.0
            
            # Financial pressure factors
            financial_pressure = 5.0
            
            # Check damage features
            if "case_characteristics" in features and "damages" in features["case_characteristics"]:
                damages = features["case_characteristics"]["damages"]
                
                # High damages create more pressure
                if damages.get("total_estimated_damages", 0) > 1000000:
                    financial_pressure += 3.0
                elif damages.get("total_estimated_damages", 0) > 500000:
                    financial_pressure += 2.0
                elif damages.get("total_estimated_damages", 0) > 100000:
                    financial_pressure += 1.0
            
            # Check defendant features
            if "party_specific" in features and "defendant" in features["party_specific"]:
                defendant = features["party_specific"]["defendant"]
                
                # Insurance involvement reduces financial pressure
                if defendant.get("insurance_involved", False):
                    financial_pressure -= 1.0
                
                # Deep pockets reduce financial pressure
                if defendant.get("deep_pockets", 0) > 0.7:
                    financial_pressure -= 1.0
            
            pressure_factors["financial_pressure"] = min(10.0, financial_pressure) / 10.0
            
            # Reputational risk factors
            reputation_pressure = 5.0
            
            # Check defendant features for PR risk
            if "party_specific" in features and "defendant" in features["party_specific"]:
                defendant = features["party_specific"]["defendant"]
                
                # High PR risk increases pressure
                pr_risk = defendant.get("public_relations_risk", 0)
                reputation_pressure += pr_risk * 5.0
            
            pressure_factors["reputation_pressure"] = min(10.0, reputation_pressure) / 10.0
            
            # Precedent-setting concerns
            precedent_pressure = 5.0
            
            # Check case type features
            if "case_characteristics" in features and "case_type" in features["case_characteristics"]:
                case_type = features["case_characteristics"]["case_type"]
                
                # Novel or complex cases have higher precedent concerns
                if case_type.get("complexity") == "novel":
                    precedent_pressure += 3.0
                elif case_type.get("complexity") == "complex":
                    precedent_pressure += 1.5
            
            pressure_factors["precedent_pressure"] = min(10.0, precedent_pressure) / 10.0
            
            # Calculate overall pressure index (1-10 scale)
            pressure_index = (
                pressure_factors["time_pressure"] * 3.0 +
                pressure_factors["financial_pressure"] * 3.0 +
                pressure_factors["reputation_pressure"] * 2.0 +
                pressure_factors["precedent_pressure"] * 2.0
            ) / 10.0 * 10.0
            
        except Exception as e:
            print(f"Error creating settlement pressure index: {e}")
            # Return default values if an error occurs
        
        return {
            "settlement_pressure_index": {
                "overall_index": min(10.0, pressure_index),
                "factors": pressure_factors
            }
        }
    
    def create_case_strength_ratio(self, features: Dict[str, Any], case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create case strength ratio composite feature."""
        # Initialize with default values
        plaintiff_strength = 5.0
        defendant_strength = 5.0
        strength_factors = {}
        
        try:
            # Evidence strength factor
            if "evidence_based" in features and "evidence_strength" in features["evidence_based"]:
                evidence_strength = features["evidence_based"]["evidence_strength"]["overall_strength"]
                plaintiff_strength += (evidence_strength - 0.5) * 6.0
                defendant_strength -= (evidence_strength - 0.5) * 6.0
                
                strength_factors["evidence_strength"] = evidence_strength
            
            # Expert opinion factor
            if "evidence_based" in features and "expert_opinion" in features["evidence_based"]:
                expert_advantage = features["evidence_based"]["expert_opinion"]["expert_advantage"]
                plaintiff_strength += expert_advantage * 4.0
                defendant_strength -= expert_advantage * 4.0
                
                strength_factors["expert_advantage"] = expert_advantage
            
            # Witness credibility factor
            if "evidence_based" in features and "witness" in features["evidence_based"]:
                witness_credibility = features["evidence_based"]["witness"]["witness_credibility"]
                plaintiff_strength += (witness_credibility - 0.5) * 4.0
                defendant_strength -= (witness_credibility - 0.5) * 4.0
                
                strength_factors["witness_credibility"] = witness_credibility
            
            # Procedural advantage factor
            if "procedural_strategic" in features and "procedural_posture" in features["procedural_strategic"]:
                procedural_advantage = features["procedural_strategic"]["procedural_posture"]["procedural_advantage"]
                plaintiff_strength += procedural_advantage * 3.0
                defendant_strength -= procedural_advantage * 3.0
                
                strength_factors["procedural_advantage"] = procedural_advantage
            
            # Representation strength factor
            if "party_specific" in features and "attorney" in features["party_specific"]:
                representation_asymmetry = features["party_specific"]["attorney"]["representation_asymmetry"]
                plaintiff_strength += representation_asymmetry * 2.0
                defendant_strength -= representation_asymmetry * 2.0
                
                strength_factors["representation_asymmetry"] = representation_asymmetry
            
            # Ensure strengths are within bounds
            plaintiff_strength = max(1.0, min(10.0, plaintiff_strength))
            defendant_strength = max(1.0, min(10.0, defendant_strength))
            
            # Calculate strength ratio
            strength_ratio = plaintiff_strength / defendant_strength if defendant_strength > 0 else 10.0
            
        except Exception as e:
            print(f"Error creating case strength ratio: {e}")
            # Return default values if an error occurs
            plaintiff_strength = 5.0
            defendant_strength = 5.0
            strength_ratio = 1.0
        
        return {
            "case_strength_ratio": {
                "plaintiff_strength": plaintiff_strength,
                "defendant_strength": defendant_strength,
                "strength_ratio": strength_ratio,
                "factors": strength_factors
            }
        }
    
    def create_litigation_risk_profile(self, features: Dict[str, Any], case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create litigation risk profile composite feature."""
        # Initialize with default values
        risk_profile = {
            "outcome_uncertainty": "medium",  # high, medium, low
            "damage_range_width": "medium",   # wide, medium, narrow
            "precedential_impact": "limited", # significant, moderate, limited
            "cost_benefit_alignment": "neutral" # favorable, neutral, unfavorable
        }
        
        try:
            # Determine outcome uncertainty
            uncertainty_score = 0.5  # Default to medium
            
            # Evidence strength affects uncertainty
            if "evidence_based" in features and "evidence_strength" in features["evidence_based"]:
                evidence_strength = features["evidence_based"]["evidence_strength"]["overall_strength"]
                if evidence_strength > 0.8:
                    uncertainty_score -= 0.3
                elif evidence_strength < 0.3:
                    uncertainty_score += 0.3
            
            # Case complexity affects uncertainty
            if "case_characteristics" in features and "case_type" in features["case_characteristics"]:
                complexity = features["case_characteristics"]["case_type"].get("complexity", "standard")
                if complexity == "novel":
                    uncertainty_score += 0.3
                elif complexity == "complex":
                    uncertainty_score += 0.2
            
            # Set outcome uncertainty category
            if uncertainty_score > 0.7:
                risk_profile["outcome_uncertainty"] = "high"
            elif uncertainty_score < 0.3:
                risk_profile["outcome_uncertainty"] = "low"
            
            # Determine damage range width
            if "case_characteristics" in features and "damages" in features["case_characteristics"]:
                damages = features["case_characteristics"]["damages"]
                economic = damages.get("economic_damages", 0)
                non_economic = damages.get("estimated_non_economic_damages", 0)
                
                # High non-economic to economic ratio indicates wider range
                if economic > 0:
                    ratio = non_economic / economic
                    if ratio > 3:
                        risk_profile["damage_range_width"] = "wide"
                    elif ratio < 1:
                        risk_profile["damage_range_width"] = "narrow"
            
            # Determine precedential impact
            if "case_characteristics" in features and "case_type" in features["case_characteristics"]:
                complexity = features["case_characteristics"]["case_type"].get("complexity", "standard")
                if complexity == "novel":
                    risk_profile["precedential_impact"] = "significant"
                elif complexity == "complex":
                    risk_profile["precedential_impact"] = "moderate"
            
            # Determine cost-benefit alignment
            if "composite" in features and "settlement_pressure_index" in features["composite"]:
                pressure = features["composite"]["settlement_pressure_index"]["overall_index"]
                
                if "composite" in features and "case_strength_ratio" in features["composite"]:
                    strength_ratio = features["composite"]["case_strength_ratio"]["strength_ratio"]
                    
                    # High pressure and favorable strength ratio indicates good cost-benefit
                    if pressure > 7 and strength_ratio > 1.5:
                        risk_profile["cost_benefit_alignment"] = "favorable"
                    # High pressure and unfavorable strength ratio indicates poor cost-benefit
                    elif pressure > 7 and strength_ratio < 0.7:
                        risk_profile["cost_benefit_alignment"] = "unfavorable"
            
        except Exception as e:
            print(f"Error creating litigation risk profile: {e}")
            # Return default values if an error occurs
        
        return {"litigation_risk_profile": risk_profile}
    
    def format_features_for_prompt(self, features: Dict[str, Any]) -> str:
        """
        Format extracted features for inclusion in an OpenAI prompt.
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Formatted string representation of features
        """
        formatted = "## CASE FEATURES\n\n"
        
        # Format case characteristics
        if "case_characteristics" in features:
            formatted += "### Case Characteristics\n\n"
            
            # Jurisdiction
            if "jurisdiction" in features["case_characteristics"]:
                jurisdiction = features["case_characteristics"]["jurisdiction"]
                formatted += "**Jurisdiction Analysis:**\n"
                formatted += f"- Jurisdiction: {jurisdiction['jurisdiction'].title()}\n"
                formatted += f"- Venue Type: {jurisdiction['venue_type'].replace('_', ' ').title()}\n"
                
                # Add jurisdiction data if available
                jur_data = jurisdiction.get("jurisdiction_data", {})
                if jur_data:
                    if "avg_settlement" in jur_data:
                        formatted += f"- Average Settlement: ${jur_data['avg_settlement']:,}\n"
                    if "jury_favorability" in jur_data:
                        formatted += f"- Jury Favorability: {jur_data['jury_favorability']:.2f} (0-1 scale)\n"
                    if "damage_caps" in jur_data and jur_data["damage_caps"]:
                        formatted += "- Damage Caps: "
                        caps = [f"{k.replace('_', ' ').title()}: ${v:,}" for k, v in jur_data["damage_caps"].items()]
                        formatted += ", ".join(caps) + "\n"
                
                formatted += "\n"
            
            # Case type
            if "case_type" in features["case_characteristics"]:
                case_type = features["case_characteristics"]["case_type"]
                formatted += "**Case Classification:**\n"
                formatted += f"- Primary Type: {case_type['primary_type'].replace('_', ' ').title()}\n"
                formatted += f"- Subtype: {case_type['subtype'].replace('_', ' ').title()}\n"
                formatted += f"- Complexity: {case_type['complexity'].title()}\n"
                
                # Add case type data if available
                type_data = case_type.get("type_data", {})
                if type_data:
                    if "avg_duration" in type_data:
                        formatted += f"- Average Duration: {type_data['avg_duration']} months\n"
                    if "settlement_rate" in type_data:
                        formatted += f"- Settlement Rate: {type_data['settlement_rate']:.2f} (0-1 scale)\n"
                
                formatted += "\n"
            
            # Temporal features
            if "temporal" in features["case_characteristics"]:
                temporal = features["case_characteristics"]["temporal"]
                formatted += "**Temporal Analysis:**\n"
                if temporal.get("days_since_filing") is not None:
                    formatted += f"- Days Since Filing: {temporal['days_since_filing']}\n"
                if temporal.get("time_to_trial_estimate") is not None:
                    formatted += f"- Estimated Time to Trial: {temporal['time_to_trial_estimate']:.1f} months\n"
                if temporal.get("statute_of_limitations_risk") != "unknown":
                    formatted += f"- Statute of Limitations Risk: {temporal['statute_of_limitations_risk'].title()}\n"
                
                formatted += "\n"
            
            # Damage features
            if "damages" in features["case_characteristics"]:
                damages = features["case_characteristics"]["damages"]
                formatted += "**Damage Analysis:**\n"
                formatted += f"- Economic Damages: ${damages['economic_damages']:,.2f}\n"
                formatted += f"- Estimated Non-Economic Damages: ${damages['estimated_non_economic_damages']:,.2f}\n"
                formatted += f"- Total Estimated Damages: ${damages['total_estimated_damages']:,.2f}\n"
                formatted += f"- Damage Multiplier: {damages['damage_multiplier']:.2f}x\n"
                
                formatted += "\n"
        
        # Format party-specific features
        if "party_specific" in features:
            formatted += "### Party-Specific Factors\n\n"
            
            # Plaintiff features
            if "plaintiff" in features["party_specific"]:
                plaintiff = features["party_specific"]["plaintiff"]
                formatted += "**Plaintiff Analysis:**\n"
                formatted += f"- Type: {plaintiff['type'].title()}\n"
                formatted += f"- Sympathetic Factors: {plaintiff['sympathetic_factors']:.2f} (0-1 scale)\n"
                formatted += f"- Credibility Factors: {plaintiff['credibility_factors']:.2f} (0-1 scale)\n"
                
                formatted += "\n"
            
            # Defendant features
            if "defendant" in features["party_specific"]:
                defendant = features["party_specific"]["defendant"]
                formatted += "**Defendant Analysis:**\n"
                formatted += f"- Type: {defendant['type'].title()}\n"
                formatted += f"- Insurance Involved: {'Yes' if defendant['insurance_involved'] else 'No'}\n"
                formatted += f"- Deep Pockets Factor: {defendant['deep_pockets']:.2f} (0-1 scale)\n"
                formatted += f"- Public Relations Risk: {defendant['public_relations_risk']:.2f} (0-1 scale)\n"
                
                formatted += "\n"
            
            # Attorney features
            if "attorney" in features["party_specific"]:
                attorney = features["party_specific"]["attorney"]
                formatted += "**Legal Representation Analysis:**\n"
                formatted += f"- Plaintiff Representation Strength: {attorney['plaintiff_representation_strength']:.2f} (0-1 scale)\n"
                formatted += f"- Defendant Representation Strength: {attorney['defendant_representation_strength']:.2f} (0-1 scale)\n"
                formatted += f"- Representation Asymmetry: {attorney['representation_asymmetry']:.2f} (positive favors plaintiff)\n"
                
                formatted += "\n"
            
            # Relationship features
            if "relationship" in features["party_specific"]:
                relationship = features["party_specific"]["relationship"]
                formatted += "**Party Relationship Analysis:**\n"
                formatted += f"- Relationship Type: {relationship['relationship_type'].replace('_', ' ').title()}\n"
                formatted += f"- Ongoing Relationship: {'Yes' if relationship['ongoing_relationship'] else 'No'}\n"
                formatted += f"- Power Dynamic: {relationship['power_dynamic']:.2f} (positive favors plaintiff)\n"
                
                formatted += "\n"
        
        # Format evidence-based features
        if "evidence_based" in features:
            formatted += "### Evidence-Based Factors\n\n"
            
            # Evidence strength
            if "evidence_strength" in features["evidence_based"]:
                evidence = features["evidence_based"]["evidence_strength"]
                formatted += "**Evidence Strength Assessment:**\n"
                formatted += f"- Overall Strength: {evidence['overall_strength']:.2f} (0-1 scale)\n"
                
                if evidence["key_evidence_types"]:
                    formatted += "- Key Evidence Types: " + ", ".join(t.replace("_", " ").title() for t in evidence["key_evidence_types"]) + "\n"
                
                if evidence["evidence_gaps"]:
                    formatted += "- Evidence Gaps: " + ", ".join(g.replace("_", " ").title() for g in evidence["evidence_gaps"]) + "\n"
                
                formatted += "\n"
            
            # Expert opinion
            if "expert_opinion" in features["evidence_based"]:
                expert = features["evidence_based"]["expert_opinion"]
                formatted += "**Expert Opinion Analysis:**\n"
                formatted += f"- Plaintiff Expert Strength: {expert['plaintiff_expert_strength']:.2f} (0-1 scale)\n"
                formatted += f"- Defendant Expert Strength: {expert['defendant_expert_strength']:.2f} (0-1 scale)\n"
                formatted += f"- Expert Advantage: {expert['expert_advantage']:.2f} (positive favors plaintiff)\n"
                
                formatted += "\n"
            
            # Documentary evidence
            if "documentary_evidence" in features["evidence_based"]:
                documentary = features["evidence_based"]["documentary_evidence"]
                formatted += "**Documentary Evidence Analysis:**\n"
                formatted += f"- Documentary Evidence Strength: {documentary['documentary_evidence_strength']:.2f} (0-1 scale)\n"
                
                if documentary["key_document_types"]:
                    formatted += "- Key Document Types: " + ", ".join(t.replace("_", " ").title() for t in documentary["key_document_types"]) + "\n"
                
                formatted += "\n"
            
            # Witness features
            if "witness" in features["evidence_based"]:
                witness = features["evidence_based"]["witness"]
                formatted += "**Witness Credibility Analysis:**\n"
                formatted += f"- Witness Credibility: {witness['witness_credibility']:.2f} (0-1 scale)\n"
                
                if witness["witness_types"]:
                    formatted += "- Witness Types: " + ", ".join(t.replace("_", " ").title() for t in witness["witness_types"]) + "\n"
                
                formatted += "\n"
        
        # Format procedural and strategic features
        if "procedural_strategic" in features:
            formatted += "### Procedural and Strategic Factors\n\n"
            
            # Procedural posture
            if "procedural_posture" in features["procedural_strategic"]:
                posture = features["procedural_strategic"]["procedural_posture"]
                formatted += "**Procedural Posture Analysis:**\n"
                formatted += f"- Current Stage: {posture['stage'].replace('_', ' ').title()}\n"
                formatted += f"- Trial Readiness: {posture['trial_readiness']:.2f} (0-1 scale)\n"
                formatted += f"- Procedural Advantage: {posture['procedural_advantage']:.2f} (positive favors plaintiff)\n"
                
                formatted += "\n"
            
            # Motion practice
            if "motion_practice" in features["procedural_strategic"]:
                motion = features["procedural_strategic"]["motion_practice"]
                formatted += "**Motion Practice Analysis:**\n"
                formatted += f"- Pending Motions: {'Yes' if motion['pending_motions'] else 'No'}\n"
                formatted += f"- Dispositive Motion Risk: {motion['dispositive_motion_risk']:.2f} (0-1 scale)\n"
                formatted += f"- Motion Outcome Prediction: {motion['motion_outcome_prediction']:.2f} (higher favors plaintiff)\n"
                
                formatted += "\n"
            
            # Settlement history
            if "settlement_history" in features["procedural_strategic"]:
                settlement = features["procedural_strategic"]["settlement_history"]
                formatted += "**Settlement History Analysis:**\n"
                formatted += f"- Prior Negotiations: {'Yes' if settlement['prior_negotiations'] else 'No'}\n"
                
                if settlement["last_demand"] is not None:
                    formatted += f"- Last Demand: ${settlement['last_demand']:,.2f}\n"
                
                if settlement["last_offer"] is not None:
                    formatted += f"- Last Offer: ${settlement['last_offer']:,.2f}\n"
                
                if settlement["negotiation_gap"] is not None:
                    formatted += f"- Negotiation Gap: ${settlement['negotiation_gap']:,.2f}\n"
                
                formatted += "\n"
            
            # ADR features
            if "adr" in features["procedural_strategic"]:
                adr = features["procedural_strategic"]["adr"]
                formatted += "**Alternative Dispute Resolution Analysis:**\n"
                formatted += f"- ADR Suitability: {adr['adr_suitability']:.2f} (0-1 scale)\n"
                formatted += f"- Mediation Attempted: {'Yes' if adr['mediation_attempted'] else 'No'}\n"
                formatted += f"- Arbitration Clause: {'Yes' if adr['arbitration_clause'] else 'No'}\n"
                
                formatted += "\n"
        
        # Format composite features
        if "composite" in features:
            formatted += "### Composite Strategic Indicators\n\n"
            
            # Settlement pressure index
            if "settlement_pressure_index" in features["composite"]:
                pressure = features["composite"]["settlement_pressure_index"]
                formatted += "**Settlement Pressure Index:**\n"
                formatted += f"- Overall Pressure Index: {pressure['overall_index']:.1f} (1-10 scale)\n"
                
                if "factors" in pressure:
                    factors = pressure["factors"]
                    formatted += "- Component Factors:\n"
                    for name, value in factors.items():
                        formatted += f"  * {name.replace('_', ' ').title()}: {value:.2f} (0-1 scale)\n"
                
                formatted += "\n"
            
            # Case strength ratio
            if "case_strength_ratio" in features["composite"]:
                strength = features["composite"]["case_strength_ratio"]
                formatted += "**Case Strength Analysis:**\n"
                formatted += f"- Plaintiff Case Strength: {strength['plaintiff_strength']:.1f} (1-10 scale)\n"
                formatted += f"- Defendant Case Strength: {strength['defendant_strength']:.1f} (1-10 scale)\n"
                formatted += f"- Strength Ratio (P/D): {strength['strength_ratio']:.2f}\n"
                
                if "factors" in strength:
                    factors = strength["factors"]
                    formatted += "- Key Strength Factors:\n"
                    for name, value in factors.items():
                        formatted += f"  * {name.replace('_', ' ').title()}: {value:.2f}\n"
                
                formatted += "\n"
            
            # Litigation risk profile
            if "litigation_risk_profile" in features["composite"]:
                risk = features["composite"]["litigation_risk_profile"]
                formatted += "**Litigation Risk Profile:**\n"
                formatted += f"- Outcome Uncertainty: {risk['outcome_uncertainty'].title()}\n"
                formatted += f"- Damage Range Width: {risk['damage_range_width'].title()}\n"
                formatted += f"- Precedential Impact: {risk['precedential_impact'].title()}\n"
                formatted += f"- Cost-Benefit Alignment: {risk['cost_benefit_alignment'].title()}\n"
                
                formatted += "\n"
        
        return formatted
