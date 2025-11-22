from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    """
    Pagination class for messages.
    Fetches 20 messages per page.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Override to include page.paginator.count in response"""
        response = super().get_paginated_response(data)
        # Access page.paginator.count for total count
        if hasattr(self, 'page') and self.page:
            total_count = self.page.paginator.count
            response.data['total_count'] = total_count
        return response

