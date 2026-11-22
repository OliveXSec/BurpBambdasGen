"""Tests for the generated-Bambda validator."""

from src.generation.validator import BambdaValidator


def test_valid_view_filter_has_no_errors():
    validator = BambdaValidator()
    code = """/**
 * Show only 403 responses.
 * @author test
 */
if (!requestResponse.hasResponse()) {
    return false;
}
return requestResponse.response().statusCode() == 403;"""
    result = validator.validate(code, "VIEW_FILTER")
    assert result.is_valid
    assert result.errors == []


def test_custom_column_returning_String_is_not_flagged_as_a_typo():
    """Regression: the typo check used to run case-insensitively, so the correct
    capitalized `String` matched `\\bstring\\b` and every valid column was invalid."""
    validator = BambdaValidator()
    code = """/**
 * Server header.
 * @author test
 */
String server = requestResponse.response().headerValue("Server");
return server;"""
    result = validator.validate(code, "CUSTOM_COLUMN")
    assert result.is_valid
    assert not any("capitalized" in e for e in result.errors)


def test_lowercase_string_type_is_flagged():
    validator = BambdaValidator()
    code = 'string server = "x";\nreturn server;'
    result = validator.validate(code, "CUSTOM_COLUMN")
    assert any("capitalized" in e for e in result.errors)


def test_unbalanced_braces_are_reported():
    validator = BambdaValidator()
    result = validator.validate("if (true) {\n return true;", "VIEW_FILTER")
    assert not result.is_valid
    assert any("Unbalanced braces" in e for e in result.errors)


def test_missing_javadoc_is_a_warning_not_an_error():
    validator = BambdaValidator()
    result = validator.validate("return true;", "VIEW_FILTER")
    assert result.is_valid
    assert any("Javadoc" in w for w in result.warnings)


def test_scan_check_requires_audit_result():
    validator = BambdaValidator()
    result = validator.validate("return true;", "SCAN_CHECK_PASSIVE")
    assert not result.is_valid
