#!/usr/bin/env python3
"""
Managed File Writer Tool for MarketResearcher CrewAI Project
A custom file writer that integrates with the output manager
"""

from crewai_tools import BaseTool
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from utils.output_manager import get_output_manager


class ManagedFileWriterInput(BaseModel):
    """Input schema for ManagedFileWriter tool."""
    content: str = Field(..., description="Content to write to the file")
    company_name: str = Field(..., description="Company name for generating unique filename")
    report_type: str = Field(default="final_proposal", description="Type of report being written")


class ManagedFileWriter(BaseTool):
    """
    File writer tool that automatically generates unique filenames and manages output directories.
    """
    
    name: str = "managed_file_writer"
    description: str = (
        "Write content to a file with automatic unique filename generation. "
        "Use this tool when you need to save the final proposal or any report content. "
        "The tool automatically generates unique filenames based on company name and timestamp "
        "to prevent overwrite issues."
    )
    args_schema: Type[BaseModel] = ManagedFileWriterInput
    
    def __init__(self):
        super().__init__()
        self.output_manager = get_output_manager()
    
    def _run(self, content: str, company_name: str, report_type: str = "final_proposal") -> str:
        """
        Write content to a uniquely named file.
        
        Args:
            content: The content to write to the file
            company_name: Company name for generating unique filename
            report_type: Type of report (default: "final_proposal")
        
        Returns:
            Success message with file path
        """
        try:
            # Generate unique file path
            file_path = self.output_manager.get_report_path(company_name, report_type)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Successfully wrote content to: {file_path}"
            
        except Exception as e:
            return f"❌ Error writing file: {str(e)}"


# Factory function for easy import
def create_managed_file_writer() -> ManagedFileWriter:
    """Create and return a ManagedFileWriter instance."""
    return ManagedFileWriter()
