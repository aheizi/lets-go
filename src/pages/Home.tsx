import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Users, Sparkles, Clock, Heart, Star, ArrowRight, Zap } from 'lucide-react';
import Layout from '../components/Layout';

const Home: React.FC = () => {
  const features = [
    {
      icon: Sparkles,
      title: 'AI智能规划',
      description: '基于你的喜好和预算，AI为你量身定制完美行程',
      color: 'from-primary-500 to-accent-pink',
      bgColor: 'bg-primary-50',
    },
    {
      icon: Users,
      title: '协作出行',
      description: '邀请朋友一起规划，实时协作，让旅行更有趣',
      color: 'from-secondary-500 to-accent-yellow',
      bgColor: 'bg-secondary-50',
    },
    {
      icon: Clock,
      title: '实时优化',
      description: '根据实际情况动态调整行程，让旅行更顺畅',
      color: 'from-accent-yellow to-primary-500',
      bgColor: 'bg-yellow-50',
    },
  ];

  const highlights = [
    {
      emoji: '🎯',
      title: '精准匹配',
      description: '基于个人喜好的智能推荐',
    },
    {
      emoji: '💰',
      title: '预算控制',
      description: '智能分配预算，物超所值',
    },
    {
      emoji: '🤝',
      title: '团队协作',
      description: '多人实时协作规划行程',
    },
    {
      emoji: '📱',
      title: '移动优先',
      description: '随时随地管理你的旅行',
    },
  ];

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center bg-gradient-hero overflow-hidden">
        {/* Background Animation */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-20 h-20 bg-white/10 rounded-full animate-float" />
          <div className="absolute top-40 right-20 w-16 h-16 bg-white/10 rounded-full animate-bounce-slow" />
          <div className="absolute bottom-32 left-1/4 w-12 h-12 bg-white/10 rounded-full animate-pulse-slow" />
          <div className="absolute bottom-20 right-1/3 w-24 h-24 bg-white/10 rounded-full animate-float" />
        </div>

        <div className="relative z-10 text-center px-4 max-w-6xl mx-auto">
          {/* Main Heading */}
          <div className="mb-8">
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-display font-bold text-white mb-4">
              Let's
              <span className="block bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
                Go!
              </span>
            </h1>
            <div className="text-2xl md:text-3xl lg:text-4xl font-bold text-white/90 mb-6">
              来次够 🎉
            </div>
          </div>

          {/* Brand Slogan */}
          <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto leading-relaxed">
            让AI为你定制专属旅行计划 ✨<br />
            与朋友协作规划，让每一次出行都充满惊喜！
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Link
              to="/plan/create"
              className="group bg-white text-primary-600 hover:text-primary-700 font-bold py-4 px-8 rounded-2xl text-lg transition-all duration-300 transform hover:scale-105 shadow-brand-lg hover:shadow-2xl flex items-center space-x-2"
            >
              <Zap className="w-6 h-6" />
              <span>开始智能规划</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/login"
              className="bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 font-bold py-4 px-8 rounded-2xl text-lg transition-all duration-300 border border-white/30 hover:border-white/50"
            >
              立即体验
            </Link>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto">
            {highlights.map((item, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl mb-2">{item.emoji}</div>
                <div className="text-white font-semibold text-sm md:text-base">{item.title}</div>
                <div className="text-white/70 text-xs md:text-sm">{item.description}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-gray-900 mb-6">
              为什么选择 <span className="bg-gradient-brand bg-clip-text text-transparent">Let'sGo</span>？
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              我们用AI技术重新定义旅行规划，让每一次出行都成为难忘的回忆
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className={`${feature.bgColor} rounded-3xl p-8 hover:shadow-brand-lg transition-all duration-300 transform hover:-translate-y-2 group`}
                >
                  <div className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-gray-900 mb-6">
              三步开启完美旅程
            </h2>
            <p className="text-xl text-gray-600">
              简单几步，AI帮你搞定一切
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-primary-500 to-accent-pink rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">告诉我们你的想法</h3>
              <p className="text-gray-600">输入目的地、时间、预算和兴趣偏好</p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-secondary-500 to-accent-yellow rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">AI智能生成方案</h3>
              <p className="text-gray-600">基于大数据和AI算法，为你定制专属行程</p>
            </div>

            <div className="text-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-accent-yellow to-primary-500 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">邀请朋友协作</h3>
              <p className="text-gray-600">分享给朋友，一起完善行程，开启美好旅程</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-yellow">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-display font-bold text-white mb-6">
            准备好开始你的旅程了吗？
          </h2>
          <p className="text-xl text-white/90 mb-8">
            加入数万用户，体验AI驱动的智能旅行规划
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/plan/create"
              className="bg-white text-primary-600 hover:text-primary-700 font-bold py-4 px-8 rounded-2xl text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center space-x-2"
            >
              <Star className="w-6 h-6" />
              <span>免费开始规划</span>
            </Link>
            <Link
              to="/collaborate/sample-plan"
              className="bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 font-bold py-4 px-8 rounded-2xl text-lg transition-all duration-300 border border-white/30 hover:border-white/50 flex items-center justify-center space-x-2"
            >
              <Users className="w-6 h-6" />
              <span>体验协作功能</span>
            </Link>
            <Link
              to="/login"
              className="bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 font-bold py-4 px-8 rounded-2xl text-lg transition-all duration-300 border border-white/30 hover:border-white/50 flex items-center justify-center space-x-2"
            >
              <Heart className="w-6 h-6" />
              <span>了解更多</span>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Home;