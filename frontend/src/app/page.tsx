'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Heart, Brain, TrendingUp, Activity, Cpu, Clock } from 'lucide-react';
import VoiceAssistant from '@/components/VoiceAssistant';
import { useTranslations } from 'next-intl';

const Home = () => {
  const t = useTranslations('Home');
  
  const benefits = [
    {
      icon: TrendingUp,
      title: t('benefits.0.title'),
      description: t('benefits.0.description'),
      mechanism: t('benefits.0.mechanism')
    },
    {
      icon: Brain,
      title: t('benefits.1.title'),
      description: t('benefits.1.description'),
      mechanism: t('benefits.1.mechanism')
    },
    {
      icon: Heart,
      title: t('benefits.2.title'),
      description: t('benefits.2.description'),
      mechanism: t('benefits.2.mechanism')
    },
    {
      icon: Activity,
      title: t('benefits.3.title'),
      description: t('benefits.3.description'),
      mechanism: t('benefits.3.mechanism')
    }
  ];

  const mechanisms = [
    {
      step: t('mechanisms.0.step'),
      title: t('mechanisms.0.title'),
      description: t('mechanisms.0.description'),
      scientific: t('mechanisms.0.scientific')
    },
    {
      step: t('mechanisms.1.step'),
      title: t('mechanisms.1.title'),
      description: t('mechanisms.1.description'),
      scientific: t('mechanisms.1.scientific')
    },
    {
      step: t('mechanisms.2.step'),
      title: t('mechanisms.2.title'),
      description: t('mechanisms.2.description'),
      scientific: t('mechanisms.2.scientific')
    },
    {
      step: t('mechanisms.3.step'),
      title: t('mechanisms.3.title'),
      description: t('mechanisms.3.description'),
      scientific: t('mechanisms.3.scientific')
    }
  ];

  const aiFeatures = [
    {
      title: t('aiFeatures.0.title'),
      description: t('aiFeatures.0.description')
    },
    {
      title: t('aiFeatures.1.title'),
      description: t('aiFeatures.1.description')
    },
    {
      title: t('aiFeatures.2.title'),
      description: t('aiFeatures.2.description')
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-keto-surface via-background to-keto-surface/50">
      {/* Hero Section */}
      <section className="relative py-16 sm:py-20 lg:py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <Badge className="mb-6 bg-keto-primary/10 text-keto-primary border-keto-primary/20 text-sm sm:text-base">
            {t('hero.badge')}
          </Badge>
          
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
            {t('hero.title')}
          </h1>
          
          <p className="text-lg sm:text-xl text-muted-foreground mb-8 max-w-4xl mx-auto leading-relaxed">
            {t('hero.subtitle')}
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Badge variant="outline" className="border-keto-primary text-keto-primary hover:bg-keto-surface transition-colors duration-300 px-4 py-2">
              {t('hero.scientificBadge')}
            </Badge>
          </div>
        </div>
      </section>

      {/* Personalization Section */}
      <section className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4 text-keto-primary">
              AI-Powered Personalization
            </h2>
            <p className="text-base sm:text-lg text-muted-foreground max-w-3xl mx-auto">
              Advanced algorithms tailored to your unique metabolic profile and lifestyle
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {aiFeatures.map((feature, index) => (
              <Card key={index} className="text-center border-keto-primary/20 hover:border-keto-primary/40 transition-all duration-300 group hover:shadow-lg">
                <CardContent className="p-6 sm:p-8">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-keto-primary to-keto-accent rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Cpu className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
                  </div>
                  <h3 className="font-semibold text-lg sm:text-xl mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm sm:text-base leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Mechanisms Section */}
      <section className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
              {t('sections.mechanisms')}
            </h2>
            <p className="text-base sm:text-lg text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              {t('descriptions.mechanisms')}
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {mechanisms.map((mechanism, index) => (
              <Card key={index} className="text-center border-keto-primary/20 hover:border-keto-primary/40 transition-all duration-300 group hover:shadow-lg">
                <CardContent className="p-6 sm:p-8">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-keto-primary to-keto-primary-dark rounded-full flex items-center justify-center text-white font-bold text-lg sm:text-xl mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    {mechanism.step}
                  </div>
                  <h3 className="font-semibold text-lg sm:text-xl mb-3">{mechanism.title}</h3>
                  <p className="text-muted-foreground text-sm sm:text-base mb-4 leading-relaxed">{mechanism.description}</p>
                  <p className="text-xs sm:text-sm text-keto-primary font-medium italic leading-relaxed">{mechanism.scientific}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
              {t('sections.benefits')}
            </h2>
            <p className="text-base sm:text-lg text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              {t('descriptions.benefits')}
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {benefits.map((benefit, index) => (
              <Card key={index} className="text-center group hover:shadow-lg transition-all duration-300 border-keto-primary/20 hover:border-keto-primary/40">
                <CardContent className="p-6 sm:p-8">
                  <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-keto-primary/10 to-keto-accent/10 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <benefit.icon className="w-7 h-7 sm:w-8 sm:h-8 text-keto-primary" />
                  </div>
                  <h3 className="font-semibold text-lg sm:text-xl mb-3">{benefit.title}</h3>
                  <p className="text-muted-foreground text-sm sm:text-base mb-4 leading-relaxed">{benefit.description}</p>
                  <p className="text-xs sm:text-sm text-keto-accent font-medium italic leading-relaxed">{benefit.mechanism}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Research Note */}
      <section className="py-12 sm:py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <Card className="border-keto-primary/20 bg-keto-surface/30 hover:border-keto-primary/40 transition-all duration-300">
            <CardContent className="p-6 sm:p-8 lg:p-10 text-center">
              <div className="flex items-center justify-center mb-4">
                <Clock className="w-6 h-6 sm:w-8 sm:h-8 text-keto-primary mr-3" />
                <h3 className="text-xl sm:text-2xl font-semibold text-keto-primary">{t('sections.research')}</h3>
              </div>
              <p className="text-muted-foreground text-sm sm:text-base lg:text-lg leading-relaxed max-w-4xl mx-auto">
                {t('descriptions.research')}
              </p>
            </CardContent>
          </Card>
        </div>
      </section>


      {/* Floating Voice Assistant */}
      <VoiceAssistant />
    </div>
  );
};

export default Home;