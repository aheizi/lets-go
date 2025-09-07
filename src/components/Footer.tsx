import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Users, Smartphone, Mail, Heart } from 'lucide-react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  const quickLinks = [
    { name: '智能规划', href: '/plan/create' },
    { name: '协作功能', href: '/collaborate/demo' },
    { name: '个人中心', href: '/profile' },
    { name: '登录', href: '/login' },
  ];

  const supportLinks = [
    { name: '使用帮助', href: '#' },
    { name: '用户协议', href: '#' },
    { name: '隐私政策', href: '#' },
    { name: '联系我们', href: '#' },
  ];

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-pink-500 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">来</span>
              </div>
              <div>
                <h3 className="text-2xl font-bold bg-gradient-to-r from-orange-400 to-pink-400 bg-clip-text text-transparent">
                  Let'sGo
                </h3>
                <p className="text-gray-400 text-sm">来次够 - AI智能旅行规划</p>
              </div>
            </div>
            <p className="text-gray-300 mb-6 max-w-md">
              让AI为你定制专属旅行计划，与朋友协作规划，让每一次出行都充满惊喜！
            </p>
            <div className="flex space-x-4">
              <div className="flex items-center space-x-2 text-orange-400">
                <MapPin className="w-5 h-5" />
                <span className="text-sm">智能规划</span>
              </div>
              <div className="flex items-center space-x-2 text-blue-400">
                <Users className="w-5 h-5" />
                <span className="text-sm">协作出行</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-orange-400">快速导航</h4>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-gray-300 hover:text-orange-400 transition-colors duration-200 text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-blue-400">帮助支持</h4>
            <ul className="space-y-2">
              {supportLinks.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    className="text-gray-300 hover:text-blue-400 transition-colors duration-200 text-sm"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
            <div className="mt-6">
              <div className="flex items-center space-x-2 text-gray-300 mb-2">
                <Mail className="w-4 h-4" />
                <span className="text-sm">support@letsgo.com</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-300">
                <Smartphone className="w-4 h-4" />
                <span className="text-sm">400-123-4567</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-800 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-1 text-gray-400 text-sm mb-4 md:mb-0">
              <span>© {currentYear} Let'sGo (来次够). Made with</span>
              <Heart className="w-4 h-4 text-red-500" />
              <span>for travelers</span>
            </div>
            <div className="flex space-x-6 text-sm text-gray-400">
              <span>ICP备案号: 京ICP备12345678号</span>
              <span>版本 v1.0.0</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;