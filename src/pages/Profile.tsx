import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import Avatar from '../components/Avatar';
import { useUserStore, usePlanStore } from '../store';
import { User, Settings, MapPin, Calendar, Plane, Trophy, Star, Heart, Users } from 'lucide-react';

const Profile: React.FC = () => {
  const { user, setUser } = useUserStore();
  const { plans } = usePlanStore();
  
  // Mock user data initialization
  useEffect(() => {
    if (!user) {
      setUser({
        id: 'user_1',
        name: '张小明',
        email: 'zhangxiaoming@example.com',
        avatar: 'https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=friendly%20asian%20person%20avatar%20profile%20picture%20smiling&image_size=square',
        phone: '+86 138 0013 8000',
        preferences: {
          language: 'zh-CN',
          currency: 'CNY',
          interests: ['美食探索', '文化体验', '自然风光'],
          budgetMin: 1000,
          budgetMax: 5000,
          transportation: '飞机'
        },
        notifications: {
          planReminder: true,
          friendInvite: true,
          weatherAlert: false,
          promotions: true
        },
        privacy: {
          publicProfile: true,
          shareItinerary: false
        }
      });
    }
  }, [user, setUser]);
  
  // Calculate statistics from plans
  const totalPlans = plans.length;
  const completedPlans = plans.filter(plan => plan.status === 'completed').length;
  const favoriteDestinations = ['东京', '巴黎', '纽约'];
  // Recent plans from store
  const recentPlans = plans.slice(0, 3).map(plan => ({
    id: plan.id,
    title: plan.title,
    destination: plan.details.destination,
    date: plan.details.startDate,
    status: plan.status,
    image: `https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(plan.details.destination + ' travel destination beautiful scenery')}&image_size=landscape_4_3`
  }));
  
  if (!user) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <p className="text-gray-600">加载用户信息中...</p>
          </div>
        </div>
      </Layout>
    );
  }

  // User data from store
  const userData = {
    name: user.name,
    avatar: user.avatar,
    phone: user.phone,
    joinDate: user.joinDate || '2024-01-15', // Use real join date or fallback
    totalPlans: totalPlans,
    completedPlans: completedPlans,
    favoriteDestinations: favoriteDestinations
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed':
        return '已确认';
      case 'pending':
        return '待确认';
      case 'completed':
        return '已完成';
      default:
        return '未知';
    }
  };

  return (
    <Layout>
      {/* Hero Section */}
      <div className="bg-gradient-brand-warm py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="flex justify-center mb-6">
            <User className="w-16 h-16 text-white animate-float" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            我的档案
          </h1>
          <p className="text-xl text-white/90 max-w-2xl mx-auto">
            管理你的旅行偏好，查看历史记录，发现更多精彩
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 -mt-8">
        {/* User Information Card */}
        <div className="bg-white rounded-3xl shadow-brand-lg p-8 mb-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-gray-900">个人信息</h2>
            <Link 
              to="/profile/settings"
              className="flex items-center space-x-3 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-6 py-3 rounded-2xl transition-all duration-300 transform hover:scale-105 shadow-lg font-bold"
            >
              <Settings className="w-5 h-5" />
              <span>设置</span>
            </Link>
          </div>
          
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
            <Avatar src={user.avatar} name={user.name} size="xl" />
            <div className="flex-1 text-center md:text-left">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{user.name}</h3>
              {user.email && <p className="text-lg text-gray-600 mb-2">{user.email}</p>}
              {user.phone && <p className="text-lg text-gray-600 mb-2">{user.phone}</p>}
              <div className="flex items-center justify-center md:justify-start space-x-2 text-gray-500">
                <Calendar className="w-4 h-4" />
                <span className="text-sm">加入时间：{userData.joinDate}</span>
              </div>
            </div>
          </div>
          
        </div>

        {/* Statistics Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-3xl shadow-brand-lg p-8 text-center transform hover:scale-105 transition-all duration-300">
            <div className="flex justify-center mb-4">
              <Plane className="w-12 h-12 text-accent-orange" />
            </div>
            <div className="text-4xl font-bold text-accent-orange mb-2">{totalPlans}</div>
            <div className="text-lg font-semibold text-gray-600">总计划数</div>
          </div>
          <div className="bg-white rounded-3xl shadow-brand-lg p-8 text-center transform hover:scale-105 transition-all duration-300">
            <div className="flex justify-center mb-4">
              <Trophy className="w-12 h-12 text-primary-500" />
            </div>
            <div className="text-4xl font-bold text-primary-500 mb-2">{completedPlans}</div>
            <div className="text-lg font-semibold text-gray-600">已完成</div>
          </div>
          <div className="bg-white rounded-3xl shadow-brand-lg p-8 text-center transform hover:scale-105 transition-all duration-300">
            <div className="flex justify-center mb-4">
              <Star className="w-12 h-12 text-accent-yellow" />
            </div>
            <div className="text-4xl font-bold text-accent-yellow mb-2">{favoriteDestinations.length}</div>
            <div className="text-lg font-semibold text-gray-600">收藏目的地</div>
          </div>
        </div>

        {/* Recent Travel Plans */}
        <div className="bg-white rounded-3xl shadow-brand-lg p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">最近的旅行计划</h2>
          <div className="space-y-6">
            {recentPlans.map((plan) => (
              <div key={plan.id} className="border-2 border-gray-100 rounded-2xl p-6 hover:shadow-lg hover:border-primary-200 transition-all duration-300 transform hover:scale-[1.02]">
                <div className="flex flex-col md:flex-row md:items-center justify-between space-y-4 md:space-y-0">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 mb-3">{plan.title}</h3>
                    <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-6 text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-5 h-5 text-secondary-500" />
                        <span className="font-medium">{plan.date}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Users className="w-5 h-5 text-primary-500" />
                        <span className="font-medium">{plan.participants}人</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
                    <span className={`px-4 py-2 rounded-2xl text-sm font-bold ${
                      plan.status === 'completed' ? 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-800' :
                      plan.status === 'confirmed' ? 'bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800' :
                      'bg-gradient-to-r from-yellow-100 to-orange-100 text-yellow-800'
                    }`}>
                      {getStatusText(plan.status)}
                    </span>
                    <Link
                      to={`/plan/${plan.id}`}
                      className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-6 py-2 rounded-2xl font-bold transition-all duration-300 transform hover:scale-105 shadow-lg"
                    >
                      查看详情
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Favorite Destinations */}
        <div className="bg-white rounded-3xl shadow-brand-lg p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">收藏的目的地</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {userData.favoriteDestinations.map((destination, index) => (
              <div key={index} className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-accent-orange/10 to-accent-pink/10 p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-105 border-2 border-transparent hover:border-primary-200">
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                    <MapPin className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{destination}</h3>
                    <p className="text-gray-600 font-medium">中国</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Heart className="w-5 h-5 text-red-500 fill-current" />
                    <span className="text-sm font-semibold text-gray-600">已收藏</span>
                  </div>
                  <button className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-4 py-2 rounded-xl font-bold text-sm transition-all duration-300 transform hover:scale-105 shadow-lg">
                    查看详情
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Profile;