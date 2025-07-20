#!/usr/bin/env python3
"""
Output Manager Utility for MarketResearcher CrewAI Project
Handles unique filename generation and output folder organization
"""

import os
from datetime import datetime
from pathlib import Path
import json
import hashlib


class OutputManager:
    """Manages output files and folder organization for CrewAI reports"""
    
    def __init__(self, base_output_dir: str = None):
        """
        Initialize the output manager
        
        Args:
            base_output_dir: Base directory for outputs. If None, uses project root/output
        """
        if base_output_dir is None:
            # Get project root (3 levels up from src/marketresearcher/utils)
            project_root = Path(__file__).parent.parent.parent.parent
            self.base_output_dir = project_root / "output"
        else:
            self.base_output_dir = Path(base_output_dir)
        
        # Create output subdirectories
        self.reports_dir = self.base_output_dir / "reports"
        self.logs_dir = self.base_output_dir / "logs"
        self.temp_dir = self.base_output_dir / "temp"
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create output directories if they don't exist"""
        for directory in [self.reports_dir, self.logs_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_unique_filename(self, company_name: str, report_type: str = "final_proposal", 
                                extension: str = "md") -> str:
        """
        Generate a unique filename based on company name and timestamp
        
        Args:
            company_name: Name of the company being researched
            report_type: Type of report (e.g., 'final_proposal', 'industry_analysis')
            extension: File extension (default: 'md')
        
        Returns:
            Unique filename string
        """
        # Clean company name for filename
        clean_company = self._clean_filename(company_name)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create unique identifier (first 6 chars of hash)
        unique_id = self._generate_unique_id(company_name)
        
        return f"{clean_company}_{report_type}_{timestamp}_{unique_id}.{extension}"
    
    def get_report_path(self, company_name: str, report_type: str = "final_proposal") -> Path:
        """
        Get full path for a report file
        
        Args:
            company_name: Name of the company being researched
            report_type: Type of report
        
        Returns:
            Full Path object for the report file
        """
        filename = self.generate_unique_filename(company_name, report_type)
        return self.reports_dir / filename
    
    def get_log_path(self, company_name: str, log_type: str = "execution") -> Path:
        """
        Get full path for a log file
        
        Args:
            company_name: Name of the company being researched
            log_type: Type of log
        
        Returns:
            Full Path object for the log file
        """
        filename = self.generate_unique_filename(company_name, log_type, "log")
        return self.logs_dir / filename
    
    def save_metadata(self, company_name: str, metadata: dict) -> Path:
        """
        Save execution metadata to a JSON file
        
        Args:
            company_name: Name of the company being researched
            metadata: Dictionary containing execution metadata
        
        Returns:
            Path to the saved metadata file
        """
        filename = self.generate_unique_filename(company_name, "metadata", "json")
        filepath = self.reports_dir / filename
        
        # Add timestamp to metadata
        metadata["generated_at"] = datetime.now().isoformat()
        metadata["company"] = company_name
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def list_reports(self, company_name: str = None) -> list:
        """
        List all reports, optionally filtered by company name
        
        Args:
            company_name: Optional company name filter
        
        Returns:
            List of report file paths
        """
        pattern = "*.md"
        if company_name:
            clean_company = self._clean_filename(company_name)
            pattern = f"{clean_company}_*.md"
        
        return list(self.reports_dir.glob(pattern))
    
    def cleanup_old_files(self, days_old: int = 30):
        """
        Clean up files older than specified days
        
        Args:
            days_old: Number of days after which files should be deleted
        """
        import time
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        for directory in [self.reports_dir, self.logs_dir, self.temp_dir]:
            for file_path in directory.glob("*"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    print(f"Deleted old file: {file_path}")
    
    @staticmethod
    def _clean_filename(text: str) -> str:
        """
        Clean text to be safe for use as filename
        
        Args:
            text: Input text to clean
        
        Returns:
            Cleaned text safe for filenames
        """
        # Remove/replace problematic characters
        cleaned = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_'))
        cleaned = cleaned.replace(' ', '_').lower()
        # Remove multiple underscores
        while '__' in cleaned:
            cleaned = cleaned.replace('__', '_')
        return cleaned.strip('_')
    
    @staticmethod
    def _generate_unique_id(text: str) -> str:
        """
        Generate a short unique identifier based on input text
        
        Args:
            text: Input text to generate ID from
        
        Returns:
            6-character unique identifier
        """
        return hashlib.md5(text.encode()).hexdigest()[:6]


# Global instance for easy access
output_manager = OutputManager()


def get_output_manager() -> OutputManager:
    """Get the global output manager instance"""
    return output_manager


if __name__ == "__main__":
    # Test the output manager
    manager = OutputManager()
    
    # Test filename generation
    test_company = "BNY Mellon"
    print(f"Unique filename: {manager.generate_unique_filename(test_company)}")
    print(f"Report path: {manager.get_report_path(test_company)}")
    print(f"Log path: {manager.get_log_path(test_company)}")
    
    # Test metadata saving
    test_metadata = {
        "agents_used": ["industry_researcher", "competitor_researcher", "proposal_writer"],
        "execution_time": 45.6,
        "status": "completed"
    }
    metadata_path = manager.save_metadata(test_company, test_metadata)
    print(f"Metadata saved to: {metadata_path}")
