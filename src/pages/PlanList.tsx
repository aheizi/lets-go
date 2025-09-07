import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { usePlanStore } from '../store/usePlanStore';
import { Calendar, MapPin, Users, Clock, Plus, Eye, Edit } from 'lucide-react';
import Layout from '../components/Layout';

const PlanList: React.FC = () => {
  const { plans, isLoading, fetchPlans } = usePlanStore();

  useEffect(() => {
    console.log('PlanList组件加载，开始获取计划列表...');
    fetchPlans().then(() => {
      console.log('计划列表获取完成');
    }).catch((error) => {
      console.error('获取计划列表失败:', error);
    });
  }, [fetchPlans]);

  const formatDate = (dateString: string) => {
    if (!dateString) return '待定';
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  const getStatusText = (status: string) => {
    const statusMap = {
      draft: '草稿',
      planning: '规划中',
      confirmed: '已确认',
      completed: '已完成',
      cancelled: '已取消'
    };
    return statusMap[status as keyof typeof statusMap] || status;
  };

  const getStatusColor = (status: string) => {
    const colorMap = {
      draft: 'bg-gray-100 text-gray-800',
      planning: 'bg-blue-100 text-blue-800',
      confirmed: 'bg-green-100 text-green-800',
      completed: 'bg-purple-100 text-purple-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colorMap[status as keyof typeof colorMap] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">正在加载计划列表...</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              我的旅行计划
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              管理和查看您的所有旅行计划
            </p>
            <Link
              to="/create"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-5 h-5 mr-2" />
              创建新计划
            </Link>
          </div>

          {/* Plans Grid */}
          {plans.length === 0 ? (
            <div className="text-center py-12">
              <div className="bg-white rounded-lg shadow-lg p-8 max-w-md mx-auto">
                <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  还没有旅行计划
                </h3>
                <p className="text-gray-600 mb-6">
                  开始创建您的第一个旅行计划吧！
                </p>
                <Link
                  to="/create"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  创建计划
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
                >
                  {/* Plan Header */}
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <h3 className="text-xl font-semibold text-gray-900 truncate">
                        {plan.title}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(plan.status)}`}>
                        {getStatusText(plan.status)}
                      </span>
                    </div>

                    {/* Plan Details */}
                    <div className="space-y-3">
                      <div className="flex items-center text-gray-600">
                        <MapPin className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span className="truncate">{plan.details.destination || '待定'}</span>
                      </div>
                      
                      <div className="flex items-center text-gray-600">
                        <Calendar className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span className="text-sm">
                          {formatDate(plan.details.startDate)} - {formatDate(plan.details.endDate)}
                        </span>
                      </div>
                      
                      <div className="flex items-center text-gray-600">
                        <Users className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span className="text-sm">{plan.details.participants} 人</span>
                      </div>
                      
                      <div className="flex items-center text-gray-600">
                        <Clock className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span className="text-sm">
                          创建于 {formatDate(plan.createdAt)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Plan Actions */}
                  <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                    <div className="flex space-x-2">
                      <Link
                        to={`/plan/${plan.id}`}
                        className="flex-1 inline-flex items-center justify-center px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        查看
                      </Link>
                      <Link
                        to={`/edit-plan/${plan.id}`}
                        className="flex-1 inline-flex items-center justify-center px-3 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors"
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        编辑
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default PlanList;