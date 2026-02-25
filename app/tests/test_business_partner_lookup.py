"""Unit tests for business_partner_lookup tool"""

import sys
import os

# Add parent directory to path to import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.business_partner_lookup import search_business_partner, business_partner_lookup


class TestBusinessPartnerLookup:
    """Test suite for business partner lookup functionality"""
    
    def test_exact_match(self):
        """Test exact name match (case-insensitive)"""
        result = search_business_partner("Acme Corp")
        assert result is not None
        assert result["name"] == "Acme Corp"
        assert result["id"] == "BP001"
        assert result["city"] == "New York"
        assert result["country"] == "USA"
    
    def test_partial_match(self):
        """Test partial name match"""
        result = search_business_partner("Acme")
        assert result is not None
        assert result["name"] == "Acme Corp"
    
    def test_case_insensitive(self):
        """Test case-insensitive matching"""
        result = search_business_partner("acme corp")
        assert result is not None
        assert result["name"] == "Acme Corp"
        
        result2 = search_business_partner("TECHVENTURES")
        assert result2 is not None
        assert result2["name"] == "TechVentures GmbH"
    
    def test_no_match(self):
        """Test behavior when no match is found"""
        result = search_business_partner("NonExistent Company")
        assert result is None
    
    def test_empty_query(self):
        """Test behavior with empty query"""
        result = search_business_partner("")
        assert result is None
    
    def test_tool_wrapper_success(self):
        """Test LangChain tool wrapper with successful lookup"""
        result = business_partner_lookup.invoke({"partner_name": "Acme Corp"})
        assert "Acme Corp" in result
        assert "BP001" in result
        assert "New York" in result
        assert "USA" in result
    
    def test_tool_wrapper_not_found(self):
        """Test LangChain tool wrapper with no match"""
        result = business_partner_lookup.invoke({"partner_name": "NonExistent"})
        assert "not found" in result.lower()
    
    def test_tool_wrapper_suggestions(self):
        """Test tool wrapper provides suggestions for similar names"""
        result = business_partner_lookup.invoke({"partner_name": "Tech"})
        # Should find TechVentures GmbH or Dragon Tech Co
        assert "TechVentures" in result or "Dragon Tech" in result


if __name__ == "__main__":
    # Run tests
    test = TestBusinessPartnerLookup()
    
    print("Running business_partner_lookup tests...")
    test.test_exact_match()
    print("✓ test_exact_match passed")
    
    test.test_partial_match()
    print("✓ test_partial_match passed")
    
    test.test_case_insensitive()
    print("✓ test_case_insensitive passed")
    
    test.test_no_match()
    print("✓ test_no_match passed")
    
    test.test_empty_query()
    print("✓ test_empty_query passed")
    
    test.test_tool_wrapper_success()
    print("✓ test_tool_wrapper_success passed")
    
    test.test_tool_wrapper_not_found()
    print("✓ test_tool_wrapper_not_found passed")
    
    test.test_tool_wrapper_suggestions()
    print("✓ test_tool_wrapper_suggestions passed")
    
    print("\nAll business_partner_lookup tests passed! ✓")
