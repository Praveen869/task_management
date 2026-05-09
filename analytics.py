import pandas as pd
import numpy as np
from models import get_db_connection

def get_analytics(user_id):
    """
    Fetches tasks for a specific user and calculates summary analytics using Pandas and NumPy.
    
    Args:
        user_id (int): The ID of the user whose tasks will be analyzed.
        
    Returns:
        dict: A dictionary containing 'total_tasks', 'completed_tasks', 
              'pending_tasks', 'in_progress_tasks', and 'completion_percentage'.
    """
    conn = get_db_connection()
    
    # Database se tasks fetch karo
    df = pd.read_sql_query(
        "SELECT * FROM tasks WHERE user_id = %s",
        conn,
        params=(user_id,)
    )
    conn.close()
    
    # Agar koi task nahi hai
    if df.empty:
        return {
            'total_tasks': 0,
            'completed_tasks': 0,
            'pending_tasks': 0,
            'in_progress_tasks': 0,
            'completion_percentage': 0.0,
            'status_breakdown': {},
            'priority_breakdown': {},
            'tasks_per_day': {},
            'avg_tasks_per_day': 0.0
        }
    
    # Pandas & NumPy se analytics calculate karo
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['status'] = df['status'].str.lower()
    df['priority'] = df['priority'].str.lower()
    
    status_counts = df['status'].value_counts().to_dict()
    priority_counts = df['priority'].value_counts().to_dict()
    tasks_per_day = df['created_at'].dt.date.value_counts().sort_index()
    
    # NumPy use: calculate mean tasks per active day
    avg_tasks_per_day = np.round(np.mean(tasks_per_day.values), 2)
    
    total = len(df)
    completed = status_counts.get('completed', 0)
    pending = status_counts.get('pending', 0)
    in_progress = status_counts.get('in_progress', 0)
    
    # NumPy se percentage calculate karo
    completion_percentage = np.round((completed / total) * 100, 2) if total > 0 else 0.0
    
    return {
        'total_tasks': int(total),
        'completed_tasks': int(completed),
        'pending_tasks': int(pending),
        'in_progress_tasks': int(in_progress),
        'completion_percentage': float(completion_percentage),
        'status_breakdown': status_counts,
        'priority_breakdown': priority_counts,
        'tasks_per_day': {str(k): int(v) for k, v in tasks_per_day.to_dict().items()},
        'avg_tasks_per_day': float(avg_tasks_per_day)
    }