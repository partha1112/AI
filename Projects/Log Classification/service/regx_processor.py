import re

# Define patterns (pattern, label)
patterns = [
    (r"\b(GET|POST|PUT|DELETE|PATCH)\b.*\b(200|201|204|301|302|400|401|403|404|500|502|503)\b", "HTTP_STATUS"),

    (r"\b(login|logged in|signin|authenticated).*(success|successful)\b", "USER_ACTION"),

    (r"\b(login|authentication|signin).*(fail|failed|error|unsuccessful|denied)\b", "SECURITY_ALERT"),

    (r"\b(access|permission|authorization).*(denied|forbidden|unauthorized|rejected)\b", "SECURITY_ALERT"),

    (r"\b(db|database).*(fail|error|timeout|unreachable|lost|issue)\b", "ERROR"),

    (r"\b(exception|fatal).*(null|undefined|pointer|crash)?\b", "CRITICAL_ERROR"),

    (r"\b(memory|cpu|disk|resource).*(high|low|exceed|spike|leak|full|usage)\b", "RESOURCE_USAGE"),

    (r"\b(service|server|application).*(start|started|stop|stopped|restart|restarted)\b", "SYSTEM_NOTIFICATION"),

    (r"\b(file|resource|document).*(not found|missing|unavailable)\b", "ERROR"),

    (r"\b(timeout|timed out|took too long|delayed)\b", "ERROR"),

    (r"\b(api|endpoint|service).*(fail|error|unavailable|down)\b", "ERROR"),

    (r"\b(payment|transaction|billing|invoice).*(fail|error|declined|pending)\b", "WORKFLOW_ERROR"),

    (r"\b(deprecated|obsolete|no longer supported|will be removed)\b", "DEPRECATION_WARNING"),

    (r"\b(config|configuration|setting).*(invalid|missing|error|incorrect)\b", "ERROR"),

    (r"\b(suspicious|attack|intrusion|malicious|threat)\b", "SECURITY_ALERT"),

    (r"\b(job|task|queue|process).*(start|started|complete|completed|fail|failed)\b", "SYSTEM_NOTIFICATION"),

    (r"\b(cache).*(miss|fail|error|evict|clear)\b", "RESOURCE_USAGE"),
]

# Compile all patterns once
compiled_patterns = [(re.compile(p, re.IGNORECASE), label) for p, label in patterns]


def classify(log_message: str) -> str:
    for pattern, label in compiled_patterns:
        if pattern.search(log_message):
            return label
    return "UNKNOWN"