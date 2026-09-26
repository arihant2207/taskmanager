from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from utils.auth import require_auth
from utils.supabase_client import get_supabase_client
from utils.email import send_task_created_email, send_task_completed_email

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api')

@tasks_bp.route('/tasks', methods=['GET'])
@require_auth
def get_tasks():
    user_id = request.user_id
    supabase = get_supabase_client()
    try:
        response = supabase.table('tasks').select('*').or_(f'created_by.eq.{user_id},assigned_to.eq.{user_id}').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/users', methods=['GET'])
@require_auth
def get_users():
    supabase = get_supabase_client()
    try:
        response = supabase.table('profiles').select('id, email, full_name').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks', methods=['POST'])
@require_auth
def create_task():
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    assigned_to = data.get('assigned_to')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    supabase = get_supabase_client()
    task_payload = {
        'title': title,
        'description': description,
        'created_by': request.user_id,
        'assigned_to': assigned_to if assigned_to else None,
        'status': 'todo'
    }

    try:
        response = supabase.table('tasks').insert(task_payload).execute()
        if not response.data:
            return jsonify({'error': 'Failed to create task'}), 500
        
        created_task = response.data[0]

        if assigned_to:
            try:
                profile_resp = supabase.table('profiles').select('email, full_name').eq('id', assigned_to).execute()
                if profile_resp.data:
                    assignee = profile_resp.data[0]
                    send_task_created_email(
                        assignee_email=assignee.get('email', ''),
                        assignee_name=assignee.get('full_name') or assignee.get('email', ''),
                        task_title=created_task.get('title', '')
                    )
            except Exception as mail_err:
                print(f"Failed to send task assignment email: {mail_err}")

        return jsonify(created_task), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<task_id>', methods=['PATCH'])
@require_auth
def update_task(task_id):
    supabase = get_supabase_client()
    try:
        existing_resp = supabase.table('tasks').select('*').eq('id', task_id).execute()
        if not existing_resp.data:
            return jsonify({'error': 'Task not found'}), 404
        
        existing_task = existing_resp.data[0]
        if existing_task['created_by'] != request.user_id and existing_task['assigned_to'] != request.user_id:
            return jsonify({'error': 'Unauthorized to update this task'}), 403

        data = request.get_json() or {}
        updates = {}

        new_status = data.get('status')
        if new_status:
            updates['status'] = new_status
            if new_status == 'done':
                updates['completed_at'] = datetime.now(timezone.utc).isoformat()
            else:
                updates['completed_at'] = None

        if 'title' in data:
            updates['title'] = data['title']
        if 'description' in data:
            updates['description'] = data['description']
        if 'assigned_to' in data:
            updates['assigned_to'] = data['assigned_to']

        if not updates:
            return jsonify(existing_task), 200

        update_resp = supabase.table('tasks').update(updates).eq('id', task_id).execute()
        if not update_resp.data:
            return jsonify({'error': 'Failed to update task'}), 500

        updated_task = update_resp.data[0]

        if new_status == 'done' and existing_task.get('status') != 'done':
            creator_id = existing_task.get('created_by')
            if creator_id:
                try:
                    profile_resp = supabase.table('profiles').select('email, full_name').eq('id', creator_id).execute()
                    if profile_resp.data:
                        creator = profile_resp.data[0]
                        send_task_completed_email(
                            creator_email=creator.get('email', ''),
                            creator_name=creator.get('full_name') or creator.get('email', ''),
                            task_title=updated_task.get('title', '')
                        )
                except Exception as mail_err:
                    print(f"Failed to send task completion email: {mail_err}")

        return jsonify(updated_task), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
