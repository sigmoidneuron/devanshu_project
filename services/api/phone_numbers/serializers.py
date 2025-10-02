from __future__ import annotations

from rest_framework import serializers

from shared.core.models import Number
from shared.core.validators import AREA_CODE_REGEX, PHONE_NUMBER_REGEX


class PrefixSerializer(serializers.Serializer):
    area_code = serializers.RegexField(AREA_CODE_REGEX)
    count = serializers.IntegerField(min_value=0)


class SearchQuerySerializer(serializers.Serializer):
    area_code = serializers.RegexField(AREA_CODE_REGEX)
    number = serializers.RegexField(PHONE_NUMBER_REGEX)


class SearchResultSerializer(serializers.Serializer):
    area_code = serializers.RegexField(AREA_CODE_REGEX)
    phone_number = serializers.RegexField(PHONE_NUMBER_REGEX)
    full_number = serializers.CharField()
    cost = serializers.IntegerField(min_value=0)
    similarity_score = serializers.FloatField()
    distance = serializers.IntegerField(min_value=0)
