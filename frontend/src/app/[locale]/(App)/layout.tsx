import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';
import { Toaster } from "sonner";
import "../../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "IntelliDoc AI - Smart Document Intelligence Platform",
  description: "Upload your documents and let our AI extract text, analyze content, and convert files into structured data. Simple, fast, and secure document processing with advanced OCR technology.",
  keywords: [
    "document processing",
    "AI document analysis", 
    "OCR technology",
    "text extraction",
    "PDF converter",
    "document intelligence",
    "file conversion",
    "smart document processing",
    "AI-powered OCR",
    "document automation"
  ],
  authors: [{ name: "IntelliDoc AI Team" }],
  creator: "IntelliDoc AI",
  publisher: "IntelliDoc AI",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '',
    siteName: 'IntelliDoc AI',
    title: 'IntelliDoc AI - Smart Document Intelligence Platform',
    description: 'Transform your documents with AI-powered intelligence. Extract text, analyze content, and convert files with enterprise-grade accuracy and security.',
    images: [
      {
        url: '/page.svg',
        width: 1200,
        height: 630,
        alt: 'IntelliDoc AI - Smart Document Processing Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'IntelliDoc AI - Smart Document Intelligence Platform',
    description: 'Transform your documents with AI-powered intelligence. Extract text, analyze content, and convert files securely.',
    images: ['/page.svg'],
    creator: '@intellidoc_ai',
  },
  icons: {
    icon: '/page.svg',
  },
  manifest: '/site.webmanifest',
  category: 'technology',
}

type Props = {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
};

export default async function RootLayout({
  children,
  params
}: Props) {
  const { locale } = await params;
  
  // Ensure that the incoming `locale` is valid
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#2563eb" />
  
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <NextIntlClientProvider messages={messages}>
          <Toaster position="top-right" richColors theme="light" />
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
