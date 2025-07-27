'use client'

import React from 'react'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import LocaleSwitcher from '@/components/LocaleSwitcher'

const Header: React.FC = () => {
  const t = useTranslations('Header')
  
  return (
    <header className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600">
              <i className="ri-brain-line text-white text-xl" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                {t('brand')}
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {t('subtitle')}
              </p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a 
              href="#upload-section" 
              className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
            >
              {t('navigation.upload')}
            </a>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <Button 
              onClick={() => document.getElementById('upload-section')?.scrollIntoView({ behavior: 'smooth' })}
              size="sm"
              className="hidden sm:flex"
            >
              <i className="ri-upload-line w-4 h-4 mr-2" />
              {t('cta')}
            </Button>
            {/* Mobile upload button */}
            <Button 
              onClick={() => document.getElementById('upload-section')?.scrollIntoView({ behavior: 'smooth' })}
              size="sm"
              className="sm:hidden"
            >
              <i className="ri-upload-line w-4 h-4" />
            </Button>
            <LocaleSwitcher />
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
