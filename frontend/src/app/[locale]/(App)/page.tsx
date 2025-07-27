import Header from '@/components/layout/header'
import Footer from '@/components/layout/footer'
import Hero from '@/components/sections/hero'
import FileUploader from '@/components/file-uploader'

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        <Hero />
        
        <section className="py-20 bg-white dark:bg-gray-900">
          <FileUploader />
        </section>
      </main>

      <Footer />
    </div>
  );
}
