from django.db.models import Prefetch
from django.shortcuts import redirect, render

from .models import TeamMember, TeamPole


def team_list(request):
    poles = TeamPole.objects.filter(is_active=True).prefetch_related(
        Prefetch("members", queryset=TeamMember.objects.filter(is_active=True, is_verified=True))
    )
    poles = [pole for pole in poles if pole.members.all()]
    if not poles:
        return redirect("pages:about")
    return render(request, "team/list.html", {"poles": poles})
