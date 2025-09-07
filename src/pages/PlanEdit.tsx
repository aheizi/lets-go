import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  MapPin, Calendar, Users, DollarSign, Clock, Heart, Sparkles,
  ArrowLeft, Save, X
} from 'lucide-react';
import { usePlanStore } from '../store';
import Layout from '../components/Layout';
import { toast } from 'sonner';

interface FormData {
  destination: string;
  startDate: string;
  endDate: string;
  participants: number;
  budget: string;
  travelStyle: string;
  interests: string[];
  specialRequests: string;
}

const PlanEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentPlan, updatePlan, isLoading, setCurrentPlan } = usePlanStore();
  const [isUpdating, setIsUpdating] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    destination: '',
    startDate: '',
    endDate: '',
    participants: 2,
    budget: '',
    travelStyle: '',
    interests: [],
    specialRequests: ''
  });

  // 兴趣选项
  const interestOptions = [
    { id: 'culture', label: '文化历史', emoji: '🏛️', color: 'from-purple-500 to-pink-500' },
    { id: 'food', label: '美食体验', emoji: '🍜', color: 'from-orange-500 to-red-500' },
    { id: 'nature', label: '自然风光', emoji: '🌿', color: 'from-green-500 to-teal-500' },
    { id: 'adventure', label: '户外探险', emoji: '🏔️', color: 'from-blue-500 to-indigo-500' },
    { id: 'shopping', label: '购物血拼', emoji: '🛍️', color: 'from-pink-500 to-purple-500' },
    { id: 'nightlife', label: '夜生活', emoji: '🌃', color: 'from-indigo-500 to-purple-500' },
    { id: 'art', label: '艺术展览', emoji: '🎨', color: 'from-yellow-500 to-orange-500' },
    { id: 'photography', label: '摄影打卡', emoji: '📸', color: 'from-cyan-500 to-blue-500' }
  ];

  // 旅行风格选项
  const travelStyles = [
    {
      id: 'relaxed',
      label: '悠闲慢游',
      icon: '🌸',
      description: '慢节奏，深度体验'
    },
    {
      id: 'balanced',
      label: '经典游览',
      icon: '⚖️',
      description: '景点与休闲并重'
    },
    {
      id: 'intensive',
      label: '紧凑高效',
      icon: '⚡',
      description: '充实行程，不留遗憾'
    }
  ];

  // 加载计划数据
  useEffect(() => {
    const loadPlan = async () => {
      if (!id) {
        toast.error('计划ID不存在');
        navigate('/profile');
        return;
      }

      try {
        // 如果当前计划不是要编辑的计划，则重新获取
        if (!currentPlan || currentPlan.id !== id) {
          const response = await fetch(`http://localhost:3001/api/plans/${id}`);
          if (!response.ok) {
            throw new Error('获取计划失败');
          }
          const plan = await response.json();
          setCurrentPlan(plan);
        }
      } catch (error) {
        console.error('加载计划失败:', error);
        toast.error('加载计划失败');
        navigate('/profile');
      }
    };

    loadPlan();
  }, [id, currentPlan, setCurrentPlan, navigate]);

  // 当计划数据加载完成后，填充表单
  useEffect(() => {
    if (currentPlan && currentPlan.id === id) {
      setFormData({
        destination: currentPlan.details.destination || '',
        startDate: currentPlan.details.startDate || '',
        endDate: currentPlan.details.endDate || '',
        participants: currentPlan.details.participants || 2,
        budget: currentPlan.details.budget || '',
        travelStyle: currentPlan.details.travelStyle || '',
        interests: currentPlan.details.interests || [],
        specialRequests: currentPlan.details.specialRequests || ''
      });
    }
  }, [currentPlan, id]);

  // 处理兴趣选择
  const handleInterestToggle = (interestId: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interestId)
        ? prev.interests.filter(id => id !== interestId)
        : [...prev.interests, interestId]
    }));
  };

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 表单验证
    if (!formData.destination.trim()) {
      toast.error('请输入目的地');
      return;
    }
    
    if (!formData.startDate || !formData.endDate) {
      toast.error('请选择出发和返回日期');
      return;
    }
    
    if (new Date(formData.startDate) >= new Date(formData.endDate)) {
      toast.error('返回日期必须晚于出发日期');
      return;
    }
    
    if (!formData.budget) {
      toast.error('请选择预算范围');
      return;
    }
    
    if (!formData.travelStyle) {
      toast.error('请选择旅行节奏');
      return;
    }
    
    if (formData.interests.length === 0) {
      toast.error('请至少选择一个兴趣偏好');
      return;
    }
    
    if (!id || !currentPlan) {
      toast.error('计划数据不存在');
      return;
    }

    setIsUpdating(true);
    
    try {
      // 更新计划详情
      const updatedDetails = {
        ...currentPlan.details,
        destination: formData.destination.trim(),
        startDate: formData.startDate,
        endDate: formData.endDate,
        participants: formData.participants,
        budget: formData.budget,
        travelStyle: formData.travelStyle,
        interests: formData.interests,
        specialRequests: formData.specialRequests
      };

      // 使用store的updatePlan方法，它会调用后端API
      await updatePlan(id, { details: updatedDetails });
      
      toast.success('计划更新成功！');
      navigate(`/plan/${id}`);
    } catch (error: any) {
      console.error('更新计划失败:', error);
      
      // 根据错误类型显示不同的错误信息
      let errorMessage = '更新计划失败，请重试';
      
      if (error.message) {
        if (error.message.includes('计划不存在')) {
          errorMessage = '计划不存在，请检查计划ID';
        } else if (error.message.includes('计划正在生成中')) {
          errorMessage = '计划正在生成中，请稍后再试';
        } else if (error.message.includes('网络')) {
          errorMessage = '网络连接失败，请检查网络后重试';
        } else if (error.message.includes('更新失败')) {
          errorMessage = error.message;
        }
      }
      
      toast.error(errorMessage);
    } finally {
      setIsUpdating(false);
    }
  };

  // 取消编辑
  const handleCancel = () => {
    navigate(`/plan/${id}`);
  };

  if (isLoading || !currentPlan) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
          <div className="text-center">
            <Sparkles className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
            <p className="text-lg text-gray-600">加载计划数据中...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={handleCancel}
              className="flex items-center text-gray-600 hover:text-gray-800 mb-4 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              返回计划详情
            </button>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-2">
              编辑计划
            </h1>
            <p className="text-gray-600">
              修改你的旅行计划信息
            </p>
          </div>

          {/* Form */}
          <div className="bg-white rounded-3xl shadow-brand-lg p-6 sm:p-8">
            <form onSubmit={handleSubmit} className="space-y-8">
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
                  placeholder="你想去哪里？"
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

              {/* 特殊需求 */}
              <div className="space-y-3">
                <label className="flex items-center text-lg font-bold text-gray-800">
                  <div className="w-8 h-8 bg-gradient-to-r from-secondary-500 to-primary-500 rounded-lg flex items-center justify-center mr-3">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  特殊需求
                </label>
                <textarea
                  value={formData.specialRequests}
                  onChange={(e) => setFormData(prev => ({ ...prev, specialRequests: e.target.value }))}
                  placeholder="有什么特殊要求或偏好吗？比如无障碍设施、素食餐厅等..."
                  rows={4}
                  className="w-full px-6 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-lg resize-none"
                />
              </div>

              {/* 提交按钮 */}
              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="flex-1 flex items-center justify-center px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-2xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-semibold text-lg"
                >
                  <X className="w-5 h-5 mr-2" />
                  取消
                </button>
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="flex-1 flex items-center justify-center px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl hover:from-primary-600 hover:to-secondary-600 transition-all duration-200 font-semibold text-lg shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isUpdating ? (
                    <>
                      <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                      更新中...
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5 mr-2" />
                      保存修改
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PlanEdit;