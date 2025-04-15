"""
Confidence Scoring Mechanism for SaaS Case Analysis Application

This module implements a comprehensive confidence scoring system for legal settlement
predictions. It provides multi-dimensional confidence assessment, statistical confidence
intervals, and Bayesian confidence updating to enhance the reliability and explainability
of settlement predictions.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import math
import json
from scipy import stats

class ConfidenceScorer:
    """
    Implements various confidence scoring mechanisms for legal settlement predictions.
    Provides multi-dimensional confidence assessment, statistical confidence intervals,
    and Bayesian confidence updating.
    """
    
    def __init__(self):
        """Initialize the confidence scorer with necessary resources."""
        # Default dimension weights for different case types
        self.default_dimension_weights = {
            "personal_injury": {
                "evidential_confidence": 0.25,
                "methodological_confidence": 0.15,
                "precedential_confidence": 0.20,
                "data_adequacy_confidence": 0.25,
                "stability_confidence": 0.15
            },
            "contract_dispute": {
                "evidential_confidence": 0.20,
                "methodological_confidence": 0.15,
                "precedential_confidence": 0.25,
                "data_adequacy_confidence": 0.20,
                "stability_confidence": 0.20
            },
            "employment": {
                "evidential_confidence": 0.20,
                "methodological_confidence": 0.15,
                "precedential_confidence": 0.25,
                "data_adequacy_confidence": 0.20,
                "stability_confidence": 0.20
            },
            "default": {
                "evidential_confidence": 0.20,
                "methodological_confidence": 0.20,
                "precedential_confidence": 0.20,
                "data_adequacy_confidence": 0.20,
                "stability_confidence": 0.20
            }
        }
        
        # Confidence level classifications
        self.confidence_classifications = {
            (9, 10): "Very High Confidence",
            (7, 8): "High Confidence",
            (5, 6): "Moderate Confidence",
            (3, 4): "Low Confidence",
            (1, 2): "Very Low Confidence"
        }
    
    def calculate_multi_dimensional_confidence(self, 
                                              case_data: Dict[str, Any], 
                                              extracted_features: Dict[str, Any],
                                              dimension_scores: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate multi-dimensional confidence scores for a case prediction.
        
        Args:
            case_data: Dictionary containing case information
            extracted_features: Dictionary of extracted features
            dimension_scores: Optional dictionary of pre-calculated dimension scores
            
        Returns:
            Dictionary containing confidence assessment results
        """
        # Determine case type for appropriate weighting
        case_type = "default"
        if "case_characteristics" in extracted_features and "case_type" in extracted_features["case_characteristics"]:
            case_type = extracted_features["case_characteristics"]["case_type"]["primary_type"]
            if case_type not in self.default_dimension_weights:
                case_type = "default"
        
        # Use provided dimension scores or calculate default ones
        if dimension_scores is None:
            dimension_scores = self._calculate_default_dimension_scores(case_data, extracted_features)
        
        # Get appropriate dimension weights
        dimension_weights = self.default_dimension_weights[case_type]
        
        # Calculate weighted average
        weighted_sum = 0
        for dimension, score in dimension_scores.items():
            if dimension in dimension_weights:
                weighted_sum += score * dimension_weights[dimension]
        
        # Calculate overall confidence score (1-10 scale)
        overall_score = min(10, max(1, weighted_sum * 10))
        
        # Determine confidence classification
        confidence_classification = "Unknown"
        for score_range, classification in self.confidence_classifications.items():
            if score_range[0] <= overall_score <= score_range[1]:
                confidence_classification = classification
                break
        
        # Generate improvement recommendations
        improvement_recommendations = {}
        for dimension, score in dimension_scores.items():
            if score < 0.7:  # Only provide recommendations for dimensions below 0.7
                improvement_recommendations[dimension] = self._generate_improvement_recommendations(
                    dimension, score, case_data, extracted_features
                )
        
        # Compile results
        results = {
            "dimension_scores": dimension_scores,
            "dimension_weights": dimension_weights,
            "overall_confidence_score": overall_score,
            "confidence_classification": confidence_classification,
            "improvement_recommendations": improvement_recommendations
        }
        
        return results
    
    def _calculate_default_dimension_scores(self, case_data: Dict[str, Any], 
                                           extracted_features: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate default dimension scores based on case data and extracted features.
        
        Args:
            case_data: Dictionary containing case information
            extracted_features: Dictionary of extracted features
            
        Returns:
            Dictionary of dimension scores (0-1 scale)
        """
        dimension_scores = {
            "evidential_confidence": 0.5,  # Default to medium confidence
            "methodological_confidence": 0.5,
            "precedential_confidence": 0.5,
            "data_adequacy_confidence": 0.5,
            "stability_confidence": 0.5
        }
        
        # Calculate evidential confidence
        if "evidence_based" in extracted_features:
            evidence_features = extracted_features["evidence_based"]
            
            # Start with base score
            evidential_score = 0.5
            
            # Adjust based on evidence strength
            if "evidence_strength" in evidence_features:
                strength = evidence_features["evidence_strength"].get("overall_strength", 0.5)
                evidential_score = strength
            
            # Adjust based on evidence gaps
            if "evidence_strength" in evidence_features and "evidence_gaps" in evidence_features["evidence_strength"]:
                gaps = evidence_features["evidence_strength"]["evidence_gaps"]
                evidential_score -= len(gaps) * 0.05  # Reduce score for each gap
            
            # Adjust based on witness credibility
            if "witness" in evidence_features:
                witness_credibility = evidence_features["witness"].get("witness_credibility", 0.5)
                evidential_score = (evidential_score + witness_credibility) / 2
            
            # Adjust based on expert opinions
            if "expert_opinion" in evidence_features:
                expert_strength = max(
                    evidence_features["expert_opinion"].get("plaintiff_expert_strength", 0),
                    evidence_features["expert_opinion"].get("defendant_expert_strength", 0)
                )
                evidential_score = (evidential_score + expert_strength) / 2
            
            # Ensure score is within bounds
            dimension_scores["evidential_confidence"] = max(0.1, min(1.0, evidential_score))
        
        # Calculate methodological confidence
        # This is more about the confidence in our analytical approach
        methodological_score = 0.7  # Start with relatively high confidence in our method
        
        # Adjust based on case type - more common case types have better validated methods
        if "case_characteristics" in extracted_features and "case_type" in extracted_features["case_characteristics"]:
            case_type = extracted_features["case_characteristics"]["case_type"]
            
            # Common case types have higher methodological confidence
            if case_type["primary_type"] in ["personal_injury", "contract_dispute", "employment"]:
                methodological_score += 0.1
            
            # Complex or novel cases have lower methodological confidence
            if case_type.get("complexity") == "novel":
                methodological_score -= 0.2
            elif case_type.get("complexity") == "complex":
                methodological_score -= 0.1
        
        # Ensure score is within bounds
        dimension_scores["methodological_confidence"] = max(0.1, min(1.0, methodological_score))
        
        # Calculate precedential confidence
        precedential_score = 0.5  # Default to medium confidence
        
        # Adjust based on similar cases if available
        if "similar_cases" in case_data and case_data["similar_cases"]:
            similar_cases = case_data["similar_cases"]
            
            # More similar cases increase precedential confidence
            if len(similar_cases) >= 3:
                precedential_score += 0.2
            elif len(similar_cases) >= 1:
                precedential_score += 0.1
            
            # High similarity scores increase precedential confidence
            avg_similarity = sum(case.get("similarity", 0) for case in similar_cases) / len(similar_cases)
            precedential_score += avg_similarity * 0.3
        else:
            # No similar cases reduces precedential confidence
            precedential_score -= 0.2
        
        # Adjust based on jurisdiction data
        if "case_characteristics" in extracted_features and "jurisdiction" in extracted_features["case_characteristics"]:
            jurisdiction = extracted_features["case_characteristics"]["jurisdiction"]
            
            # Having jurisdiction data increases precedential confidence
            if jurisdiction.get("jurisdiction") != "unknown" and jurisdiction.get("jurisdiction_data"):
                precedential_score += 0.1
        
        # Ensure score is within bounds
        dimension_scores["precedential_confidence"] = max(0.1, min(1.0, precedential_score))
        
        # Calculate data adequacy confidence
        data_adequacy_score = 0.5  # Default to medium confidence
        
        # Check for missing critical fields
        missing_fields = []
        critical_fields = ["title", "claim_type", "facts", "injury_details", "damages"]
        
        for field in critical_fields:
            if field not in case_data or not case_data[field]:
                missing_fields.append(field)
        
        # Reduce score based on missing critical fields
        data_adequacy_score -= len(missing_fields) * 0.1
        
        # Check for optional but valuable fields
        valuable_fields = ["court", "date_filed", "judge", "plaintiff_medical_expert", "defendant_medical_expert"]
        present_valuable_fields = sum(1 for field in valuable_fields if field in case_data and case_data[field])
        
        # Increase score based on presence of valuable fields
        data_adequacy_score += present_valuable_fields * 0.05
        
        # Check for detailed facts and injury description
        if "facts" in case_data and len(case_data["facts"].split()) > 100:
            data_adequacy_score += 0.1
        
        if "injury_details" in case_data and len(case_data["injury_details"].split()) > 100:
            data_adequacy_score += 0.1
        
        # Ensure score is within bounds
        dimension_scores["data_adequacy_confidence"] = max(0.1, min(1.0, data_adequacy_score))
        
        # Calculate stability confidence
        stability_score = 0.5  # Default to medium confidence
        
        # Composite features can help assess stability
        if "composite" in extracted_features:
            composite = extracted_features["composite"]
            
            # Check litigation risk profile
            if "litigation_risk_profile" in composite:
                risk_profile = composite["litigation_risk_profile"]
                
                # High outcome uncertainty reduces stability confidence
                if risk_profile.get("outcome_uncertainty") == "high":
                    stability_score -= 0.2
                elif risk_profile.get("outcome_uncertainty") == "low":
                    stability_score += 0.2
                
                # Wide damage range reduces stability confidence
                if risk_profile.get("damage_range_width") == "wide":
                    stability_score -= 0.2
                elif risk_profile.get("damage_range_width") == "narrow":
                    stability_score += 0.2
            
            # Check settlement pressure index
            if "settlement_pressure_index" in composite:
                pressure = composite["settlement_pressure_index"]
                
                # Very high or very low pressure can indicate volatility
                overall_index = pressure.get("overall_index", 5.0)
                if overall_index > 8 or overall_index < 2:
                    stability_score -= 0.1
            
            # Check case strength ratio
            if "case_strength_ratio" in composite:
                strength = composite["case_strength_ratio"]
                
                # Extreme strength ratios can indicate more stable predictions
                ratio = strength.get("strength_ratio", 1.0)
                if ratio > 3 or ratio < 0.3:
                    stability_score += 0.1
        
        # Procedural stage affects stability
        if "procedural_strategic" in extracted_features and "procedural_posture" in extracted_features["procedural_strategic"]:
            posture = extracted_features["procedural_strategic"]["procedural_posture"]
            
            # Later stages have more stable predictions
            stage = posture.get("stage", "pre_filing")
            if stage in ["trial", "pretrial"]:
                stability_score += 0.2
            elif stage in ["dispositive_motions", "discovery"]:
                stability_score += 0.1
            elif stage == "pre_filing":
                stability_score -= 0.1
        
        # Ensure score is within bounds
        dimension_scores["stability_confidence"] = max(0.1, min(1.0, stability_score))
        
        return dimension_scores
    
    def _generate_improvement_recommendations(self, dimension: str, score: float, 
                                             case_data: Dict[str, Any], 
                                             extracted_features: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations to improve confidence for a specific dimension.
        
        Args:
            dimension: The confidence dimension to generate recommendations for
            score: The current confidence score for this dimension
            case_data: Dictionary containing case information
            extracted_features: Dictionary of extracted features
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if dimension == "evidential_confidence":
            # Recommendations for improving evidential confidence
            if "evidence_based" in extracted_features and "evidence_strength" in extracted_features["evidence_based"]:
                evidence = extracted_features["evidence_based"]["evidence_strength"]
                
                # Check for evidence gaps
                if "evidence_gaps" in evidence:
                    for gap in evidence["evidence_gaps"]:
                        recommendations.append(f"Address evidence gap: {gap.replace('_', ' ').title()}")
            
            # General recommendations
            recommendations.extend([
                "Obtain additional witness statements to corroborate key facts",
                "Secure documentary evidence supporting damage claims",
                "Consider retaining expert witnesses to strengthen technical aspects",
                "Obtain medical records or treatment documentation if applicable",
                "Gather photographic or video evidence if available"
            ])
            
        elif dimension == "methodological_confidence":
            # Recommendations for improving methodological confidence
            if "case_characteristics" in extracted_features and "case_type" in extracted_features["case_characteristics"]:
                case_type = extracted_features["case_characteristics"]["case_type"]
                
                # Recommendations for complex or novel cases
                if case_type.get("complexity") in ["complex", "novel"]:
                    recommendations.append("Consult with specialists experienced in this specific case type")
                    recommendations.append("Research methodological approaches for similar complex cases")
            
            # General recommendations
            recommendations.extend([
                "Apply multiple analytical frameworks to cross-validate findings",
                "Conduct sensitivity analysis on key assumptions",
                "Review recent literature on settlement valuation methodologies",
                "Consult with colleagues on methodological approach",
                "Document and validate key analytical assumptions"
            ])
            
        elif dimension == "precedential_confidence":
            # Recommendations for improving precedential confidence
            if "similar_cases" not in case_data or not case_data["similar_cases"]:
                recommendations.append("Search for additional similar cases in the jurisdiction")
            
            # General recommendations
            recommendations.extend([
                "Research recent settlements or verdicts in the same jurisdiction",
                "Identify cases with similar fact patterns and damage profiles",
                "Consult specialized legal databases for precedential cases",
                "Review jury verdict reporters for comparable cases",
                "Analyze trends in settlements for this case type over time"
            ])
            
        elif dimension == "data_adequacy_confidence":
            # Recommendations for improving data adequacy confidence
            missing_fields = []
            critical_fields = ["title", "claim_type", "facts", "injury_details", "damages"]
            
            for field in critical_fields:
                if field not in case_data or not case_data[field]:
                    missing_fields.append(field)
            
            for field in missing_fields:
                recommendations.append(f"Provide missing information: {field.replace('_', ' ').title()}")
            
            # Check for detailed facts and injury description
            if "facts" in case_data and len(case_data["facts"].split()) < 100:
                recommendations.append("Provide more detailed description of case facts")
            
            if "injury_details" in case_data and len(case_data["injury_details"].split()) < 100:
                recommendations.append("Provide more detailed description of injuries or damages")
            
            # General recommendations
            recommendations.extend([
                "Obtain complete medical records and treatment history",
                "Gather detailed information about economic damages",
                "Document all aspects of non-economic damages",
                "Collect information about all parties involved",
                "Obtain complete procedural history of the case"
            ])
            
        elif dimension == "stability_confidence":
            # Recommendations for improving stability confidence
            if "composite" in extracted_features and "litigation_risk_profile" in extracted_features["composite"]:
                risk_profile = extracted_features["composite"]["litigation_risk_profile"]
                
                if risk_profile.get("outcome_uncertainty") == "high":
                    recommendations.append("Identify and address key sources of outcome uncertainty")
                
                if risk_profile.get("damage_range_width") == "wide":
                    recommendations.append("Narrow damage estimates through additional documentation")
            
            # General recommendations
            recommendations.extend([
                "Conduct additional scenario analysis to understand prediction sensitivity",
                "Identify and monitor key variables that could change prediction",
                "Establish regular review points to update prediction as case evolves",
                "Document assumptions that could change over time",
                "Develop contingency plans for significant case developments"
            ])
        
        # Return a subset of recommendations (max 3) to avoid overwhelming the user
        if len(recommendations) > 3:
            return recommendations[:3]
        return recommendations
    
    def calculate_statistical_confidence_intervals(self, 
                                                 point_estimate: float,
                                                 extracted_features: Dict[str, Any],
                                                 confidence_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate statistical confidence intervals for a settlement prediction.
        
        Args:
            point_estimate: The most likely settlement value
            extracted_features: Dictionary of extracted features
            confidence_assessment: Results from multi-dimensional confidence assessment
            
        Returns:
            Dictionary containing confidence interval results
        """
        # Determine variance based on confidence assessment and case features
        variance = self._estimate_prediction_variance(point_estimate, extracted_features, confidence_assessment)
        
        # Calculate standard deviation
        std_dev = math.sqrt(variance)
        
        # Determine appropriate distribution
        # For settlement values, we often use log-normal distribution since values can't be negative
        # and are often right-skewed
        distribution = "log-normal"
        distribution_params = {}
        
        if distribution == "log-normal":
            # For log-normal, we need to convert our parameters
            if point_estimate > 0:
                # Calculate mu and sigma for log-normal distribution
                # For log-normal, the mean is exp(mu + sigma^2/2)
                # So mu = log(mean) - sigma^2/2
                
                # First, estimate coefficient of variation (CV) based on confidence
                cv = 1.0 - (confidence_assessment["overall_confidence_score"] / 10.0)
                cv = max(0.1, min(1.0, cv))  # Bound CV between 0.1 and 1.0
                
                # Calculate sigma from CV for log-normal
                sigma = math.sqrt(math.log(1 + cv**2))
                
                # Calculate mu from mean and sigma
                mu = math.log(point_estimate) - (sigma**2 / 2)
                
                distribution_params = {
                    "mu": mu,
                    "sigma": sigma
                }
            else:
                # Fallback to normal distribution if point estimate is not positive
                distribution = "normal"
        
        if distribution == "normal":
            # For normal distribution, we use point estimate as mean and calculated std_dev
            distribution_params = {
                "mean": point_estimate,
                "std_dev": std_dev
            }
        
        # Calculate confidence intervals
        intervals = {}
        
        if distribution == "log-normal" and point_estimate > 0:
            # Calculate percentiles for log-normal distribution
            mu = distribution_params["mu"]
            sigma = distribution_params["sigma"]
            
            # 90% confidence interval (5th to 95th percentile)
            intervals["90%"] = {
                "lower": math.exp(mu + stats.norm.ppf(0.05) * sigma),
                "upper": math.exp(mu + stats.norm.ppf(0.95) * sigma)
            }
            
            # 80% confidence interval (10th to 90th percentile)
            intervals["80%"] = {
                "lower": math.exp(mu + stats.norm.ppf(0.10) * sigma),
                "upper": math.exp(mu + stats.norm.ppf(0.90) * sigma)
            }
            
            # 50% confidence interval (25th to 75th percentile)
            intervals["50%"] = {
                "lower": math.exp(mu + stats.norm.ppf(0.25) * sigma),
                "upper": math.exp(mu + stats.norm.ppf(0.75) * sigma)
            }
            
        else:
            # Calculate percentiles for normal distribution
            mean = distribution_params["mean"]
            std_dev = distribution_params["std_dev"]
            
            # 90% confidence interval (5th to 95th percentile)
            intervals["90%"] = {
                "lower": max(0, mean + stats.norm.ppf(0.05) * std_dev),
                "upper": mean + stats.norm.ppf(0.95) * std_dev
            }
            
            # 80% confidence interval (10th to 90th percentile)
            intervals["80%"] = {
                "lower": max(0, mean + stats.norm.ppf(0.10) * std_dev),
                "upper": mean + stats.norm.ppf(0.90) * std_dev
            }
            
            # 50% confidence interval (25th to 75th percentile)
            intervals["50%"] = {
                "lower": max(0, mean + stats.norm.ppf(0.25) * std_dev),
                "upper": mean + stats.norm.ppf(0.75) * std_dev
            }
        
        # Compile results
        results = {
            "point_estimate": point_estimate,
            "distribution_type": distribution,
            "distribution_parameters": distribution_params,
            "confidence_intervals": intervals,
            "interval_interpretation": self._generate_interval_interpretation(intervals, point_estimate, confidence_assessment)
        }
        
        return results
    
    def _estimate_prediction_variance(self, point_estimate: float, 
                                     extracted_features: Dict[str, Any],
                                     confidence_assessment: Dict[str, Any]) -> float:
        """
        Estimate the variance of the prediction based on case features and confidence assessment.
        
        Args:
            point_estimate: The most likely settlement value
            extracted_features: Dictionary of extracted features
            confidence_assessment: Results from multi-dimensional confidence assessment
            
        Returns:
            Estimated variance of the prediction
        """
        # Base coefficient of variation (CV) derived from overall confidence
        # Lower confidence = higher CV = higher variance
        base_cv = 1.0 - (confidence_assessment["overall_confidence_score"] / 10.0)
        
        # Adjust CV based on case features
        adjusted_cv = base_cv
        
        # Adjust based on case type and complexity
        if "case_characteristics" in extracted_features and "case_type" in extracted_features["case_characteristics"]:
            case_type = extracted_features["case_characteristics"]["case_type"]
            
            # Complex or novel cases have higher variance
            if case_type.get("complexity") == "novel":
                adjusted_cv *= 1.5
            elif case_type.get("complexity") == "complex":
                adjusted_cv *= 1.2
        
        # Adjust based on evidence strength
        if "evidence_based" in extracted_features and "evidence_strength" in extracted_features["evidence_based"]:
            evidence_strength = extracted_features["evidence_based"]["evidence_strength"].get("overall_strength", 0.5)
            
            # Stronger evidence reduces variance
            evidence_factor = 1.5 - evidence_strength
            adjusted_cv *= evidence_factor
        
        # Adjust based on procedural stage
        if "procedural_strategic" in extracted_features and "procedural_posture" in extracted_features["procedural_strategic"]:
            stage = extracted_features["procedural_strategic"]["procedural_posture"].get("stage", "pre_filing")
            
            # Earlier stages have higher variance
            stage_factors = {
                "pre_filing": 1.3,
                "post_filing": 1.2,
                "discovery": 1.1,
                "dispositive_motions": 0.9,
                "pretrial": 0.8,
                "trial": 0.7
            }
            
            if stage in stage_factors:
                adjusted_cv *= stage_factors[stage]
        
        # Adjust based on damage range width
        if "composite" in extracted_features and "litigation_risk_profile" in extracted_features["composite"]:
            damage_range = extracted_features["composite"]["litigation_risk_profile"].get("damage_range_width", "medium")
            
            # Wider damage ranges have higher variance
            range_factors = {
                "wide": 1.3,
                "medium": 1.0,
                "narrow": 0.7
            }
            
            if damage_range in range_factors:
                adjusted_cv *= range_factors[damage_range]
        
        # Ensure CV is within reasonable bounds
        adjusted_cv = max(0.1, min(2.0, adjusted_cv))
        
        # Calculate variance from CV and point estimate
        # Variance = (CV * mean)^2
        variance = (adjusted_cv * point_estimate) ** 2
        
        return variance
    
    def _generate_interval_interpretation(self, intervals: Dict[str, Dict[str, float]],
                                         point_estimate: float,
                                         confidence_assessment: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate interpretations for the calculated confidence intervals.
        
        Args:
            intervals: Dictionary of confidence intervals
            point_estimate: The most likely settlement value
            confidence_assessment: Results from multi-dimensional confidence assessment
            
        Returns:
            Dictionary of interval interpretations
        """
        interpretations = {}
        
        # Interpret 90% confidence interval
        if "90%" in intervals:
            interval_90 = intervals["90%"]
            width_90 = interval_90["upper"] - interval_90["lower"]
            width_ratio_90 = width_90 / point_estimate if point_estimate > 0 else float('inf')
            
            if width_ratio_90 < 0.5:
                interpretations["90%"] = (
                    f"There is a 90% probability that the settlement value will fall between "
                    f"${interval_90['lower']:,.2f} and ${interval_90['upper']:,.2f}. "
                    f"This relatively narrow range indicates high confidence in the prediction."
                )
            elif width_ratio_90 < 1.0:
                interpretations["90%"] = (
                    f"There is a 90% probability that the settlement value will fall between "
                    f"${interval_90['lower']:,.2f} and ${interval_90['upper']:,.2f}. "
                    f"This moderate range reflects reasonable confidence in the prediction."
                )
            else:
                interpretations["90%"] = (
                    f"There is a 90% probability that the settlement value will fall between "
                    f"${interval_90['lower']:,.2f} and ${interval_90['upper']:,.2f}. "
                    f"This wide range indicates significant uncertainty in the prediction."
                )
        
        # Interpret 80% confidence interval
        if "80%" in intervals:
            interval_80 = intervals["80%"]
            interpretations["80%"] = (
                f"There is an 80% probability that the settlement value will fall between "
                f"${interval_80['lower']:,.2f} and ${interval_80['upper']:,.2f}."
            )
        
        # Interpret 50% confidence interval
        if "50%" in intervals:
            interval_50 = intervals["50%"]
            interpretations["50%"] = (
                f"There is a 50% probability that the settlement value will fall between "
                f"${interval_50['lower']:,.2f} and ${interval_50['upper']:,.2f}. "
                f"This is the most likely range for the settlement."
            )
        
        # Generate factors affecting interval width
        factors_affecting_width = []
        
        # Check dimension scores from confidence assessment
        dimension_scores = confidence_assessment.get("dimension_scores", {})
        
        if dimension_scores.get("evidential_confidence", 1.0) < 0.6:
            factors_affecting_width.append("Limited or uncertain evidence")
        
        if dimension_scores.get("data_adequacy_confidence", 1.0) < 0.6:
            factors_affecting_width.append("Incomplete case information")
        
        if dimension_scores.get("precedential_confidence", 1.0) < 0.6:
            factors_affecting_width.append("Limited precedential cases")
        
        if dimension_scores.get("stability_confidence", 1.0) < 0.6:
            factors_affecting_width.append("High sensitivity to changing assumptions")
        
        # Add general factors
        factors_affecting_width.extend([
            "Inherent uncertainty in legal outcomes",
            "Potential for new evidence to emerge",
            "Variability in jury/judge decision-making"
        ])
        
        # Select a subset of factors
        selected_factors = factors_affecting_width[:3]
        
        interpretations["factors_affecting_width"] = (
            f"The width of these intervals is primarily affected by: "
            f"{', '.join(selected_factors)}."
        )
        
        # Generate information to narrow intervals
        interpretations["narrowing_intervals"] = (
            f"To narrow these intervals and increase prediction precision, "
            f"address the improvement recommendations provided in the confidence assessment."
        )
        
        return interpretations
    
    def calculate_similarity_based_confidence(self, 
                                            similar_cases: List[Dict[str, Any]],
                                            point_estimate: float) -> Dict[str, Any]:
        """
        Calculate confidence based on similarity to reference cases.
        
        Args:
            similar_cases: List of similar cases with similarity scores
            point_estimate: The most likely settlement value
            
        Returns:
            Dictionary containing similarity-based confidence results
        """
        if not similar_cases:
            return {
                "similarity_confidence_score": 0.3,
                "explanation": "No similar cases available for comparison, resulting in low confidence.",
                "case_count_factor": 0.0,
                "similarity_factor": 0.0,
                "value_consistency_factor": 0.0
            }
        
        # Extract similarity scores and settlement values
        similarities = []
        settlement_values = []
        
        for case in similar_cases:
            similarity = case.get("similarity", 0)
            similarities.append(similarity)
            
            # Extract settlement value from case description if available
            value = self._extract_settlement_value_from_case(case)
            if value is not None:
                settlement_values.append(value)
        
        # Calculate case count factor (0-1)
        # More cases = higher confidence, up to a point
        case_count = len(similar_cases)
        case_count_factor = min(1.0, case_count / 5)
        
        # Calculate similarity factor (0-1)
        # Higher average similarity = higher confidence
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        similarity_factor = avg_similarity
        
        # Calculate value consistency factor (0-1)
        # More consistent settlement values = higher confidence
        value_consistency_factor = 0.5  # Default medium consistency
        
        if len(settlement_values) >= 2:
            # Calculate coefficient of variation (CV) of settlement values
            mean_value = sum(settlement_values) / len(settlement_values)
            if mean_value > 0:
                variance = sum((x - mean_value) ** 2 for x in settlement_values) / len(settlement_values)
                std_dev = math.sqrt(variance)
                cv = std_dev / mean_value
                
                # Convert CV to consistency factor (lower CV = higher consistency)
                value_consistency_factor = max(0.0, min(1.0, 1.0 - cv))
            
            # Check if point estimate is within the range of similar cases
            min_value = min(settlement_values)
            max_value = max(settlement_values)
            
            if point_estimate < min_value * 0.5 or point_estimate > max_value * 1.5:
                # Point estimate is far outside the range of similar cases
                value_consistency_factor *= 0.5
            elif min_value <= point_estimate <= max_value:
                # Point estimate is within the range of similar cases
                value_consistency_factor *= 1.2
        
        # Calculate overall similarity confidence score (0-1)
        # Weight factors based on importance
        similarity_confidence_score = (
            case_count_factor * 0.3 +
            similarity_factor * 0.4 +
            value_consistency_factor * 0.3
        )
        
        # Ensure score is within bounds
        similarity_confidence_score = max(0.1, min(1.0, similarity_confidence_score))
        
        # Generate explanation
        explanation = self._generate_similarity_confidence_explanation(
            case_count, avg_similarity, value_consistency_factor, similarity_confidence_score,
            settlement_values, point_estimate
        )
        
        # Compile results
        results = {
            "similarity_confidence_score": similarity_confidence_score,
            "explanation": explanation,
            "case_count_factor": case_count_factor,
            "similarity_factor": similarity_factor,
            "value_consistency_factor": value_consistency_factor,
            "similar_case_count": case_count,
            "average_similarity": avg_similarity
        }
        
        if settlement_values:
            results["settlement_value_range"] = {
                "min": min(settlement_values),
                "max": max(settlement_values),
                "mean": sum(settlement_values) / len(settlement_values)
            }
        
        return results
    
    def _extract_settlement_value_from_case(self, case: Dict[str, Any]) -> Optional[float]:
        """
        Extract settlement value from a case description.
        
        Args:
            case: Dictionary containing case information
            
        Returns:
            Settlement value if found, None otherwise
        """
        # Check if settlement value is directly provided
        if "settlement_value" in case:
            return float(case["settlement_value"])
        
        # Try to extract from description using regex
        if "description" in case:
            description = case["description"]
            
            # Look for patterns like "$X", "settled for $X", "awarded $X", etc.
            import re
            
            # Pattern for currency amounts
            patterns = [
                r'\$\s*([0-9,]+(?:\.[0-9]{2})?)',  # $X or $ X
                r'settled for\s*\$\s*([0-9,]+(?:\.[0-9]{2})?)',  # settled for $X
                r'settlement of\s*\$\s*([0-9,]+(?:\.[0-9]{2})?)',  # settlement of $X
                r'awarded\s*\$\s*([0-9,]+(?:\.[0-9]{2})?)',  # awarded $X
                r'verdict of\s*\$\s*([0-9,]+(?:\.[0-9]{2})?)',  # verdict of $X
                r'judgment of\s*\$\s*([0-9,]+(?:\.[0-9]{2})?)'  # judgment of $X
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, description, re.IGNORECASE)
                if matches:
                    # Take the largest value if multiple matches
                    values = []
                    for match in matches:
                        try:
                            values.append(float(match.replace(',', '')))
                        except ValueError:
                            pass
                    
                    if values:
                        return max(values)
        
        # Check metadata if available
        if "metadata" in case:
            metadata = case["metadata"]
            
            if "settlement_value" in metadata:
                return float(metadata["settlement_value"])
            
            if "verdict_amount" in metadata:
                return float(metadata["verdict_amount"])
            
            if "judgment_amount" in metadata:
                return float(metadata["judgment_amount"])
        
        # No settlement value found
        return None
    
    def _generate_similarity_confidence_explanation(self, case_count: int, avg_similarity: float,
                                                  value_consistency: float, confidence_score: float,
                                                  settlement_values: List[float], point_estimate: float) -> str:
        """
        Generate an explanation for the similarity-based confidence score.
        
        Args:
            case_count: Number of similar cases
            avg_similarity: Average similarity score
            value_consistency: Consistency factor for settlement values
            confidence_score: Overall similarity confidence score
            settlement_values: List of settlement values from similar cases
            point_estimate: The most likely settlement value
            
        Returns:
            Explanation string
        """
        # Case count explanation
        if case_count == 0:
            case_count_explanation = "No similar cases were found, which significantly reduces confidence."
        elif case_count == 1:
            case_count_explanation = "Only one similar case was found, providing limited comparative data."
        elif case_count < 3:
            case_count_explanation = f"{case_count} similar cases were found, providing some comparative data."
        else:
            case_count_explanation = f"{case_count} similar cases were found, providing a good basis for comparison."
        
        # Similarity explanation
        if avg_similarity < 0.3:
            similarity_explanation = "The similar cases have low similarity to the current case."
        elif avg_similarity < 0.6:
            similarity_explanation = "The similar cases have moderate similarity to the current case."
        else:
            similarity_explanation = "The similar cases have high similarity to the current case."
        
        # Value consistency explanation
        if len(settlement_values) < 2:
            consistency_explanation = "Insufficient settlement values to assess consistency."
        elif value_consistency < 0.3:
            consistency_explanation = "Settlement values in similar cases show high variability."
        elif value_consistency < 0.6:
            consistency_explanation = "Settlement values in similar cases show moderate consistency."
        else:
            consistency_explanation = "Settlement values in similar cases show high consistency."
        
        # Point estimate comparison
        if settlement_values:
            min_value = min(settlement_values)
            max_value = max(settlement_values)
            mean_value = sum(settlement_values) / len(settlement_values)
            
            if point_estimate < min_value * 0.5:
                estimate_explanation = (
                    f"The predicted settlement value (${point_estimate:,.2f}) is significantly lower than "
                    f"the range of similar cases (${min_value:,.2f} to ${max_value:,.2f})."
                )
            elif point_estimate > max_value * 1.5:
                estimate_explanation = (
                    f"The predicted settlement value (${point_estimate:,.2f}) is significantly higher than "
                    f"the range of similar cases (${min_value:,.2f} to ${max_value:,.2f})."
                )
            elif min_value <= point_estimate <= max_value:
                estimate_explanation = (
                    f"The predicted settlement value (${point_estimate:,.2f}) falls within "
                    f"the range of similar cases (${min_value:,.2f} to ${max_value:,.2f})."
                )
            else:
                estimate_explanation = (
                    f"The predicted settlement value (${point_estimate:,.2f}) is near "
                    f"the range of similar cases (${min_value:,.2f} to ${max_value:,.2f})."
                )
        else:
            estimate_explanation = "No settlement values available from similar cases for comparison."
        
        # Overall confidence explanation
        if confidence_score < 0.3:
            overall_explanation = "Overall, there is low confidence based on similar case comparison."
        elif confidence_score < 0.6:
            overall_explanation = "Overall, there is moderate confidence based on similar case comparison."
        else:
            overall_explanation = "Overall, there is high confidence based on similar case comparison."
        
        # Combine explanations
        explanation = (
            f"{case_count_explanation} {similarity_explanation} {consistency_explanation} "
            f"{estimate_explanation} {overall_explanation}"
        )
        
        return explanation
    
    def calculate_consensus_confidence(self, 
                                      multi_dimensional_confidence: Dict[str, Any],
                                      statistical_confidence: Dict[str, Any],
                                      similarity_confidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate consensus-based confidence by combining multiple confidence measures.
        
        Args:
            multi_dimensional_confidence: Results from multi-dimensional confidence assessment
            statistical_confidence: Results from statistical confidence interval calculation
            similarity_confidence: Results from similarity-based confidence assessment
            
        Returns:
            Dictionary containing consensus confidence results
        """
        # Extract individual confidence scores
        multi_dim_score = multi_dimensional_confidence["overall_confidence_score"] / 10.0  # Convert to 0-1 scale
        similarity_score = similarity_confidence["similarity_confidence_score"]
        
        # Extract statistical confidence interval width as a proxy for confidence
        # Narrower intervals = higher confidence
        interval_width_ratio = 0.5  # Default medium confidence
        
        if "confidence_intervals" in statistical_confidence and "90%" in statistical_confidence["confidence_intervals"]:
            interval_90 = statistical_confidence["confidence_intervals"]["90%"]
            point_estimate = statistical_confidence["point_estimate"]
            
            if point_estimate > 0:
                width_ratio = (interval_90["upper"] - interval_90["lower"]) / point_estimate
                # Convert width ratio to confidence score (narrower = higher confidence)
                interval_width_ratio = max(0.1, min(1.0, 1.0 / (1.0 + width_ratio)))
        
        # Calculate weighted consensus score
        # Weight the scores based on reliability and importance
        weights = {
            "multi_dimensional": 0.5,  # Highest weight as it's most comprehensive
            "statistical": 0.3,
            "similarity": 0.2
        }
        
        consensus_score = (
            multi_dim_score * weights["multi_dimensional"] +
            interval_width_ratio * weights["statistical"] +
            similarity_score * weights["similarity"]
        )
        
        # Ensure score is within bounds
        consensus_score = max(0.1, min(1.0, consensus_score))
        
        # Convert to 1-10 scale for consistency with other measures
        consensus_score_10 = consensus_score * 10
        
        # Determine confidence classification
        confidence_classification = "Unknown"
        for score_range, classification in self.confidence_classifications.items():
            if score_range[0] <= consensus_score_10 <= score_range[1]:
                confidence_classification = classification
                break
        
        # Generate explanation
        explanation = self._generate_consensus_confidence_explanation(
            multi_dim_score, interval_width_ratio, similarity_score,
            weights, consensus_score, confidence_classification
        )
        
        # Compile results
        results = {
            "consensus_confidence_score": consensus_score_10,
            "confidence_classification": confidence_classification,
            "explanation": explanation,
            "component_scores": {
                "multi_dimensional": multi_dim_score * 10,  # Convert back to 1-10 scale
                "statistical": interval_width_ratio * 10,
                "similarity": similarity_score * 10
            },
            "component_weights": weights
        }
        
        return results
    
    def _generate_consensus_confidence_explanation(self, multi_dim_score: float,
                                                 interval_width_ratio: float,
                                                 similarity_score: float,
                                                 weights: Dict[str, float],
                                                 consensus_score: float,
                                                 classification: str) -> str:
        """
        Generate an explanation for the consensus confidence score.
        
        Args:
            multi_dim_score: Multi-dimensional confidence score (0-1)
            interval_width_ratio: Confidence score derived from interval width (0-1)
            similarity_score: Similarity-based confidence score (0-1)
            weights: Dictionary of component weights
            consensus_score: Overall consensus confidence score (0-1)
            classification: Confidence classification string
            
        Returns:
            Explanation string
        """
        # Component explanations
        if multi_dim_score < 0.3:
            multi_dim_explanation = "multi-dimensional assessment indicates low confidence"
        elif multi_dim_score < 0.6:
            multi_dim_explanation = "multi-dimensional assessment indicates moderate confidence"
        else:
            multi_dim_explanation = "multi-dimensional assessment indicates high confidence"
        
        if interval_width_ratio < 0.3:
            statistical_explanation = "statistical analysis shows wide prediction intervals"
        elif interval_width_ratio < 0.6:
            statistical_explanation = "statistical analysis shows moderate prediction intervals"
        else:
            statistical_explanation = "statistical analysis shows narrow prediction intervals"
        
        if similarity_score < 0.3:
            similarity_explanation = "similar case comparison provides limited support"
        elif similarity_score < 0.6:
            similarity_explanation = "similar case comparison provides moderate support"
        else:
            similarity_explanation = "similar case comparison provides strong support"
        
        # Identify strongest and weakest components
        components = {
            "multi-dimensional assessment": multi_dim_score,
            "statistical analysis": interval_width_ratio,
            "similar case comparison": similarity_score
        }
        
        strongest = max(components.items(), key=lambda x: x[1])[0]
        weakest = min(components.items(), key=lambda x: x[1])[0]
        
        # Generate overall explanation
        explanation = (
            f"The overall confidence in this prediction is classified as '{classification}' "
            f"with a score of {consensus_score * 10:.1f}/10. This consensus score combines multiple "
            f"confidence measures where the {strongest} provides the strongest support, while "
            f"the {weakest} contributes less certainty. Specifically, the {multi_dim_explanation}, "
            f"{statistical_explanation}, and {similarity_explanation}."
        )
        
        return explanation
    
    def generate_confidence_visualization_data(self, 
                                             consensus_confidence: Dict[str, Any],
                                             statistical_confidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data for visualizing confidence in the frontend.
        
        Args:
            consensus_confidence: Results from consensus confidence calculation
            statistical_confidence: Results from statistical confidence interval calculation
            
        Returns:
            Dictionary containing visualization data
        """
        visualization_data = {
            "confidence_meter": {
                "score": consensus_confidence["consensus_confidence_score"],
                "classification": consensus_confidence["confidence_classification"],
                "color": self._get_confidence_color(consensus_confidence["consensus_confidence_score"])
            },
            "confidence_breakdown": {
                "labels": list(consensus_confidence["component_scores"].keys()),
                "scores": list(consensus_confidence["component_scores"].values()),
                "weights": list(consensus_confidence["component_weights"].values())
            }
        }
        
        # Add confidence intervals for visualization
        if "confidence_intervals" in statistical_confidence:
            intervals = statistical_confidence["confidence_intervals"]
            point_estimate = statistical_confidence["point_estimate"]
            
            visualization_data["confidence_intervals"] = {
                "point_estimate": point_estimate,
                "intervals": intervals
            }
        
        return visualization_data
    
    def _get_confidence_color(self, confidence_score: float) -> str:
        """
        Get color code for confidence visualization based on score.
        
        Args:
            confidence_score: Confidence score (1-10)
            
        Returns:
            Hex color code
        """
        if confidence_score >= 9:
            return "#2E7D32"  # Dark green
        elif confidence_score >= 7:
            return "#4CAF50"  # Green
        elif confidence_score >= 5:
            return "#FFC107"  # Amber
        elif confidence_score >= 3:
            return "#FF9800"  # Orange
        else:
            return "#F44336"  # Red
    
    def calculate_combined_confidence(self, case_data: Dict[str, Any], 
                                     extracted_features: Dict[str, Any],
                                     point_estimate: float,
                                     similar_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate combined confidence assessment using all available methods.
        
        Args:
            case_data: Dictionary containing case information
            extracted_features: Dictionary of extracted features
            point_estimate: The most likely settlement value
            similar_cases: List of similar cases with similarity scores
            
        Returns:
            Dictionary containing comprehensive confidence assessment results
        """
        # Calculate multi-dimensional confidence
        multi_dimensional_confidence = self.calculate_multi_dimensional_confidence(
            case_data, extracted_features
        )
        
        # Calculate statistical confidence intervals
        statistical_confidence = self.calculate_statistical_confidence_intervals(
            point_estimate, extracted_features, multi_dimensional_confidence
        )
        
        # Calculate similarity-based confidence
        similarity_confidence = self.calculate_similarity_based_confidence(
            similar_cases, point_estimate
        )
        
        # Calculate consensus confidence
        consensus_confidence = self.calculate_consensus_confidence(
            multi_dimensional_confidence, statistical_confidence, similarity_confidence
        )
        
        # Generate visualization data
        visualization_data = self.generate_confidence_visualization_data(
            consensus_confidence, statistical_confidence
        )
        
        # Compile comprehensive results
        results = {
            "consensus_confidence": consensus_confidence,
            "multi_dimensional_confidence": multi_dimensional_confidence,
            "statistical_confidence": statistical_confidence,
            "similarity_confidence": similarity_confidence,
            "visualization_data": visualization_data
        }
        
        return results
