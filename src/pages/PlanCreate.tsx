import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { usePlanStore } from '../store';
import { MapPin, Calendar, Users, DollarSign, Heart, Sparkles, Zap, Clock, ArrowRight } from 'lucide-react';

const PlanCreate: React.FC = () => {
  const navigate = useNavigate();
  const { createPlan, generateItinerary, isGenerating } = usePlanStore();
  
  const [formData, setFormData] = useState({
    destination: '',
    startDate: '',
    endDate: '',
    participants: 1,
    budget: '',
    travelStyle: '',
    interests: [] as string[],
    specialRequests: ''
  });



  const interestOptions = [
    { id: 'food', label: '美食探索', emoji: '🍜', color: 'from-red-400 to-pink-500' },
    { id: 'shopping', label: '购物天堂', emoji: '🛍️', color: 'from-purple-400 to-pink-500' },
    { id: 'culture', label: '文化体验', emoji: '🏛️', color: 'from-blue-400 to-indigo-500' },
    { id: 'nature', label: '自然风光', emoji: '🌿', color: 'from-green-400 to-emerald-500' },
    { id: 'adventure', label: '冒险刺激', emoji: '🏔️', color: 'from-orange-400 to-red-500' },
    { id: 'relax', label: '休闲放松', emoji: '🧘', color: 'from-cyan-400 to-blue-500' },
    { id: 'photography', label: '摄影打卡', emoji: '📸', color: 'from-yellow-400 to-orange-500' },
    { id: 'history', label: '历史古迹', emoji: '🏯', color: 'from-gray-400 to-gray-600' },
  ];

  const travelStyles = [
    { id: 'slow', label: '慢节奏', description: '深度体验，不赶时间', icon: '🐌' },
    { id: 'balanced', label: '平衡型', description: '景点与休息并重', icon: '⚖️' },
    { id: 'packed', label: '紧凑型', description: '充实行程，多看多玩', icon: '⚡' },
  ];

  const handleInterestToggle = (interestId: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interestId)
        ? prev.interests.filter(i => i !== interestId)
        : [...prev.interests, interestId]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      console.log('开始创建计划...');
      
      // Create the plan using Zustand store
      const planId = await createPlan({
        destination: formData.destination,
        startDate: formData.startDate,
        endDate: formData.endDate,
        participants: formData.participants,
        budget: formData.budget,
        travelStyle: formData.travelStyle,
        interests: formData.interests
      });
      
      console.log('计划创建成功:', planId);
      
      // Generate AI itinerary
      console.log('开始生成行程...');
      await generateItinerary(planId);
      
      console.log('行程生成请求已发送');
      
      // Navigate to the plan detail page
      navigate(`/plan/${planId}`);
    } catch (error) {
      console.error('创建计划出错:', error);
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-8 sm:py-12">
        <div className="max-w-4xl mx-auto px-4">
          {/* Hero Section */}
          <div className="text-center mb-8 sm:mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-3xl mb-4 sm:mb-6 animate-float">
              <Zap className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold text-gray-900 mb-4">
              智能旅行规划
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto px-4">
              告诉我们你的想法，AI将为你定制完美的旅行计划 ✨
            </p>
          </div>

          {/* Planning Form */}
          <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8 mb-8">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 sm:mb-8 text-center">
              🎯 告诉我们你的旅行想法
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-8">
              {/* 目的地 */}
              <div className="space-y-3">
                <label className="flex items-center text-lg font-bold text-gray-800">
                  <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center mr-3">
                    <MapPin className="w-4 h-4 text-white" />
                  </div>
                  目的地
                </label>
                <input
                  type="text"
                  value={formData.destination}
                  onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
                  placeholder="想去哪里？"
                  className="w-full px-6 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-lg"
                  required
                />
              </div>

              {/* 日期 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <label className="flex items-center text-lg font-bold text-gray-800">
                    <div className="w-8 h-8 bg-gradient-to-r from-secondary-500 to-accent-yellow rounded-lg flex items-center justify-center mr-3">
                      <Calendar className="w-4 h-4 text-white" />
                    </div>
                    出发日期
                  </label>
                  <input
                    type="date"
                    value={formData.startDate}
                    onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
                    className="w-full px-6 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-lg"
                    required
                  />
                </div>
                <div className="space-y-3">
                  <label className="flex items-center text-lg font-bold text-gray-800">
                    <div className="w-8 h-8 bg-gradient-to-r from-secondary-500 to-accent-yellow rounded-lg flex items-center justify-center mr-3">
                      <Calendar className="w-4 h-4 text-white" />
                    </div>
                    返回日期
                  </label>
                  <input
                    type="date"
                    value={formData.endDate}
                    onChange={(e) => setFormData(prev => ({ ...prev, endDate: e.target.value }))}
                    className="w-full px-6 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-lg"
                    required
                  />
                </div>
              </div>

              {/* 人数和预算 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <label className="flex items-center text-lg font-bold text-gray-800">
                    <div className="w-8 h-8 bg-gradient-to-r from-accent-pink to-primary-500 rounded-lg flex items-center justify-center mr-3">
                      <Users className="w-4 h-4 text-white" />
                    </div>
                    参与人数
                  </label>
                  <select
                    value={formData.participants}
                    onChange={(e) => setFormData(prev => ({ ...prev, participants: parseInt(e.target.value) }))}
                    className="w-full px-6 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-lg"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
                      <option key={num} value={num}>{num}人</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center text-lg font-bold text-gray-800">
                    <div className="w-8 h-8 bg-gradient-to-r from-accent-yellow to-secondary-500 rounded-lg flex items-center justify-center mr-3">
                      <DollarSign className="w-4 h-4 text-white" />
                    </div>
                    预算范围
                  </label>
                  <select
                    value={formData.budget}
                    onChange={(e) => setFormData(prev => ({ ...prev, budget: e.target.value }))}
                    className="w-full px-6 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-lg"
                    required
                  >
                    <option value="">选择预算范围</option>
                    <option value="budget">经济型 (&lt; ¥3000/人)</option>
                    <option value="mid-range">舒适型 (¥3000-8000/人)</option>
                    <option value="luxury">豪华型 (&gt; ¥8000/人)</option>
                  </select>
                </div>
              </div>

              {/* 旅行节奏 */}
              <div className="space-y-4">
                <label className="flex items-center text-lg font-bold text-gray-800">
                  <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center mr-3">
                    <Clock className="w-4 h-4 text-white" />
                  </div>
                  旅行节奏
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {travelStyles.map(style => (
                    <button
                      key={style.id}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, travelStyle: style.id }))}
                      className={`p-4 rounded-2xl border-2 transition-all duration-200 text-left ${
                        formData.travelStyle === style.id
                          ? 'bg-primary-50 border-primary-500 shadow-lg'
                          : 'bg-white border-gray-200 hover:border-primary-300 hover:shadow-md'
                      }`}
                    >
                      <div className="text-2xl mb-2">{style.icon}</div>
                      <div className="font-bold text-gray-800 mb-1">{style.label}</div>
                      <div className="text-sm text-gray-600">{style.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 兴趣偏好 */}
              <div className="space-y-4">
                <label className="flex items-center text-lg font-bold text-gray-800">
                  <div className="w-8 h-8 bg-gradient-to-r from-accent-pink to-accent-yellow rounded-lg flex items-center justify-center mr-3">
                    <Heart className="w-4 h-4 text-white" />
                  </div>
                  兴趣偏好 <span className="text-sm text-gray-500 ml-2">(可多选)</span>
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {interestOptions.map(interest => (
                    <button
                      key={interest.id}
                      type="button"
                      onClick={() => handleInterestToggle(interest.id)}
                      className={`p-4 rounded-2xl border-2 transition-all duration-200 text-center group ${
                        formData.interests.includes(interest.id)
                          ? 'bg-gradient-to-r ' + interest.color + ' text-white border-transparent shadow-lg'
                          : 'bg-white text-gray-700 border-gray-200 hover:border-primary-300 hover:shadow-md'
                      }`}
                    >
                      <div className="text-2xl mb-2">{interest.emoji}</div>
                      <div className="font-semibold text-sm">{interest.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Special Requirements */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2 sm:mb-3">
                  💭 特殊需求或想法
                </label>
                <textarea
                  value={formData.specialRequests}
                  onChange={(e) => setFormData(prev => ({ ...prev, specialRequests: e.target.value }))}
                  placeholder="告诉我们你的特殊需求、兴趣爱好或任何想法...\n例如：\n- 想体验当地特色美食\n- 希望住在市中心\n- 对历史文化特别感兴趣\n- 需要无障碍设施"
                  rows={4}
                  className="w-full p-3 sm:p-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent text-base sm:text-lg resize-none"
                />
              </div>

              {/* Submit Button */}
              <div className="flex justify-center pt-4 sm:pt-6">
                <button
                  type="submit"
                  disabled={isGenerating}
                  className="group relative w-full sm:w-auto px-8 sm:px-12 py-3 sm:py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-bold text-lg sm:text-xl rounded-2xl hover:from-primary-600 hover:to-secondary-600 transform hover:scale-105 transition-all duration-300 shadow-brand-lg hover:shadow-brand-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 sm:w-6 sm:h-6 animate-spin rounded-full border-b-2 border-white mr-2 sm:mr-3 inline"></div>
                      AI正在为你规划中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 mr-2 sm:mr-3 inline group-hover:animate-pulse" />
                      开始AI智能规划
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Tips */}
          <div className="mt-8 text-center">
            <p className="text-gray-500">
              💡 提示：信息越详细，AI生成的行程越符合你的期望
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PlanCreate;