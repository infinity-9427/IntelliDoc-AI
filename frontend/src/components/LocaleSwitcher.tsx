"use client";

import { useState, useTransition } from "react";
import { useTranslations } from "next-intl";
import { useRouter, usePathname } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";
import { useParams } from "next/navigation";

export default function LocaleSwitcher() {
  const t = useTranslations("LocaleSwitcher");
  const router = useRouter();
  const pathname = usePathname();
  const params = useParams();
  const [isPending, startTransition] = useTransition();

  // Controls opening/closing the dropdown
  const [isOpen, setIsOpen] = useState(false);

  // When the user picks a locale
  function handleLocaleChange(nextLocale: string) {
    startTransition(() => {
      router.replace(
        // @ts-expect-error -- TypeScript will validate that only known `params`
        // are used in combination with a given `pathname`. Since the two will
        // always match for the current route, we can skip runtime checks.
        { pathname, params },
        { locale: nextLocale }
      );
    });
    setIsOpen(false);
  }

  // Get current locale display
  const currentLocale = params.locale as string;

  // Get current locale code for display (simplified - only the code part)
  const getCurrentLocaleCode = (locale: string) => {
    switch (locale) {
      case 'en': return 'EN';
      case 'es': return 'ES';
      case 'de': return 'DE';
      case 'fr': return 'FR';
      case 'it': return 'IT';
      case 'pr': return 'PT';
      default: return locale.toUpperCase();
    }
  };

  // Extract flag from translation string
  const getCurrentFlag = (locale: string) => {
    const localeString = t("locale", { locale });
    // Extract emoji flag from the beginning of the string (e.g., "🇺🇸 English" -> "🇺🇸")
    const flagMatch = localeString.match(/^([\u{1F1E6}-\u{1F1FF}]{2})/u);
    return flagMatch ? flagMatch[1] : '🌐';
  };

  return (
    <div className="relative inline-block text-left">
      {/* Compact Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        disabled={isPending}
        className="flex items-center space-x-2 px-3 py-2 rounded-md text-white hover:bg-white/20 transition-all duration-200 border border-white/30 backdrop-blur-sm text-sm min-w-[80px] bg-white/10 hover:shadow-md"
        aria-label={t("label")}
      >
        <i className="ri-global-line text-sm" />
        <span className="font-medium flex items-center space-x-1">
          <span className="text-lg">{getCurrentFlag(currentLocale)}</span>
          <span>{getCurrentLocaleCode(currentLocale)}</span>
        </span>
        <i className={`ri-arrow-down-s-line text-sm transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Compact Dropdown */}
          <div className="absolute right-0 mt-1 w-44 bg-white/95 backdrop-blur-md border border-emerald-400/60 rounded-lg shadow-2xl z-20 overflow-hidden ring-1 ring-emerald-500/20">
            <div className="py-1">
              {routing.locales.map((locale) => (
                <button
                  key={locale}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleLocaleChange(locale);
                  }}
                  className={`group block w-full text-left px-4 py-3 text-sm transition-all duration-300 ease-out hover:bg-gradient-to-r hover:from-emerald-500 hover:to-green-600 hover:text-white hover:font-semibold hover:shadow-md hover:ring-1 hover:ring-emerald-400/50 ${
                    locale === currentLocale 
                      ? 'text-emerald-700 font-semibold bg-emerald-50' 
                      : 'text-slate-800'
                  }`}
                  disabled={isPending}
                >
                  <div className="flex items-center justify-between">
                    <span className="transition-all duration-300 ease-out">
                      {t("locale", { locale })}
                    </span>
                    {locale === currentLocale && (
                      <i className="ri-check-line text-lg text-emerald-700 group-hover:text-white drop-shadow-sm transition-colors duration-300" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
