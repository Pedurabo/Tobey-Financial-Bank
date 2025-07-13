"""
Audit service for Tobey Finance Bank
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.audit_log import AuditLog, AuditAction
from ..utils.database import DatabaseManager

class AuditService:
    """Service class for audit operations"""
    
    def __init__(self, database_manager: DatabaseManager):
        self.db = database_manager
    
    def log_action(self, employee_id: str, action: AuditAction, target_type: str = "", 
                   target_id: str = "", details: str = "", success: bool = True,
                   additional_data: Dict[str, Any] = None) -> AuditLog:
        """Log an employee action"""
        if additional_data is None:
            additional_data = {}
        
        audit_log = AuditLog(
            employee_id=employee_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            success=success,
            additional_data=additional_data
        )
        
        self.db.save_audit_log(audit_log.to_dict())
        return audit_log
    
    def get_employee_logs(self, employee_id: str, days: int = 30) -> List[AuditLog]:
        """Get audit logs for a specific employee"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        logs_data = self.db.get_audit_logs(employee_id=employee_id, 
                                          start_date=start_date, 
                                          end_date=end_date)
        return [AuditLog.from_dict(log) for log in logs_data]
    
    def get_action_logs(self, action: AuditAction, days: int = 30) -> List[AuditLog]:
        """Get audit logs for a specific action type"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        logs_data = self.db.get_audit_logs(action=action.value, 
                                          start_date=start_date, 
                                          end_date=end_date)
        return [AuditLog.from_dict(log) for log in logs_data]
    
    def get_failed_logs(self, days: int = 30) -> List[AuditLog]:
        """Get failed audit logs"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        logs_data = self.db.get_audit_logs(start_date=start_date, end_date=end_date)
        failed_logs = [log for log in logs_data if not log.get('success', True)]
        return [AuditLog.from_dict(log) for log in failed_logs]
    
    def get_recent_logs(self, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs"""
        logs_data = self.db.get_audit_logs()
        return [AuditLog.from_dict(log) for log in logs_data[:limit]]
    
    def search_logs(self, search_term: str, days: int = 30) -> List[AuditLog]:
        """Search audit logs by details or target_id"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        logs_data = self.db.get_audit_logs(start_date=start_date, end_date=end_date)
        
        results = []
        search_term = search_term.lower()
        for log in logs_data:
            if (search_term in log.get('details', '').lower() or
                search_term in log.get('target_id', '').lower() or
                search_term in log.get('employee_id', '').lower()):
                results.append(AuditLog.from_dict(log))
        
        return results 