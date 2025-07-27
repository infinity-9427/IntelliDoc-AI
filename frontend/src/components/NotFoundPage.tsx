'use client'
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import Link from './NavigationLink';
import PageLayout from './PageLayout';

export default function NotFoundPage() {
  const t = useTranslations('NotFoundPage');
  const menuT = useTranslations('Menu');

  return (
    <PageLayout title={t('title')}>
      <div className="w-full h-[calc(100vh-200px)] flex flex-col items-center justify-center px-4 py-4 relative">
        {/* Animated 404 Title */}
        <div className="text-center mb-4 sm:mb-6">
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-red-600 bg-clip-text animate-pulse mb-2 sm:mb-4">
            404
          </h1>
          <h2 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-semibold text-gray-800 dark:text-gray-200 mb-2 animate-fade-in-up">
            {t('title')}
          </h2>
        </div>

        {/* Animated Image */}
        <div className="relative mb-4 sm:mb-6 animate-float">
          <div className="relative w-48 h-48 sm:w-56 sm:h-56 md:w-64 md:h-64 lg:w-72 lg:h-72">
            <Image
              src="/404.webp"
              alt="Page not found"
              fill
              className="object-contain filter drop-shadow-lg"
              priority
            />
          </div>
          {/* Floating particles animation */}
          <div className="absolute -inset-4 opacity-30">
            <div className="absolute top-0 left-0 w-2 h-2 bg-blue-400 rounded-full animate-ping" style={{ animationDelay: '0s' }}></div>
            <div className="absolute top-8 right-4 w-1 h-1 bg-purple-400 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
            <div className="absolute bottom-12 left-8 w-1.5 h-1.5 bg-red-400 rounded-full animate-ping" style={{ animationDelay: '2s' }}></div>
            <div className="absolute bottom-4 right-0 w-1 h-1 bg-green-400 rounded-full animate-ping" style={{ animationDelay: '0.5s' }}></div>
          </div>
        </div>

        {/* Description */}
        <p className="text-center text-gray-600 dark:text-gray-400 text-sm sm:text-base md:text-lg lg:text-xl max-w-xl mx-auto mb-6 sm:mb-8 animate-fade-in-up leading-relaxed px-4">
          {t('description')}
        </p>

        {/* Action Buttons */}
        <div className="flex justify-center animate-fade-in-up">
          <Link
            href="/"
            className="px-4 py-2 sm:px-6 sm:py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 hover:shadow-lg text-center text-sm sm:text-base"
          >
            {menuT('home')}
          </Link>
        </div>

        {/* Decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
          <div className="absolute -top-20 -right-20 w-40 h-40 sm:w-60 sm:h-60 bg-gradient-to-br from-blue-400/10 to-purple-400/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-20 -left-20 w-40 h-40 sm:w-60 sm:h-60 bg-gradient-to-br from-purple-400/10 to-red-400/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-20px);
          }
        }
        
        .animate-fade-in-up {
          animation: fade-in-up 0.8s ease-out forwards;
        }
        
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
      `}</style>
    </PageLayout>
  );
}
