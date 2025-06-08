import axios from 'axios';
// Error types from backend
export interface APIErrorResponse {
  error: boolean;
  error_type: string;
  message: string;
  details?: string;
  suggestions?: string[];
}

export interface WarningInfo {
  type: string;
  message: string;
  suggestions: string[];
}

// API response types
export interface GenerateReportResponse {
  message: string;
  html_url?: string;
  pdf_url?: string | null;
  success?: boolean;
  warning?: WarningInfo;
}

// Custom error class for API errors
export class APIError extends Error {
  constructor(
    message: string,
    public errorType: string,
    public details?: string,
    public suggestions: string[] = []
  ) {
    super(message);
    this.name = 'APIError';
  }

  static fromResponse(errorData: APIErrorResponse): APIError {
    return new APIError(
      errorData.message,
      errorData.error_type,
      errorData.details,
      errorData.suggestions || []
    );
  }

  getUserFriendlyMessage(): string {
    switch (this.errorType) {
      case 'token_limit_exceeded':
        return 'The request is too large for the AI model. Please try a shorter company name.';
      case 'api_quota_exceeded':
        return 'API usage limit reached. Please wait a few minutes and try again.';
      case 'api_timeout':
        return 'The request timed out. Please try again.';
      case 'invalid_api_key':
        return 'API configuration issue. Please contact support.';
      case 'network_error':
        return 'Network connection issue. Please check your internet and try again.';
      case 'processing_error':
        return 'Error processing your request. Please try with a different company name.';
      case 'pdf_conversion_error':
        return 'Report generated but PDF creation failed. You can download the HTML version.';
      case 'invalid_input':
        return this.message; // Use the specific validation message
      default:
        return this.message || 'An unexpected error occurred. Please try again.';
    }
  }
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
      
      // Check if this is our structured error response
      if (errorData.detail && typeof errorData.detail === 'object' && errorData.detail.error) {
        throw APIError.fromResponse(errorData.detail);
      }
      
      // Handle FastAPI validation errors
      if (errorData.detail && Array.isArray(errorData.detail)) {
        const validationErrors = errorData.detail.map((err: any) => err.msg).join(', ');
        throw new APIError(
          `Validation error: ${validationErrors}`,
          'invalid_input',
          validationErrors,
          ['Please check your input and try again']
        );
      }
      
      // Fallback for other error formats
      throw new APIError(
        errorData.detail || 'Failed to generate report',
        'server_error',
        undefined,
        ['Please try again or contact support if the issue persists']
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    
    // Handle network errors and other exceptions
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError(
        'Unable to connect to the server. Please check your internet connection.',
        'network_error',
        error.message,
        ['Check your internet connection', 'Try again in a few moments', 'Contact support if the issue persists']
      );
    }
    
    console.error('Unexpected error generating report:', error);
    throw new APIError(
      'An unexpected error occurred while generating the report.',
      'processing_error',
      error instanceof Error ? error.message : String(error),
      ['Please try again', 'Contact support if the issue persists']
    );
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
      if (response.status === 404) {
        throw new APIError(
          'Markdown file not found. Please generate a report first.',
          'processing_error',
          'The requested markdown file does not exist',
          ['Generate a new report for this company', 'Check that the company name is correct']
        );
      }
      throw new APIError(
        'Failed to download markdown file',
        'server_error',
        `HTTP ${response.status}`,
        ['Try again in a few moments', 'Contact support if the issue persists']
      );
    }
    
    return await response.blob();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    console.error('Error downloading markdown:', error);
    throw new APIError(
      'Network error while downloading markdown file',
      'network_error',
      error instanceof Error ? error.message : String(error),
      ['Check your internet connection', 'Try again in a few moments']
    );
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
      if (response.status === 404) {
        throw new APIError(
          'PDF file not found. It may have failed to generate or you need to generate a report first.',
          'pdf_conversion_error',
          'The requested PDF file does not exist',
          [
            'Try downloading the HTML version instead',
            'Generate a new report for this company',
            'Check that the company name is correct'
          ]
        );
      }
      throw new APIError(
        'Failed to download PDF file',
        'server_error',
        `HTTP ${response.status}`,
        ['Try downloading the HTML version instead', 'Contact support if PDF is critical']
      );
    }
    
    return await response.blob();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    console.error('Error downloading PDF:', error);
    throw new APIError(
      'Network error while downloading PDF file',
      'network_error',
      error instanceof Error ? error.message : String(error),
      ['Check your internet connection', 'Try downloading the HTML version instead']
    );
  }
};

/**
 * Download HTML file for a company report
 * @param company The name of the company
 * @returns Promise with the blob data for the HTML file
 */
export const downloadHtml = async (company: string): Promise<Blob> => {
  try {
    const response = await fetch(`${API_BASE_URL}/download/html/${company}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new APIError(
          'HTML file not found. Please generate a report first.',
          'processing_error',
          'The requested HTML file does not exist',
          ['Generate a new report for this company', 'Check that the company name is correct']
        );
      }
      throw new APIError(
        'Failed to download HTML file',
        'server_error',
        `HTTP ${response.status}`,
        ['Try again in a few moments', 'Contact support if the issue persists']
      );
    }
    
    return await response.blob();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    console.error('Error downloading HTML:', error);
    throw new APIError(
      'Network error while downloading HTML file',
      'network_error',
      error instanceof Error ? error.message : String(error),
      ['Check your internet connection', 'Try again in a few moments']
    );
  }
};

