'use client'

import React from 'react'
import { useTranslations } from 'next-intl'
import ExternalLink from '@/components/ExternalLink'

const Footer: React.FC = () => {
  const t = useTranslations('Footer')
  
  return (
    <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Company */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
                <i className="ri-brain-line text-white text-sm" />
              </div>
              <span className="font-bold text-gray-900 dark:text-white">{t('brand.name')}</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('brand.description')}
            </p>
          </div>

          {/* What We Do */}
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900 dark:text-white">{t('sections.whatWeDo.title')}</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              {t.raw('sections.whatWeDo.items').map((item: string, index: number) => (
                <li key={index} className="flex items-center space-x-2">
                  <i className="ri-check-line text-green-500 w-4 h-4" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* How to Use */}
          <div className="space-y-4" id="how-it-works">
            <h3 className="font-semibold text-gray-900 dark:text-white">{t('sections.howToUse.title')}</h3>
            <ol className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              {t.raw('sections.howToUse.steps').map((step: string, index: number) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full w-5 h-5 flex items-center justify-center text-xs font-semibold mt-0.5">
                    {index + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {t('copyright', { year: new Date().getFullYear() })}
            </div>
            <div className="flex items-center space-x-6 mt-4 md:mt-0">
              <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center">
                Built with{' '}
                <i className="ri-heart-fill text-red-500 mx-1" />
                {' '}by{' '}
                <ExternalLink 
                  href="https://theinfinitydev.com/en" 
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors font-medium ml-1"
                >
                  infinity dev
                </ExternalLink>
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
