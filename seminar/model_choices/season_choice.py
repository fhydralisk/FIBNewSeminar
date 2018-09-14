from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from seminar.utils.field_choice import FieldChoice


class _SeasonChoice(FieldChoice):
    MAX_LENGTH = 4
    CHOICE_DISPLAY = (
        (1, _("Spring"), "SPRING"),
        (2, _("Summer"), "SUMMER"),
        (3, _("Autumn"), "AUTUMN"),
        (4, _("Winter"), "WINTER"),
    )


season_choice = _SeasonChoice()
