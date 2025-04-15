"""
Enhanced SaaS Case Analysis Application

This module integrates the feature extraction, enhanced prompt templates, and confidence scoring
components with the existing Flask application to provide improved settlement predictions.
"""

import os
import json
import openai
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from enhanced_rag_system import EnhancedRAGSystem

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize our enhanced RAG system
rag_system = EnhancedRAGSystem()

@app.route('/')
def index():
    """Render the input form."""
    return render_template('input.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process the form data and analyze the case."""
    try:
        # Extract form data
        case_data = {
            'title': request.form.get('title', ''),
            'case_number': request.form.get('case_number', ''),
            'court': request.form.get('court', ''),
            'date_filed': request.form.get('date_filed', ''),
            'judge': request.form.get('judge', ''),
            'claim_type': request.form.get('claim_type', ''),
            'facts': request.form.get('facts', ''),
            'injury_details': request.form.get('injury_details', ''),
            'injury_types': request.form.getlist('injury_types'),
            'insurance_company': request.form.get('insurance_company', ''),
            'plaintiff_medical_expert': request.form.get('plaintiff_medical_expert', ''),
            'defendant_medical_expert': request.form.get('defendant_medical_expert', ''),
            'plaintiff_non_medical_expert': request.form.get('plaintiff_non_medical_expert', ''),
            'defendant_non_medical_expert': request.form.get('defendant_non_medical_expert', '')
        }
        
        # Convert damages to float if provided
        damages = request.form.get('damages', '')
        if damages:
            try:
                case_data['damages'] = float(damages.replace(',', '').replace('$', ''))
            except ValueError:
                case_data['damages'] = 0
        
        # Analyze the case using our enhanced RAG system
        analysis_result = rag_system.analyze_case(case_data)
        
        # For demo purposes, store the result in a unique ID
        # In a real application, this would be stored in a database
        result_id = '12345'  # This would be a unique ID in a real application
        
        # Return the result page with the result ID
        return redirect(url_for('results', id=result_id))
    
    except Exception as e:
        # Log the error
        print(f"Error analyzing case: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return an error message
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/results')
def results():
    """Render the results page."""
    return render_template('enhanced_results.html')

@app.route('/api/results/<result_id>')
def get_results(result_id):
    """API endpoint to get the analysis results."""
    # In a real application, this would fetch the results from a database
    # For demo purposes, we'll return a mock result
    mock_result = {
        'prediction': 'Based on the analysis of similar cases and the specific details of this case, I predict a settlement value of $75,000 to $95,000, with $85,000 being the most likely outcome.',
        'settlement_value': 85000,
        'confidence': {
            'overall_score': 7.8,
            'classification': 'High Confidence',
            'explanation': 'The overall confidence in this prediction is classified as \'High Confidence\' with a score of 7.8/10. This consensus score combines multiple confidence measures where the multi-dimensional assessment provides the strongest support, while the similar case comparison contributes less certainty. Specifically, the multi-dimensional assessment indicates high confidence, statistical analysis shows moderate prediction intervals, and similar case comparison provides moderate support.',
            'detailed_scores': {
                'multi_dimensional_confidence': {
                    'dimension_scores': {
                        'evidential_confidence': 0.82,
                        'methodological_confidence': 0.75,
                        'precedential_confidence': 0.68,
                        'data_adequacy_confidence': 0.79,
                        'stability_confidence': 0.71
                    },
                    'dimension_weights': {
                        'evidential_confidence': 0.25,
                        'methodological_confidence': 0.15,
                        'precedential_confidence': 0.20,
                        'data_adequacy_confidence': 0.25,
                        'stability_confidence': 0.15
                    },
                    'overall_confidence_score': 7.6
                },
                'statistical_confidence': {
                    'point_estimate': 85000,
                    'confidence_intervals': {
                        '90%': {
                            'lower': 65000,
                            'upper': 105000
                        },
                        '80%': {
                            'lower': 70000,
                            'upper': 100000
                        },
                        '50%': {
                            'lower': 78000,
                            'upper': 92000
                        }
                    }
                },
                'similarity_confidence': {
                    'similarity_confidence_score': 6.8
                }
            }
        },
        'similar_cases': [
            {
                'id': 'case1',
                'title': 'Smith v. Johnson',
                'similarity': 0.85,
                'description': 'Personal injury case with similar damages and injury profile. Settled for $82,500.'
            },
            {
                'id': 'case2',
                'title': 'Davis v. City Hospital',
                'similarity': 0.78,
                'description': 'Medical malpractice case with comparable injuries. Settled for $90,000.'
            },
            {
                'id': 'case3',
                'title': 'Wilson v. ABC Insurance',
                'similarity': 0.72,
                'description': 'Auto accident case with similar liability profile. Settled for $78,000.'
            }
        ],
        'extracted_features': {
            'case_characteristics': {
                'case_type': {
                    'primary_type': 'personal_injury',
                    'subtypes': ['auto_accident'],
                    'complexity': 'moderate'
                },
                'jurisdiction': {
                    'jurisdiction': 'California',
                    'venue_characteristics': 'plaintiff-friendly'
                },
                'damages': {
                    'total_damages': 85000,
                    'economic_damages': 35000,
                    'non_economic_damages': 50000
                }
            },
            'composite': {
                'settlement_pressure_index': {
                    'overall_index': 7.2,
                    'time_pressure': 'moderate',
                    'financial_pressure': 'high'
                },
                'case_strength_ratio': {
                    'strength_ratio': 1.4,
                    'plaintiff_strength': 'moderate-high',
                    'defendant_strength': 'moderate'
                },
                'litigation_risk_profile': {
                    'overall_risk_level': 'moderate',
                    'outcome_uncertainty': 'moderate',
                    'damage_range_width': 'moderate'
                }
            }
        },
        'visualization_data': {
            'confidence_meter': {
                'score': 7.8,
                'classification': 'High Confidence',
                'color': '#4CAF50'
            },
            'confidence_breakdown': {
                'labels': ['Evidential', 'Methodological', 'Precedential', 'Data Adequacy', 'Stability'],
                'scores': [8.2, 7.5, 6.8, 7.9, 7.1],
                'weights': [0.25, 0.15, 0.20, 0.25, 0.15]
            },
            'confidence_intervals': {
                'point_estimate': 85000,
                'intervals': {
                    '90%': {
                        'lower': 65000,
                        'upper': 105000
                    },
                    '80%': {
                        'lower': 70000,
                        'upper': 100000
                    },
                    '50%': {
                        'lower': 78000,
                        'upper': 92000
                    }
                }
            }
        }
    }
    
    return jsonify(mock_result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
