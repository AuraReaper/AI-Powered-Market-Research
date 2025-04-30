import axios from 'axios';

// API response types
export interface GenerateReportResponse {
  message: string;
  markdown_url: string;
  pdf_url: string;
}

// Base URL for the API
const API_BASE_URL = 'http://localhost:8000';

/**
 * Generate a market research report for a company
 * @param company The name of the company
 * @returns Promise with the response containing download URLs
 */
export const generateReport = async (company: string): Promise<GenerateReportResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to generate report');
    }

    return await response.json();
  } catch (error) {
    console.error('Error generating report:', error);
    throw error;
  }
};

/**
 * Download a markdown file for a company report
 * @param company The name of the company
 * @returns Promise with the blob data for the markdown file
 */
export const downloadMarkdown = async (company: string): Promise<Blob> => {
  try {
    const response = await fetch(`${API_BASE_URL}/download/md/${company}`);
    
    if (!response.ok) {
      throw new Error('Failed to download markdown file');
    }
    
    return await response.blob();
  } catch (error) {
    console.error('Error downloading markdown:', error);
    throw error;
  }
};

/**
 * Download a PDF file for a company report
 * @param company The name of the company
 * @returns Promise with the blob data for the PDF file
 */
export const downloadPdf = async (company: string): Promise<Blob> => {
  try {
    const response = await fetch(`${API_BASE_URL}/download/pdf/${company}`);
    
    if (!response.ok) {
      throw new Error('Failed to download PDF file');
    }
    
    return await response.blob();
  } catch (error) {
    console.error('Error downloading PDF:', error);
    throw error;
  }
};

