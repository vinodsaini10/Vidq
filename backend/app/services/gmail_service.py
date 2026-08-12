import logging
import httpx
from typing import Dict, Any, List, Optional
from app.core.encryption import decrypt_token

logger = logging.getLogger("gmail_service")

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class GmailService:
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch Google User Profile info (email, name, picture)."""
        plain_token = decrypt_token(access_token) if len(access_token) > 100 and " " not in access_token else access_token
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {plain_token}"}
            )
            if resp.status_code != 200:
                logger.error(f"Failed to fetch Google user profile: {resp.text}")
                return {}
            return resp.json()

    async def get_gmail_profile(self, access_token: str) -> Dict[str, Any]:
        """Fetch Gmail Account Details (email address, messagesTotal, threadsTotal)."""
        plain_token = decrypt_token(access_token) if len(access_token) > 100 and " " not in access_token else access_token
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{GMAIL_API_BASE}/profile",
                headers={"Authorization": f"Bearer {plain_token}"}
            )
            if resp.status_code != 200:
                logger.error(f"Failed to fetch Gmail profile: {resp.text}")
                return {}
            return resp.json()

    async def list_recent_messages(
        self, access_token: str, max_results: int = 10, query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List recent Gmail messages or search for sponsorship/channel inquiries."""
        plain_token = decrypt_token(access_token) if len(access_token) > 100 and " " not in access_token else access_token
        params = {"maxResults": max_results}
        if query:
            params["q"] = query

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{GMAIL_API_BASE}/messages",
                headers={"Authorization": f"Bearer {plain_token}"},
                params=params,
            )
            if resp.status_code != 200:
                logger.error(f"Failed to list Gmail messages: {resp.text}")
                return []
            
            data = resp.json()
            messages_summary = []
            message_stubs = data.get("messages", [])

            for msg_stub in message_stubs[:max_results]:
                msg_id = msg_stub.get("id")
                if not msg_id:
                    continue
                
                detail_resp = await client.get(
                    f"{GMAIL_API_BASE}/messages/{msg_id}",
                    headers={"Authorization": f"Bearer {plain_token}"},
                    params={"format": "full"},
                )
                if detail_resp.status_code == 200:
                    detail = detail_resp.json()
                    headers = {h.get("name", "").lower(): h.get("value", "") for h in detail.get("payload", {}).get("headers", [])}
                    messages_summary.append({
                        "id": detail.get("id"),
                        "thread_id": detail.get("threadId"),
                        "snippet": detail.get("snippet"),
                        "subject": headers.get("subject", "No Subject"),
                        "from": headers.get("from", "Unknown"),
                        "date": headers.get("date", ""),
                        "unread": "UNREAD" in detail.get("labelIds", []),
                    })

            return messages_summary


gmail_service = GmailService()
