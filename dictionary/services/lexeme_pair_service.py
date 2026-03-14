from django.utils.text import slugify

from dictionary.models import (
    TextLemma,
    GestureLemma,
    Meaning,
    TextMeaningMapping,
    GestureMeaningMapping,
    LexemePair
)


def create_pair(text, user):

    text = text.strip().lower()

    text_lemma, _ = TextLemma.objects.get_or_create(
        text=text,
        defaults={
            "slug": slugify(text),
            "author": user
        }
    )

    gesture_lemma, _ = GestureLemma.objects.get_or_create(
        text=text,
        defaults={
            "author": user
        }
    )

    meaning = Meaning.objects.create(
        description=text
    )

    TextMeaningMapping.objects.get_or_create(
        text_lemma=text_lemma,
        meaning=meaning,
        defaults={"is_primary": True}
    )

    GestureMeaningMapping.objects.get_or_create(
        gesture_lemma=gesture_lemma,
        meaning=meaning,
        defaults={"is_primary": True}
    )

    pair = LexemePair.objects.create(
        text_lemma=text_lemma,
        gesture_lemma=gesture_lemma,
        meaning=meaning,
        created_by=user
    )

    return pair
