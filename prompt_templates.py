"""
Enhanced Prompt Templates for SaaS Case Analysis Application

This module implements a modular prompt template system for legal case analysis
to enhance the accuracy of settlement predictions. It creates structured prompts
for the OpenAI API that incorporate extracted case features and follow best practices
for legal settlement prediction.
"""

from typing import Dict, Any, List, Optional
import json

class PromptTemplateManager:
    """
    Manages the creation and customization of prompt templates for legal case analysis.
    Implements a modular component system that can be tailored to specific case types.
    """
    
    def __init__(self):
        """Initialize the prompt template manager with necessary resources."""
        # Template components for different case types
        self.case_type_templates = {
            "personal_injury": {
                "analysis_framework": self._personal_injury_analysis_framework,
                "prediction_requirements": self._personal_injury_prediction_requirements,
                "explanation_framework": self._personal_injury_explanation_framework
            },
            "contract_dispute": {
                "analysis_framework": self._contract_dispute_analysis_framework,
                "prediction_requirements": self._contract_dispute_prediction_requirements,
                "explanation_framework": self._contract_dispute_explanation_framework
            },
            "employment": {
                "analysis_framework": self._employment_analysis_framework,
                "prediction_requirements": self._employment_prediction_requirements,
                "explanation_framework": self._employment_explanation_framework
            }
        }
        
        # Default template components for unknown case types
        self.default_templates = {
            "analysis_framework": self._default_analysis_framework,
            "prediction_requirements": self._default_prediction_requirements,
            "explanation_framework": self._default_explanation_framework
        }
    
    def create_enhanced_prompt(self, case_data: Dict[str, Any], extracted_features: Dict[str, Any], 
                              similar_cases: List[Dict[str, Any]], components: Optional[List[str]] = None) -> str:
        """
        Create an enhanced prompt with selected components.
        
        Args:
            case_data: Dictionary containing case information
            extracted_features: Dictionary of extracted features from the feature extraction module
            similar_cases: List of similar cases retrieved from the RAG system
            components: List of components to include (defaults to all)
            
        Returns:
            Structured prompt for OpenAI API
        """
        # Default components if none specified
        if components is None:
            components = [
                'case_information',
                'case_features',
                'similar_cases',
                'analysis_framework',
                'prediction_requirements',
                'explanation_framework',
                'confidence_assessment',
                'scenario_analysis',
                'limitations_acknowledgment'
            ]
        
        # Initialize prompt
        prompt_parts = ["# LEGAL SETTLEMENT PREDICTION WITH PREDICTIVE ANALYTICS\n"]
        
        # Determine case type for specialized templates
        case_type = "unknown"
        if "case_characteristics" in extracted_features and "case_type" in extracted_features["case_characteristics"]:
            case_type = extracted_features["case_characteristics"]["case_type"]["primary_type"]
        
        # Add selected components
        for component in components:
            if component == 'case_information':
                prompt_parts.append(self.create_case_information_component(case_data))
            elif component == 'case_features':
                prompt_parts.append(self.create_case_features_component(extracted_features))
            elif component == 'similar_cases':
                prompt_parts.append(self.create_similar_cases_component(similar_cases))
            elif component == 'analysis_framework':
                prompt_parts.append(self.create_analysis_framework_component(case_data, case_type))
            elif component == 'prediction_requirements':
                prompt_parts.append(self.create_prediction_requirements_component(case_data, case_type))
            elif component == 'explanation_framework':
                prompt_parts.append(self.create_explanation_framework_component(case_data, case_type))
            elif component == 'confidence_assessment':
                prompt_parts.append(self.create_confidence_assessment_component(case_data))
            elif component == 'scenario_analysis':
                prompt_parts.append(self.create_scenario_analysis_component(case_data))
            elif component == 'limitations_acknowledgment':
                prompt_parts.append(self.create_limitations_acknowledgment_component(case_data))
        
        # Combine all components into final prompt
        return "\n".join(prompt_parts)
    
    def create_case_information_component(self, case_data: Dict[str, Any]) -> str:
        """
        Create the case information component of the prompt.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Formatted case information component
        """
        component = "## CASE INFORMATION\n\n"
        
        # Format case title and number
        component += f"### Case Title\n{case_data.get('title', 'Untitled Case')}\n\n"
        
        if case_data.get('case_number'):
            component += f"### Case Number\n{case_data.get('case_number')}\n\n"
        
        # Format court information
        if case_data.get('court'):
            component += f"### Court\n{case_data.get('court')}\n\n"
        
        # Format date filed
        if case_data.get('date_filed'):
            component += f"### Date Filed\n{case_data.get('date_filed')}\n\n"
        
        # Format judge information
        if case_data.get('judge'):
            component += f"### Judge/Arbitrator/Mediator\n{case_data.get('judge')}\n\n"
        
        # Format insurance company
        if case_data.get('insurance_company'):
            component += f"### Insurance Company\n{case_data.get('insurance_company')}\n\n"
        
        # Format claim type
        component += f"### Claim Type\n{case_data.get('claim_type', 'Unknown')}\n\n"
        
        # Format injury types
        if case_data.get('injury_types'):
            component += "### Injury Types\n"
            for injury in case_data.get('injury_types', []):
                component += f"- {injury}\n"
            component += "\n"
        
        # Format facts
        component += "### Facts\n"
        component += f"{case_data.get('facts', 'No facts provided.')}\n\n"
        
        # Format injury details
        component += "### Injury Details\n"
        component += f"{case_data.get('injury_details', 'No injury details provided.')}\n\n"
        
        # Format economic damages
        component += "### Economic Damages\n"
        component += f"${case_data.get('damages', 0):,.2f}\n\n"
        
        # Format expert information
        if case_data.get('plaintiff_medical_expert'):
            component += "### Plaintiff Medical Expert\n"
            component += f"{case_data.get('plaintiff_medical_expert')}\n\n"
        
        if case_data.get('defendant_medical_expert'):
            component += "### Defendant Medical Expert\n"
            component += f"{case_data.get('defendant_medical_expert')}\n\n"
        
        if case_data.get('plaintiff_non_medical_expert'):
            component += "### Plaintiff Non-Medical Expert\n"
            component += f"{case_data.get('plaintiff_non_medical_expert')}\n\n"
        
        if case_data.get('defendant_non_medical_expert'):
            component += "### Defendant Non-Medical Expert\n"
            component += f"{case_data.get('defendant_non_medical_expert')}\n\n"
        
        return component
    
    def create_case_features_component(self, extracted_features: Dict[str, Any]) -> str:
        """
        Create the case features component of the prompt.
        
        Args:
            extracted_features: Dictionary of extracted features
            
        Returns:
            Formatted case features component
        """
        # This function assumes that the feature extractor has a method to format features for prompts
        # If the formatted features are already provided, we can use them directly
        if "formatted_features" in extracted_features:
            return extracted_features["formatted_features"]
        
        # Otherwise, we'll create a basic formatted representation
        component = "## CASE FEATURES\n\n"
        
        # Format case characteristics
        if "case_characteristics" in extracted_features:
            component += "### Case Characteristics\n\n"
            
            # Format jurisdiction features
            if "jurisdiction" in extracted_features["case_characteristics"]:
                jurisdiction = extracted_features["case_characteristics"]["jurisdiction"]
                component += "**Jurisdiction Analysis:**\n"
                for key, value in jurisdiction.items():
                    if isinstance(value, dict):
                        component += f"- {key.replace('_', ' ').title()}:\n"
                        for subkey, subvalue in value.items():
                            component += f"  - {subkey.replace('_', ' ').title()}: {subvalue}\n"
                    else:
                        component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
            
            # Format case type features
            if "case_type" in extracted_features["case_characteristics"]:
                case_type = extracted_features["case_characteristics"]["case_type"]
                component += "**Case Classification:**\n"
                for key, value in case_type.items():
                    if isinstance(value, dict):
                        component += f"- {key.replace('_', ' ').title()}:\n"
                        for subkey, subvalue in value.items():
                            component += f"  - {subkey.replace('_', ' ').title()}: {subvalue}\n"
                    else:
                        component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
            
            # Format temporal features
            if "temporal" in extracted_features["case_characteristics"]:
                temporal = extracted_features["case_characteristics"]["temporal"]
                component += "**Temporal Analysis:**\n"
                for key, value in temporal.items():
                    component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
            
            # Format damage features
            if "damages" in extracted_features["case_characteristics"]:
                damages = extracted_features["case_characteristics"]["damages"]
                component += "**Damage Analysis:**\n"
                for key, value in damages.items():
                    if isinstance(value, float):
                        component += f"- {key.replace('_', ' ').title()}: ${value:,.2f}\n"
                    else:
                        component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
        
        # Format party-specific features
        if "party_specific" in extracted_features:
            component += "### Party-Specific Factors\n\n"
            
            for party_type, party_data in extracted_features["party_specific"].items():
                component += f"**{party_type.replace('_', ' ').title()} Analysis:**\n"
                for key, value in party_data.items():
                    component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
        
        # Format evidence-based features
        if "evidence_based" in extracted_features:
            component += "### Evidence-Based Factors\n\n"
            
            for evidence_type, evidence_data in extracted_features["evidence_based"].items():
                component += f"**{evidence_type.replace('_', ' ').title()} Analysis:**\n"
                for key, value in evidence_data.items():
                    if isinstance(value, list):
                        component += f"- {key.replace('_', ' ').title()}: {', '.join(value)}\n"
                    elif isinstance(value, dict):
                        component += f"- {key.replace('_', ' ').title()}:\n"
                        for subkey, subvalue in value.items():
                            component += f"  - {subkey.replace('_', ' ').title()}: {subvalue}\n"
                    else:
                        component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
        
        # Format procedural and strategic features
        if "procedural_strategic" in extracted_features:
            component += "### Procedural and Strategic Factors\n\n"
            
            for proc_type, proc_data in extracted_features["procedural_strategic"].items():
                component += f"**{proc_type.replace('_', ' ').title()} Analysis:**\n"
                for key, value in proc_data.items():
                    component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
        
        # Format composite features
        if "composite" in extracted_features:
            component += "### Composite Strategic Indicators\n\n"
            
            for comp_type, comp_data in extracted_features["composite"].items():
                component += f"**{comp_type.replace('_', ' ').title()}:**\n"
                for key, value in comp_data.items():
                    if isinstance(value, dict):
                        component += f"- {key.replace('_', ' ').title()}:\n"
                        for subkey, subvalue in value.items():
                            component += f"  - {subkey.replace('_', ' ').title()}: {subvalue}\n"
                    else:
                        component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
        
        return component
    
    def create_similar_cases_component(self, similar_cases: List[Dict[str, Any]]) -> str:
        """
        Create the similar cases component of the prompt.
        
        Args:
            similar_cases: List of similar cases retrieved from the RAG system
            
        Returns:
            Formatted similar cases component
        """
        component = "## SIMILAR CASES\n\n"
        
        if not similar_cases:
            component += "No similar cases found in the database.\n\n"
            return component
        
        for i, case in enumerate(similar_cases, 1):
            component += f"### Similar Case {i}: {case.get('title', 'Untitled Case')}\n"
            component += f"**Similarity Score:** {case.get('similarity', 0):.2f}\n\n"
            
            # Format case description
            component += "**Case Description:**\n"
            component += f"{case.get('description', 'No description available.')}\n\n"
            
            # Format additional metadata if available
            if "metadata" in case:
                component += "**Additional Information:**\n"
                for key, value in case.get("metadata", {}).items():
                    if key not in ["title", "description"]:
                        component += f"- {key.replace('_', ' ').title()}: {value}\n"
                component += "\n"
        
        component += "### Comparative Analysis Instructions\n"
        component += "When analyzing the current case, consider these similar cases with the following approach:\n"
        component += "1. Identify key similarities and differences in fact patterns\n"
        component += "2. Compare liability theories and strength of evidence\n"
        component += "3. Analyze damage awards or settlements in similar cases\n"
        component += "4. Consider jurisdictional differences that may impact outcomes\n"
        component += "5. Evaluate how procedural postures compare to the current case\n\n"
        
        return component
    
    def create_analysis_framework_component(self, case_data: Dict[str, Any], case_type: str) -> str:
        """
        Create the analysis framework component of the prompt.
        
        Args:
            case_data: Dictionary containing case information
            case_type: Type of case for specialized templates
            
        Returns:
            Formatted analysis framework component
        """
        # Use case-specific template if available, otherwise use default
        if case_type in self.case_type_templates:
            return self.case_type_templates[case_type]["analysis_framework"](case_data)
        else:
            return self.default_templates["analysis_framework"](case_data)
    
    def _personal_injury_analysis_framework(self, case_data: Dict[str, Any]) -> str:
        """Personal injury specific analysis framework."""
        component = "## ANALYSIS FRAMEWORK\n\n"
        component += "Analyze this personal injury case using the following structured approach:\n\n"
        
        component += "### 1. Liability Analysis\n"
        component += "- Evaluate the strength of evidence supporting liability\n"
        component += "- Assess comparative fault/contributory negligence factors\n"
        component += "- Identify applicable legal standards and burden of proof\n"
        component += "- Analyze causation strength between defendant's actions and injuries\n\n"
        
        component += "### 2. Damages Analysis\n"
        component += "- Evaluate economic damages (medical expenses, lost wages, etc.)\n"
        component += "- Assess non-economic damages (pain and suffering, emotional distress)\n"
        component += "- Consider potential punitive damages if applicable\n"
        component += "- Analyze damage caps or limitations in the jurisdiction\n\n"
        
        component += "### 3. Injury Severity Assessment\n"
        component += "- Evaluate the nature and extent of physical injuries\n"
        component += "- Assess permanence and long-term prognosis\n"
        component += "- Consider impact on quality of life and daily activities\n"
        component += "- Analyze psychological/emotional impact\n\n"
        
        component += "### 4. Procedural Considerations\n"
        component += "- Evaluate current stage of litigation and its impact\n"
        component += "- Assess strength of expert testimony on both sides\n"
        component += "- Consider jury appeal factors in the venue\n"
        component += "- Analyze potential motion outcomes\n\n"
        
        component += "### 5. Settlement Valuation Methodology\n"
        component += "- Apply appropriate multiplier to special damages\n"
        component += "- Compare to similar case outcomes in the jurisdiction\n"
        component += "- Adjust for case-specific strengths and weaknesses\n"
        component += "- Consider settlement timing strategy\n\n"
        
        return component
    
    def _contract_dispute_analysis_framework(self, case_data: Dict[str, Any]) -> str:
        """Contract dispute specific analysis framework."""
        component = "## ANALYSIS FRAMEWORK\n\n"
        component += "Analyze this contract dispute case using the following structured approach:\n\n"
        
        component += "### 1. Contract Validity Analysis\n"
        component += "- Evaluate formation elements (offer, acceptance, consideration)\n"
        component += "- Assess potential defenses to formation\n"
        component += "- Analyze contract interpretation principles applicable\n"
        component += "- Consider parol evidence issues\n\n"
        
        component += "### 2. Breach Analysis\n"
        component += "- Identify specific contractual provisions allegedly breached\n"
        component += "- Evaluate evidence supporting/refuting breach claims\n"
        component += "- Assess materiality of alleged breaches\n"
        component += "- Analyze potential affirmative defenses\n\n"
        
        component += "### 3. Damages Assessment\n"
        component += "- Evaluate direct/consequential damages claimed\n"
        component += "- Assess liquidated damages provisions if applicable\n"
        component += "- Consider limitation of liability clauses\n"
        component += "- Analyze mitigation of damages issues\n\n"
        
        component += "### 4. Procedural Considerations\n"
        component += "- Evaluate current stage of litigation and its impact\n"
        component += "- Assess strength of documentary evidence\n"
        component += "- Consider arbitration/ADR provisions\n"
        component += "- Analyze potential motion outcomes\n\n"
        
        component += "### 5. Settlement Valuation Methodology\n"
        component += "- Calculate expected value based on liability probability\n"
        component += "- Compare to similar contract dispute outcomes\n"
        component += "- Adjust for case-specific strengths and weaknesses\n"
        component += "- Consider business relationship preservation value\n\n"
        
        return component
    
    def _employment_analysis_framework(self, case_data: Dict[str, Any]) -> str:
        """Employment case specific analysis framework."""
        component = "## ANALYSIS FRAMEWORK\n\n"
        component += "Analyze this employment case using the following structured approach:\n\n"
        
        component += "### 1. Legal Theory Analysis\n"
        component += "- Identify specific employment laws/regulations at issue\n"
        component += "- Evaluate prima facie case elements\n"
        component += "- Assess potential employer defenses\n"
        component += "- Analyze burden-shifting frameworks applicable\n\n"
        
        component += "### 2. Evidence Assessment\n"
        component += "- Evaluate documentary evidence strength\n"
        component += "- Assess witness credibility and testimony\n"
        component += "- Consider circumstantial evidence patterns\n"
        component += "- Analyze employer policies and their application\n\n"
        
        component += "### 3. Damages Calculation\n"
        component += "- Evaluate back pay/front pay calculations\n"
        component += "- Assess compensatory damages potential\n"
        component += "- Consider punitive damages exposure\n"
        component += "- Analyze statutory damages/penalties\n\n"
        
        component += "### 4. Procedural Considerations\n"
        component += "- Evaluate administrative exhaustion compliance\n"
        component += "- Assess current stage of litigation and its impact\n"
        component += "- Consider arbitration agreement enforceability\n"
        component += "- Analyze potential motion outcomes\n\n"
        
        component += "### 5. Settlement Valuation Methodology\n"
        component += "- Calculate expected value based on liability probability\n"
        component += "- Compare to similar employment case outcomes\n"
        component += "- Adjust for case-specific strengths and weaknesses\n"
        component += "- Consider non-monetary settlement terms\n\n"
        
        return component
    
    def _default_analysis_framework(self, case_data: Dict[str, Any]) -> str:
        """Default analysis framework for unknown case types."""
        component = "## ANALYSIS FRAMEWORK\n\n"
        component += "Analyze this case using the following structured approach:\n\n"
        
        component += "### 1. Legal Theory Analysis\n"
        component += "- Identify applicable laws and legal standards\n"
        component += "- Evaluate elements of claims and defenses\n"
        component += "- Assess burden of proof considerations\n"
        component += "- Analyze legal precedents in the jurisdiction\n\n"
        
        component += "### 2. Evidence Assessment\n"
        component += "- Evaluate strength and credibility of available evidence\n"
        component += "- Assess witness testimony and credibility\n"
        component += "- Consider documentary and physical evidence\n"
        component += "- Analyze expert opinions and their impact\n\n"
        
        component += "### 3. Damages Evaluation\n"
        component += "- Identify categories of damages claimed\n"
        component += "- Assess evidence supporting damage calculations\n"
        component += "- Consider limitations or caps on damages\n"
        component += "- Analyze causation between liability and damages\n\n"
        
        component += "### 4. Procedural Considerations\n"
        component += "- Evaluate current stage of litigation and its impact\n"
        component += "- Assess potential motion outcomes\n"
        component += "- Consider venue and jury characteristics\n"
        component += "- Analyze timing factors affecting settlement\n\n"
        
        component += "### 5. Settlement Valuation Methodology\n"
        component += "- Calculate expected value based on liability probability\n"
        component += "- Compare to similar case outcomes\n"
        component += "- Adjust for case-specific strengths and weaknesses\n"
        component += "- Consider non-monetary factors affecting settlement\n\n"
        
        return component
    
    def create_prediction_requirements_component(self, case_data: Dict[str, Any], case_type: str) -> str:
        """
        Create the prediction requirements component of the prompt.
        
        Args:
            case_data: Dictionary containing case information
            case_type: Type of case for specialized templates
            
        Returns:
            Formatted prediction requirements component
        """
        # Use case-specific template if available, otherwise use default
        if case_type in self.case_type_templates:
            return self.case_type_templates[case_type]["prediction_requirements"](case_data)
        else:
            return self.default_templates["prediction_requirements"](case_data)
    
    def _personal_injury_prediction_requirements(self, case_data: Dict[str, Any]) -> str:
        """Personal injury specific prediction requirements."""
        component = "## PREDICTION REQUIREMENTS\n\n"
        component += "Provide the following specific predictions for this personal injury case:\n\n"
        
        component += "### 1. Settlement Value Prediction\n"
        component += "- Provide a specific settlement value range (minimum to maximum)\n"
        component += "- State the most likely settlement value within that range\n"
        component += "- Break down the settlement value by damage categories:\n"
        component += "  * Past medical expenses\n"
        component += "  * Future medical expenses\n"
        component += "  * Past lost wages/income\n"
        component += "  * Future lost wages/income\n"
        component += "  * Pain and suffering\n"
        component += "  * Other non-economic damages\n\n"
        
        component += "### 2. Liability Assessment\n"
        component += "- Provide a specific liability percentage for the defendant\n"
        component += "- Assess comparative fault percentage for the plaintiff (if applicable)\n"
        component += "- Evaluate the strength of causation evidence (strong, moderate, weak)\n\n"
        
        component += "### 3. Timeline Prediction\n"
        component += "- Estimate optimal timing for settlement discussions\n"
        component += "- Predict time to trial if case does not settle\n"
        component += "- Assess impact of delay on settlement value\n\n"
        
        component += "### 4. Settlement Probability\n"
        component += "- Provide percentage probability of settlement before trial\n"
        component += "- Identify key factors that would increase settlement likelihood\n"
        component += "- Specify settlement obstacles that must be overcome\n\n"
        
        component += "### 5. Trial Outcome Prediction\n"
        component += "- Predict probability of plaintiff verdict at trial\n"
        component += "- Estimate likely jury award range if plaintiff prevails\n"
        component += "- Assess appellate risk factors\n\n"
        
        return component
    
    def _contract_dispute_prediction_requirements(self, case_data: Dict[str, Any]) -> str:
        """Contract dispute specific prediction requirements."""
        component = "## PREDICTION REQUIREMENTS\n\n"
        component += "Provide the following specific predictions for this contract dispute case:\n\n"
        
        component += "### 1. Settlement Value Prediction\n"
        component += "- Provide a specific settlement value range (minimum to maximum)\n"
        component += "- State the most likely settlement value within that range\n"
        component += "- Break down the settlement value by categories:\n"
        component += "  * Direct damages from breach\n"
        component += "  * Consequential damages\n"
        component += "  * Interest and penalties\n"
        component += "  * Attorney fees (if recoverable)\n\n"
        
        component += "### 2. Liability Assessment\n"
        component += "- Assess probability of finding enforceable contract\n"
        component += "- Evaluate likelihood of breach determination\n"
        component += "- Assess strength of potential defenses\n"
        component += "- Evaluate probability of counterclaim success\n\n"
        
        component += "### 3. Timeline Prediction\n"
        component += "- Estimate optimal timing for settlement discussions\n"
        component += "- Predict time to dispositive motions and their outcomes\n"
        component += "- Assess impact of delay on settlement value\n\n"
        
        component += "### 4. Settlement Probability\n"
        component += "- Provide percentage probability of settlement before trial\n"
        component += "- Identify key contract terms that affect settlement\n"
        component += "- Specify settlement obstacles that must be overcome\n\n"
        
        component += "### 5. Business Relationship Impact\n"
        component += "- Assess impact of litigation on business relationships\n"
        component += "- Evaluate potential for relationship preservation through settlement\n"
        component += "- Recommend non-monetary settlement terms to preserve relationships\n\n"
        
        return component
    
    def _employment_prediction_requirements(self, case_data: Dict[str, Any]) -> str:
        """Employment case specific prediction requirements."""
        component = "## PREDICTION REQUIREMENTS\n\n"
        component += "Provide the following specific predictions for this employment case:\n\n"
        
        component += "### 1. Settlement Value Prediction\n"
        component += "- Provide a specific settlement value range (minimum to maximum)\n"
        component += "- State the most likely settlement value within that range\n"
        component += "- Break down the settlement value by categories:\n"
        component += "  * Back pay/front pay\n"
        component += "  * Compensatory damages\n"
        component += "  * Punitive damages (if applicable)\n"
        component += "  * Attorney fees and costs\n\n"
        
        component += "### 2. Liability Assessment\n"
        component += "- Assess probability of establishing prima facie case\n"
        component += "- Evaluate strength of employer defenses\n"
        component += "- Assess likelihood of summary judgment outcomes\n"
        component += "- Evaluate impact of key witnesses and documents\n\n"
        
        component += "### 3. Timeline Prediction\n"
        component += "- Estimate optimal timing for settlement discussions\n"
        component += "- Predict administrative and litigation timeline\n"
        component += "- Assess impact of delay on settlement value\n\n"
        
        component += "### 4. Settlement Probability\n"
        component += "- Provide percentage probability of settlement before trial\n"
        component += "- Identify key factors that would increase settlement likelihood\n"
        component += "- Specify settlement obstacles that must be overcome\n\n"
        
        component += "### 5. Non-Monetary Terms\n"
        component += "- Recommend appropriate non-monetary settlement terms\n"
        component += "- Assess importance of confidentiality provisions\n"
        component += "- Evaluate reference/re-employment provisions\n"
        component += "- Recommend appropriate release language\n\n"
        
        return component
    
    def _default_prediction_requirements(self, case_data: Dict[str, Any]) -> str:
        """Default prediction requirements for unknown case types."""
        component = "## PREDICTION REQUIREMENTS\n\n"
        component += "Provide the following specific predictions for this case:\n\n"
        
        component += "### 1. Settlement Value Prediction\n"
        component += "- Provide a specific settlement value range (minimum to maximum)\n"
        component += "- State the most likely settlement value within that range\n"
        component += "- Break down the settlement value by major components\n"
        component += "- Explain key factors driving the valuation\n\n"
        
        component += "### 2. Liability Assessment\n"
        component += "- Assess probability of liability finding\n"
        component += "- Evaluate strength of claims and defenses\n"
        component += "- Identify critical liability determinants\n"
        component += "- Assess evidentiary strengths and weaknesses\n\n"
        
        component += "### 3. Timeline Prediction\n"
        component += "- Estimate optimal timing for settlement discussions\n"
        component += "- Predict litigation timeline through resolution\n"
        component += "- Assess impact of delay on settlement value\n\n"
        
        component += "### 4. Settlement Probability\n"
        component += "- Provide percentage probability of settlement before trial\n"
        component += "- Identify key factors that would increase settlement likelihood\n"
        component += "- Specify settlement obstacles that must be overcome\n\n"
        
        component += "### 5. Alternative Outcomes\n"
        component += "- Predict probability of alternative resolution methods\n"
        component += "- Assess likely outcomes of dispositive motions\n"
        component += "- Evaluate appellate risk if case proceeds to judgment\n\n"
        
        return component
    
    def create_explanation_framework_component(self, case_data: Dict[str, Any], case_type: str) -> str:
        """
        Create the explanation framework component of the prompt.
        
        Args:
            case_data: Dictionary containing case information
            case_type: Type of case for specialized templates
            
        Returns:
            Formatted explanation framework component
        """
        # Use case-specific template if available, otherwise use default
        if case_type in self.case_type_templates:
            return self.case_type_templates[case_type]["explanation_framework"](case_data)
        else:
            return self.default_templates["explanation_framework"](case_data)
    
    def _personal_injury_explanation_framework(self, case_data: Dict[str, Any]) -> str:
        """Personal injury specific explanation framework."""
        component = "## EXPLANATION FRAMEWORK\n\n"
        component += "Explain your predictions for this personal injury case using the following framework:\n\n"
        
        component += "### 1. Liability Explanation\n"
        component += "- Explain the legal basis for liability determination\n"
        component += "- Analyze how evidence supports or undermines liability\n"
        component += "- Explain comparative fault/contributory negligence impact\n"
        component += "- Discuss causation strength and challenges\n\n"
        
        component += "### 2. Damages Explanation\n"
        component += "- Justify economic damages calculation methodology\n"
        component += "- Explain non-economic damages multiplier selection\n"
        component += "- Discuss how injury severity impacts valuation\n"
        component += "- Explain any damage caps or limitations applied\n\n"
        
        component += "### 3. Similar Case Comparison\n"
        component += "- Compare and contrast with provided similar cases\n"
        component += "- Explain why settlement value may differ from similar cases\n"
        component += "- Discuss jurisdiction-specific factors affecting comparison\n"
        component += "- Analyze trend patterns from similar cases\n\n"
        
        component += "### 4. Risk Factor Analysis\n"
        component += "- Explain key risks for plaintiff and defendant\n"
        component += "- Discuss evidentiary uncertainties and their impact\n"
        component += "- Analyze jury perception risks in this venue\n"
        component += "- Explain how risks influence settlement recommendation\n\n"
        
        component += "### 5. Strategic Recommendations\n"
        component += "- Provide concrete negotiation strategy recommendations\n"
        component += "- Explain optimal timing for settlement discussions\n"
        component += "- Discuss information gathering priorities\n"
        component += "- Recommend settlement versus trial approach\n\n"
        
        return component
    
    def _contract_dispute_explanation_framework(self, case_data: Dict[str, Any]) -> str:
        """Contract dispute specific explanation framework."""
        component = "## EXPLANATION FRAMEWORK\n\n"
        component += "Explain your predictions for this contract dispute case using the following framework:\n\n"
        
        component += "### 1. Contract Analysis Explanation\n"
        component += "- Explain contract formation and validity assessment\n"
        component += "- Analyze key contractual provisions at issue\n"
        component += "- Discuss contract interpretation principles applied\n"
        component += "- Explain how evidence supports contract claims/defenses\n\n"
        
        component += "### 2. Breach and Damages Explanation\n"
        component += "- Justify breach determination analysis\n"
        component += "- Explain damages calculation methodology\n"
        component += "- Discuss limitations on recovery and their basis\n"
        component += "- Analyze causation between breach and claimed damages\n\n"
        
        component += "### 3. Similar Case Comparison\n"
        component += "- Compare and contrast with provided similar cases\n"
        component += "- Explain why settlement value may differ from similar cases\n"
        component += "- Discuss industry-specific factors affecting comparison\n"
        component += "- Analyze trend patterns from similar contract disputes\n\n"
        
        component += "### 4. Risk Factor Analysis\n"
        component += "- Explain key risks for each party\n"
        component += "- Discuss contract interpretation uncertainties\n"
        component += "- Analyze business relationship impact risks\n"
        component += "- Explain how risks influence settlement recommendation\n\n"
        
        component += "### 5. Strategic Recommendations\n"
        component += "- Provide concrete negotiation strategy recommendations\n"
        component += "- Explain optimal approach to settlement discussions\n"
        component += "- Discuss business relationship preservation strategies\n"
        component += "- Recommend settlement versus litigation approach\n\n"
        
        return component
    
    def _employment_explanation_framework(self, case_data: Dict[str, Any]) -> str:
        """Employment case specific explanation framework."""
        component = "## EXPLANATION FRAMEWORK\n\n"
        component += "Explain your predictions for this employment case using the following framework:\n\n"
        
        component += "### 1. Legal Theory Explanation\n"
        component += "- Explain application of relevant employment laws\n"
        component += "- Analyze prima facie case elements and evidence\n"
        component += "- Discuss strength of employer defenses\n"
        component += "- Explain burden-shifting analysis applied\n\n"
        
        component += "### 2. Damages Explanation\n"
        component += "- Justify economic damages calculation methodology\n"
        component += "- Explain compensatory damages assessment\n"
        component += "- Discuss punitive damages potential and limitations\n"
        component += "- Analyze statutory damages/penalties applicable\n\n"
        
        component += "### 3. Similar Case Comparison\n"
        component += "- Compare and contrast with provided similar cases\n"
        component += "- Explain why settlement value may differ from similar cases\n"
        component += "- Discuss jurisdiction/industry-specific factors\n"
        component += "- Analyze trend patterns in employment litigation\n\n"
        
        component += "### 4. Risk Factor Analysis\n"
        component += "- Explain key risks for employer and employee\n"
        component += "- Discuss evidentiary uncertainties and their impact\n"
        component += "- Analyze reputational and precedential risks\n"
        component += "- Explain how risks influence settlement recommendation\n\n"
        
        component += "### 5. Strategic Recommendations\n"
        component += "- Provide concrete negotiation strategy recommendations\n"
        component += "- Explain optimal non-monetary settlement terms\n"
        component += "- Discuss confidentiality and release considerations\n"
        component += "- Recommend settlement versus litigation approach\n\n"
        
        return component
    
    def _default_explanation_framework(self, case_data: Dict[str, Any]) -> str:
        """Default explanation framework for unknown case types."""
        component = "## EXPLANATION FRAMEWORK\n\n"
        component += "Explain your predictions for this case using the following framework:\n\n"
        
        component += "### 1. Legal Analysis Explanation\n"
        component += "- Explain application of relevant laws and legal standards\n"
        component += "- Analyze strength of claims and defenses\n"
        component += "- Discuss burden of proof considerations\n"
        component += "- Explain how evidence supports legal conclusions\n\n"
        
        component += "### 2. Damages Explanation\n"
        component += "- Justify damages calculation methodology\n"
        component += "- Explain valuation of different damage components\n"
        component += "- Discuss limitations on recovery and their basis\n"
        component += "- Analyze causation between liability and damages\n\n"
        
        component += "### 3. Similar Case Comparison\n"
        component += "- Compare and contrast with provided similar cases\n"
        component += "- Explain why settlement value may differ from similar cases\n"
        component += "- Discuss jurisdiction-specific factors affecting comparison\n"
        component += "- Analyze trend patterns from similar cases\n\n"
        
        component += "### 4. Risk Factor Analysis\n"
        component += "- Explain key risks for each party\n"
        component += "- Discuss evidentiary uncertainties and their impact\n"
        component += "- Analyze procedural and strategic risks\n"
        component += "- Explain how risks influence settlement recommendation\n\n"
        
        component += "### 5. Strategic Recommendations\n"
        component += "- Provide concrete negotiation strategy recommendations\n"
        component += "- Explain optimal timing for settlement discussions\n"
        component += "- Discuss information gathering priorities\n"
        component += "- Recommend settlement versus litigation approach\n\n"
        
        return component
    
    def create_confidence_assessment_component(self, case_data: Dict[str, Any]) -> str:
        """
        Create the confidence assessment component of the prompt.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Formatted confidence assessment component
        """
        component = "## CONFIDENCE ASSESSMENT\n\n"
        component += "Provide a comprehensive confidence assessment for your predictions using this framework:\n\n"
        
        component += "### 1. Multi-Dimensional Confidence Scoring\n"
        component += "Evaluate prediction confidence across these dimensions:\n\n"
        
        component += "- **Evidential Confidence (1-10)**\n"
        component += "  * Assess the strength and reliability of available evidence\n"
        component += "  * Consider evidence completeness, quality, and consistency\n"
        component += "  * Evaluate corroboration between evidence sources\n"
        component += "  * Score: [1-10] with justification\n\n"
        
        component += "- **Methodological Confidence (1-10)**\n"
        component += "  * Assess the reliability of analytical methods for this case type\n"
        component += "  * Consider methodological limitations and assumptions\n"
        component += "  * Evaluate method validation for similar cases\n"
        component += "  * Score: [1-10] with justification\n\n"
        
        component += "- **Precedential Confidence (1-10)**\n"
        component += "  * Assess the strength and relevance of legal precedents\n"
        component += "  * Consider precedent consistency and recency\n"
        component += "  * Evaluate jurisdictional alignment of precedents\n"
        component += "  * Score: [1-10] with justification\n\n"
        
        component += "- **Data Adequacy Confidence (1-10)**\n"
        component += "  * Assess the completeness of case information\n"
        component += "  * Consider information gaps and their significance\n"
        component += "  * Evaluate the reliability of information sources\n"
        component += "  * Score: [1-10] with justification\n\n"
        
        component += "- **Stability Confidence (1-10)**\n"
        component += "  * Assess prediction sensitivity to assumption changes\n"
        component += "  * Consider potential new information impact\n"
        component += "  * Evaluate temporal stability of the prediction\n"
        component += "  * Score: [1-10] with justification\n\n"
        
        component += "### 2. Dimensional Weighting\n"
        component += "- Assign weights to each dimension based on case characteristics\n"
        component += "- Explain weighting rationale\n"
        component += "- Calculate weighted average for overall confidence score\n\n"
        
        component += "### 3. Overall Confidence Classification\n"
        component += "- Classify overall confidence as:\n"
        component += "  * Very High Confidence (9-10)\n"
        component += "  * High Confidence (7-8)\n"
        component += "  * Moderate Confidence (5-6)\n"
        component += "  * Low Confidence (3-4)\n"
        component += "  * Very Low Confidence (1-2)\n\n"
        
        component += "### 4. Confidence Interval Calculation\n"
        component += "- Calculate 90% confidence interval for settlement prediction\n"
        component += "- Calculate 80% confidence interval for settlement prediction\n"
        component += "- Calculate 50% confidence interval for settlement prediction\n"
        component += "- Explain interval calculation methodology\n\n"
        
        component += "### 5. Confidence Improvement Recommendations\n"
        component += "- For each dimension scoring below 7:\n"
        component += "  * Provide specific recommendations to improve confidence\n"
        component += "  * Identify additional information needed\n"
        component += "  * Suggest analytical approaches to increase confidence\n\n"
        
        return component
    
    def create_scenario_analysis_component(self, case_data: Dict[str, Any]) -> str:
        """
        Create the scenario analysis component of the prompt.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Formatted scenario analysis component
        """
        component = "## SCENARIO ANALYSIS\n\n"
        component += "Conduct a scenario analysis for this case using the following framework:\n\n"
        
        component += "### 1. Best Case Scenario\n"
        component += "- Identify favorable assumptions for settlement/outcome\n"
        component += "- Calculate best case settlement value\n"
        component += "- Assess probability of best case scenario\n"
        component += "- Identify factors that would lead to best case\n\n"
        
        component += "### 2. Worst Case Scenario\n"
        component += "- Identify unfavorable assumptions for settlement/outcome\n"
        component += "- Calculate worst case settlement value or liability\n"
        component += "- Assess probability of worst case scenario\n"
        component += "- Identify factors that would lead to worst case\n\n"
        
        component += "### 3. Most Likely Scenario\n"
        component += "- Identify most realistic assumptions\n"
        component += "- Calculate most likely settlement value\n"
        component += "- Explain why this scenario is most probable\n"
        component += "- Identify key determinants of this scenario\n\n"
        
        component += "### 4. Alternative Scenario\n"
        component += "- Identify an important alternative scenario\n"
        component += "- Calculate settlement value under this scenario\n"
        component += "- Assess probability of this alternative\n"
        component += "- Explain significance of this alternative\n\n"
        
        component += "### 5. Sensitivity Analysis\n"
        component += "- Identify the 3 most impactful variables affecting outcome\n"
        component += "- For each variable, calculate outcome impact if variable changes\n"
        component += "- Rank variables by settlement value sensitivity\n"
        component += "- Recommend focus areas based on sensitivity\n\n"
        
        return component
    
    def create_limitations_acknowledgment_component(self, case_data: Dict[str, Any]) -> str:
        """
        Create the limitations acknowledgment component of the prompt.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Formatted limitations acknowledgment component
        """
        component = "## LIMITATIONS ACKNOWLEDGMENT\n\n"
        component += "Acknowledge the limitations of this analysis using the following framework:\n\n"
        
        component += "### 1. Information Limitations\n"
        component += "- Identify critical missing information\n"
        component += "- Assess impact of information gaps on prediction reliability\n"
        component += "- Acknowledge assumptions made to bridge information gaps\n"
        component += "- Recommend specific information gathering to improve analysis\n\n"
        
        component += "### 2. Methodological Limitations\n"
        component += "- Acknowledge limitations of analytical approach\n"
        component += "- Identify potential biases in methodology\n"
        component += "- Discuss alternative methodologies not employed\n"
        component += "- Explain how methodological limitations affect confidence\n\n"
        
        component += "### 3. Predictive Limitations\n"
        component += "- Acknowledge inherent uncertainty in legal predictions\n"
        component += "- Identify specific unpredictable factors\n"
        component += "- Discuss limitations in similar case comparisons\n"
        component += "- Explain how these limitations affect prediction ranges\n\n"
        
        component += "### 4. Scope Limitations\n"
        component += "- Clarify aspects of the case not addressed in analysis\n"
        component += "- Acknowledge specialized issues requiring expert input\n"
        component += "- Identify potential collateral issues not considered\n"
        component += "- Explain rationale for analysis scope decisions\n\n"
        
        component += "### 5. Usage Guidance\n"
        component += "- Provide guidance on appropriate use of this analysis\n"
        component += "- Identify circumstances requiring analysis update\n"
        component += "- Recommend complementary analyses or approaches\n"
        component += "- Emphasize professional judgment importance alongside analysis\n\n"
        
        return component
