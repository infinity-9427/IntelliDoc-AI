'use client'

import React, { useCallback, useState, useRef } from 'react'
import { useTranslations } from 'next-intl'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useFileUpload, FileUploadState } from '@/hooks/useFileUpload'

const FileUploader: React.FC = () => {
  const t = useTranslations('FileUploader')
  const { 
    files, 
    isUploading, 
    addFiles, 
    removeFile, 
    clearAllFiles, 
    uploadAllFiles,
    downloadResult 
  } = useFileUpload()
  
  const [isDragActive, setIsDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateFile = (file: File): string | null => {
    const maxSize = 50 * 1024 * 1024 // 50MB
    const allowedTypes = [
      'application/pdf',
      'image/jpeg',
      'image/png',
      'image/gif'
    ]

    if (file.size > maxSize) {
      return t('validation.fileSizeError')
    }

    if (!allowedTypes.includes(file.type)) {
      return t('validation.fileTypeError')
    }

    return null
  }

  const handleAddFiles = useCallback((newFiles: File[]) => {
    const validFiles: File[] = []
    let hasError = false

    newFiles.forEach((file) => {
      const validation = validateFile(file)
      if (validation) {
        setError(validation)
        hasError = true
        return
      }

      if (files.some(f => f.name === file.name)) {
        setError(t('validation.duplicateFileError'))
        hasError = true
        return
      }

      validFiles.push(file)
    })

    if (!hasError && validFiles.length > 0) {
      setError(null)
      addFiles(validFiles)
    }
  }, [files, addFiles, t])

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || [])
    handleAddFiles(selectedFiles)
    event.target.value = ''
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(true)
  }

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    handleAddFiles(droppedFiles)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleDownload = async (file: FileUploadState, format: 'docx' | 'txt' = 'docx') => {
    try {
      await downloadResult(file.id, format)
    } catch (error) {
      console.error('Download failed:', error)
      setError('Download failed. Please try again.')
    }
  }

  const getFileIcon = (type: string): string => {
    if (type.includes('pdf')) return 'ri-file-pdf-line'
    if (type.includes('image')) return 'ri-image-line'
    return 'ri-file-line'
  }

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'pending': return 'ri-time-line'
      case 'uploading': return 'ri-upload-line'
      case 'processing': return 'ri-loader-2-line'
      case 'completed': return 'ri-checkbox-circle-line'
      case 'error': return 'ri-error-warning-line'
      default: return 'ri-file-line'
    }
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
      case 'error': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
      case 'processing': 
      case 'uploading': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
    }
  }

  return (
    <section className="w-full max-w-6xl mx-auto p-6 space-y-8"
      id="upload-section"
    >
      {/* Header */}
      <div className="text-center space-y-4 mb-8">
        <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-sm font-medium">
          <i className="ri-upload-cloud-line w-4 h-4 mr-2" />
          {t('header.badge')}
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          {t('header.title')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          {t('header.description')}
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
          <i className="ri-error-warning-line w-4 h-4 text-red-600" />
          <AlertDescription className="text-red-700 dark:text-red-400">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Drop Zone */}
      <Card className="relative">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
          className={`
            border-2 border-dashed rounded-lg p-12 text-center transition-all duration-200 cursor-pointer
            ${isDragActive 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
              : 'border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600'
            }
          `}
        >
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
              <i className="ri-upload-cloud-2-line text-2xl text-gray-600 dark:text-gray-400" />
            </div>
            
            <div className="space-y-2">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {t('dropzone.title')}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {t('dropzone.subtitle')}
              </p>
            </div>

            <div className="flex justify-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              {['PDF', 'PNG', 'JPG', 'JPEG'].map((format: string, index: number) => (
                <Badge key={index} variant="outline">{format}</Badge>
              ))}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileInput}
              className="hidden"
              accept=".pdf,.jpg,.jpeg,.png,.gif"
            />
          </div>
        </div>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              {t('fileList.title')} ({files.length})
            </h3>
            <div className="space-x-2">
              <Button
                onClick={uploadAllFiles}
                disabled={files.every(f => f.status !== 'pending') || isUploading}
                size="sm"
              >
                <i className="ri-upload-line w-4 h-4 mr-2" />
                {isUploading ? 'Processing...' : t('fileList.actions.uploadAll')}
              </Button>
              <Button
                onClick={clearAllFiles}
                variant="outline"
                size="sm"
                disabled={isUploading}
              >
                <i className="ri-delete-bin-line w-4 h-4 mr-2" />
                {t('fileList.actions.clearAll')}
              </Button>
            </div>
          </div>

          <div className="space-y-3">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center space-x-4 p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50"
              >
                <div className="flex-shrink-0">
                  <i className={`${getFileIcon(file.type)} text-2xl text-gray-600 dark:text-gray-400`} />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {file.name}
                    </p>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(file.status)}>
                        <i className={`${getStatusIcon(file.status)} w-3 h-3 mr-1 ${
                          file.status === 'uploading' || file.status === 'processing' ? 'animate-spin' : ''
                        }`} />
                        {t(`status.${file.status}`)}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatFileSize(file.size)}
                    </p>
                    {(file.status === 'uploading' || file.status === 'processing') && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {Math.round(file.progress)}%
                      </span>
                    )}
                  </div>

                  {(file.status === 'uploading' || file.status === 'processing') && (
                    <Progress value={file.progress} className="mt-2 h-2" />
                  )}

                  {file.error && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                      {file.error}
                    </p>
                  )}

                  {file.status === 'completed' && file.result && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs text-green-600 dark:text-green-400">
                        ✓ Text extracted: {file.result.text_statistics?.word_count || 0} words
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Confidence: {Math.round((file.result.text_confidence || 0) * 100)}%
                      </p>
                      <div className="flex space-x-2 mt-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(file, 'docx')}
                          className="text-xs"
                        >
                          <i className="ri-download-line w-3 h-3 mr-1" />
                          Download DOCX
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(file, 'txt')}
                          className="text-xs"
                        >
                          <i className="ri-download-line w-3 h-3 mr-1" />
                          Download TXT
                        </Button>
                      </div>
                    </div>
                  )}
                </div>

                <Button
                  onClick={() => removeFile(file.id)}
                  variant="ghost"
                  size="sm"
                  className="flex-shrink-0"
                  disabled={isUploading && (file.status === 'uploading' || file.status === 'processing')}
                >
                  <i className="ri-close-line w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Upload Statistics */}
      {files.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {files.length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('stats.totalFiles')}</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {files.filter(f => f.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('stats.processed')}</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {files.filter(f => f.status === 'error').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Failed</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-gray-600 dark:text-gray-400">
              {formatFileSize(files.reduce((total, file) => total + file.size, 0))}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('stats.totalSize')}</div>
          </Card>
        </div>
      )}
    </section>
  )
}

export default FileUploader
