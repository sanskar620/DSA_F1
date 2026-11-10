import os
import re

def audit_directory(root_dir):
    print(f"Auditing directory: {root_dir}")
    
    suspicious_patterns = [
        r"MockPredictor", r"MockModel", r"DummyModel", r"Stub",
        r"mock_", r"fake_", r"dummy_", r"sample prediction",
        r"return \{[\"']prediction[\"']: \d+\}",
        r"return \{[\"']strategy[\"']: [\"']\w+[\"']\}",
        r"return \{[\"']probability[\"']: \d+\.\d+\}",
        r"hardcoded", r"fallback", r"synthetic prediction"
    ]
    
    found_issues = []
    
    for subdir, _, files in os.walk(root_dir):
        # Ignore tests and scripts for the STRICT production audit
        if "tests" in subdir or "scripts" in subdir or "__pycache__" in subdir:
            continue
            
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(subdir, file)
                with open(path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        for pattern in suspicious_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                found_issues.append({
                                    "file": path,
                                    "line": i + 1,
                                    "pattern": pattern,
                                    "content": line.strip()
                                })
                                
    return found_issues

def main():
    print("=== Automated Mock Detection Audit ===")
    issues = audit_directory("backend")
    
    if not issues:
        print("[PASS] No suspicious mock logic found in production (backend/) code.")
    else:
        print(f"[FAIL] Found {len(issues)} suspicious lines:")
        for issue in issues:
            print(f"WARNING: {issue['file']}:{issue['line']}")
            print(f"Pattern matched: {issue['pattern']}")
            print(f"Content: {issue['content']}")
            
if __name__ == "__main__":
    main()
