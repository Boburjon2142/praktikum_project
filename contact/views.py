from typing import Dict

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods

from .utils import send_contact_message


@require_http_methods(["GET", "POST"])
def contact_view(request: HttpRequest) -> HttpResponse:
    """
    Handle contact form submissions.

    - On POST: read 'name', 'email', 'message', send to Telegram via utils.
      On success: show JS alert and then redirect (GET) to the same URL.
    - On GET: return a minimal OK response (placeholder) so this view is usable
      without requiring a template. Projects can render a proper template instead.
    """
    if request.method == "POST":
        name: str = (request.POST.get("name") or "").strip()
        email: str = (request.POST.get("email") or "").strip()
        message: str = (request.POST.get("message") or "").strip()

        if not (name and email and message):
            return HttpResponseBadRequest("Missing name, email, or message.")

        data: Dict[str, str] = {"name": name, "email": email, "message": message}
        ok = send_contact_message(data)

        if ok:
            # JavaScript alert before redirecting back to this page as GET
            target = request.path
            script = (
                "<script>"
                "alert('✅ Xabar muvaffaqiyatli yuborildi!');"
                f"window.location.href='{target}';"
                "</script>"
            )
            return HttpResponse(script)
        else:
            script = (
                "<script>"
                "alert('❌ Xabar yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko`ring.');"
                "history.back();"
                "</script>"
            )
            return HttpResponse(script, status=502)

    # Minimal placeholder GET response; replace with template render if desired
    return HttpResponse("Contact form endpoint is ready.")

