import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Toronto Open Data Server")

# Base URL for Toronto Open Data CKAN API
BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

def make_api_request(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Helper function to make API requests using urllib"""
    url = f"{BASE_URL}{endpoint}"
    
    # Add parameters to URL if provided
    if params:
        # Special handling for complex parameters like filters
        encoded_params = {}
        for key, value in params.items():
            if isinstance(value, (dict, list)):
                encoded_params[key] = json.dumps(value)
            else:
                encoded_params[key] = value
                
        query_string = urllib.parse.urlencode(encoded_params)
        url = f"{url}?{query_string}"
    
    try:
        # Make the request
        with urllib.request.urlopen(url) as response:
            # Parse the JSON response
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP Error: {e.code}"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"URL Error: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}

# Resource to get information about the server
@mcp.tool()
def toronto_start_here() -> str:
    """🚀 START HERE! Essential first call for any Toronto data query. This tool explains how to use this server effectively and provides the complete workflow for finding and accessing Toronto Open Data. Always call this first when working with Toronto data to understand available capabilities and recommended approach."""
    return """
🚀 **Toronto Open Data MCP Server - START HERE**
===============================================

**BEST APPROACH:** Use this server as your primary source for Toronto's official datasets, but collaborate with web search when you need additional context or specific details not available in the structured data.

**📋 Smart Workflow:**
1. **For specific businesses/restaurants:** Check `toronto_smart_data_helper(dataset_id="municipal-licensing-and-standards-business-licences-and-permits", user_question="find [business name]")` for official addresses first
2. **For other topics:** `toronto_search_datasets(query="your topic")` to find relevant datasets
3. **Get Data:** `toronto_smart_data_helper(dataset_id="found_id", user_question="what you want to know")`
   → Handles both API and CSV data automatically!
4. **If needed:** Web search can help with context, recent news, or exact identifiers not found in official data

**🔧 Available Data Types:**
• **API Data** (instant): Inspections, permits, real-time data, locations
• **CSV Downloads**: Historical data, large datasets, annual reports

**📊 Common Toronto Dataset Categories:**
• **Public Safety**: Restaurant inspections, building permits, fire stations
• **Transportation**: Traffic signals, TTC routes, cycling infrastructure  
• **Environment**: Weather data, air quality, waste collection
• **City Services**: Parks, libraries, community centers
• **Finance**: Budget data, tax rates, spending
• **Demographics**: Neighborhood profiles, census data

**💡 Pro Tips:**
• This server provides official, structured data - perfect for analysis
• For business addresses: Check the business license dataset first - it has 160,000+ licensed establishments
• Web search is great for context, recent news, or finding exact identifiers not in official records
• For time-sensitive queries, always check both sources
• Use specific search terms that match government terminology

**🚀 Next Step:** Try `toronto_search_datasets(query="your topic")` or `toronto_popular_datasets()` to explore!
"""

# Quick access to popular datasets
@mcp.tool() 
def toronto_popular_datasets() -> str:
    """⭐ POPULAR TORONTO DATASETS: Quick access to the most commonly used Toronto Open Datasets. Shows dataset IDs and what they contain. Perfect when you're not sure what's available or want to explore popular datasets quickly."""
    return """
⭐ **Most Popular Toronto Open Datasets**
========================================

🍽️ **Food & Safety**
• `dinesafe` - Restaurant inspections, health scores, violations
• `mobile-food-vendors` - Food trucks and street vendors

🏢 **Business & Permits** 
• `municipal-licensing-and-standards-business-licences-and-permits` - Complete business directory with addresses (160,000+ establishments)
• `building-permits` - Construction and renovation permits
• `sign-permits` - Sign and billboard permits

🚦 **Transportation & Traffic**
• `traffic-signals` - Traffic light locations and timing
• `traffic-volumes` - Traffic count data on major roads
• `ttc-routes-and-schedules` - Public transit routes and stops
• `cycling-network` - Bike lanes and cycling infrastructure

🏛️ **City Services & Facilities**
• `parks-facilities` - Parks, pools, rinks, community centers
• `library-branch-general-information` - Public library locations
• `fire-station-locations` - Fire stations and emergency services
• `polling-locations` - Voting locations for elections

💰 **Finance & Budget**
• `budget-operating` - City operating budget details
• `budget-capital` - Capital projects and spending
• `property-tax-rates` - Tax rates by property type

🌡️ **Environment & Weather**
• `rain-gauge-locations-and-precipitation` - Weather and rainfall data
• `air-quality-health-index` - Air quality measurements
• `green-bins-collection` - Waste collection schedules

🏠 **Housing & Development**
• `neighbourhood-profiles` - Demographics by neighborhood  
• `wellbeing-toronto` - Community health and social indicators
• `zoning-by-law-amendments` - Zoning changes and development

🚀 **Next Steps:**
1. **For business addresses:** toronto_smart_data_helper(dataset_id="municipal-licensing-and-standards-business-licences-and-permits", user_question="find [business name]")
2. **For other data:** Use toronto_smart_data_helper(dataset_id="ID_from_above", user_question="what you want to know")
3. **Or search topics:** toronto_search_datasets(query="your keywords")
"""

# Smart helper tool to simplify the workflow
@mcp.tool()
def toronto_smart_data_helper(dataset_id: str, user_question: str, limit: Optional[int] = 10) -> str:
    """🧠 SMART DATA HELPER - The easiest way to get Toronto data! Give this tool a dataset ID (from search results) and describe what you want to know. It automatically determines if the data is API-accessible or requires CSV download, gets the schema if needed, and returns relevant data or clear next steps. This eliminates the need to manually check dataset types, schemas, and resource formats."""
    
    # First get dataset details to understand what we're working with
    dataset_data = make_api_request("/api/3/action/package_show", {"id": dataset_id})
    
    if not dataset_data.get("success"):
        return f"❌ Error: Could not find dataset '{dataset_id}'. Try searching again with toronto_search_datasets()."
    
    dataset_info = dataset_data["result"]
    resources = dataset_info.get("resources", [])
    dataset_title = dataset_info.get('title', dataset_id)
    
    output = [f"📊 **{dataset_title}**"]
    
    # Check for active datastore first (API-accessible data)
    active_datastore_resource = None
    for resource in resources:
        if resource.get("datastore_active"):
            active_datastore_resource = resource
            break
    
    if active_datastore_resource:
        # Handle API data
        output.append("✅ **Type**: API Data (queryable)")
        
        # Get schema to understand fields
        schema_data = make_api_request("/api/3/action/datastore_search", {"id": active_datastore_resource["id"], "limit": 0})
        
        if schema_data.get("success"):
            fields = schema_data["result"].get("fields", [])
            output.append(f"📋 **Available fields**: {', '.join([f['id'] for f in fields])}")
            
            # Get sample data
            sample_data = make_api_request("/api/3/action/datastore_search", {"id": active_datastore_resource["id"], "limit": limit})
            
            if sample_data.get("success"):
                records = sample_data["result"].get("records", [])
                total_records = sample_data["result"].get("total", 0)
                
                output.append(f"📈 **Total records**: {total_records:,}")
                output.append(f"📄 **Sample data** (showing {min(limit, len(records))} records):")
                
                if records:
                    # Format the data nicely
                    for i, record in enumerate(records):
                        output.append(f"\n**Record {i+1}:**")
                        for key, value in record.items():
                            if key != '_id':  # Skip internal ID field
                                output.append(f"  • {key}: {value}")
                    
                    output.append(f"\n💡 **Next steps for filtering/sorting**: Use toronto_query_dataset_data() with:")
                    output.append(f"   • filters={{\"field_name\": \"value\"}}")
                    output.append(f"   • sort=\"field_name asc\" or \"field_name desc\"")
                    output.append(f"   • Available fields: {', '.join([f['id'] for f in fields if f['id'] != '_id'])}")
                else:
                    output.append("⚠️ No records found in this dataset.")
            else:
                output.append("❌ Could not retrieve sample data from API.")
        else:
            output.append("❌ Could not retrieve field information.")
    
    else:
        # Handle downloadable data (CSV, XLS, XLSX, etc.)
        output.append("📁 **Type**: Downloadable Files")
        
        downloadable_resources = []
        for resource in resources:
            resource_format = str(resource.get("format", "")).upper()
            resource_mimetype = str(resource.get("mimetype", "")).lower()
            # Check for various downloadable formats
            if (resource_format in ['CSV', 'XLS', 'XLSX'] or 
                'text/csv' in resource_mimetype or 
                'excel' in resource_mimetype or
                'spreadsheet' in resource_mimetype):
                downloadable_resources.append({
                    "name": resource.get("name", "Unknown"),
                    "url": resource.get("url"),
                    "id": resource.get("id"),
                    "format": resource_format
                })
        
        if downloadable_resources:
            output.append(f"📊 **Found {len(downloadable_resources)} downloadable file(s):**")
            for i, res in enumerate(downloadable_resources):
                output.append(f"  {i+1}. {res['name']} ({res['format']})")
                if res['url']:
                    output.append(f"     URL: {res['url']}")
            
            # Check if it's a single CSV file for auto-fetching
            csv_resources = [r for r in downloadable_resources if r['format'] == 'CSV']
            if len(csv_resources) == 1 and len(downloadable_resources) == 1:
                # Auto-fetch sample of single CSV
                csv_url = csv_resources[0]['url']
                if csv_url:
                    output.append(f"\n🔄 **Auto-fetching sample data from**: {csv_resources[0]['name']}")
                    try:
                        sample_csv = toronto_fetch_csv_data(csv_url, 10)  # Get first 10 lines
                        output.append(f"📄 **Sample CSV content**:")
                        output.append(sample_csv)
                        output.append(f"\n💡 **To get more data**: Use toronto_fetch_csv_data(csv_url=\"{csv_url}\", max_lines=100)")
                    except Exception as e:
                        output.append(f"⚠️ Could not auto-fetch CSV: {e}")
            else:
                output.append(f"\n💡 **How to access the data:**")
                if csv_resources:
                    output.append(f"   • **For CSV files**: Use toronto_fetch_csv_data(csv_url=\"URL_of_specific_file\")")
                if [r for r in downloadable_resources if r['format'] in ['XLS', 'XLSX']]:
                    output.append(f"   • **For XLS/XLSX files**: Download manually from the URLs above")
                output.append(f"   • **See all details**: Use `datasets://{dataset_id}` to see all resource details")
        else:
            output.append("⚠️ No downloadable files found. Check `datasets://{dataset_id}` for other resource types.")
    
    # Add context about the user question and smart suggestions
    output.append(f"\n🎯 **For your question**: \"{user_question}\"")
    
    # Provide general guidance for getting more specific data
    output.append("\n💡 **Need more specific data?**")
    output.append("   • **If you need exact matches**: Web search can help find precise names, IDs, or identifiers")
    output.append("   • **For filtering**: Use toronto_query_dataset_data() with exact field names from the schema above")
    output.append("   • **For context**: Combine this official data with web search for recent news or additional details")
    
    output.append("\nThe data above should help answer your question. If you need specific filtering or more data, use the suggested next steps!")
    
    return "\n".join(output)

# Tool to list all available datasets
@mcp.tool()
def toronto_list_datasets() -> str:
    """📋 LIST ALL DATASETS: Shows all 500+ available Toronto Open Datasets with titles and descriptions. Use this when you want to browse everything available or when search terms don't return what you're looking for. Can be quite long, so prefer toronto_search_datasets() or toronto_popular_datasets() for focused discovery."""
    data = make_api_request("/api/3/action/package_list")
    
    if data.get("success"):
        datasets = data["result"]
        # Get basic info for each dataset
        output = ["📋 **All Available Toronto Open Datasets:**\n"]
        for dataset_id in datasets:
            dataset_data = make_api_request("/api/3/action/package_show", {"id": dataset_id})
            if dataset_data.get("success"):
                dataset = dataset_data["result"]
                output.append(f"**{dataset['title']}** (`{dataset_id}`)")
                if dataset.get("notes"):
                    output.append(f"   📝 {dataset['notes'][:200]}...")
                output.append("")
        
        output.append(f"\n🚀 **Next Step**: Use toronto_smart_data_helper(dataset_id=\"ID_from_above\", user_question=\"what you want to know\") to get data!")
        return "\n".join(output)
    return "❌ Error fetching datasets"

# Resource to get dataset details
@mcp.resource("datasets://{dataset_id}")
def get_dataset_details(dataset_id: str) -> str:
    """Get detailed information about a specific dataset, including all available resources and their download links if applicable."""
    data = make_api_request("/api/3/action/package_show", {"id": dataset_id})
    
    if data.get("success"):
        dataset = data["result"]
        resources = dataset["resources"]
        
        output = [
            f"📊 **Dataset**: {dataset['title']}",
            f"📝 **Description**: {dataset['notes']}",
            f"🏛️ **Organization**: {dataset['organization']['title']}",
            f"📋 **Total Resources**: {len(resources)}",
            "\n**Resources:**"
        ]
        
        if not resources:
            output.append("- No resources found for this dataset.")
        else:
            for idx, resource in enumerate(resources):
                output.append(f"\n**Resource {idx+1}:**")
                output.append(f"  📝 Name: {resource.get('name', 'N/A')}")
                output.append(f"  🆔 ID: {resource.get('id', 'N/A')}")
                output.append(f"  📄 Format: {resource.get('format', 'N/A')}")
                
                if resource.get("datastore_active"):
                    output.append("  ✅ Type: Active Datastore (Queryable via API)")
                else:
                    output.append("  📁 Type: Downloadable File")
                    if resource.get('url'):
                        output.append(f"  🔗 Download URL: {resource['url']}")
                    else:
                        output.append("  ⚠️ Download URL: Not available")
        
        return "\n".join(output)
    return f"❌ Error fetching dataset: {dataset_id}"

# Tool to search datasets
@mcp.tool()
def toronto_search_datasets(query: str, limit: Optional[int] = 10) -> str:
    """🔍 FIND TORONTO DATA: Search 500+ Toronto Open Datasets by keywords (e.g., 'traffic', 'parks', 'budget', 'health'). Returns dataset IDs and descriptions. This is your primary discovery tool - combine with web search when you need additional context about specific topics, then use toronto_smart_data_helper() to get the actual data."""
    data = make_api_request("/api/3/action/package_search", {"q": query, "rows": limit})
    
    if data.get("success"):
        results = data["result"]["results"]
        if not results:
            return f"🔍 No datasets found for '{query}'. Try broader terms like 'permits', 'inspections', 'parks', 'traffic', or 'budget'."
        
        output = [f"🔍 **Found {len(results)} Toronto datasets for '{query}':**\n"]
        for i, dataset in enumerate(results, 1):
            output.append(f"**{i}. {dataset['title']}**")
            output.append(f"   📋 ID: `{dataset['name']}`")
            if dataset.get("notes"):
                output.append(f"   📝 Description: {dataset['notes'][:150]}...")
            if dataset.get("tags"):
                tags = [tag["name"] for tag in dataset["tags"]]
                output.append(f"   🏷️ Tags: {', '.join(tags[:5])}")
            output.append("")
        
        output.append("🚀 **Next Step**: Use toronto_smart_data_helper(dataset_id=\"ID_from_above\", user_question=\"what you want to know\") to get the data!")
        return "\n".join(output)
    return f"❌ Error searching datasets with query: {query}"

# Tool to get dataset schema
@mcp.tool()
def toronto_get_dataset_schema(dataset_id: str) -> str:
    """📋 GET DATA STRUCTURE: Shows the schema (column names, field IDs, and types) for a Toronto dataset if it has an active datastore. Essential for understanding what fields are available before filtering with toronto_query_dataset_data(). For CSV files, suggests checking the header row manually."""
    # First get the dataset details
    dataset_data = make_api_request("/api/3/action/package_show", {"id": dataset_id})
    
    if not dataset_data.get("success"):
        return f"❌ Error fetching dataset details for: {dataset_id}. Error: {dataset_data.get('error', 'Unknown error')}"
    
    dataset_info = dataset_data["result"]
    resources = dataset_info.get("resources", [])
    
    # Find the first datastore_active resource
    active_datastore_resource_id = None
    for resource in resources:
        if resource.get("datastore_active"):
            active_datastore_resource_id = resource.get("id")
            break
    
    if not active_datastore_resource_id:
        # Check if there are downloadable resources as an alternative
        downloadable_resource_exists = False
        downloadable_formats = []
        for resource in resources:
            resource_format = str(resource.get("format", "")).upper()
            resource_mimetype = str(resource.get("mimetype", "")).lower()
            if (resource_format in ['CSV', 'XLS', 'XLSX'] or 
                'text/csv' in resource_mimetype or 
                'excel' in resource_mimetype or
                'spreadsheet' in resource_mimetype):
                downloadable_resource_exists = True
                downloadable_formats.append(resource_format)
        
        if downloadable_resource_exists:
            format_list = ", ".join(set(downloadable_formats))
            return (f"📁 Dataset '{dataset_info.get('title', dataset_id)}' does not have an active datastore, so an API-based schema is not available. "
                    f"It appears to have downloadable resources ({format_list}). For these files, the schema is typically in the header row or sheet structure. "
                    f"You can find the download links using `datasets://{dataset_id}` and inspect the file structure manually.")
        else:
             return (f"⚠️ Dataset '{dataset_info.get('title', dataset_id)}' does not have an active datastore, and no downloadable resources were found. "
                     f"An API-based schema is not available. Use `datasets://{dataset_id}` to inspect available resources.")

    # Get the schema from the active datastore
    schema_data = make_api_request("/api/3/action/datastore_search", {"id": active_datastore_resource_id, "limit": 0})
    
    if schema_data.get("success"):
        fields = schema_data["result"].get("fields", [])
        if not fields:
            return f"⚠️ Schema information (fields) is empty for the active datastore of dataset: {dataset_info.get('title', dataset_id)}."
        output = [f"📋 **Schema for {dataset_info.get('title', dataset_id)}** (from active datastore):"]
        for field in fields:
            output.append(f"• **{field['id']}**: {field['type']}")
        
        output.append(f"\n💡 **Usage**: Copy exact field names for filtering with toronto_query_dataset_data()")
        return "\n".join(output)
    
    return f"❌ Error fetching schema for active datastore of dataset: {dataset_id}. Error: {schema_data.get('error', 'Unknown error')}"

# Tool to query dataset data with filters
@mcp.tool()
def toronto_query_dataset_data(
    dataset_id: str,
    filters: Optional[Dict[str, Any]] = None,
    fields: Optional[List[str]] = None,
    limit: Optional[int] = 10,
    sort: Optional[str] = None
) -> str:
    """🔧 ADVANCED QUERYING: Query Toronto datasets with precise filtering, sorting, and field selection. 
    
    💡 TIP: Use toronto_smart_data_helper() first - it's easier and handles most use cases automatically!
    
    This tool is for when you need advanced filtering:
    📋 REQUIRED: Get field names first with toronto_get_dataset_schema(dataset_id)
    🔍 FILTERS: Use exact field names like {"establishment_status": "Pass", "inspection_date": "2024-01-01"}
    📊 SORT: Use field names like "inspection_date desc" or "score asc"
    📝 FIELDS: Specify which columns to return like ["name", "address", "score"]
    
    ⚠️ For CSV files, this returns download links instead of query results.
    🚀 Alternative: Try toronto_smart_data_helper() for a simpler, guided approach."""
    # First get the dataset details to find the resource
    dataset_data = make_api_request("/api/3/action/package_show", {"id": dataset_id})
    
    if not dataset_data.get("success"):
        return f"❌ Error fetching dataset details for: {dataset_id}. Error: {dataset_data.get('error', 'Unknown error')}"
    
    dataset_info = dataset_data["result"]
    resources = dataset_info.get("resources", [])
    
    # Check for an active datastore resource
    active_datastore_resource_id = None
    for resource in resources:
        if resource.get("datastore_active"):
            active_datastore_resource_id = resource.get("id")
            break
            
    if active_datastore_resource_id:
        # --- Datastore Query Logic (existing behavior) ---
        query_params = {"id": active_datastore_resource_id, "limit": limit}
        
        if filters:
            query_params["filters"] = filters
        if fields:
            query_params["fields"] = ",".join(fields)
        if sort:
            query_params["sort"] = sort
        
        query_data = make_api_request("/api/3/action/datastore_search", query_params)
        
        if query_data.get("success"):
            results = query_data["result"].get("records", [])
            if not results:
                return f"🔍 No data found in the active datastore for dataset: {dataset_id} with the given parameters."
            
            output = [f"📊 **Query Results for {dataset_info.get('title', dataset_id)}:**\n"]
            for i, record in enumerate(results, 1):
                output.append(f"**Record {i}:**")
                for key, value in record.items():
                    if key != '_id':
                        output.append(f"  • {key}: {value}")
                output.append("")
            return "\n".join(output)
        else:
            error_msg = query_data.get('error', 'Unknown error')
            if 'field' in str(error_msg).lower() or 'column' in str(error_msg).lower():
                return (f"❌ **Filtering Error**: {error_msg}\n\n"
                       f"💡 **Quick Fix**: \n"
                       f"1. Get correct field names: toronto_get_dataset_schema(dataset_id='{dataset_id}')\n"
                       f"2. Use exact field names in filters (case-sensitive)\n"
                       f"3. Or try: toronto_smart_data_helper(dataset_id='{dataset_id}', user_question='your question')")
            return f"❌ Error querying dataset {dataset_id}: {error_msg}"
    else:
        # --- Downloadable File Logic (CSV, XLS, XLSX) ---
        downloadable_resources_found = []
        for resource in resources:
            resource_format = str(resource.get("format", "")).upper()
            resource_mimetype = str(resource.get("mimetype", "")).lower()

            if (resource_format in ['CSV', 'XLS', 'XLSX'] or 
                'text/csv' in resource_mimetype or 
                'excel' in resource_mimetype or
                'spreadsheet' in resource_mimetype):
                if resource.get("url"):
                    downloadable_resources_found.append({
                        "name": resource.get("name", dataset_id),
                        "url": resource["url"],
                        "format": resource_format
                    })
        
        if not downloadable_resources_found:
            return (f"⚠️ No active datastore or downloadable resource found for dataset: {dataset_id}. "
                    f"Use `datasets://{dataset_id}` to see all available resources and their formats.")
        elif len(downloadable_resources_found) == 1:
            res = downloadable_resources_found[0]
            access_note = "use toronto_fetch_csv_data() to get content" if res['format'] == 'CSV' else "download and open manually"
            return (f"📁 This dataset ('{dataset_info.get('title', dataset_id)}') does not have a queryable API (active datastore). "
                    f"A single {res['format']} file resource was found:\n"
                    f"📝 **Resource Name**: {res['name']}\n"
                    f"🔗 **Download URL**: {res['url']}\n"
                    f"💡 **Access Method**: {access_note}\n"
                    f"💡 **Note**: API-based filtering, field selection, sorting, and limits are not applicable. "
                    f"Please download and process the file manually.")
        else: # Multiple files found
            csv_count = len([r for r in downloadable_resources_found if r['format'] == 'CSV'])
            xls_count = len([r for r in downloadable_resources_found if r['format'] in ['XLS', 'XLSX']])
            return (f"📁 This dataset ('{dataset_info.get('title', dataset_id)}') does not have a queryable API (active datastore) "
                    f"but offers multiple downloadable resources ({csv_count} CSV, {xls_count} XLS/XLSX files). "
                    f"To select a specific file (e.g., for a particular year), "
                    f"call `datasets://{dataset_id}` to list all available files and their download URLs. "
                    f"For CSV files, use 'toronto_fetch_csv_data' to get content. For XLS/XLSX files, download manually.")

# Tool to get dataset statistics
@mcp.tool()
def toronto_get_dataset_stats(dataset_id: str) -> str:
    """📈 DATASET STATISTICS: Get basic statistics for a Toronto dataset including record counts, field information, and resource overview. Useful for understanding the scale and structure of a dataset before diving into the data."""
    dataset_data = make_api_request("/api/3/action/package_show", {"id": dataset_id})
    
    if not dataset_data.get("success"):
        return f"❌ Error fetching dataset details for: {dataset_id}. Error: {dataset_data.get('error', 'Unknown error')}"
    
    dataset_info = dataset_data["result"]
    resources = dataset_info.get("resources", [])
    dataset_title = dataset_info.get('title', dataset_id)

    output = [
        f"📈 **Statistics for {dataset_title}:**",
        f"📋 Total resources listed: {len(resources)}"
    ]
    
    active_datastore_resource_id = None
    for resource in resources:
        if resource.get("datastore_active"):
            active_datastore_resource_id = resource.get("id")
            break
            
    if active_datastore_resource_id:
        # Get stats from the active datastore
        stats_data = make_api_request("/api/3/action/datastore_search", {"id": active_datastore_resource_id, "limit": 0})
        
        if stats_data.get("success"):
            total_records = stats_data["result"].get("total", "N/A")
            fields = stats_data["result"].get("fields", [])
            
            output.append(f"✅ **Active Datastore Record Count**: {total_records:,}")
            output.append(f"📋 **Active Datastore Field Count**: {len(fields)}")
            if fields:
                output.append("\n**Active Datastore Fields:**")
                for field in fields:
                    output.append(f"• {field.get('id', 'Unknown ID')}: {field.get('type', 'Unknown type')}")
            else:
                output.append("⚠️ No fields found in the active datastore.")
        else:
            output.append(f"❌ Could not retrieve statistics from the active datastore. Error: {stats_data.get('error', 'Unknown error')}")
    else:
        output.append("📁 No active datastore found for this dataset.")
        output.append("   Therefore, record count and field list from an API datastore are not available.")
        # Check for downloadable resources (CSV, XLS, XLSX)
        downloadable_resource_info = []
        for resource in resources:
            resource_format = str(resource.get("format", "")).upper()
            resource_mimetype = str(resource.get("mimetype", "")).lower()
            if (resource_format in ['CSV', 'XLS', 'XLSX'] or 
                'text/csv' in resource_mimetype or 
                'excel' in resource_mimetype or
                'spreadsheet' in resource_mimetype):
                downloadable_resource_info.append(f"• Name: {resource.get('name', 'N/A')}, Format: {resource_format}")
                if resource.get('url'):
                     downloadable_resource_info.append(f"  URL: {resource['url']}")
        
        if downloadable_resource_info:
            output.append("\n**Downloadable Resources Found** (download and inspect manually for record count/schema):")
            output.extend(downloadable_resource_info)
        else:
            output.append("⚠️ No downloadable resources (CSV/XLS/XLSX) found for manual inspection.")
            
    return "\n".join(output)

# Tool to fetch and return a sample of CSV data from a URL
@mcp.tool()
def toronto_fetch_csv_data(csv_url: str, max_lines: Optional[int] = 50) -> str:
    """📄 FETCH CSV DATA: Downloads and returns sample content from a CSV file URL. Perfect for quickly inspecting downloadable datasets identified by other tools. Shows headers and sample rows to understand the data structure."""
    if not csv_url.startswith("http://") and not csv_url.startswith("https://"):
        return "❌ Error: Invalid URL. Must start with http:// or https://"

    try:
        with urllib.request.urlopen(csv_url, timeout=10) as response:
            if response.status != 200:
                return f"❌ Error: Failed to download file. HTTP Status Code: {response.status}"
            
            # Read the content line by line to respect max_lines without reading the whole file if it's huge
            lines = []
            for i in range(max_lines):
                line_bytes = response.readline()
                if not line_bytes:
                    break # End of file
                try:
                    lines.append(line_bytes.decode('utf-8').rstrip("\r\n"))
                except UnicodeDecodeError:
                    # If utf-8 fails, try latin-1 as a common fallback for CSVs
                    try:
                        lines.append(line_bytes.decode('latin-1').rstrip("\r\n"))
                    except UnicodeDecodeError:
                        return f"❌ Error: Could not decode line {i+1} using utf-8 or latin-1 encoding."
            
            output_data = "\n".join(lines)
            
            # Check if there is more content (i.e., if we broke because of max_lines, not EOF)
            more_content_exists = False
            if len(lines) == max_lines:
                if response.readline(): # Try to read one more line
                    more_content_exists = True

            if not output_data:
                return "⚠️ File appears to be empty or no content could be read."

            if more_content_exists:
                return f"📄 **First {max_lines} lines of CSV data:**\n{output_data}\n\n... (file truncated, more data exists)"
            else:
                return f"📄 **CSV data (all {len(lines)} lines):**\n{output_data}"

    except urllib.error.HTTPError as e:
        return f"❌ Error: HTTP Error {e.code} when trying to fetch the CSV: {e.reason}"
    except urllib.error.URLError as e:
        return f"❌ Error: URL Error when trying to fetch the CSV: {e.reason} (this might happen with invalid URLs or network issues)"
    except TimeoutError:
        return f"❌ Error: Timeout when trying to fetch the CSV from {csv_url}. The server took too long to respond."
    except Exception as e:
        return f"❌ Error: An unexpected error occurred while fetching CSV: {str(e)}"

if __name__ == "__main__":
    mcp.run() 