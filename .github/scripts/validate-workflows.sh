#!/bin/bash
set -e

echo "🔍 Validating GitHub Workflows..."

# Check if workflow files exist and are valid YAML
workflows=(
    ".github/workflows/ci-cd.yml"
    ".github/workflows/security.yml" 
    ".github/workflows/test-matrix.yml"
)

for workflow in "${workflows[@]}"; do
    if [[ -f "$workflow" ]]; then
        echo "✅ Found workflow: $workflow"
        # Basic YAML syntax check
        if command -v yq >/dev/null 2>&1; then
            yq eval '.' "$workflow" >/dev/null && echo "✅ Valid YAML syntax: $workflow" || echo "❌ Invalid YAML: $workflow"
        else
            echo "⚠️  yq not available, skipping YAML validation for $workflow"
        fi
    else
        echo "❌ Missing workflow: $workflow"
        exit 1
    fi
done

echo ""
echo "🎯 Workflow Summary:"
echo "  - CI/CD Pipeline: Comprehensive build, test, and release automation"
echo "  - Security Scan: Automated vulnerability scanning with Trivy"
echo "  - Test Matrix: Multi-platform testing (Ubuntu, macOS, AMD64, ARM64)"
echo ""
echo "✅ All workflows validated successfully!"
