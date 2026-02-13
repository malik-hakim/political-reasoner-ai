

#app/routes.py
from flask import Blueprint, request, jsonify , render_template
from .reasoner import PoliticalReasoner
from .openai_manager import OpenAIManager
import json
import logging
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)
reasoner = PoliticalReasoner()
openai_manager = OpenAIManager()

# Route untuk UI
@main.route('/')
def index():
    """Render halaman utama dengan UI"""
    return render_template('index.html')

# route untuk API
@main.route('/health', methods=['GET'])
def health():
    ok, msg = openai_manager.test_connection()
    return jsonify({"status": "healthy" if ok else "unhealthy", "message": msg})

@main.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        analysis = reasoner.analyze_political_text(text)
        if "error" in analysis:
            return jsonify({"error": analysis["error"]}), 500
            
        insights = reasoner.extract_key_insights(analysis)
        if "error" in insights:
            return jsonify({"error": insights["error"]}), 500
            
        return jsonify({
            "analysis": analysis, 
            "key_insights": insights,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@main.route('/generate-narrative', methods=['POST'])
def narrative():
    try:
        data = request.get_json()
        analysis_data = data.get('analysis_data')
        if not analysis_data:
            return jsonify({"error": "Analysis data is required"}), 400
        
        narrative_result = reasoner.generate_narrative(analysis_data)
        if "error" in narrative_result:
            return jsonify({"error": narrative_result["error"]}), 500
            
        return jsonify({"narrative": narrative_result})
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@main.route('/policy-recommendations', methods=['POST'])
def policy():
    try:
        data = request.get_json()
        context = data.get('context', '')
        issue = data.get('issue', '')
        if not context or not issue:
            return jsonify({"error": "Context and issue are required"}), 400
        
        result = reasoner.generate_policy_recommendations(context, issue)
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
            
        return jsonify({"recommendations": result})
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@main.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('question', '')
        context = data.get('context')
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        response = reasoner.chat_response(question, context)
        if "error" in response:
            return jsonify({"error": response["error"]}), 500
            
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@main.route('/complete-analysis', methods=['POST'])
def complete():
    try:
        data = request.get_json()
        text = data.get('text')
        policy_context = data.get('policy_context')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Analisis dasar
        analysis = reasoner.analyze_political_text(text)
        if "error" in analysis:
            return jsonify({"error": f"Analysis failed: {analysis['error']}"}), 500
        
        # Extract insights
        insights = reasoner.extract_key_insights(analysis)
        if "error" in insights:
            return jsonify({"error": f"Insights extraction failed: {insights['error']}"}), 500
        
        # Generate narrative
        narrative = reasoner.generate_narrative(analysis)
        if "error" in narrative:
            return jsonify({"error": f"Narrative generation failed: {narrative['error']}"}), 500
        
        # Policy recommendations (optional)
        recommendations = None
        if policy_context and insights.get('critical_issues') and len(insights['critical_issues']) > 0:
            main_issue = insights['critical_issues'][0] if insights['critical_issues'][0] else "General policy issue"
            recommendations = reasoner.generate_policy_recommendations(policy_context, main_issue)
            if "error" in recommendations:
                # Don't fail the whole request if recommendations fail
                recommendations = {"error": recommendations["error"]}
        
        return jsonify({
            "complete_analysis": {
                "basic_analysis": analysis,
                "key_insights": insights,
                "narrative": narrative,
                "policy_recommendations": recommendations
            },
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
