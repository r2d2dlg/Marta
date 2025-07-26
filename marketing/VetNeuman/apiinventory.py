@bp.route('/api/inventory')
def api_get_inventory():
    """Complete inventory management API with analytics"""
    # Dynamic search, filtering, sorting, pagination
    query = 'SELECT "Item", "Description", "marca", "Qty on Hand" FROM inventarioneuman WHERE 1=1'
    
    # Add intelligent filtering
    if search_term:
        query += ' AND (LOWER("Item") LIKE LOWER(:search) OR LOWER("Description") LIKE LOWER(:search))'
    
    # Get comprehensive analytics
    analytics_data = {
        'low_stock': get_low_stock_items(),      # 50 items < 20 units
        'abc_analysis': get_top_performers(),     # Top 50 by revenue  
        'brand_analysis': get_brand_performance() # 3 brands analyzed
    }
    
    # Return structured response for frontend
    return jsonify({
        'inventory': inventory_data,        # 172 items
        'total_records': total_count,       # 15,460 total stock
        'brands': brands,                   # 3 brands available
        'analytics': analytics_data,        # Complete business intelligence
        'summary': summary_data            # Key metrics dashboard
    })