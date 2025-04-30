import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Download, FileText, FilePdf } from 'lucide-react';
import { toast } from 'sonner';

import { generateReport, downloadMarkdown, downloadPdf } from '@/api/marketResearch';

interface ReportUrls {
  markdownUrl: string;
  pdfUrl: string;
}

const MarketResearchGenerator: React.FC = () => {
  const [company, setCompany] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [reportUrls, setReportUrls] = useState<ReportUrls | null>(null);
  const [isDownloading, setIsDownloading] = useState<{
    markdown: boolean;
    pdf: boolean;
  }>({ markdown: false, pdf: false });

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

    try {
      const response = await generateReport(company.trim());
      setReportUrls({
        markdownUrl: response.markdown_url,
        pdfUrl: response.pdf_url,
      });
      toast.success('Market research report generated successfully!');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to generate report');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async (type: 'markdown' | 'pdf') => {
    if (!company.trim()) return;

    setIsDownloading((prev) => ({ ...prev, [type]: true }));

    try {
      let blob: Blob;
      let filename: string;

      if (type === 'markdown') {
        blob = await downloadMarkdown(company.trim());
        filename = `${company.trim()}.md`;
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

      toast.success(`${type === 'markdown' ? 'Markdown' : 'PDF'} downloaded successfully`);
    } catch (error) {
      toast.error(`Failed to download ${type}: ${error instanceof Error ? error.message : 'Unknown error'}`);
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
              <div className="text-sm text-center font-medium mb-2">Download Report</div>
              <div className="flex space-x-2 w-full">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => handleDownload('markdown')}
                  disabled={isDownloading.markdown}
                >
                  {isDownloading.markdown ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <FileText className="mr-2 h-4 w-4" />
                  )}
                  Markdown
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => handleDownload('pdf')}
                  disabled={isDownloading.pdf}
                >
                  {isDownloading.pdf ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <FilePdf className="mr-2 h-4 w-4" />
                  )}
                  PDF
                </Button>
              </div>
            </div>
          )}
        </CardFooter>
      </form>
    </Card>
  );
};

export default MarketResearchGenerator;

