# Toronto Open Data MCP Server

An MCP (Model Context Protocol) server that provides direct access to Toronto's Open Data through the CKAN API. This server allows LLM agents to efficiently discover, explore, and query Toronto's 500+ public datasets.

## Features

- 🔍 **Smart Dataset Discovery**: Search through 500+ Toronto datasets with intelligent suggestions
- 🧠 **Intelligent Data Helper**: Automatically handles both API and CSV data sources
- 📊 **Flexible Querying**: Support for filtering, sorting, and field selection on API datasets
- 📁 **CSV Support**: Automatic fetching and preview of downloadable CSV datasets
- 🤝 **LLM-Friendly**: Designed for collaborative use with web search when additional context is needed
- ✅ **Robust Error Handling**: Clear error messages with actionable suggestions

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/toronto-open-data-mcp-server.git
   cd toronto-open-data-mcp-server
   ```

2. **Install dependencies**:
   ```bash
   # Install main dependencies
   pip install -e .
   
   # Install test dependencies (optional)
   pip install -e ".[test]"
   ```

3. **Run the server**:
   ```bash
   python main.py
   ```

## Usage

### Quick Start

The server provides several tools designed for LLM agents:

1. **`toronto_start_here()`** - Essential first call that explains the workflow
2. **`toronto_search_datasets(query)`** - Find relevant datasets by keywords
3. **`toronto_smart_data_helper(dataset_id, user_question)`** - Intelligent data retrieval
4. **`toronto_popular_datasets()`** - Quick access to commonly used datasets

### Example Workflow

```python
# 1. Start with guidance
toronto_start_here()

# 2. Search for relevant data
toronto_search_datasets("restaurant inspection")

# 3. Get data intelligently
toronto_smart_data_helper("dinesafe", "recent restaurant inspection failures")

# 4. Advanced filtering (if needed)
toronto_query_dataset_data("dinesafe", 
                           filters={"establishment_status": "Conditional Pass"},
                           sort="inspection_date desc",
                           limit=10)
```

### Popular Datasets

- **`dinesafe`** - Restaurant inspections and health scores
- **`traffic-signals`** - Traffic light locations and timing
- **`parks-facilities`** - Parks, pools, and recreation facilities
- **`business-licences`** - Licensed businesses in Toronto
- **`building-permits`** - Construction and renovation permits

## Testing

This project includes comprehensive tests covering unit tests, integration tests, and workflow tests.

### Prerequisites

Install test dependencies:
```bash
pip install -e ".[test]"
```

### Running Tests

#### Quick Test Commands

```bash
# Run unit tests only (recommended for development)
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run with coverage report
python run_tests.py --coverage

# Run integration tests (hits real Toronto API)
python run_tests.py --integration

# Run all tests (unit + integration)
python run_tests.py --all
```

#### Direct pytest Commands

```bash
# Unit tests only (excludes integration tests)
pytest test_toronto_mcp.py -m "not integration"

# Integration tests only (hits real API)
pytest test_toronto_mcp.py -m "integration"

# All tests
pytest test_toronto_mcp.py test_workflows.py

# With coverage
pytest --cov=main --cov-report=html test_toronto_mcp.py
```

### Test Structure

- **`test_toronto_mcp.py`** - Core unit and integration tests
  - `TestMakeApiRequest` - API request functionality
  - `TestTorontoSearchDatasets` - Dataset search functionality  
  - `TestTorontoSmartDataHelper` - Smart helper functionality
  - `TestIntegration` - Integration tests with real API
  
- **`test_workflows.py`** - End-to-end workflow tests
  - `TestCommonWorkflows` - Typical user workflows
  - `TestErrorScenarios` - Error handling
  - `TestUserStories` - Complete user stories

### Test Categories

- **Unit Tests**: Fast tests with mocked API calls (default)
- **Integration Tests**: Tests that hit the real Toronto Open Data API
- **Workflow Tests**: End-to-end scenarios demonstrating common usage patterns

### Coverage

Run tests with coverage to see how much of the code is tested:

```bash
python run_tests.py --coverage
# View report: open htmlcov/index.html
```

## API Reference

### Core Tools

#### `toronto_start_here() -> str`
Essential first call that provides workflow guidance and server capabilities.

#### `toronto_search_datasets(query: str, limit: int = 10) -> str`
Search Toronto datasets by keywords.

#### `toronto_smart_data_helper(dataset_id: str, user_question: str, limit: int = 10) -> str`
Intelligent helper that automatically handles both API and CSV data sources.

#### `toronto_query_dataset_data(dataset_id: str, filters: Dict = None, fields: List = None, limit: int = 10, sort: str = None) -> str`
Advanced querying with filtering and sorting for API datasets.

### Utility Tools

#### `toronto_popular_datasets() -> str`
Quick access to commonly used datasets.

#### `toronto_get_dataset_schema(dataset_id: str) -> str`
Get field names and types for API datasets.

#### `toronto_fetch_csv_data(csv_url: str, max_lines: int = 50) -> str`
Fetch and preview CSV file content.

## Architecture

- **FastMCP Framework**: Built on the FastMCP framework for easy tool definition
- **CKAN API**: Direct integration with Toronto's CKAN-based Open Data portal
- **Collaborative Design**: Works alongside web search rather than replacing it
- **Error Recovery**: Intelligent error handling with actionable suggestions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite: `python run_tests.py --all`
5. Submit a pull request