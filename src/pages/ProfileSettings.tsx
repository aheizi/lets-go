import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import Avatar from '../components/Avatar';
import { useUserStore } from '../store';
import { ArrowLeft, Settings, User, Bell, Shield, Save, Camera, Upload } from 'lucide-react';

const ProfileSettings: React.FC = () => {
  const { user, updateUser, updatePreferences, updateNotifications, updatePrivacy } = useUserStore();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    avatar: '',
    language: 'zh-CN',
    currency: 'CNY',
    planReminder: true,
    friendInvite: true,
    weatherAlert: false,
    promotions: true,
    budgetMin: 1000,
    budgetMax: 5000,
    transportation: '飞机',
    interests: [] as string[],
    publicProfile: true,
    shareItinerary: false
  });
  
  // Initialize form data from user store
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name,
        email: user.email,
        phone: user.phone || '',
        avatar: user.avatar || '',
        language: user.preferences.language,
        currency: user.preferences.currency,
        planReminder: user.notifications.planReminder,
        friendInvite: user.notifications.friendInvite,
        weatherAlert: user.notifications.weatherAlert,
        promotions: user.notifications.promotions,
        budgetMin: user.preferences.budgetMin,
        budgetMax: user.preferences.budgetMax,
        transportation: user.preferences.transportation,
        interests: user.preferences.interests,
        publicProfile: user.privacy.publicProfile,
        shareItinerary: user.privacy.shareItinerary
      });
    }
  }, [user]);



  const interestOptions = ['美食', '购物', '文化', '户外', '运动', '摄影', '娱乐', '休闲'];
  const transportationOptions = ['地铁', '公交', '自驾', '步行', '骑行', '打车'];

  const handleInterestToggle = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleSave = () => {
    if (!user) return;
    
    // Update basic user information
    updateUser({
      name: formData.name,
      email: formData.email,
      phone: formData.phone,
      avatar: formData.avatar
    });
    
    // Update preferences
    updatePreferences({
      language: formData.language,
      currency: formData.currency,
      budgetMin: formData.budgetMin,
      budgetMax: formData.budgetMax,
      transportation: formData.transportation,
      interests: formData.interests
    });
    
    // Update notifications
    updateNotifications({
      planReminder: formData.planReminder,
      friendInvite: formData.friendInvite,
      weatherAlert: formData.weatherAlert,
      promotions: formData.promotions
    });
    
    // Update privacy settings
    updatePrivacy({
      publicProfile: formData.publicProfile,
      shareItinerary: formData.shareItinerary
    });
    
    alert('设置已保存！');
  };

  return (
    <Layout>
      {/* Hero Section */}
      <div className="bg-gradient-brand-cool py-6 sm:py-8 lg:py-16">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <div className="flex justify-center mb-4 sm:mb-6">
            <Settings className="w-12 h-12 sm:w-16 sm:h-16 text-white animate-float" />
          </div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2 sm:mb-4">
            个人设置
          </h1>
          <p className="text-base sm:text-lg lg:text-xl text-white/90 max-w-2xl mx-auto">
            自定义你的旅行偏好，管理通知和隐私设置
          </p>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-8 -mt-8">
        {/* Header Navigation */}
        <div className="flex items-center space-x-4 mb-8">
          <Link 
            to="/profile"
            className="flex items-center space-x-3 bg-white text-gray-700 hover:text-primary-600 px-6 py-3 rounded-2xl shadow-lg transition-all duration-300 transform hover:scale-105 font-bold"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>返回个人资料</span>
          </Link>
        </div>

        {/* Basic Information */}
        <div className="bg-white rounded-3xl shadow-brand-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-3">
            <User className="w-7 h-7 text-primary-500" />
            <span>基本信息</span>
          </h2>
          
          <div className="space-y-6">
            {/* Avatar Section */}
            <div>
              <label className="block text-lg font-semibold text-gray-700 mb-3">头像</label>
              <div className="flex items-center space-x-6">
                <Avatar src={formData.avatar} name={formData.name || '用户'} size="lg" />
                <div className="flex-1">
                  <div className="grid grid-cols-2 gap-4">
                    {/* Avatar Options */}
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-gray-600 mb-2">选择头像</label>
                      
                      {/* Emoji Avatars */}
                      <div className="mb-4">
                        <h4 className="text-xs font-medium text-gray-500 mb-2">表情头像</h4>
                        <div className="grid grid-cols-6 gap-2 p-3 border-2 border-gray-200 rounded-xl">
                          {[
                            '👨‍💼', '👩‍💼', '🧑‍🎓', '👨‍🎓', '👩‍🎓', '🧑‍💻', 
                            '👨‍💻', '👩‍💻', '👨‍🎨', '👩‍🎨', '🧑‍🍳', '👨‍🍳',
                            '👩‍🍳', '🧑‍⚕️', '👨‍⚕️', '👩‍⚕️', '🧑‍🏫', '👨‍🏫',
                            '👩‍🏫', '🧑‍🎤', '👨‍🎤', '👩‍🎤', '🧑‍✈️', '👨‍✈️'
                          ].map((emoji) => (
                            <button
                              key={emoji}
                              type="button"
                              onClick={() => setFormData({...formData, avatar: emoji})}
                              className={`p-2 text-xl rounded-lg hover:bg-gray-100 transition-colors ${
                                formData.avatar === emoji ? 'bg-primary-100 ring-2 ring-primary-500' : ''
                              }`}
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      </div>
                      
                      {/* Preset Images */}
                      <div>
                        <h4 className="text-xs font-medium text-gray-500 mb-2">预设头像</h4>
                        <div className="grid grid-cols-4 gap-2 p-3 border-2 border-gray-200 rounded-xl">
                          {[
                            `https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent('professional business person avatar portrait')}&image_size=square`,
                            `https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent('friendly traveler avatar portrait')}&image_size=square`,
                            `https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent('creative artist avatar portrait')}&image_size=square`,
                            `https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent('tech professional avatar portrait')}&image_size=square`
                          ].map((imageUrl, index) => (
                            <button
                              key={index}
                              type="button"
                              onClick={() => setFormData({...formData, avatar: imageUrl})}
                              className={`relative w-12 h-12 rounded-lg overflow-hidden hover:ring-2 hover:ring-primary-300 transition-all ${
                                formData.avatar === imageUrl ? 'ring-2 ring-primary-500' : ''
                              }`}
                            >
                              <img
                                src={imageUrl}
                                alt={`预设头像 ${index + 1}`}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement;
                                  target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiByeD0iMjQiIGZpbGw9IiNGM0Y0RjYiLz4KPHN2ZyB4PSIxMiIgeT0iMTIiIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMTIgMTJDMTQuNzYxNCAxMiAxNyA5Ljc2MTQyIDE3IDdDMTcgNC4yMzg1OCAxNC43NjE0IDIgMTIgMkM5LjIzODU4IDIgNyA0LjIzODU4IDcgN0M3IDkuNzYxNDIgOS4yMzg1OCAxMiAxMiAxMloiIGZpbGw9IiM5Q0EzQUYiLz4KPHBhdGggZD0iTTEyIDE0QzguNjg2MjkgMTQgNiAxNi42ODYzIDYgMjBIMThDMTggMTYuNjg2MyAxNS4zMTM3IDE0IDEyIDE0WiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4KPC9zdmc+';
                                }}
                              />
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                    
                    {/* File Upload */}
                    <div>
                      <label className="block text-sm font-medium text-gray-600 mb-2">上传图片</label>
                      <div className="border-2 border-dashed border-gray-300 rounded-xl p-4 text-center hover:border-primary-400 transition-colors">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              const reader = new FileReader();
                              reader.onload = (event) => {
                                const result = event.target?.result as string;
                                setFormData({...formData, avatar: result});
                              };
                              reader.readAsDataURL(file);
                            }
                          }}
                          className="hidden"
                          id="avatar-upload"
                        />
                        <label htmlFor="avatar-upload" className="cursor-pointer">
                          <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                          <p className="text-sm text-gray-600">点击上传</p>
                        </label>
                      </div>
                    </div>
                  </div>
                  
                  {/* Clear Avatar Button */}
                  {formData.avatar && (
                    <button
                      type="button"
                      onClick={() => setFormData({...formData, avatar: ''})}
                      className="mt-3 text-sm text-red-600 hover:text-red-800 transition-colors"
                    >
                      清除头像
                    </button>
                  )}
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-lg font-semibold text-gray-700 mb-3">昵称</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full p-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg transition-all duration-300"
              />
            </div>
            
            <div>
              <label className="block text-lg font-semibold text-gray-700 mb-3">手机号</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                className="w-full p-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg transition-all duration-300"
              />
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8 mb-6 lg:mb-8">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6 flex items-center space-x-2 sm:space-x-3">
            <Bell className="w-5 h-5 sm:w-6 sm:h-6 lg:w-7 lg:h-7 text-secondary-500" />
            <span>通知设置</span>
          </h2>
          
          <div className="space-y-4 sm:space-y-6">
            <div className="flex items-center justify-between p-3 sm:p-4 bg-gray-50 rounded-2xl">
              <div className="flex-1 min-w-0 mr-3 sm:mr-4">
                <div className="text-base sm:text-lg font-semibold text-gray-700">行程提醒</div>
                <div className="text-xs sm:text-sm text-gray-600">出行前发送提醒通知</div>
              </div>
              <button
                onClick={() => setFormData({...formData, planReminder: !formData.planReminder})}
                className={`w-12 h-6 sm:w-14 sm:h-7 rounded-full transition-colors duration-200 flex-shrink-0 ${
                  formData.planReminder ? 'bg-gradient-to-r from-primary-500 to-secondary-500' : 'bg-gray-300'
                }`}
              >
                <div className={`w-5 h-5 sm:w-6 sm:h-6 bg-white rounded-full transition-transform duration-200 ${
                  formData.planReminder ? 'translate-x-6 sm:translate-x-7' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between p-3 sm:p-4 bg-gray-50 rounded-2xl">
              <div className="flex-1 min-w-0 mr-3 sm:mr-4">
                <div className="text-base sm:text-lg font-semibold text-gray-700">好友邀请</div>
                <div className="text-xs sm:text-sm text-gray-600">收到好友邀请时通知</div>
              </div>
              <button
                onClick={() => setFormData({...formData, friendInvite: !formData.friendInvite})}
                className={`w-12 h-6 sm:w-14 sm:h-7 rounded-full transition-colors duration-200 flex-shrink-0 ${
                  formData.friendInvite ? 'bg-gradient-to-r from-primary-500 to-secondary-500' : 'bg-gray-300'
                }`}
              >
                <div className={`w-5 h-5 sm:w-6 sm:h-6 bg-white rounded-full transition-transform duration-200 ${
                  formData.friendInvite ? 'translate-x-6 sm:translate-x-7' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between p-3 sm:p-4 bg-gray-50 rounded-2xl">
              <div className="flex-1 min-w-0 mr-3 sm:mr-4">
                <div className="text-base sm:text-lg font-semibold text-gray-700">天气提醒</div>
                <div className="text-xs sm:text-sm text-gray-600">出行当天天气预报</div>
              </div>
              <button
                onClick={() => setFormData({...formData, weatherAlert: !formData.weatherAlert})}
                className={`w-12 h-6 sm:w-14 sm:h-7 rounded-full transition-colors duration-200 flex-shrink-0 ${
                  formData.weatherAlert ? 'bg-gradient-to-r from-primary-500 to-secondary-500' : 'bg-gray-300'
                }`}
              >
                <div className={`w-5 h-5 sm:w-6 sm:h-6 bg-white rounded-full transition-transform duration-200 ${
                  formData.weatherAlert ? 'translate-x-6 sm:translate-x-7' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between p-3 sm:p-4 bg-gray-50 rounded-2xl">
              <div className="flex-1 min-w-0 mr-3 sm:mr-4">
                <div className="text-base sm:text-lg font-semibold text-gray-700">优惠推广</div>
                <div className="text-xs sm:text-sm text-gray-600">接收优惠活动信息</div>
              </div>
              <button
                onClick={() => setFormData({...formData, promotions: !formData.promotions})}
                className={`w-12 h-6 sm:w-14 sm:h-7 rounded-full transition-colors duration-200 flex-shrink-0 ${
                  formData.promotions ? 'bg-gradient-to-r from-primary-500 to-secondary-500' : 'bg-gray-300'
                }`}
              >
                <div className={`w-5 h-5 sm:w-6 sm:h-6 bg-white rounded-full transition-transform duration-200 ${
                  formData.promotions ? 'translate-x-6 sm:translate-x-7' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
          </div>
        </div>

        {/* Travel Preferences */}
        <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8 mb-6 lg:mb-8">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6 flex items-center space-x-2 sm:space-x-3">
            <Settings className="w-5 h-5 sm:w-6 sm:h-6 lg:w-7 lg:h-7 text-accent-500" />
            <span>旅行偏好</span>
          </h2>
          
          <div className="space-y-4 sm:space-y-6">
            <div>
              <label className="block text-base sm:text-lg font-semibold text-gray-700 mb-2 sm:mb-3">偏好语言</label>
              <select
                value={formData.language}
                onChange={(e) => setFormData({...formData, language: e.target.value})}
                className="w-full p-3 sm:p-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent text-base sm:text-lg transition-all duration-300 bg-white"
              >
                <option value="zh">中文</option>
                <option value="en">English</option>
                <option value="ja">日本語</option>
                <option value="ko">한국어</option>
              </select>
            </div>
            <div>
              <label className="block text-base sm:text-lg font-semibold text-gray-700 mb-2 sm:mb-3">货币单位</label>
              <select
                value={formData.currency}
                onChange={(e) => setFormData({...formData, currency: e.target.value})}
                className="w-full p-3 sm:p-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent text-base sm:text-lg transition-all duration-300 bg-white"
              >
                <option value="CNY">人民币 (¥)</option>
                <option value="USD">美元 ($)</option>
                <option value="EUR">欧元 (€)</option>
                <option value="JPY">日元 (¥)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-base sm:text-lg font-semibold text-gray-700 mb-2 sm:mb-3">
                最低预算 (¥{formData.budgetMin})
              </label>
              <input
                type="range"
                min="500"
                max="10000"
                step="500"
                value={formData.budgetMin}
                onChange={(e) => setFormData({ ...formData, budgetMin: parseInt(e.target.value) })}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
          </div>
        </div>

        {/* Travel Preferences */}
        <div className="bg-white rounded-3xl shadow-brand-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-3">
            <User className="w-7 h-7 text-green-500" />
            <span>出行偏好</span>
          </h2>
          
          <div className="space-y-6">
            {/* 兴趣标签 */}
            <div>
              <label className="block text-lg font-semibold text-gray-700 mb-3">兴趣偏好</label>
              <div className="flex flex-wrap gap-3">
                {interestOptions.map(interest => (
                  <button
                    key={interest}
                    onClick={() => handleInterestToggle(interest)}
                    className={`px-6 py-3 rounded-2xl text-lg font-medium transition-all duration-300 transform hover:scale-105 ${
                      formData.interests.includes(interest)
                        ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {interest}
                  </button>
                ))}
              </div>
            </div>
            
            {/* 预算范围 */}
            <div>
              <label className="flex items-center space-x-3 text-lg font-semibold text-gray-700 mb-3">
                <Settings className="w-6 h-6" />
                <span>预算范围: ¥{formData.budgetMin} - ¥{formData.budgetMax}</span>
              </label>
              <div className="space-y-6">
                <div>
                  <label className="text-base text-gray-600 mb-2 block">最低预算: ¥{formData.budgetMin}</label>
                  <input
                    type="range"
                    min="50"
                    max="1000"
                    step="50"
                    value={formData.budgetMin}
                    onChange={(e) => setFormData({...formData, budgetMin: parseInt(e.target.value)})}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
                <div>
                  <label className="text-base text-gray-600 mb-2 block">最高预算: ¥{formData.budgetMax}</label>
                  <input
                    type="range"
                    min="100"
                    max="2000"
                    step="50"
                    value={formData.budgetMax}
                    onChange={(e) => setFormData({...formData, budgetMax: parseInt(e.target.value)})}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
              </div>
            </div>
            
            {/* 交通偏好 */}
            <div>
              <label className="flex items-center space-x-3 text-lg font-semibold text-gray-700 mb-3">
                <ArrowLeft className="w-6 h-6" />
                <span>偏好交通方式</span>
              </label>
              <div className="flex flex-wrap gap-3">
                {transportationOptions.map(transport => (
                  <button
                    key={transport}
                    onClick={() => setFormData({...formData, transportation: transport})}
                    className={`px-6 py-3 rounded-2xl text-lg font-medium transition-all duration-300 transform hover:scale-105 ${
                      formData.transportation === transport
                        ? 'bg-gradient-to-r from-accent-500 to-primary-500 text-white shadow-lg'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {transport}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Privacy & Security */}
        <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8 mb-6 lg:mb-8">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6 flex items-center space-x-2 sm:space-x-3">
            <Shield className="w-5 h-5 sm:w-6 sm:h-6 lg:w-7 lg:h-7 text-pink-500" />
            <span>隐私与安全</span>
          </h2>
          
          <div className="space-y-4 sm:space-y-6">
            <div className="flex items-center justify-between p-3 sm:p-4 bg-gray-50 rounded-2xl">
              <div className="flex-1 min-w-0 mr-3 sm:mr-4">
                <div className="text-base sm:text-lg font-semibold text-gray-700">公开个人资料</div>
                <div className="text-xs sm:text-sm text-gray-600">允许其他用户查看你的基本信息</div>
              </div>
              <button
                onClick={() => setFormData({...formData, publicProfile: !formData.publicProfile})}
                className={`w-12 h-6 sm:w-14 sm:h-7 rounded-full transition-colors duration-200 flex-shrink-0 ${
                  formData.publicProfile ? 'bg-gradient-to-r from-primary-500 to-secondary-500' : 'bg-gray-300'
                }`}
              >
                <div className={`w-5 h-5 sm:w-6 sm:h-6 bg-white rounded-full transition-transform duration-200 ${
                  formData.publicProfile ? 'translate-x-6 sm:translate-x-7' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            <div className="flex items-center justify-between p-3 sm:p-4 bg-gray-50 rounded-2xl">
              <div className="flex-1 min-w-0 mr-3 sm:mr-4">
                <div className="text-base sm:text-lg font-semibold text-gray-700">允许好友查看行程</div>
                <div className="text-xs sm:text-sm text-gray-600">允许好友查看你的旅行计划</div>
              </div>
              <button
                onClick={() => setFormData({...formData, shareItinerary: !formData.shareItinerary})}
                className={`w-12 h-6 sm:w-14 sm:h-7 rounded-full transition-colors duration-200 flex-shrink-0 ${
                  formData.shareItinerary ? 'bg-gradient-to-r from-primary-500 to-secondary-500' : 'bg-gray-300'
                }`}
              >
                <div className={`w-5 h-5 sm:w-6 sm:h-6 bg-white rounded-full transition-transform duration-200 ${
                  formData.shareItinerary ? 'translate-x-6 sm:translate-x-7' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
          </div>
        </div>

        {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-bold text-base sm:text-lg hover:shadow-brand-lg transition-all duration-300 transform hover:scale-105 w-full sm:w-auto"
            >
              保存设置
            </button>
          </div>
      </div>
    </Layout>
  );
};

export default ProfileSettings;