from typing import Any, Dict, List, Optional
from app.supabase_client import supabase


def fetch_pending_answers(limit: int = 100) -> List[Dict[str, Any]]:
    response = (
        supabase.table("answers_raw")
        .select("*")
        .eq("status", "pending")
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return response.data or []


def fetch_pending_asks(limit: int = 100) -> List[Dict[str, Any]]:
    response = (
        supabase.table("asks_raw")
        .select("*")
        .eq("status", "pending")
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return response.data or []


def insert_answers_raw(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    supabase.table("answers_raw").insert(rows).execute()


def insert_asks_raw(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    supabase.table("asks_raw").insert(rows).execute()


def mark_answers_processing(answer_ids: List[str]) -> None:
    if not answer_ids:
        return

    (
        supabase.table("answers_raw")
        .update({"status": "processing"})
        .in_("id", answer_ids)
        .execute()
    )


def mark_answers_processed(answer_ids: List[str]) -> None:
    if not answer_ids:
        return

    (
        supabase.table("answers_raw")
        .update({"status": "processed"})
        .in_("id", answer_ids)
        .execute()
    )


def mark_answers_error(answer_ids: List[str], error_message: str) -> None:
    if not answer_ids:
        return

    (
        supabase.table("answers_raw")
        .update({
            "status": "error",
            "error_message": error_message
        })
        .in_("id", answer_ids)
        .execute()
    )


def mark_asks_processing(ask_ids: List[str]) -> None:
    if not ask_ids:
        return

    (
        supabase.table("asks_raw")
        .update({"status": "processing"})
        .in_("id", ask_ids)
        .execute()
    )


def mark_asks_processed(ask_ids: List[str]) -> None:
    if not ask_ids:
        return

    (
        supabase.table("asks_raw")
        .update({"status": "processed"})
        .in_("id", ask_ids)
        .execute()
    )


def mark_asks_error(ask_ids: List[str], error_message: str) -> None:
    if not ask_ids:
        return

    (
        supabase.table("asks_raw")
        .update({
            "status": "error",
            "error_message": error_message
        })
        .in_("id", ask_ids)
        .execute()
    )


def upsert_answer_analysis_results(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return

    supabase.table("answer_analysis_results").upsert(
        rows,
        on_conflict="answer_id"
    ).execute()


def upsert_dashboard_cache(payload: Dict[str, Any]) -> None:
    supabase.table("dashboard_cache").upsert(
        {
            "cache_key": "latest",
            "payload": payload,
            "source": "fastapi"
        },
        on_conflict="cache_key"
    ).execute()


def create_analysis_run() -> Optional[str]:
    response = supabase.table("analysis_runs").insert(
        {"status": "running"}
    ).execute()

    data = response.data or []
    return data[0]["id"] if data else None


def finish_analysis_run(
    run_id: Optional[str],
    status: str,
    total_answers_read: int,
    total_answers_processed: int,
    total_asks_read: int = 0,
    total_asks_processed: int = 0,
    message: str = "",
    payload_summary: Optional[Dict[str, Any]] = None
) -> None:
    if not run_id:
        return

    (
        supabase.table("analysis_runs")
        .update(
            {
                "status": status,
                "finished_at": "now()",
                "total_answers_read": total_answers_read,
                "total_answers_processed": total_answers_processed,
                "total_asks_read": total_asks_read,
                "total_asks_processed": total_asks_processed,
                "message": message,
                "payload_summary": payload_summary or {},
            }
        )
        .eq("id", run_id)
        .execute()
    )