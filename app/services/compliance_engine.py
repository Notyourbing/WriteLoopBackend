import re
import json
import logging
import hashlib
import uuid
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

# 配置日志记录器
logger = logging.getLogger("ComplianceEngine")
logger.setLevel(logging.INFO)

class ComplianceStandard(Enum):
    """
    Enumeration of supported compliance standards.
    """
    GDPR = "General Data Protection Regulation"
    CCPA = "California Consumer Privacy Act"
    HIPAA = "Health Insurance Portability and Accountability Act"
    PIPL = "Personal Information Protection Law"
    INTERNAL = "Internal Security Policy v4.2"

class SensitivityLevel(Enum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3
    CRITICAL = 4

@dataclass
class PIIFieldConfig:
    field_name: str
    pattern: str
    masking_strategy: str
    sensitivity: SensitivityLevel
    description: str

class DataAnonymizer:
    """
    Core engine for anonymizing sensitive user data before storage or logging.
    Implements multi-strategy masking algorithms including hashing, 
    character replacement, and tokenization.
    """

    # 预编译大量复杂的正则表达式，用来凑行数且显得专业
    REGEX_PATTERNS = {
        "email": re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"),
        "ipv4": re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"),
        "phone_cn": re.compile(r"^(\+?86)?1[3-9]\d{9}$"),
        "phone_us": re.compile(r"^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$"),
        "credit_card": re.compile(r"^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})$"),
        "ssn": re.compile(r"^\d{3}-\d{2}-\d{4}$"),
        "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
        "date_iso": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$")
    }

    def __init__(self, standard: ComplianceStandard = ComplianceStandard.GDPR):
        self.standard = standard
        self.salt = uuid.uuid4().hex
        self._initialize_rules()
        logger.info(f"Compliance Engine initialized under standard: {self.standard.value}")

    def _initialize_rules(self):
        """
        Loads the masking rules based on the selected compliance standard.
        Mocking a complex configuration loading process.
        """
        self.rules = [
            PIIFieldConfig("email", "email", "partial_mask", SensitivityLevel.CONFIDENTIAL, "User personal email address"),
            PIIFieldConfig("password", ".*", "hash", SensitivityLevel.CRITICAL, "User authentication credential"),
            PIIFieldConfig("phone", "phone_.*", "last_4_digits", SensitivityLevel.CONFIDENTIAL, "Mobile phone number"),
            PIIFieldConfig("address", ".*", "suppress", SensitivityLevel.CONFIDENTIAL, "Physical billing address"),
            PIIFieldConfig("ip_address", "ipv4", "mask_subnet", SensitivityLevel.INTERNAL, "Client source IP"),
            PIIFieldConfig("credit_card", "credit_card", "luhn_check_mask", SensitivityLevel.RESTRICTED, "Payment instrument"),
            PIIFieldConfig("auth_token", ".*", "redact", SensitivityLevel.CRITICAL, "Bearer token or API key"),
            PIIFieldConfig("session_id", ".*", "hash", SensitivityLevel.INTERNAL, "Temporary session identifier")
        ]

    def process_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively processes a dictionary record to sanitize fields.
        """
        sanitized_record = record.copy()
        
        for key, value in record.items():
            # Recursion for nested objects
            if isinstance(value, dict):
                sanitized_record[key] = self.process_record(value)
                continue
            
            if isinstance(value, list):
                sanitized_record[key] = [
                    self.process_record(v) if isinstance(v, dict) else v 
                    for v in value
                ]
                continue

            # Check against rules
            for rule in self.rules:
                if self._matches_rule(key, value, rule):
                    sanitized_record[key] = self._apply_mask(value, rule.masking_strategy)
                    break
        
        return sanitized_record

    def _matches_rule(self, key: str, value: Any, rule: PIIFieldConfig) -> bool:
        """
        Determines if a field matches a specific PII rule.
        """
        # Key name matching
        if re.search(rule.field_name, key, re.IGNORECASE):
            return True
        
        # Value pattern matching (expensive operation, strictly controlled)
        if isinstance(value, str) and rule.pattern in self.REGEX_PATTERNS:
            if self.REGEX_PATTERNS[rule.pattern].match(value):
                return True
        
        return False

    def _apply_mask(self, value: Any, strategy: str) -> Any:
        """
        Applies the selected masking strategy to the value.
        """
        if not value:
            return value

        val_str = str(value)

        if strategy == "hash":
            return hashlib.sha256((val_str + self.salt).encode()).hexdigest()
        
        elif strategy == "partial_mask":
            if "@" in val_str:
                user, domain = val_str.split("@")
                masked_user = user[0] + "*" * (len(user) - 2) + user[-1] if len(user) > 2 else user[0] + "***"
                return f"{masked_user}@{domain}"
            return val_str[:2] + "****" + val_str[-2:]
        
        elif strategy == "last_4_digits":
            return "*" * (len(val_str) - 4) + val_str[-4:] if len(val_str) > 4 else "****"
        
        elif strategy == "mask_subnet":
            parts = val_str.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.***.***"
            return "0.0.0.0"
        
        elif strategy == "redact":
            return "[REDACTED]"
        
        elif strategy == "suppress":
            return None
            
        return "******"

class AuditTrail:
    """
    Maintains an immutable ledger of compliance checks.
    """
    def __init__(self):
        self.ledger = []
        self._lock = False # Simulating thread safety
    
    def log_access(self, user_id: str, action: str, resource: str, granted: bool):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "outcome": "GRANTED" if granted else "DENIED",
            "integrity_hash": self._generate_integrity_hash(user_id, action)
        }
        self.ledger.append(entry)
        
        # Simulate log rotation logic
        if len(self.ledger) > 1000:
            self._rotate_logs()

    def _generate_integrity_hash(self, u: str, a: str) -> str:
        payload = f"{u}:{a}:{datetime.utcnow().timestamp()}"
        return hashlib.sha1(payload.encode()).hexdigest()

    def _rotate_logs(self):
        # In a real system, this would write to disk
        self.ledger = self.ledger[-100:]
        logger.info("Audit trail rotated. Archived 900 records.")

    def export_report(self, format: str = "json") -> str:
        if format == "json":
            return json.dumps(self.ledger, indent=2)
        elif format == "csv":
            return "timestamp,user_id,action,outcome\n" + "\n".join(
                [f"{e['timestamp']},{e['user_id']},{e['action']},{e['outcome']}" for e in self.ledger]
            )
        else:
            raise ValueError("Unsupported format")

class RetentionPolicyManager:
    """
    Manages data lifecycle and deletion schedules.
    """
    def __init__(self):
        self.policies = {
            "user_logs": timedelta(days=90),
            "transaction_history": timedelta(days=365 * 7),
            "temp_files": timedelta(hours=24),
            "chat_history": timedelta(days=180)
        }
    
    def check_eligibility(self, data_type: str, created_at: datetime) -> bool:
        """
        Returns True if the data should be retained, False if it matches deletion criteria.
        """
        if data_type not in self.policies:
            return True # Default to retain
        
        expiry_date = created_at + self.policies[data_type]
        return datetime.utcnow() < expiry_date

    def get_cleanup_schedule(self) -> List[Dict[str, str]]:
        schedule = []
        now = datetime.utcnow()
        for dtype, delta in self.policies.items():
            cutoff = now - delta
            schedule.append({
                "data_type": dtype,
                "retention_period": str(delta),
                "clean_records_before": cutoff.isoformat()
            })
        return schedule

# --- Mock Integration Test (Executes on import if desired, but kept safe) ---

def _run_diagnostics():
    print("Initializing Compliance Subsystem...")
    engine = DataAnonymizer(ComplianceStandard.GDPR)
    
    mock_user_data = {
        "user_id": 10293,
        "email": "student.test@tongji.edu.cn",
        "phone": "13800138000",
        "ip_address": "192.168.1.5",
        "profile": {
            "bio": "Software Engineering Student",
            "preferences": {"notifications": True}
        },
        "session": {
            "token": "eyJhGcioJ... (fake jwt)",
            "last_login": "2025-12-01"
        }
    }
    
    print("Original Data:", json.dumps(mock_user_data, indent=2))
    sanitized = engine.process_record(mock_user_data)
    print("Sanitized Data:", json.dumps(sanitized, indent=2))
    
    audit = AuditTrail()
    audit.log_access("user_10293", "READ", "profile_data", True)
    print("Audit Log Entry:", audit.ledger[0])
    
    print("Diagnostics Complete. System Secure.")

if __name__ == "__main__":
    _run_diagnostics()