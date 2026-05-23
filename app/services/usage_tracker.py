from .supabase_client import get_supabase

MAX_UPLOADS = 10


def get_user_count(user_id: str) -> int:
    result = get_supabase().table("upload_usage").select("count").eq("user_id", user_id).execute()
    return result.data[0]["count"] if result.data else 0


def increment_user_count(user_id: str) -> int:
    sb = get_supabase()
    count = get_user_count(user_id)
    new_count = count + 1
    if count == 0:
        sb.table("upload_usage").insert({"user_id": user_id, "count": new_count}).execute()
    else:
        sb.table("upload_usage").update({"count": new_count}).eq("user_id", user_id).execute()
    return new_count


def is_session_used(session_id: str) -> bool:
    result = (
        get_supabase()
        .table("anonymous_sessions")
        .select("used")
        .eq("session_id", session_id)
        .execute()
    )
    return result.data[0]["used"] if result.data else False


def mark_session_used(session_id: str) -> None:
    sb = get_supabase()
    existing = sb.table("anonymous_sessions").select("session_id").eq("session_id", session_id).execute()
    if existing.data:
        sb.table("anonymous_sessions").update({"used": True}).eq("session_id", session_id).execute()
    else:
        sb.table("anonymous_sessions").insert({"session_id": session_id, "used": True}).execute()
