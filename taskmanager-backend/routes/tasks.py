import traceback
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from utils.auth import require_auth
from utils.supabase_client import get_supabase_client
from utils.email import send_task_created_email, send_task_completed_email

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api')

@tasks_bp.route('/tasks', methods=['GET'])
@require_auth
def get_tasks():
    print("[ROUTE START] GET /api/tasks", flush=True)
    try:
        user_id = request.user_id
        print(f"[SUPABASE CALL START] Fetching tasks for user_id={user_id}", flush=True)
        supabase = get_supabase_client()
        response = supabase.table('tasks').select('*').or_(f'created_by.eq.{user_id},assigned_to.eq.{user_id}').execute()
        print(f"[SUPABASE CALL SUCCESS] Fetched {len(response.data) if response.data else 0} tasks", flush=True)
        print("[ROUTE END] GET /api/tasks successfully returning", flush=True)
        return jsonify(response.data), 200
    except Exception as e:
        print(f"[ROUTE EXCEPTION] GET /api/tasks failed: {e}", flush=True)
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch tasks: {str(e)}'}), 500

@tasks_bp.route('/users', methods=['GET'])
@require_auth
def get_users():
    print("[ROUTE START] GET /api/users", flush=True)
    try:
        print("[SUPABASE CALL START] Fetching profiles table...", flush=True)
        supabase = get_supabase_client()
        response = supabase.table('profiles').select('id, email, full_name').execute()
        print(f"[SUPABASE CALL SUCCESS] Fetched {len(response.data) if response.data else 0} profiles", flush=True)
        print("[ROUTE END] GET /api/users successfully returning", flush=True)
        return jsonify(response.data), 200
    except Exception as e:
        print(f"[ROUTE EXCEPTION] GET /api/users failed: {e}", flush=True)
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500

@tasks_bp.route('/tasks', methods=['POST'])
@require_auth
def create_task():
    print("[ROUTE START] POST /api/tasks", flush=True)
    try:
        data = request.get_json() or {}
        title = data.get('title')
        description = data.get('description')
        assigned_to = data.get('assigned_to')

        if not title:
            print("[ROUTE END] POST /api/tasks missing title", flush=True)
            return jsonify({'error': 'Title is required'}), 400

        task_payload = {
            'title': title,
            'description': description,
            'created_by': request.user_id,
            'assigned_to': assigned_to if assigned_to else None,
            'status': 'todo'
        }

        print("[SUPABASE CALL START] Inserting task...", flush=True)
        supabase = get_supabase_client()
        response = supabase.table('tasks').insert(task_payload).execute()
        if not response.data:
            print("[SUPABASE CALL ERROR] No data returned from task insert", flush=True)
            return jsonify({'error': 'Failed to create task'}), 500
        
        created_task = response.data[0]
        print(f"[SUPABASE CALL SUCCESS] Created task id={created_task.get('id')}", flush=True)

        if assigned_to:
            try:
                print(f"[SUPABASE CALL START] Fetching assignee profile for id={assigned_to}...", flush=True)
                profile_resp = supabase.table('profiles').select('email, full_name').eq('id', assigned_to).execute()
                if profile_resp.data:
                    assignee = profile_resp.data[0]
                    print(f"[EMAIL START] Sending task created email to {assignee.get('email')}...", flush=True)
                    send_task_created_email(
                        assignee_email=assignee.get('email', ''),
                        assignee_name=assignee.get('full_name') or assignee.get('email', ''),
                        task_title=created_task.get('title', '')
                    )
                    print("[EMAIL END] Task created email sent", flush=True)
            except Exception as mail_err:
                print(f"[EMAIL EXCEPTION] Failed to send task assignment email: {mail_err}", flush=True)
                traceback.print_exc()

        print("[ROUTE END] POST /api/tasks successfully returning", flush=True)
        return jsonify(created_task), 201
    except Exception as e:
        print(f"[ROUTE EXCEPTION] POST /api/tasks failed: {e}", flush=True)
        traceback.print_exc()
        return jsonify({'error': f'Failed to create task: {str(e)}'}), 500

@tasks_bp.route('/tasks/<task_id>', methods=['PATCH'])
@require_auth
def update_task(task_id):
    print(f"[ROUTE START] PATCH /api/tasks/{task_id}", flush=True)
    try:
        print(f"[SUPABASE CALL START] Fetching existing task id={task_id}...", flush=True)
        supabase = get_supabase_client()
        existing_resp = supabase.table('tasks').select('*').eq('id', task_id).execute()
        if not existing_resp.data:
            print(f"[SUPABASE CALL ERROR] Task id={task_id} not found", flush=True)
            return jsonify({'error': 'Task not found'}), 404
        
        existing_task = existing_resp.data[0]
        if existing_task['created_by'] != request.user_id and existing_task['assigned_to'] != request.user_id:
            print(f"[AUTH ERROR] User {request.user_id} unauthorized to update task {task_id}", flush=True)
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
            print("[ROUTE END] PATCH /api/tasks no updates provided, returning existing task", flush=True)
            return jsonify(existing_task), 200

        print(f"[SUPABASE CALL START] Updating task id={task_id}...", flush=True)
        update_resp = supabase.table('tasks').update(updates).eq('id', task_id).execute()
        if not update_resp.data:
            print("[SUPABASE CALL ERROR] Failed to update task", flush=True)
            return jsonify({'error': 'Failed to update task'}), 500

        updated_task = update_resp.data[0]
        print(f"[SUPABASE CALL SUCCESS] Updated task id={task_id}", flush=True)

        if new_status == 'done' and existing_task.get('status') != 'done':
            creator_id = existing_task.get('created_by')
            if creator_id:
                try:
                    print(f"[SUPABASE CALL START] Fetching creator profile for id={creator_id}...", flush=True)
                    profile_resp = supabase.table('profiles').select('email, full_name').eq('id', creator_id).execute()
                    if profile_resp.data:
                        creator = profile_resp.data[0]
                        print(f"[EMAIL START] Sending task completion email to {creator.get('email')}...", flush=True)
                        send_task_completed_email(
                            creator_email=creator.get('email', ''),
                            creator_name=creator.get('full_name') or creator.get('email', ''),
                            task_title=updated_task.get('title', '')
                        )
                        print("[EMAIL END] Task completion email sent", flush=True)
                except Exception as mail_err:
                    print(f"[EMAIL EXCEPTION] Failed to send task completion email: {mail_err}", flush=True)
                    traceback.print_exc()

        print(f"[ROUTE END] PATCH /api/tasks/{task_id} successfully returning", flush=True)
        return jsonify(updated_task), 200
    except Exception as e:
        print(f"[ROUTE EXCEPTION] PATCH /api/tasks/{task_id} failed: {e}", flush=True)
        traceback.print_exc()
        return jsonify({'error': f'Failed to update task: {str(e)}'}), 500
