from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response

from reconciliation.comparison import compare_systems
from reconciliation.serializers import DisagreementSerializer


class DisagreementListView(APIView):

    def get(self, request):
        results = compare_systems()

        # Filter by disagreement reason
        reason = request.query_params.get("reason")

        if reason:
            results = [
                item for item in results
                if item["reason"] == reason
            ]

        # Sort by System A or System B value
        sort_by = request.query_params.get("sort_by")
        order = request.query_params.get("order", "asc")

        if sort_by in ["system_a_value", "system_b_value"]:
            results.sort(
                key=lambda item: (
                    item[sort_by] is None,
                    float(item[sort_by])
                    if item[sort_by] is not None else 0
                ),
                reverse=(order == "desc"),
            )

        serializer = DisagreementSerializer(results, many=True)

        return Response({
            "count": len(results),
            "results": serializer.data,
        })
