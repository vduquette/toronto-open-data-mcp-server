import pytest
import json
import urllib.error
from unittest.mock import patch, Mock, MagicMock
from main import (
    make_api_request, 
    toronto_start_here,
    toronto_popular_datasets,
    toronto_search_datasets, 
    toronto_smart_data_helper,
    toronto_get_dataset_schema,
    toronto_query_dataset_data,
    toronto_get_dataset_stats,
    toronto_fetch_csv_data,
    get_dataset_details
)

class TestMakeApiRequest:
    """Test the core API request function"""
    
    @patch('urllib.request.urlopen')
    def test_successful_api_request(self, mock_urlopen):
        # Mock successful response
        mock_response = Mock()
        mock_response.read.return_value = b'{"success": true, "result": ["test"]}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = make_api_request("/api/3/action/package_list")
        
        assert result["success"] is True
        assert result["result"] == ["test"]
    
    @patch('urllib.request.urlopen')
    def test_api_request_with_params(self, mock_urlopen):
        mock_response = Mock()
        mock_response.read.return_value = b'{"success": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        params = {"id": "test_dataset", "limit": 10}
        make_api_request("/api/3/action/package_show", params)
        
        # Check that URL was constructed correctly
        called_url = mock_urlopen.call_args[0][0]
        assert "id=test_dataset" in called_url
        assert "limit=10" in called_url
    
    @patch('urllib.request.urlopen')
    def test_api_request_http_error(self, mock_urlopen):
        # Mock HTTP error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="test", code=404, msg="Not Found", hdrs=None, fp=None
        )
        
        result = make_api_request("/api/3/action/package_list")
        
        assert result["success"] is False
        assert "HTTP Error: 404" in result["error"]
    
    @patch('urllib.request.urlopen')
    def test_api_request_url_error(self, mock_urlopen):
        # Mock URL error
        mock_urlopen.side_effect = urllib.error.URLError("Connection failed")
        
        result = make_api_request("/api/3/action/package_list")
        
        assert result["success"] is False
        assert "URL Error: Connection failed" in result["error"]

class TestTorontoStartHere:
    """Test the start here function"""
    
    def test_toronto_start_here_returns_guide(self):
        result = toronto_start_here()
        
        assert "Toronto Open Data MCP Server - START HERE" in result
        assert "BEST APPROACH" in result
        assert "toronto_search_datasets" in result
        assert "toronto_smart_data_helper" in result

class TestTorontoPopularDatasets:
    """Test the popular datasets function"""
    
    def test_popular_datasets_returns_list(self):
        result = toronto_popular_datasets()
        
        assert "Most Popular Toronto Open Datasets" in result
        assert "dinesafe" in result
        assert "traffic-signals" in result
        assert "parks-facilities" in result
        assert "toronto_smart_data_helper" in result

class TestTorontoSearchDatasets:
    """Test the search datasets function"""
    
    @patch('main.make_api_request')
    def test_search_datasets_success(self, mock_api):
        # Mock successful search response
        mock_api.return_value = {
            "success": True,
            "result": {
                "results": [
                    {
                        "title": "Restaurant Inspections", 
                        "name": "dinesafe",
                        "notes": "Food safety inspection data",
                        "tags": [{"name": "food"}, {"name": "health"}]
                    }
                ]
            }
        }
        
        result = toronto_search_datasets("restaurant")
        
        assert "Found 1 Toronto datasets" in result
        assert "Restaurant Inspections" in result
        assert "dinesafe" in result
        assert "toronto_smart_data_helper" in result
    
    @patch('main.make_api_request')
    def test_search_datasets_no_results(self, mock_api):
        mock_api.return_value = {
            "success": True,
            "result": {"results": []}
        }
        
        result = toronto_search_datasets("nonexistent")
        
        assert "No datasets found" in result
        assert "Try broader terms" in result
    
    @patch('main.make_api_request')
    def test_search_datasets_api_error(self, mock_api):
        mock_api.return_value = {
            "success": False,
            "error": "API Error"
        }
        
        result = toronto_search_datasets("test")
        
        assert "Error searching datasets" in result

class TestTorontoSmartDataHelper:
    """Test the smart data helper function"""
    
    @patch('main.make_api_request')
    def test_smart_helper_api_dataset_success(self, mock_api):
        # Mock dataset details
        mock_api.side_effect = [
            {  # package_show response
                "success": True,
                "result": {
                    "title": "Restaurant Inspections",
                    "resources": [{"datastore_active": True, "id": "resource_123"}]
                }
            },
            {  # schema response
                "success": True,
                "result": {
                    "fields": [
                        {"id": "establishment_name", "type": "text"},
                        {"id": "inspection_date", "type": "date"}
                    ]
                }
            },
            {  # sample data response
                "success": True,
                "result": {
                    "records": [
                        {"establishment_name": "Test Restaurant", "inspection_date": "2024-01-01"},
                        {"establishment_name": "Another Place", "inspection_date": "2024-01-02"}
                    ],
                    "total": 1000
                }
            }
        ]
        
        result = toronto_smart_data_helper("dinesafe", "recent restaurant inspections")
        
        assert "Restaurant Inspections" in result
        assert "API Data (queryable)" in result
        assert "establishment_name, inspection_date" in result
        assert "**Total records**: 1,000" in result
        assert "Test Restaurant" in result
    
    @patch('main.make_api_request')
    def test_smart_helper_dataset_not_found(self, mock_api):
        mock_api.return_value = {"success": False, "error": "Not found"}
        
        result = toronto_smart_data_helper("nonexistent", "test question")
        
        assert "Could not find dataset 'nonexistent'" in result
        assert "Try searching again" in result
    
    @patch('main.make_api_request')
    @patch('main.toronto_fetch_csv_data')
    def test_smart_helper_csv_dataset(self, mock_fetch_csv, mock_api):
        # Mock dataset with CSV resource
        mock_api.return_value = {
            "success": True,
            "result": {
                "title": "Historical Data",
                "resources": [
                    {
                        "datastore_active": False,
                        "format": "CSV",
                        "name": "data_2024.csv",
                        "url": "http://example.com/data.csv"
                    }
                ]
            }
        }
        
        mock_fetch_csv.return_value = "CSV header\ndata1,data2\nvalue1,value2"
        
        result = toronto_smart_data_helper("historical-data", "get historical data")
        
        assert "Historical Data" in result
        assert "Downloadable Files" in result
        assert "data_2024.csv" in result
        assert "CSV header" in result

class TestTorontoGetDatasetSchema:
    """Test the dataset schema function"""
    
    @patch('main.make_api_request')
    def test_get_schema_success(self, mock_api):
        mock_api.side_effect = [
            {  # package_show
                "success": True,
                "result": {
                    "title": "Test Dataset",
                    "resources": [{"datastore_active": True, "id": "resource_123"}]
                }
            },
            {  # datastore_search for schema
                "success": True,
                "result": {
                    "fields": [
                        {"id": "name", "type": "text"},
                        {"id": "date", "type": "timestamp"},
                        {"id": "score", "type": "numeric"}
                    ]
                }
            }
        ]
        
        result = toronto_get_dataset_schema("test_dataset")
        
        assert "Schema for Test Dataset" in result
        assert "**name**: text" in result
        assert "**date**: timestamp" in result
        assert "**score**: numeric" in result
    
    @patch('main.make_api_request')
    def test_get_schema_csv_dataset(self, mock_api):
        mock_api.return_value = {
            "success": True,
            "result": {
                "title": "CSV Dataset",
                "resources": [{"datastore_active": False, "format": "CSV"}]
            }
        }
        
        result = toronto_get_dataset_schema("csv_dataset")
        
        assert "does not have an active datastore" in result
        assert "downloadable resources" in result

class TestTorontoQueryDatasetData:
    """Test the dataset query function"""
    
    @patch('main.make_api_request')
    def test_query_data_success(self, mock_api):
        mock_api.side_effect = [
            {  # package_show
                "success": True,
                "result": {
                    "title": "Test Dataset",
                    "resources": [{"datastore_active": True, "id": "resource_123"}]
                }
            },
            {  # datastore_search
                "success": True,
                "result": {
                    "records": [
                        {"name": "Test1", "score": 85},
                        {"name": "Test2", "score": 90}
                    ]
                }
            }
        ]
        
        result = toronto_query_dataset_data("test_dataset", {"score": 85}, limit=5)
        
        assert "Query Results for Test Dataset" in result
        assert "Test1" in result
        assert "score: 85" in result
    
    @patch('main.make_api_request')
    def test_query_data_filtering_error(self, mock_api):
        mock_api.side_effect = [
            {  # package_show
                "success": True,
                "result": {
                    "title": "Test Dataset",
                    "resources": [{"datastore_active": True, "id": "resource_123"}]
                }
            },
            {  # datastore_search with error
                "success": False,
                "error": "field 'invalid_field' does not exist"
            }
        ]
        
        result = toronto_query_dataset_data("test_dataset", {"invalid_field": "value"})
        
        assert "Filtering Error" in result
        assert "Quick Fix" in result
        assert "toronto_get_dataset_schema" in result

class TestTorontoFetchCsvData:
    """Test the CSV fetch function"""
    
    @patch('urllib.request.urlopen')
    def test_fetch_csv_success(self, mock_urlopen):
        # Mock CSV content
        csv_content = b"header1,header2\nvalue1,value2\nvalue3,value4\n"
        mock_response = Mock()
        mock_response.status = 200
        mock_response.readline.side_effect = [
            b"header1,header2\n",
            b"value1,value2\n", 
            b"value3,value4\n",
            b""  # EOF
        ]
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = toronto_fetch_csv_data("http://example.com/data.csv", max_lines=10)
        
        assert "CSV data" in result
        assert "header1,header2" in result
        assert "value1,value2" in result
    
    def test_fetch_csv_invalid_url(self):
        result = toronto_fetch_csv_data("invalid_url")
        
        assert "Invalid URL" in result
        assert "Must start with http" in result
    
    @patch('urllib.request.urlopen')
    def test_fetch_csv_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="test", code=404, msg="Not Found", hdrs=None, fp=None
        )
        
        result = toronto_fetch_csv_data("http://example.com/notfound.csv")
        
        assert "HTTP Error 404" in result

class TestGetDatasetDetails:
    """Test the dataset details resource function"""
    
    @patch('main.make_api_request')
    def test_get_dataset_details_success(self, mock_api):
        mock_api.return_value = {
            "success": True,
            "result": {
                "title": "Test Dataset",
                "notes": "Test description",
                "organization": {"title": "Test Org"},
                "resources": [
                    {
                        "name": "API Resource",
                        "id": "resource_1",
                        "format": "JSON",
                        "datastore_active": True
                    },
                    {
                        "name": "CSV Resource", 
                        "id": "resource_2",
                        "format": "CSV",
                        "datastore_active": False,
                        "url": "http://example.com/data.csv"
                    }
                ]
            }
        }
        
        result = get_dataset_details("test_dataset")
        
        assert "Test Dataset" in result
        assert "Test description" in result
        assert "Test Org" in result
        assert "API Resource" in result
        assert "Active Datastore" in result
        assert "CSV Resource" in result
        assert "Downloadable File" in result

# Integration tests (these will hit the real API - run sparingly)
class TestIntegration:
    """Integration tests with real Toronto Open Data API"""
    
    @pytest.mark.integration
    def test_real_api_package_list(self):
        """Test that we can actually connect to Toronto's API"""
        result = make_api_request("/api/3/action/package_list")
        
        assert result.get("success") is True
        assert "result" in result
        assert isinstance(result["result"], list)
        assert len(result["result"]) > 0
    
    @pytest.mark.integration  
    def test_real_search_dinesafe(self):
        """Test searching for a known dataset"""
        result = toronto_search_datasets("dinesafe", limit=1)
        
        assert "dinesafe" in result.lower()
        assert "restaurant" in result.lower() or "food" in result.lower()
    
    @pytest.mark.integration
    def test_real_smart_helper_dinesafe(self):
        """Test smart helper with real dinesafe data"""
        result = toronto_smart_data_helper("dinesafe", "recent restaurant inspections", limit=2)
        
        assert "Dinesafe" in result or "Restaurant" in result
        assert "API Data" in result or "CSV" in result

# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may hit real API)"
    )

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 