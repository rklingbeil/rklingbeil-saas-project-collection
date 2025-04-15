"""
Enhanced RAG System for SaaS Case Analysis Application

This module implements an enhanced Retrieval Augmented Generation (RAG) system
that incorporates feature extraction, enhanced prompt templates, and confidence
scoring to improve the accuracy and reliability of legal case settlement predictions.
"""

import os
import openai
import numpy as np
from pinecone import Pinecone
from typing import List, Dict, Any, Optional
from sklearn.decomposition import PCA

# Import our custom modules
from feature_extraction import FeatureExtractor
from prompt_templates import PromptTemplateManager
from confidence_scoring import ConfidenceScorer

class EnhancedRAGSystem:
    """
    Enhanced Retrieval Augmented Generation (RAG) system for legal case analysis.
    Integrates feature extraction, enhanced prompt templates, and confidence scoring
    with OpenAI for generation and Pinecone for retrieval of similar cases.
    """
    
    def __init__(self):
        # Initialize OpenAI client
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Initialize Pinecone client
        self.pinecone_api_key = os.environ.get('PINECONE_API_KEY')
        self.pinecone_env = os.environ.get('PINECONE_ENV')
        self.pinecone_index_name = os.environ.get('PINECONE_INDEX_NAME')
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Initialize PCA for dimensionality reduction (1536 -> 768)
        self.pca = PCA(n_components=768)
        self.pca_initialized = False
        
        # Initialize our custom components
        self.feature_extractor = FeatureExtractor()
        self.prompt_template_manager = PromptTemplateManager()
        self.confidence_scorer = ConfidenceScorer()
        
        # Get the index if it exists
        try:
            self.index = self.pc.Index(self.pinecone_index_name)
            print(f"Connected to existing Pinecone index: {self.pinecone_index_name}")
        except Exception as e:
            print(f"Error connecting to Pinecone index: {e}")
            raise
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for the given text using OpenAI."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"  # This produces 1536-dimensional vectors
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise
    
    def reduce_dimensions(self, embedding: List[float]) -> List[float]:
        """
        Reduce dimensions of the embedding from 1536 to 768 using PCA.
        If PCA is not initialized, it will use a simple slicing method.
        """
        embedding_array = np.array(embedding).reshape(1, -1)
        
        if not self.pca_initialized:
            # For the first embedding, we'll use a simple method to reduce dimensions
            # by taking every other dimension (this is a temporary solution)
            reduced_embedding = embedding_array[0, ::2].tolist()
            
            # Initialize PCA with this first embedding (not ideal but workable for demo)
            try:
                self.pca.fit(embedding_array)
                self.pca_initialized = True
                print("PCA initialized for future dimension reduction")
            except Exception as e:
                print(f"Warning: Could not initialize PCA: {e}")
                
            return reduced_embedding
        else:
            # Use PCA for dimension reduction once it's initialized
            try:
                reduced_embedding = self.pca.transform(embedding_array)[0].tolist()
                return reduced_embedding
            except Exception as e:
                print(f"Error reducing dimensions with PCA: {e}")
                # Fallback to simple method if PCA fails
                return embedding_array[0, ::2].tolist()
    
    def retrieve_similar_cases(self, query_embedding: List[float], 
                              extracted_features: Dict[str, Any],
                              top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve similar cases from Pinecone using the query embedding and extracted features.
        Enhances vector similarity with feature-based weighting.
        
        Args:
            query_embedding: Embedding vector for the query case
            extracted_features: Dictionary of extracted features from the case
            top_k: Number of similar cases to retrieve
            
        Returns:
            List of similar cases with similarity scores and metadata
        """
        try:
            # Reduce dimensions to match Pinecone index (1536 -> 768)
            reduced_embedding = self.reduce_dimensions(query_embedding)
            
            # Query Pinecone with reduced embedding
            results = self.index.query(
                vector=reduced_embedding,
                top_k=top_k * 2,  # Retrieve more candidates for re-ranking
                include_metadata=True
            )
            
            # Extract candidate cases
            candidate_cases = [
                {
                    "id": match.id,
                    "title": match.metadata.get("title", "Unknown Case"),
                    "similarity": match.score,
                    "description": match.metadata.get("description", "No description available"),
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
            
            # Re-rank candidates using feature-based similarity
            reranked_cases = self._rerank_cases_with_features(candidate_cases, extracted_features)
            
            # Return top_k cases after re-ranking
            return reranked_cases[:top_k]
        except Exception as e:
            print(f"Error retrieving similar cases: {e}")
            return []
    
    def _rerank_cases_with_features(self, candidate_cases: List[Dict[str, Any]], 
                                   extracted_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Re-rank candidate cases using feature-based similarity.
        
        Args:
            candidate_cases: List of candidate cases from vector similarity search
            extracted_features: Dictionary of extracted features from the query case
            
        Returns:
            Re-ranked list of cases
        """
        # If no features extracted, return original ranking
        if not extracted_features:
            return candidate_cases
        
        # Extract case type for feature weighting
        case_type = "unknown"
        if "case_characteristics" in extracted_features and "case_type" in extracted_features["case_characteristics"]:
            case_type = extracted_features["case_characteristics"]["case_type"]["primary_type"]
        
        # Define feature weights based on case type
        feature_weights = self._get_feature_weights(case_type)
        
        # Calculate feature-based similarity for each candidate
        for case in candidate_cases:
            # Start with vector similarity score
            vector_similarity = case["similarity"]
            
            # Extract case metadata for feature comparison
            metadata = case.get("metadata", {})
            
            # Initialize feature similarity score
            feature_similarity = 0.0
            feature_weight_sum = 0.0
            
            # Compare case type
            if "case_type" in metadata and "case_characteristics" in extracted_features:
                query_case_type = extracted_features["case_characteristics"]["case_type"]["primary_type"]
                candidate_case_type = metadata.get("case_type")
                
                if query_case_type == candidate_case_type:
                    feature_similarity += feature_weights["case_type"]
                    
                feature_weight_sum += feature_weights["case_type"]
            
            # Compare jurisdiction
            if "jurisdiction" in metadata and "case_characteristics" in extracted_features:
                query_jurisdiction = extracted_features["case_characteristics"]["jurisdiction"].get("jurisdiction")
                candidate_jurisdiction = metadata.get("jurisdiction")
                
                if query_jurisdiction == candidate_jurisdiction:
                    feature_similarity += feature_weights["jurisdiction"]
                    
                feature_weight_sum += feature_weights["jurisdiction"]
            
            # Compare damage range
            if "damages" in metadata and "case_characteristics" in extracted_features:
                query_damages = extracted_features["case_characteristics"]["damages"].get("total_damages", 0)
                candidate_damages = float(metadata.get("damages", 0))
                
                # Calculate damage similarity based on range
                if query_damages > 0 and candidate_damages > 0:
                    damage_ratio = min(query_damages, candidate_damages) / max(query_damages, candidate_damages)
                    feature_similarity += feature_weights["damages"] * damage_ratio
                    
                feature_weight_sum += feature_weights["damages"]
            
            # Compare injury types
            if "injury_types" in metadata and "case_characteristics" in extracted_features:
                query_injury_types = extracted_features["case_characteristics"].get("injury_types", [])
                candidate_injury_types = metadata.get("injury_types", [])
                
                if query_injury_types and candidate_injury_types:
                    # Calculate overlap between injury types
                    query_set = set(query_injury_types)
                    candidate_set = set(candidate_injury_types)
                    
                    if query_set and candidate_set:
                        overlap = len(query_set.intersection(candidate_set))
                        union = len(query_set.union(candidate_set))
                        
                        if union > 0:
                            injury_similarity = overlap / union
                            feature_similarity += feature_weights["injury_types"] * injury_similarity
                            
                    feature_weight_sum += feature_weights["injury_types"]
            
            # Normalize feature similarity if we have features to compare
            if feature_weight_sum > 0:
                normalized_feature_similarity = feature_similarity / feature_weight_sum
            else:
                normalized_feature_similarity = 0.0
            
            # Combine vector similarity with feature similarity
            # The alpha parameter controls the balance between vector and feature similarity
            alpha = 0.7  # 70% vector similarity, 30% feature similarity
            combined_similarity = (alpha * vector_similarity) + ((1 - alpha) * normalized_feature_similarity)
            
            # Update case similarity score
            case["original_similarity"] = case["similarity"]
            case["feature_similarity"] = normalized_feature_similarity
            case["similarity"] = combined_similarity
        
        # Sort cases by combined similarity score
        reranked_cases = sorted(candidate_cases, key=lambda x: x["similarity"], reverse=True)
        
        return reranked_cases
    
    def _get_feature_weights(self, case_type: str) -> Dict[str, float]:
        """
        Get feature weights based on case type.
        
        Args:
            case_type: Type of case
            
        Returns:
            Dictionary of feature weights
        """
        # Default weights
        default_weights = {
            "case_type": 0.3,
            "jurisdiction": 0.2,
            "damages": 0.3,
            "injury_types": 0.2
        }
        
        # Case type specific weights
        weights = {
            "personal_injury": {
                "case_type": 0.25,
                "jurisdiction": 0.15,
                "damages": 0.3,
                "injury_types": 0.3
            },
            "contract_dispute": {
                "case_type": 0.3,
                "jurisdiction": 0.2,
                "damages": 0.4,
                "injury_types": 0.1
            },
            "employment": {
                "case_type": 0.3,
                "jurisdiction": 0.25,
                "damages": 0.25,
                "injury_types": 0.2
            }
        }
        
        # Return case type specific weights if available, otherwise default
        return weights.get(case_type, default_weights)
    
    def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a legal case using enhanced RAG approach:
        1. Extract features from the case
        2. Generate embeddings for the case
        3. Retrieve and re-rank similar cases using features
        4. Create enhanced prompt using templates
        5. Generate analysis with OpenAI
        6. Calculate confidence scores
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Dictionary containing analysis results, confidence scores, and similar cases
        """
        try:
            # Step 1: Extract features from the case
            extracted_features = self.feature_extractor.extract_features(case_data)
            
            # Step 2: Prepare case text for embedding
            case_text = self._prepare_case_text_for_embedding(case_data, extracted_features)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(case_text)
            
            # Step 3: Retrieve and re-rank similar cases
            similar_cases = self.retrieve_similar_cases(embeddings, extracted_features)
            
            # If no similar cases found, return placeholder response
            if not similar_cases:
                return {
                    "prediction": "Unable to find similar cases for analysis",
                    "confidence": {
                        "overall_score": 0.0,
                        "classification": "Very Low Confidence",
                        "explanation": "No similar cases found for comparison."
                    },
                    "similar_cases": [],
                    "extracted_features": extracted_features
                }
            
            # Step 4: Create enhanced prompt using templates
            prompt = self.prompt_template_manager.create_enhanced_prompt(
                case_data, extracted_features, similar_cases
            )
            
            # Step 5: Generate analysis with OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a legal expert assistant that analyzes cases and predicts settlement outcomes with detailed confidence assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            
            # Extract settlement prediction from analysis
            settlement_prediction = self._extract_settlement_prediction(analysis)
            
            # Step 6: Calculate confidence scores
            confidence_scores = self.confidence_scorer.calculate_combined_confidence(
                case_data, extracted_features, settlement_prediction, similar_cases
            )
            
            # Prepare final result
            result = {
                "prediction": analysis,
                "settlement_value": settlement_prediction,
                "confidence": {
                    "overall_score": confidence_scores["consensus_confidence"]["consensus_confidence_score"],
                    "classification": confidence_scores["consensus_confidence"]["confidence_classification"],
                    "explanation": confidence_scores["consensus_confidence"]["explanation"],
                    "detailed_scores": confidence_scores
                },
                "similar_cases": similar_cases,
                "extracted_features": extracted_features,
                "visualization_data": confidence_scores["visualization_data"]
            }
            
            return result
            
        except Exception as e:
            print(f"Error analyzing case: {e}")
            import traceback
            traceback.print_exc()
            return {
                "prediction": f"Error analyzing case: {str(e)}",
                "confidence": {
                    "overall_score": 0.0,
                    "classification": "Error",
                    "explanation": f"An error occurred during analysis: {str(e)}"
                },
                "similar_cases": [],
                "extracted_features": {}
            }
    
    def _prepare_case_text_for_embedding(self, case_data: Dict[str, Any], 
                                        extracted_features: Dict[str, Any]) -> str:
        """
        Prepare case text for embedding generation.
        
        Args:
            case_data: Dictionary containing case information
            extracted_features: Dictionary of extracted features
            
        Returns:
            Formatted case text for embedding
        """
        case_text = f"Title: {case_data.get('title', '')}\n"
        
        # Add basic case information
        if case_data.get('court'):
            case_text += f"Court: {case_data.get('court')}\n"
        
        if case_data.get('claim_type'):
            case_text += f"Claim Type: {case_data.get('claim_type')}\n"
        
        if case_data.get('facts'):
            case_text += f"Facts: {case_data.get('facts')}\n"
        
        if case_data.get('injury_details'):
            case_text += f"Injury Details: {case_data.get('injury_details')}\n"
        
        if case_data.get('damages') is not None:
            case_text += f"Damages: ${case_data.get('damages')}\n"
        
        # Add key extracted features to improve embedding quality
        if extracted_features:
            case_text += "\nExtracted Features:\n"
            
            # Add case type
            if "case_characteristics" in extracted_features and "case_type" in extracted_features["case_characteristics"]:
                case_type = extracted_features["case_characteristics"]["case_type"]
                case_text += f"Case Type: {case_type.get('primary_type', 'unknown')}\n"
            
            # Add jurisdiction
            if "case_characteristics" in extracted_features and "jurisdiction" in extracted_features["case_characteristics"]:
                jurisdiction = extracted_features["case_characteristics"]["jurisdiction"]
                case_text += f"Jurisdiction: {jurisdiction.get('jurisdiction', 'unknown')}\n"
            
            # Add key composite features
            if "composite" in extracted_features:
                composite = extracted_features["composite"]
                
                if "settlement_pressure_index" in composite:
                    pressure = composite["settlement_pressure_index"]
                    case_text += f"Settlement Pressure: {pressure.get('overall_index', 5.0)}/10\n"
                
                if "case_strength_ratio" in composite:
                    strength = composite["case_strength_ratio"]
                    case_text += f"Case Strength Ratio: {strength.get('strength_ratio', 1.0)}\n"
                
                if "litigation_risk_profile" in composite:
                    risk = composite["litigation_risk_profile"]
                    case_text += f"Litigation Risk: {risk.get('overall_risk_level', 'medium')}\n"
        
        return case_text
    
    def _extract_settlement_prediction(self, analysis: str) -> float:
        """
        Extract the settlement prediction value from the analysis text.
        
        Args:
            analysis: Analysis text from OpenAI
            
        Returns:
            Extracted settlement value or default value
        """
        import re
        
        # Default value if extraction fails
        default_value = 50000.0
        
        # Look for patterns like "most likely settlement value: $X" or "settlement value of $X"
        patterns = [
            r'most likely settlement value.*?\$([0-9,]+(?:\.[0-9]{2})?)',
            r'settlement value of.*?\$([0-9,]+(?:\.[0-9]{2})?)',
            r'likely settlement.*?\$([0-9,]+(?:\.[0-9]{2})?)',
            r'settlement range.*?\$[0-9,]+(?:\.[0-9]{2})? to \$([0-9,]+(?:\.[0-9]{2})?)',
            r'settlement.*?\$([0-9,]+(?:\.[0-9]{2})?)',
            r'\$([0-9,]+(?:\.[0-9]{2})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, analysis, re.IGNORECASE)
            if matches:
                try:
                    # Take the first match and convert to float
                    return float(matches[0].replace(',', ''))
                except (ValueError, IndexError):
                    continue
        
        return default_value
