import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Users, Check, X, Clock, MessageSquare, Share2, MapPin, Calendar, DollarSign, AlertCircle, Home, Send, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import Layout from '../components/Layout';
import { usePlanStore } from '../store/usePlanStore';
import { useUserStore } from '../store/useUserStore';

const Collaborate: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [feedback, setFeedback] = useState('');
  const [userStatus, setUserStatus] = useState<'pending' | 'confirmed' | 'declined'>('pending');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  
  const { plans, currentPlan, setCurrentPlan, updateParticipantStatus, fetchPlanById } = usePlanStore();
  const { user } = useUserStore();
  
  // 默认用户信息，如果useUserStore没有用户数据
  const currentUser = user || { id: 'current_user', name: '我' };

  useEffect(() => {
    const loadPlan = async () => {
      if (!id) {
        setError('无效的计划ID');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        // 首先在本地plans中查找
        let plan = plans.find(p => p.id === id);
        
        // 如果本地没有找到，尝试从后端获取
        if (!plan) {
          console.log('本地未找到计划，尝试从后端获取:', id);
          plan = await fetchPlanById(id);
        }
        
        if (plan) {
          setCurrentPlan(plan);
          // Find current user's status in participants
          const currentUserParticipant = plan.participants?.find(p => p.userId === currentUser.id);
          if (currentUserParticipant) {
            setUserStatus(currentUserParticipant.status as 'pending' | 'confirmed' | 'declined');
            setFeedback(currentUserParticipant.feedback || '');
          }
        } else {
          setError('计划不存在');
        }
      } catch (error) {
        console.error('加载计划失败:', error);
        if (error instanceof Error && error.message.includes('404')) {
          setError('计划不存在');
        } else {
          setError('网络错误，请检查网络连接后重试');
        }
      } finally {
        setLoading(false);
      }
    };

    loadPlan();
  }, [id, plans, setCurrentPlan, currentUser.id, fetchPlanById]);

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <p className="text-gray-600">加载协作信息中...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !currentPlan) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50">
          <div className="text-center max-w-md mx-auto px-4">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-red-500 to-orange-500 rounded-3xl mb-6">
              <AlertCircle className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">无法访问协作计划</h2>
            <p className="text-gray-600 mb-6">
              {error === '计划不存在' 
                ? '抱歉，您访问的计划不存在或已被删除。可能是链接有误或计划已被移除。'
                : error || '抱歉，无法加载协作计划信息。'}
            </p>
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-blue-800 mb-2">💡 如何正确访问协作功能？</h3>
                <div className="space-y-2 text-sm text-blue-700">
                  <div className="flex items-start space-x-2">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span>在计划详情页面点击<strong>"分享协作"</strong>按钮获取正确链接</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span>确保使用朋友分享的<strong>协作链接</strong>（而非计划详情链接）</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                    <span>检查链接是否包含<strong>/collaborate/</strong>路径</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-amber-800 mb-2">🔗 链接格式说明</h3>
                <div className="space-y-1 text-xs text-amber-700">
                  <div>✅ 协作链接：<code className="bg-amber-100 px-1 rounded">/collaborate/计划ID</code></div>
                  <div>❌ 详情链接：<code className="bg-amber-100 px-1 rounded">/plan/计划ID</code></div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-3 mt-6">
                {error && error.includes('网络错误') && (
                  <button
                    onClick={() => window.location.reload()}
                    className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
                  >
                    <Loader2 className="w-5 h-5" />
                    <span>重试</span>
                  </button>
                )}
                <Link
                  to="/"
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
                >
                  <Home className="w-5 h-5" />
                  <span>返回首页</span>
                </Link>
                <Link
                  to="/plans"
                  className="bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 font-bold py-3 px-6 rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 shadow-sm hover:shadow-md"
                >
                  <Calendar className="w-5 h-5" />
                  <span>查看我的计划</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Transform plan data for collaboration view
  const collaborationData = {
    planId: currentPlan.id,
    planTitle: currentPlan.title,
    creator: {
      name: currentPlan.createdBy || '未知用户',
      avatar: '👨‍💼'
    },
    participants: currentPlan.participants?.map(p => ({
      id: p.userId,
      name: p.name,
      avatar: p.avatar || '👤',
      status: p.status,
      feedback: p.feedback,
      isCreator: p.userId === currentPlan.createdBy,
      isCurrentUser: p.userId === currentUser.id
    })) || [],
    deadline: currentPlan.deadline || '2024-02-10 18:00'
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'declined':
        return 'bg-red-100 text-red-800';
      case 'maybe':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <Check className="w-4 h-4" />;
      case 'declined':
        return <X className="w-4 h-4" />;
      case 'maybe':
        return <Clock className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed':
        return '已确认';
      case 'declined':
        return '已拒绝';
      case 'maybe':
        return '待定';
      default:
        return '待回复';
    }
  };

  const handleStatusChange = async (status: 'confirmed' | 'declined' | 'maybe') => {
    if (updating) return; // 防止重复点击
    
    setUpdating(true);
    setError(null);
    
    const previousStatus = userStatus;
    setUserStatus(status); // 乐观更新
    
    if (currentPlan) {
      try {
        await updateParticipantStatus(currentPlan.id, currentUser.id, status);
      } catch (error) {
        console.error('Failed to update participant status:', error);
        setUserStatus(previousStatus); // 回滚状态
        setError('更新状态失败，请重试');
      } finally {
        setUpdating(false);
      }
    } else {
      setUpdating(false);
    }
  };

  const handleFeedbackSubmit = async () => {
    if (submittingFeedback || !feedback.trim()) return;
    
    setSubmittingFeedback(true);
    setError(null);
    
    if (currentPlan) {
      try {
        await updateParticipantStatus(currentPlan.id, currentUser.id, userStatus, feedback);
        console.log('Feedback submitted:', feedback);
        // 可以添加成功提示
      } catch (error) {
        console.error('Failed to submit feedback:', error);
        setError('提交反馈失败，请重试');
      } finally {
        setSubmittingFeedback(false);
      }
    } else {
      setSubmittingFeedback(false);
    }
  };

  const confirmedCount = collaborationData.participants.filter(p => p.status === 'confirmed').length;
  const totalCount = collaborationData.participants.length;

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-8 sm:py-12">
        <div className="max-w-6xl mx-auto px-4">
          {/* Error Message */}
          {error && (
            <div className="mb-6 lg:mb-8 bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
              <div className="flex items-center">
                <X className="w-5 h-5 text-red-500 mr-2" />
                <p className="text-red-700 font-medium">错误：{error}</p>
              </div>
            </div>
          )}
          
          {/* Header */}
          <div className="text-center mb-8 sm:mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-3xl mb-4 sm:mb-6 animate-float">
              <Users className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold text-gray-900 mb-4">
              协作规划
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto px-4">
              和朋友一起确认行程，让旅行更有趣 🎉
            </p>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
            {/* Plan Details */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8 mb-6 lg:mb-8">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 sm:mb-6 space-y-2 sm:space-y-0">
                  <h2 className="text-xl sm:text-2xl font-bold text-gray-900">
                    📋 行程详情
                  </h2>
                  <span className="px-3 sm:px-4 py-2 bg-accent-yellow text-gray-800 rounded-full text-sm font-bold self-start">
                    待确认
                  </span>
                </div>
                
                <div className="space-y-4 sm:space-y-6">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                    <div className="flex items-center space-x-3">
                      <MapPin className="w-4 h-4 sm:w-5 sm:h-5 text-primary-500 flex-shrink-0" />
                      <div>
                        <p className="text-xs sm:text-sm text-gray-500">目的地</p>
                        <p className="font-bold text-gray-900 text-sm sm:text-base">{currentPlan.details.destination}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <Calendar className="w-4 h-4 sm:w-5 sm:h-5 text-primary-500 flex-shrink-0" />
                      <div>
                        <p className="text-xs sm:text-sm text-gray-500">日期</p>
                        <p className="font-bold text-gray-900 text-sm sm:text-base">
                          {currentPlan.details.startDate} - {currentPlan.details.endDate}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <Clock className="w-4 h-4 sm:w-5 sm:h-5 text-primary-500 flex-shrink-0" />
                      <div>
                        <p className="text-xs sm:text-sm text-gray-500">天数</p>
                        <p className="font-bold text-gray-900 text-sm sm:text-base">
                          {Math.ceil((new Date(currentPlan.details.endDate).getTime() - new Date(currentPlan.details.startDate).getTime()) / (1000 * 60 * 60 * 24)) + 1}天
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-primary-500 flex-shrink-0" />
                      <div>
                        <p className="text-xs sm:text-sm text-gray-500">预算</p>
                        <p className="font-bold text-gray-900 text-sm sm:text-base">{currentPlan.details.budget}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Participants Section */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8">
                <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6 flex items-center">
                  <Users className="w-5 h-5 sm:w-6 sm:h-6 text-primary-500 mr-2 sm:mr-3" />
                  参与者状态
                </h3>
                
                <div className="space-y-3 sm:space-y-4">
                  {collaborationData.participants.map((participant) => (
                    <div key={participant.id} className="flex items-center justify-between p-3 sm:p-4 bg-gray-50 rounded-2xl">
                      <div className="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
                        <div className="text-2xl sm:text-3xl flex-shrink-0">{participant.avatar}</div>
                        <div className="min-w-0 flex-1">
                          <div className="font-bold text-gray-900 text-sm sm:text-base">
                            {participant.name}
                            {participant.isCreator && (
                              <span className="ml-1 sm:ml-2 px-1 sm:px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                                发起者
                              </span>
                            )}
                            {participant.isCurrentUser && (
                              <span className="ml-1 sm:ml-2 px-1 sm:px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                我
                              </span>
                            )}
                          </div>
                          {participant.feedback && (
                            <div className="text-xs sm:text-sm text-gray-500 mt-1 truncate">
                              💬 {participant.feedback}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
                        {participant.status === 'confirmed' && (
                          <>
                            <Check className="w-4 h-4 sm:w-5 sm:h-5 text-green-500" />
                            <span className="text-green-600 font-bold text-xs sm:text-sm hidden sm:inline">已确认</span>
                          </>
                        )}
                        {participant.status === 'pending' && (
                          <>
                            <Clock className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-500" />
                            <span className="text-yellow-600 font-bold text-xs sm:text-sm hidden sm:inline">待确认</span>
                          </>
                        )}
                        {participant.status === 'declined' && (
                          <>
                            <X className="w-4 h-4 sm:w-5 sm:h-5 text-red-500" />
                            <span className="text-red-600 font-bold text-xs sm:text-sm hidden sm:inline">已拒绝</span>
                          </>
                        )}
                        {participant.status === 'maybe' && (
                          <>
                            <Clock className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-500" />
                            <span className="text-yellow-600 font-bold text-xs sm:text-sm hidden sm:inline">待定</span>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* User Action Section */}
          <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8 mb-6 lg:mb-8">
            <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6">你的确认状态</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
              <button
                onClick={() => handleStatusChange('confirmed')}
                disabled={updating}
                className={`py-3 sm:py-4 px-4 sm:px-6 rounded-2xl font-bold transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2 sm:space-x-3 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
                  userStatus === 'confirmed'
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-2xl'
                    : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 hover:from-green-50 hover:to-emerald-50 hover:text-green-700'
                }`}
              >
                {updating ? (
                  <div className="w-5 h-5 sm:w-6 sm:h-6 border-2 border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Check className="w-5 h-5 sm:w-6 sm:h-6" />
                )}
                <span className="text-sm sm:text-lg">{updating ? '更新中...' : '确认参加'}</span>
              </button>
              <button
                onClick={() => handleStatusChange('declined')}
                disabled={updating}
                className={`py-3 sm:py-4 px-4 sm:px-6 rounded-2xl font-bold transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2 sm:space-x-3 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
                  userStatus === 'declined'
                    ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-2xl'
                    : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 hover:from-red-50 hover:to-pink-50 hover:text-red-700'
                }`}
              >
                {updating ? (
                  <div className="w-5 h-5 sm:w-6 sm:h-6 border-2 border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <X className="w-5 h-5 sm:w-6 sm:h-6" />
                )}
                <span className="text-sm sm:text-lg">{updating ? '更新中...' : '无法参加'}</span>
              </button>
              <button
                onClick={() => handleStatusChange('pending')}
                disabled={updating}
                className={`py-3 sm:py-4 px-4 sm:px-6 rounded-2xl font-bold transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2 sm:space-x-3 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
                  userStatus === 'pending'
                    ? 'bg-gradient-to-r from-accent-yellow to-accent-pink text-white shadow-2xl'
                    : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 hover:from-yellow-50 hover:to-pink-50 hover:text-yellow-700'
                }`}
              >
                {updating ? (
                  <div className="w-5 h-5 sm:w-6 sm:h-6 border-2 border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Clock className="w-5 h-5 sm:w-6 sm:h-6" />
                )}
                <span className="text-sm sm:text-lg">{updating ? '更新中...' : '待定'}</span>
              </button>
            </div>
          </div>

          {/* Feedback Section */}
          <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8 mb-6 lg:mb-8">
            <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6 flex items-center space-x-2 sm:space-x-3">
              <MessageSquare className="w-6 h-6 sm:w-7 sm:h-7 text-primary-500" />
              <span>留言反馈</span>
            </h3>
            <div className="space-y-4 sm:space-y-6">
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="分享你的想法或建议..."
                rows={4}
                className="w-full p-3 sm:p-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-sm sm:text-lg"
              />
              <button
                onClick={handleFeedbackSubmit}
                disabled={submittingFeedback || !feedback.trim()}
                className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white font-bold py-2 sm:py-3 px-6 sm:px-8 rounded-2xl transition-all duration-300 transform hover:scale-105 shadow-lg flex items-center space-x-2 sm:space-x-3 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {submittingFeedback ? (
                  <div className="w-4 h-4 sm:w-5 sm:h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5" />
                )}
                <span className="text-sm sm:text-base">{submittingFeedback ? '提交中...' : '提交反馈'}</span>
              </button>
            </div>
          </div>

          {/* Status Display Section */}
          {userStatus !== 'pending' && (
            <div className="bg-white rounded-3xl shadow-brand-lg p-4 sm:p-6 lg:p-8 mb-6 lg:mb-8">
              <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6">你的状态</h3>
              <div className="flex items-center space-x-3 sm:space-x-4 mb-4 sm:mb-6">
                {userStatus === 'confirmed' && (
                  <>
                    <div className="w-3 h-3 sm:w-4 sm:h-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full animate-pulse"></div>
                    <span className="text-green-700 font-bold text-base sm:text-lg">已确认参加</span>
                    <Check className="w-5 h-5 sm:w-6 sm:h-6 text-green-500" />
                  </>
                )}
                {userStatus === 'declined' && (
                  <>
                    <div className="w-3 h-3 sm:w-4 sm:h-4 bg-gradient-to-r from-red-500 to-pink-500 rounded-full animate-pulse"></div>
                    <span className="text-red-700 font-bold text-base sm:text-lg">已确认无法参加</span>
                    <X className="w-5 h-5 sm:w-6 sm:h-6 text-red-500" />
                  </>
                )}
              </div>
              {feedback && (
                <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-4 sm:p-6 border-l-4 border-primary-500">
                  <p className="text-xs sm:text-sm font-semibold text-gray-600 mb-2 flex items-center space-x-2">
                    <MessageSquare className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span>你的反馈：</span>
                  </p>
                  <p className="text-gray-800 text-sm sm:text-lg leading-relaxed">{feedback}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Collaborate;