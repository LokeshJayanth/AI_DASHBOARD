from flask import Blueprint, request, jsonify
from services.db_service import create_prompt, get_all_prompts
from services.prompt_service import process_prompt

prompt_bp = Blueprint('prompt', __name__)

@prompt_bp.route('/')
def list_prompts():
    """List all prompts/queries"""
    prompts = get_all_prompts()
    return jsonify({'success': True, 'prompts': prompts or []}), 200

@prompt_bp.route('/submit', methods=['POST'])
def submit_prompt():
    """Submit a new prompt/query"""
    data = request.get_json()
    
    if not data or 'prompt_text' not in data:
        return jsonify({'success': False, 'error': 'Prompt text required'}), 400
    
    prompt_text = data['prompt_text']
    dataset_id = data.get('dataset_id')
    user_id = data.get('user_id', 1)  # Default user for now
    
    # Create prompt record
    prompt_id = create_prompt(user_id, dataset_id, prompt_text)
    
    if prompt_id:
        # Process the prompt (async in production)
        success, response = process_prompt(prompt_id, prompt_text, dataset_id)
        
        return jsonify({
            'success': True,
            'prompt_id': prompt_id,
            'response': response
        }), 200
    else:
        return jsonify({'success': False, 'error': 'Failed to create prompt'}), 500

@prompt_bp.route('/<int:prompt_id>')
def get_prompt(prompt_id):
    """Get a specific prompt and its response"""
    from services.db_service import execute_query
    
    query = "SELECT * FROM prompts WHERE id = %s"
    result = execute_query(query, (prompt_id,), fetch=True)
    
    if result:
        return jsonify({'success': True, 'prompt': result[0]}), 200
    else:
        return jsonify({'success': False, 'error': 'Prompt not found'}), 404
