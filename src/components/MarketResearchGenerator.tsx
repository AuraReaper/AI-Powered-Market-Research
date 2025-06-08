import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Download, FileText, FilePdf, AlertTriangle, CheckCircle, Globe } from 'lucide-react';
import { toast } from 'sonner';

import { generateReport, downloadMarkdown, downloadPdf, downloadHtml, APIError, type WarningInfo } from '@/api/marketResearch';

interface ReportUrls {
  htmlUrl?: string;
  pdfUrl?: string | null;
}

interface ErrorDetails {
  type: string;
  message: string;
  details?: string;
  suggestions: string[];
}

const MarketResearchGenerator: React.FC = () => {
  const [company, setCompany] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [reportUrls, setReportUrls] = useState<ReportUrls | null>(null);
  const [warning, setWarning] = useState<WarningInfo | null>(null);
  const [lastError, setLastError] = useState<ErrorDetails | null>(null);
  const [isDownloading, setIsDownloading] = useState<{
    html: boolean;
    pdf: boolean;
  }>({ html: false, pdf: false });

  const handleCompanyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCompany(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!company.trim()) {
      toast.error('Please enter a company name');
      return;
    }

    setIsGenerating(true);
    setReportUrls(null);
    setWarning(null);
    setLastError(null);

    try {
      const response = await generateReport(company.trim());
      
      setReportUrls({
        htmlUrl: response.html_url,
        pdfUrl: response.pdf_url,
      });
      
      // Handle warnings (e.g., PDF generation failed but HTML succeeded)
      if (response.warning) {
        setWarning(response.warning);
        toast.warning(response.warning.message);
      } else {
        toast.success('Market research report generated successfully!');
      }
      
    } catch (error) {
      if (error instanceof APIError) {
        // Store detailed error information for display
        setLastError({
          type: error.errorType,
          message: error.getUserFriendlyMessage(),
          details: error.details,
          suggestions: error.suggestions
        });
        
        // Show user-friendly toast message
        toast.error(error.getUserFriendlyMessage());
      } else {
        // Fallback for non-API errors
        const errorMessage = error instanceof Error ? error.message : 'Failed to generate report';
        setLastError({
          type: 'unknown_error',
          message: errorMessage,
          suggestions: ['Please try again', 'Contact support if the issue persists']
        });
        toast.error(errorMessage);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async (type: 'html' | 'pdf') => {
    if (!company.trim()) return;

    setIsDownloading((prev) => ({ ...prev, [type]: true }));

    try {
      let blob: Blob;
      let filename: string;

      if (type === 'html') {
        blob = await downloadHtml(company.trim());
        filename = `${company.trim()}.html`;
      } else {
        blob = await downloadPdf(company.trim());
        filename = `${company.trim()}.pdf`;
      }

      // Create a URL for the blob and trigger download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success(`${type === 'html' ? 'HTML' : 'PDF'} downloaded successfully`);
    } catch (error) {
      if (error instanceof APIError) {
        toast.error(error.getUserFriendlyMessage());
        
        // For PDF errors, suggest alternatives
        if (error.errorType === 'pdf_conversion_error' && type === 'pdf') {
          setTimeout(() => {
            toast.info('💡 Try downloading the HTML version instead - you can print it to PDF using your browser!');
          }, 2000);
        }
      } else {
        toast.error(`Failed to download ${type}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    } finally {
      setIsDownloading((prev) => ({ ...prev, [type]: false }));
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Generate Market Research Report</CardTitle>
        <CardDescription>
          Enter a company name to generate a detailed market research report.
        </CardDescription>
      </CardHeader>
      
      {/* Error Display */}
      {lastError && (
        <CardContent>
          <Alert className="mb-4 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              <div className="font-medium mb-2">{lastError.message}</div>
              {lastError.suggestions.length > 0 && (
                <div className="text-sm">
                  <p className="font-medium mb-1">Suggestions:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {lastError.suggestions.map((suggestion, index) => (
                      <li key={index}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
              {lastError.details && (
                <details className="mt-2 text-xs">
                  <summary className="cursor-pointer font-medium">Technical Details</summary>
                  <p className="mt-1 text-gray-600">{lastError.details}</p>
                </details>
              )}
            </AlertDescription>
          </Alert>
        </CardContent>
      )}
      
      {/* Warning Display */}
      {warning && (
        <CardContent>
          <Alert className="mb-4 border-yellow-200 bg-yellow-50">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800">
              <div className="font-medium mb-2">{warning.message}</div>
              {warning.suggestions.length > 0 && (
                <div className="text-sm">
                  <p className="font-medium mb-1">What you can do:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {warning.suggestions.map((suggestion, index) => (
                      <li key={index}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </AlertDescription>
          </Alert>
        </CardContent>
      )}
      <form onSubmit={handleSubmit}>
        <CardContent>
          <div className="space-y-4">
            <Input
              placeholder="Company name (e.g., Tesla, Apple)"
              value={company}
              onChange={handleCompanyChange}
              disabled={isGenerating}
              required
            />
          </div>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isGenerating || !company.trim()}
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              'Generate Report'
            )}
          </Button>

          {reportUrls && (
            <div className="w-full flex flex-col space-y-2">
              <div className="text-sm text-center font-medium mb-2 flex items-center justify-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                Download Report
              </div>
              <div className="flex space-x-2 w-full">
                {/* HTML Download Button */}
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => handleDownload('html')}
                  disabled={isDownloading.html || !reportUrls.htmlUrl}
                >
                  {isDownloading.html ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Globe className="mr-2 h-4 w-4" />
                  )}
                  HTML
                </Button>
                
                {/* PDF Download Button */}
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => handleDownload('pdf')}
                  disabled={isDownloading.pdf || !reportUrls.pdfUrl}
                >
                  {isDownloading.pdf ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <FilePdf className="mr-2 h-4 w-4" />
                  )}
                  PDF
                  {!reportUrls.pdfUrl && (
                    <span className="ml-1 text-xs text-gray-500">(unavailable)</span>
                  )}
                </Button>
              </div>
              
              {/* PDF unavailable notice */}
              {reportUrls.htmlUrl && !reportUrls.pdfUrl && (
                <div className="text-xs text-center text-gray-600 mt-2">
                  💡 PDF generation failed, but you can print the HTML version to PDF using your browser
                </div>
              )}
            </div>
          )}
        </CardFooter>
      </form>
    </Card>
  );
};

export default MarketResearchGenerator;
