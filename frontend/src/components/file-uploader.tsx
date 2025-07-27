'use client'

import React, { useCallback, useState, useRef } from 'react'
import { useTranslations } from 'next-intl'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface FileItem {
  id: string
  name: string
  size: number
  type: string
  status: 'pending' | 'uploading' | 'completed' | 'error'
  progress: number
  file: File
}

const FileUploader: React.FC = () => {
  const t = useTranslations('FileUploader')
  const [files, setFiles] = useState<FileItem[]>([])
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
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
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

  const addFiles = useCallback((newFiles: File[]) => {
    const validFiles: FileItem[] = []
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

      validFiles.push({
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'pending',
        progress: 0,
        file
      })
    })

    if (!hasError) {
      setError(null)
      setFiles(prev => [...prev, ...validFiles])
    }
  }, [files])

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(file => file.id !== id))
  }

  const clearAllFiles = () => {
    setFiles([])
    setError(null)
  }

  const simulateUpload = (fileId: string) => {
    setFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, status: 'uploading' as const }
        : file
    ))

    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 20
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        setFiles(prev => prev.map(file => 
          file.id === fileId 
            ? { ...file, status: 'completed' as const, progress: 100 }
            : file
        ))
      } else {
        setFiles(prev => prev.map(file => 
          file.id === fileId 
            ? { ...file, progress }
            : file
        ))
      }
    }, 200)
  }

  const uploadAllFiles = () => {
    files.forEach(file => {
      if (file.status === 'pending') {
        simulateUpload(file.id)
      }
    })
  }

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || [])
    addFiles(selectedFiles)
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
    addFiles(droppedFiles)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const getFileIcon = (type: string): string => {
    if (type.includes('pdf')) return 'ri-file-pdf-line'
    if (type.includes('word') || type.includes('document')) return 'ri-file-word-line'
    if (type.includes('text')) return 'ri-file-text-line'
    if (type.includes('image')) return 'ri-image-line'
    return 'ri-file-line'
  }

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'pending': return 'ri-time-line'
      case 'uploading': return 'ri-loader-2-line'
      case 'completed': return 'ri-checkbox-circle-line'
      case 'error': return 'ri-error-warning-line'
      default: return 'ri-file-line'
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
              {t.raw('dropzone.formats').map((format: string, index: number) => (
                <Badge key={index} variant="outline">{format}</Badge>
              ))}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileInput}
              className="hidden"
              accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif"
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
                disabled={files.every(f => f.status !== 'pending')}
                size="sm"
              >
                <i className="ri-upload-line w-4 h-4 mr-2" />
                {t('fileList.actions.uploadAll')}
              </Button>
              <Button
                onClick={clearAllFiles}
                variant="outline"
                size="sm"
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
                    <Badge 
                      variant={file.status === 'completed' ? 'default' : 'secondary'}
                      className="ml-2"
                    >
                      <i className={`${getStatusIcon(file.status)} w-3 h-3 mr-1 ${
                        file.status === 'uploading' ? 'animate-spin' : ''
                      }`} />
                      {t(`status.${file.status}`)}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatFileSize(file.size)}
                    </p>
                    {file.status === 'uploading' && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {Math.round(file.progress)}%
                      </span>
                    )}
                  </div>

                  {file.status === 'uploading' && (
                    <Progress value={file.progress} className="mt-2 h-2" />
                  )}
                </div>

                <Button
                  onClick={() => removeFile(file.id)}
                  variant="ghost"
                  size="sm"
                  className="flex-shrink-0"
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
