"""
Workflow tests for Toronto Open Data MCP Server

These tests demonstrate common usage patterns and workflows
"""

import pytest
from unittest.mock import patch, Mock
from main import (
    toronto_start_here,
    toronto_search_datasets,
    toronto_smart_data_helper,
    toronto_query_dataset_data
)

class TestCommonWorkflows:
    """Test common user workflows"""
    
    def test_getting_started_workflow(self):
        """Test the basic getting started workflow"""
        # Step 1: User calls start here
        guide = toronto_start_here()
        
        # Should contain key guidance
        assert "START HERE" in guide
        assert "toronto_search_datasets" in guide
        assert "toronto_smart_data_helper" in guide
    
    @patch('main.make_api_request')
    def test_restaurant_inspection_workflow(self, mock_api):
        """Test typical restaurant inspection workflow"""
        
        # Step 1: Search for restaurant data
        mock_api.return_value = {
            "success": True,
            "result": {
                "results": [
                    {
                        "title": "DineSafe Restaurant Inspections",
                        "name": "dinesafe",
                        "notes": "Food safety inspection data",
                        "tags": [{"name": "food"}, {"name": "health"}]
                    }
                ]
            }
        }
        
        search_result = toronto_search_datasets("restaurant inspection")
        assert "dinesafe" in search_result
        assert "Restaurant Inspections" in search_result
        
        # Step 2: Use smart helper to get data
        mock_api.side_effect = [
            {  # package_show
                "success": True,
                "result": {
                    "title": "DineSafe Restaurant Inspections",
                    "resources": [{"datastore_active": True, "id": "resource_123"}]
                }
            },
            {  # schema
                "success": True,
                "result": {
                    "fields": [
                        {"id": "establishment_name", "type": "text"},
                        {"id": "inspection_date", "type": "date"},
                        {"id": "establishment_status", "type": "text"}
                    ]
                }
            },
            {  # sample data
                "success": True,
                "result": {
                    "records": [
                        {
                            "establishment_name": "Joe's Pizza",
                            "inspection_date": "2024-01-15",
                            "establishment_status": "Pass"
                        }
                    ],
                    "total": 50000
                }
            }
        ]
        
        helper_result = toronto_smart_data_helper("dinesafe", "recent restaurant inspections")
        assert "DineSafe Restaurant Inspections" in helper_result
        assert "establishment_name" in helper_result
        assert "Joe's Pizza" in helper_result
        assert "50,000" in helper_result
    
    @patch('main.make_api_request')
    def test_traffic_data_workflow(self, mock_api):
        """Test traffic data discovery workflow"""
        
        # Search for traffic data
        mock_api.return_value = {
            "success": True,
            "result": {
                "results": [
                    {
                        "title": "Traffic Signal Locations",
                        "name": "traffic-signals",
                        "notes": "Location of traffic signals in Toronto",
                        "tags": [{"name": "traffic"}, {"name": "transportation"}]
                    }
                ]
            }
        }
        
        search_result = toronto_search_datasets("traffic")
        assert "traffic-signals" in search_result
        assert "Traffic Signal" in search_result
    
    @patch('main.make_api_request')
    def test_csv_dataset_workflow(self, mock_api):
        """Test workflow with CSV-only dataset"""
        
        # Mock dataset with only CSV resources
        mock_api.return_value = {
            "success": True,
            "result": {
                "title": "Historical Budget Data",
                "resources": [
                    {
                        "datastore_active": False,
                        "format": "CSV",
                        "name": "budget_2023.csv",
                        "url": "http://example.com/budget_2023.csv"
                    }
                ]
            }
        }
        
        # Mock CSV fetch
        with patch('main.toronto_fetch_csv_data') as mock_fetch:
            mock_fetch.return_value = "year,department,amount\n2023,Fire,50000000"
            
            helper_result = toronto_smart_data_helper("budget-data", "city budget information")
            
            assert "Historical Budget Data" in helper_result
            assert "Downloadable Files" in helper_result
            assert "budget_2023.csv" in helper_result
            assert "year,department,amount" in helper_result
    
    @patch('main.make_api_request')
    def test_error_handling_workflow(self, mock_api):
        """Test how errors are handled in typical workflows"""
        
        # Test dataset not found
        mock_api.return_value = {"success": False, "error": "Dataset not found"}
        
        helper_result = toronto_smart_data_helper("nonexistent", "test question")
        assert "Could not find dataset" in helper_result
        assert "Try searching again" in helper_result
    
    @patch('main.make_api_request')
    def test_filtering_workflow(self, mock_api):
        """Test advanced filtering workflow"""
        
        # Mock successful query with filters
        mock_api.side_effect = [
            {  # package_show
                "success": True,
                "result": {
                    "title": "Test Dataset",
                    "resources": [{"datastore_active": True, "id": "resource_123"}]
                }
            },
            {  # datastore_search with filters
                "success": True,
                "result": {
                    "records": [
                        {"name": "Filtered Result", "status": "Active"}
                    ]
                }
            }
        ]
        
        query_result = toronto_query_dataset_data(
            "test_dataset",
            filters={"status": "Active"},
            limit=10
        )
        
        assert "Query Results" in query_result
        assert "Filtered Result" in query_result
        assert "status: Active" in query_result

class TestErrorScenarios:
    """Test various error scenarios"""
    
    @patch('main.make_api_request')
    def test_api_down_scenario(self, mock_api):
        """Test behavior when API is down"""
        mock_api.return_value = {
            "success": False,
            "error": "HTTP Error: 500"
        }
        
        result = toronto_search_datasets("test")
        assert "Error searching datasets" in result
    
    @patch('main.make_api_request')
    def test_malformed_response_scenario(self, mock_api):
        """Test behavior with malformed API responses"""
        # Mock response missing expected fields
        mock_api.return_value = {
            "success": True,
            "result": {}  # Missing 'results' field
        }
        
        result = toronto_search_datasets("test")
        # Should handle gracefully without crashing

class TestUserStories:
    """Test complete user stories from start to finish"""
    
    @patch('main.make_api_request')
    @patch('main.toronto_fetch_csv_data')
    def test_user_story_find_park_data(self, mock_fetch_csv, mock_api):
        """
        User Story: City planner wants to find data about parks and facilities
        """
        # User searches for parks
        mock_api.return_value = {
            "success": True,
            "result": {
                "results": [
                    {
                        "title": "Parks and Recreation Facilities",
                        "name": "parks-facilities",
                        "notes": "List of parks, pools, and recreation facilities",
                        "tags": [{"name": "parks"}, {"name": "recreation"}]
                    }
                ]
            }
        }
        
        search_result = toronto_search_datasets("parks")
        assert "parks-facilities" in search_result
        
        # User gets data using smart helper
        mock_api.side_effect = [
            {  # package_show
                "success": True,
                "result": {
                    "title": "Parks and Recreation Facilities",
                    "resources": [{"datastore_active": True, "id": "parks_resource"}]
                }
            },
            {  # schema
                "success": True,
                "result": {
                    "fields": [
                        {"id": "park_name", "type": "text"},
                        {"id": "address", "type": "text"},
                        {"id": "facilities", "type": "text"}
                    ]
                }
            },
            {  # sample data
                "success": True,
                "result": {
                    "records": [
                        {
                            "park_name": "High Park",
                            "address": "1873 Bloor St W",
                            "facilities": "Playground, Tennis Courts"
                        }
                    ],
                    "total": 1500
                }
            }
        ]
        
        data_result = toronto_smart_data_helper("parks-facilities", "list of parks with playgrounds")
        assert "Parks and Recreation Facilities" in data_result
        assert "High Park" in data_result
        assert "1,500" in data_result
    
    def test_user_story_newcomer_exploration(self):
        """
        User Story: New user wants to explore what data is available
        """
        # User starts with getting started guide
        guide = toronto_start_here()
        assert "START HERE" in guide
        assert "popular datasets" in guide.lower()
        
        # User explores popular datasets
        from main import toronto_popular_datasets
        popular = toronto_popular_datasets()
        assert "Most Popular" in popular
        assert "dinesafe" in popular
        assert "parks-facilities" in popular

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 