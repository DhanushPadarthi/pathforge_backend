from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

from app.core.database import get_collection

router = APIRouter()

@router.get("/{user_id}")
async def get_user_analytics(user_id: str):
    """Get comprehensive analytics for a user"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        
        # Get all user roadmaps
        roadmaps = await roadmaps_collection.find({"user_id": user_id}).to_list(None)
        
        if not roadmaps:
            return {
                "learning_streak": 0,
                "total_time_spent": 0,
                "total_resources_completed": 0,
                "total_resources_skipped": 0,
                "total_modules_completed": 0,
                "average_progress": 0,
                "daily_activity": [],
                "weekly_summary": {
                    "this_week_hours": 0,
                    "this_week_resources": 0,
                    "this_week_progress": 0
                },
                "completion_rate": 0,
                "most_productive_day": None
            }
        
        # Calculate analytics
        all_activities = []
        total_time = 0
        total_resources_completed = 0
        total_resources_skipped = 0
        total_modules_completed = 0
        total_progress = 0
        
        for roadmap in roadmaps:
            modules = roadmap.get("modules", [])
            
            for module in modules:
                # Count completed modules
                if module.get("progress_percentage", 0) >= 100:
                    total_modules_completed += 1
                
                resources = module.get("resources", [])
                for resource in resources:
                    status = resource.get("status", "locked")
                    
                    if status == "completed":
                        total_resources_completed += 1
                        completed_at = resource.get("completed_at")
                        time_spent = resource.get("time_spent_minutes", 15)  # Default 15 min
                        
                        if completed_at:
                            all_activities.append({
                                "date": completed_at,
                                "type": "completed",
                                "time_spent": time_spent
                            })
                            total_time += time_spent
                    
                    elif status == "skipped":
                        total_resources_skipped += 1
                        skipped_at = resource.get("skipped_at")
                        if skipped_at:
                            all_activities.append({
                                "date": skipped_at,
                                "type": "skipped",
                                "time_spent": 0
                            })
            
            total_progress += roadmap.get("progress_percentage", 0)
        
        average_progress = total_progress / len(roadmaps) if roadmaps else 0
        
        # Calculate learning streak
        learning_streak = calculate_learning_streak(all_activities)
        
        # Calculate daily activity
        daily_activity = calculate_daily_activity(all_activities)
        
        # Calculate weekly summary
        weekly_summary = calculate_weekly_summary(all_activities)
        
        # Calculate completion rate
        total_resources = total_resources_completed + total_resources_skipped
        completion_rate = (total_resources_completed / total_resources * 100) if total_resources > 0 else 0
        
        # Find most productive day
        most_productive_day = find_most_productive_day(all_activities)
        
        return {
            "learning_streak": learning_streak,
            "total_time_spent": total_time,
            "total_resources_completed": total_resources_completed,
            "total_resources_skipped": total_resources_skipped,
            "total_modules_completed": total_modules_completed,
            "average_progress": round(average_progress, 1),
            "daily_activity": daily_activity,
            "weekly_summary": weekly_summary,
            "completion_rate": round(completion_rate, 1),
            "most_productive_day": most_productive_day
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_learning_streak(activities: List[Dict]) -> int:
    """Calculate consecutive days of learning activity"""
    if not activities:
        return 0
    
    # Extract unique activity dates
    activity_dates = set()
    for activity in activities:
        date = activity["date"]
        if isinstance(date, datetime):
            activity_dates.add(date.date())
        elif isinstance(date, str):
            try:
                activity_dates.add(datetime.fromisoformat(date.replace('Z', '+00:00')).date())
            except:
                continue
    
    if not activity_dates:
        return 0
    
    # Sort dates
    sorted_dates = sorted(activity_dates, reverse=True)
    
    # Check if today or yesterday has activity
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    
    if sorted_dates[0] not in [today, yesterday]:
        return 0  # Streak broken
    
    # Count consecutive days
    streak = 1
    current_date = sorted_dates[0]
    
    for i in range(1, len(sorted_dates)):
        expected_date = current_date - timedelta(days=1)
        if sorted_dates[i] == expected_date:
            streak += 1
            current_date = sorted_dates[i]
        else:
            break
    
    return streak

def calculate_daily_activity(activities: List[Dict]) -> List[Dict]:
    """Calculate activity for last 30 days"""
    if not activities:
        return []
    
    # Group by date
    daily_stats = defaultdict(lambda: {"completed": 0, "time_spent": 0})
    
    for activity in activities:
        date = activity["date"]
        if isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d")
        elif isinstance(date, str):
            try:
                date_str = datetime.fromisoformat(date.replace('Z', '+00:00')).strftime("%Y-%m-%d")
            except:
                continue
        else:
            continue
        
        if activity["type"] == "completed":
            daily_stats[date_str]["completed"] += 1
            daily_stats[date_str]["time_spent"] += activity.get("time_spent", 0)
    
    # Get last 30 days
    result = []
    today = datetime.utcnow().date()
    
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        result.append({
            "date": date_str,
            "completed": daily_stats[date_str]["completed"],
            "time_spent": daily_stats[date_str]["time_spent"]
        })
    
    return result

def calculate_weekly_summary(activities: List[Dict]) -> Dict:
    """Calculate summary for current week"""
    if not activities:
        return {"this_week_hours": 0, "this_week_resources": 0, "this_week_progress": 0}
    
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    
    this_week_time = 0
    this_week_resources = 0
    
    for activity in activities:
        date = activity["date"]
        if isinstance(date, datetime):
            activity_date = date.date()
        elif isinstance(date, str):
            try:
                activity_date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
            except:
                continue
        else:
            continue
        
        if activity_date >= week_start:
            if activity["type"] == "completed":
                this_week_resources += 1
                this_week_time += activity.get("time_spent", 0)
    
    return {
        "this_week_hours": round(this_week_time / 60, 1),
        "this_week_resources": this_week_resources,
        "this_week_progress": this_week_resources  # Simplified metric
    }

def find_most_productive_day(activities: List[Dict]) -> str:
    """Find the day of week with most completions"""
    if not activities:
        return None
    
    day_counts = defaultdict(int)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for activity in activities:
        if activity["type"] != "completed":
            continue
        
        date = activity["date"]
        if isinstance(date, datetime):
            day_index = date.weekday()
        elif isinstance(date, str):
            try:
                day_index = datetime.fromisoformat(date.replace('Z', '+00:00')).weekday()
            except:
                continue
        else:
            continue
        
        day_counts[day_index] += 1
    
    if not day_counts:
        return None
    
    most_productive = max(day_counts.items(), key=lambda x: x[1])
    return days_of_week[most_productive[0]]
