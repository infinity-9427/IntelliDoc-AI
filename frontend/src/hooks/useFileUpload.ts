import { useState, useCallback, useEffect } from 'react';
import { apiClient, UploadResponse, JobStatus, ProcessingResult } from '@/lib/api';

export interface FileUploadState {
  id: string;
  name: string;
  size: number;
  type: string;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  file: File;
  jobId?: string;
  result?: ProcessingResult;
  error?: string;
}

export const useFileUpload = () => {
  const [files, setFiles] = useState<FileUploadState[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  // Update progress based on actual backend response
  const updateFileProgress = useCallback((fileId: string, progress: number, status?: string) => {
    setFiles(prev => prev.map(f => 
      f.id === fileId 
        ? { 
            ...f, 
            progress: Math.max(f.progress, progress), // Only allow progress to increase
            ...(status && { status: status as any })
          }
        : f
    ));
  }, []);

  const addFiles = useCallback((newFiles: File[]) => {
    const fileStates: FileUploadState[] = newFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0,
      file
    }));

    setFiles(prev => [...prev, ...fileStates]);
    return fileStates;
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(file => file.id !== id));
  }, []);

  const clearAllFiles = useCallback(() => {
    setFiles([]);
  }, []);

  const uploadFile = useCallback(async (fileId: string): Promise<void> => {
    const fileState = files.find(f => f.id === fileId);
    if (!fileState) return;

    try {
      // Start upload with 1% progress
      setFiles(prev => prev.map(f => 
        f.id === fileId 
          ? { ...f, status: 'uploading', progress: 1 }
          : f
      ));

      console.log(`Starting upload for file: ${fileState.name}`);

      // Upload file with real progress tracking (1-30%)
      const uploadResponse: UploadResponse = await apiClient.uploadFile(
        fileState.file,
        (progress) => {
          // Map upload progress to 1-30% range
          const mappedProgress = Math.max(1, Math.min(30, Math.round(progress * 0.3)));
          console.log(`Upload progress: ${progress}% -> mapped: ${mappedProgress}%`);
          
          // Ensure progress increases smoothly
          setFiles(prev => prev.map(f => 
            f.id === fileId 
              ? { 
                  ...f, 
                  progress: Math.max(f.progress, mappedProgress)
                }
              : f
          ));
        }
      );
      
      console.log(`Upload completed, transitioning to processing`);
      
      // Wait a moment to ensure final upload progress is shown
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Upload complete, ensure we're at 30% before moving to processing
      setFiles(prev => prev.map(f => 
        f.id === fileId 
          ? { 
              ...f, 
              progress: Math.max(f.progress, 30) // Ensure we're at least at 30%
            }
          : f
      ));
      
      // Small delay before transitioning to processing
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Now start processing phase
      setFiles(prev => prev.map(f => 
        f.id === fileId 
          ? { 
              ...f, 
              status: 'processing', 
              progress: 31,
              jobId: uploadResponse.job_id 
            }
          : f
      ));

      console.log(`Started polling for job: ${uploadResponse.job_id}`);
      
      // Start polling for real backend progress
      pollJobStatus(fileId, uploadResponse.job_id);

    } catch (error) {
      console.error('Upload failed:', error);
      setFiles(prev => prev.map(f => 
        f.id === fileId 
          ? { 
              ...f, 
              status: 'error', 
              progress: 100, 
              error: error instanceof Error ? error.message : 'Upload failed' 
            }
          : f
      ));
    }
  }, [files, updateFileProgress]);

  const pollJobStatus = useCallback(async (fileId: string, jobId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const statusResponse: JobStatus = await apiClient.getJobStatus(jobId);
        
        // Update progress with real backend progress (direct mapping)
        const backendProgress = statusResponse.progress || 31;
        const mappedProgress = Math.max(31, Math.min(100, backendProgress));
        
        setFiles(prev => prev.map(f => 
          f.id === fileId 
            ? { 
                ...f, 
                progress: mappedProgress,
                status: statusResponse.status === 'completed' ? 'completed' : 
                        statusResponse.status === 'error' ? 'error' : 'processing',
                error: statusResponse.error
              }
            : f
        ));

        // If completed, get results and set to 100%
        if (statusResponse.status === 'completed') {
          clearInterval(pollInterval);
          
          try {
            const results: ProcessingResult = await apiClient.getProcessingResults(jobId);
            // Set to 100% immediately
            setFiles(prev => prev.map(f => 
              f.id === fileId 
                ? { ...f, result: results, progress: 100, status: 'completed' }
                : f
            ));
          } catch (error) {
            console.error('Failed to get results:', error);
            setFiles(prev => prev.map(f => 
              f.id === fileId 
                ? { 
                    ...f, 
                    status: 'error', 
                    error: 'Failed to retrieve results' 
                  }
                : f
            ));
          }
        }

        // If error, stop polling
        if (statusResponse.status === 'error') {
          clearInterval(pollInterval);
        }

      } catch (error) {
        console.error('Status polling failed:', error);
        clearInterval(pollInterval);
        setFiles(prev => prev.map(f => 
          f.id === fileId 
            ? { 
                ...f, 
                status: 'error', 
                error: 'Connection lost - please try again' 
              }
            : f
        ));
      }
    }, 1000); // Poll every 1 second for real-time progress updates

    // Stop polling after 15 minutes for large files
    setTimeout(() => {
      clearInterval(pollInterval);
      setFiles(prev => prev.map(f => 
        f.id === fileId && f.status === 'processing'
          ? { 
              ...f, 
              status: 'error', 
              error: 'Processing timeout - file may be too large' 
            }
          : f
      ));
    }, 15 * 60 * 1000);
  }, [updateFileProgress]);

  const uploadAllFiles = useCallback(async () => {
    setIsUploading(true);
    
    const pendingFiles = files.filter(f => f.status === 'pending');
    
    try {
      // Upload files sequentially to avoid overwhelming the server
      for (const file of pendingFiles) {
        await uploadFile(file.id);
        // Small delay between uploads
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    } finally {
      setIsUploading(false);
    }
  }, [files, uploadFile]);

  const downloadResult = useCallback(async (fileId: string, format: 'docx' | 'txt' = 'docx') => {
    const fileState = files.find(f => f.id === fileId);
    if (!fileState?.jobId) {
      throw new Error('No job ID found for file');
    }

    try {
      const blob = await apiClient.downloadProcessedFile(fileState.jobId, format);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${fileState.name.replace(/\.[^/.]+$/, '')}_processed.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      throw error;
    }
  }, [files]);

  return {
    files,
    isUploading,
    addFiles,
    removeFile,
    clearAllFiles,
    uploadFile,
    uploadAllFiles,
    downloadResult
  };
};
