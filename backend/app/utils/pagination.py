from flask import request

def get_pagination_params():
    """
    Get pagination parameters from request arguments
    
    Returns:
        Tuple of (page, per_page)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Enforce limits
    page = max(1, page)
    per_page = min(max(1, per_page), 100)  # Limit to 100 items per page
    
    return page, per_page

def paginate_query(query, page, per_page):
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query
        page: Page number
        per_page: Items per page
        
    Returns:
        Dict with items and pagination info
    """
    paginated = query.paginate(page=page, per_page=per_page)
    
    return {
        "items": paginated.items,
        "pagination": {
            "total": paginated.total,
            "pages": paginated.pages,
            "current_page": paginated.page,
            "per_page": per_page,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev
        }
    }
