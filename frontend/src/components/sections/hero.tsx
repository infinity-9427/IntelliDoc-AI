'use client'

import React from 'react'
import { useTranslations } from 'next-intl'
import { Card } from '@/components/ui/card'

const Hero: React.FC = () => {
  const t = useTranslations('Hero')
  
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-950 dark:via-slate-900 dark:to-blue-950">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-slate-100 dark:bg-grid-slate-900 bg-[size:20px_20px] opacity-50" />
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-sm font-medium">
            <i className="ri-sparkle-line w-4 h-4 mr-2" />
            {t('badge')}
          </div>

          {/* Headline */}
          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white leading-tight">
              {t('title')}
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {t('titleHighlight')}
              </span>
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
              {t('description')}
            </p>
          </div>

          {/* Value Props */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {t.raw('features').map((feature: any, index: number) => (
              <Card key={index} className="p-6 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-0 shadow-lg">
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    index === 0 ? 'bg-green-100 dark:bg-green-900/30' :
                    index === 1 ? 'bg-blue-100 dark:bg-blue-900/30' :
                    'bg-purple-100 dark:bg-purple-900/30'
                  }`}>
                    <i className={`${
                      index === 0 ? 'ri-file-text-line text-green-600 dark:text-green-400' :
                      index === 1 ? 'ri-file-transfer-line text-blue-600 dark:text-blue-400' :
                      'ri-shield-check-line text-purple-600 dark:text-purple-400'
                    }`} />
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">{feature.title}</h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </Card>
            ))}
          </div>

          {/* CTA */}
          <div className="pt-8">
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {t('cta.text')}
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              {t.raw('cta.badges').map((badge: string, index: number) => (
                <div key={index} className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                  <i className="ri-check-line text-green-500" />
                  <span>{badge}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero
