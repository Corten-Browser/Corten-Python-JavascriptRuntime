"""
FR-ES24-B-003: Lookbehind assertions (?<=...) and (?<!...)
"""

import pytest
from src.parser import RegExpParser
from src.executor import RegExpExecutor


class TestLookbehindParsing:
    """Test parsing of lookbehind assertions"""

    def test_parse_positive_lookbehind(self):
        """Parse positive lookbehind"""
        parser = RegExpParser()
        lb = parser.parse_lookbehind(r"\$", positive=True)
        assert lb.positive is True
        assert lb.pattern == r"\$"

    def test_parse_negative_lookbehind(self):
        """Parse negative lookbehind"""
        parser = RegExpParser()
        lb = parser.parse_lookbehind(r"\d", positive=False)
        assert lb.positive is False

    def test_unbounded_quantifier_error(self):
        """Unbounded quantifiers in lookbehind should error"""
        parser = RegExpParser()
        with pytest.raises(SyntaxError):
            parser.parse_lookbehind(r"a+")


class TestLookbehindExecution:
    """Test lookbehind execution"""

    def test_positive_lookbehind_matches(self):
        """Positive lookbehind matches"""
        executor = RegExpExecutor()
        assertion = RegExpParser().parse_lookbehind(r"\$", positive=True)
        # "Price $100" - position 7 is right after '$'
        # P=0, r=1, i=2, c=3, e=4, space=5, $=6, 1=7
        result = executor.execute_lookbehind(assertion, 7, "Price $100")
        assert result is True

    def test_positive_lookbehind_fails(self):
        """Positive lookbehind fails when pattern not behind"""
        executor = RegExpExecutor()
        assertion = RegExpParser().parse_lookbehind(r"\$", positive=True)
        result = executor.execute_lookbehind(assertion, 0, "100")
        assert result is False

    def test_negative_lookbehind_matches(self):
        """Negative lookbehind matches when pattern not present"""
        executor = RegExpExecutor()
        assertion = RegExpParser().parse_lookbehind(r"\d", positive=False)
        result = executor.execute_lookbehind(assertion, 4, "Year 2024")
        # Position 4 is after "Year", no digit behind
        assert result is True

    def test_negative_lookbehind_fails(self):
        """Negative lookbehind fails when pattern is present"""
        executor = RegExpExecutor()
        assertion = RegExpParser().parse_lookbehind(r"\d", positive=False)
        result = executor.execute_lookbehind(assertion, 4, "2024")
        # Position 4, digits are behind
        assert result is False

    @pytest.mark.skip(reason="Full pattern integration pending")
    def test_lookbehind_in_pattern(self):
        """Use lookbehind in full pattern"""
        executor = RegExpExecutor()
        pattern = r"(?<=\$)\d+\.\d{2}"
        result = executor.execute(pattern, "Price: $19.99")
        assert result.matched
        assert result.match_text == "19.99"

    @pytest.mark.skip(reason="Full pattern integration pending")
    def test_negative_lookbehind_in_pattern(self):
        """Use negative lookbehind in pattern"""
        executor = RegExpExecutor()
        pattern = r"(?<!\d)\d{4}(?!\d)"
        result = executor.execute(pattern, "Year 2024 not 20244")
        assert result.matched
        assert result.match_text == "2024"
