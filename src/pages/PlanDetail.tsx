import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  MapPin, Clock, DollarSign, Users, Share2, Loader2,
  Camera, Utensils, ShoppingBag, TreePine, Music,
  Building, Mountain, Waves, Star,
  Calendar, Edit3, UserPlus, Heart, Bookmark, Plane, Car, Gamepad2, Coffee,
  Check, Copy, ChevronDown, ChevronUp
} from 'lucide-react';
import { usePlanStore } from '../store';
import { WeatherOverview, DayWeather } from '../components/WeatherInfo';
import Layout from '../components/Layout';

// 单日行程组件
const DayItinerary: React.FC<{
  dayData: any;
  dayIndex: number;
  getCategoryColor: (category: string) => string;
  getCategoryIcon: (category: string) => React.ReactNode;
  weatherData?: any;
}> = ({ dayData, dayIndex, getCategoryColor, getCategoryIcon, weatherData }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="animate-fade-in-up" style={{animationDelay: `${dayIndex * 0.2}s`}}>
      {/* 日期标题 */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between mb-4 p-4 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 rounded-xl border border-indigo-100 cursor-pointer hover:shadow-md hover:border-indigo-200 transition-all duration-200"
      >
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
            {dayData.day}
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-3">
              <div>
                <h3 className="text-lg font-bold text-gray-800">{dayData.theme}</h3>
                {dayData.date && (
                  <p className="text-sm text-gray-600">{dayData.date}</p>
                )}
              </div>
              <DayWeather date={dayData.date} weatherData={weatherData} className="hidden sm:flex" />
            </div>
            {/* 移动端天气信息 */}
            <div className="mt-1 sm:hidden">
              <DayWeather date={dayData.date} weatherData={weatherData} />
            </div>
          </div>
        </div>
        <div className="px-3 py-1 bg-white/80 rounded-lg border border-gray-200 text-sm font-medium text-gray-700 transition-all duration-200 flex items-center space-x-1">
          <span>{isExpanded ? '收起' : '展开'}</span>
          <div className={`transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
            ▼
          </div>
        </div>
      </div>

      {/* 活动列表 */}
      {isExpanded && (
        <div className="space-y-4 transition-all duration-300">
        {dayData.activities.map((activity: any, actIndex: number) => (
          <div key={activity.id} className="flex space-x-3 sm:space-x-4">
            {/* 时间轴 */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className="w-3 h-3 bg-gradient-to-br from-violet-400 to-pink-400 rounded-full"></div>
              {actIndex < dayData.activities.length - 1 && (
                <div className="w-0.5 h-16 bg-gradient-to-b from-violet-200 to-pink-200 mt-2"></div>
              )}
            </div>
            
            {/* 活动卡片 */}
            <div className="flex-1">
              <div className="bg-gradient-to-br from-white to-gray-50/50 rounded-xl p-4 hover:shadow-lg transition-all duration-300 border border-gray-100/50 hover:border-purple-200/50">
                <div className="flex flex-col space-y-3">
                  {/* 活动头部 */}
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start space-y-2 sm:space-y-0">
                    <div className="flex-1 sm:pr-4">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-xs font-medium text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
                          {activity.timeSlot}
                        </span>
                        <span className="text-sm text-gray-600">{activity.time}</span>
                      </div>
                      <h4 className="text-base font-bold text-gray-800 mb-2">{activity.title}</h4>
                      <div className="flex items-center space-x-1 text-gray-600 text-sm">
                        <MapPin className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{activity.location}</span>
                      </div>
                    </div>
                    <div className="flex sm:flex-col sm:items-end justify-between sm:justify-start items-center space-x-2 sm:space-x-0 sm:space-y-2">
                      <div className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(activity.category)}`}>
                        {getCategoryIcon(activity.category)}
                        <span>{activity.category}</span>
                      </div>
                      <div className="text-lg font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                        ¥{activity.cost}
                      </div>
                    </div>
                  </div>
                  
                  {/* 活动描述 */}
                  {activity.description && (
                    <p className="text-gray-600 text-sm leading-relaxed">{activity.description}</p>
                  )}
                  
                  {/* 详细信息 */}
                  {isExpanded && (
                    <div>
                      {activity.details && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3 p-3 bg-gray-50/50 rounded-lg">
                          {activity.details.openTime && (
                            <div className="text-sm">
                              <span className="font-medium text-gray-700">开放时间：</span>
                              <span className="text-gray-600">{activity.details.openTime}</span>
                            </div>
                          )}
                          {activity.details.ticketPrice && (
                            <div className="text-sm">
                              <span className="font-medium text-gray-700">门票价格：</span>
                              <span className="text-gray-600">{activity.details.ticketPrice}</span>
                            </div>
                          )}
                          {activity.details.specialties && (
                            <div className="text-sm sm:col-span-2">
                              <span className="font-medium text-gray-700">推荐特色：</span>
                              <span className="text-gray-600">{activity.details.specialties}</span>
                            </div>
                          )}
                          {activity.details.features && (
                            <div className="text-sm sm:col-span-2">
                              <span className="font-medium text-gray-700">特色亮点：</span>
                              <span className="text-gray-600">{activity.details.features}</span>
                            </div>
                          )}
                          {activity.details.tips && (
                            <div className="text-sm sm:col-span-2">
                              <span className="font-medium text-gray-700">贴心提示：</span>
                              <span className="text-gray-600">{activity.details.tips}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        </div>
      )}
    </div>
  );
};

const PlanDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [planData, setPlanData] = useState<any>(null);
  const [weatherData, setWeatherData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [shareStatus, setShareStatus] = useState<'idle' | 'copying' | 'copied'>('idle');
  const [shareCollabStatus, setShareCollabStatus] = useState<'idle' | 'copying' | 'copied'>('idle');
  const [inviteStatus, setInviteStatus] = useState<'idle' | 'sharing' | 'shared'>('idle');

  useEffect(() => {
    const fetchPlanData = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);

        
        // 统一使用plans接口获取计划数据（NeMo和普通计划都存储在同一个地方）
        const apiEndpoint = `http://localhost:3001/api/plans/result/${id}`;
        
        const response = await fetch(apiEndpoint);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const planResult = await response.json();

        
        // Transform plan data to match the component's expected format
        const transformedData = {
          id: id,
          title: planResult.title || '旅行计划',
          location: planResult.destination || '未知目的地',
          date: planResult.start_date || new Date().toISOString().split('T')[0],
          participants: planResult.participants || 1,
          totalCost: calculateTotalCost(planResult.itinerary || []),
          status: 'confirmed',
          itinerary: transformItinerary(planResult.itinerary || []),
          totalDays: planResult.itinerary?.length || 1
        };
        
        // 保存天气数据
        if (planResult.weather_info) {
          setWeatherData(planResult.weather_info);
        }

        setPlanData(transformedData);
      } catch (error) {
        console.error('获取计划数据失败:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchPlanData();
  }, [id]);

  const calculateTotalCost = (itinerary: any[] = []) => {
    return itinerary.reduce((total, day) => {
      const timeSlots = ['breakfast', 'morning', 'lunch', 'afternoon', 'dinner', 'evening'];
      return total + timeSlots.reduce((dayTotal: number, slot: string) => {
        return dayTotal + (day[slot]?.cost || 0);
      }, 0);
    }, 0);
  };

  // 编辑计划按钮处理函数
  const handleEditPlan = () => {
    if (id) {
      navigate(`/edit-plan/${id}`);
    }
  };

  // 邀请好友按钮处理函数
  const handleInviteFriends = async () => {
    setInviteStatus('sharing');
    try {
      const shareUrl = `${window.location.origin}/plan/${id}`;
      const shareText = `来看看我的旅行计划：${planData?.title || '精彩旅程'}`;
      
      if (navigator.share) {
        // 使用原生分享API（移动端）
        await navigator.share({
          title: shareText,
          url: shareUrl
        });
        setInviteStatus('shared');
      } else {
        // 复制链接到剪贴板（桌面端）
        await navigator.clipboard.writeText(`${shareText} ${shareUrl}`);
        setInviteStatus('shared');
      }
      
      // 3秒后重置状态
      setTimeout(() => setInviteStatus('idle'), 3000);
    } catch (error) {
      console.error('邀请好友失败:', error);
      setInviteStatus('idle');
    }
  };

  // 分享计划按钮处理函数
  const handleSharePlan = async () => {
    setShareStatus('copying');
    try {
      const shareUrl = `${window.location.origin}/plan/${id}`;
      await navigator.clipboard.writeText(shareUrl);
      setShareStatus('copied');
      
      // 3秒后重置状态
      setTimeout(() => setShareStatus('idle'), 3000);
    } catch (error) {
      console.error('复制链接失败:', error);
      setShareStatus('idle');
    }
  };

  // 分享协作按钮处理函数
  const handleShareCollaboration = async () => {
    setShareCollabStatus('copying');
    try {
      const shareUrl = `${window.location.origin}/collaborate/${id}`;
      await navigator.clipboard.writeText(shareUrl);
      setShareCollabStatus('copied');
      
      // 3秒后重置状态
      setTimeout(() => setShareCollabStatus('idle'), 3000);
    } catch (error) {
      console.error('复制协作链接失败:', error);
      setShareCollabStatus('idle');
    }
  };

  const transformItinerary = (itinerary: any[] = []) => {
    return itinerary.map((day, dayIndex) => {
      let activities: any[] = [];
      
      // 检查数据结构类型
      if (day.activities && Array.isArray(day.activities)) {
        // 处理activities数组格式（新的后端格式）
        activities = day.activities.map((activity: any, activityIndex: number) => {
          // 从description中提取详细信息
          const description = activity.description || '';
          const openTimeMatch = description.match(/开放时间[：:]\s*([^\n]+)/);
          const ticketMatch = description.match(/门票[：:]\s*([^\n]+)/);
          const addressMatch = description.match(/地址[：:]\s*([^\n]+)/);
          const specialtiesMatch = description.match(/推荐菜品[：:]\s*([^\n]+)/);
          const consumeMatch = description.match(/人均消费[：:]\s*([^\n]+)/);
          
          const activityDetails = {
            openTime: openTimeMatch ? openTimeMatch[1].trim() : '',
            ticketPrice: ticketMatch ? ticketMatch[1].trim() : '',
            specialties: specialtiesMatch ? specialtiesMatch[1].trim() : '',
            features: '',
            tips: activity.tips || ''
          };
          

          
          return {
            id: `${dayIndex}-${activityIndex}`,
            timeSlot: getTimeSlotFromActivity(activity.activity),
            time: activity.time || '09:00',
            title: activity.activity,
            description: activity.description || '',
            location: activity.location || '待定',
            cost: activity.cost || 0,
            category: getCategoryFromActivity(activity.activity),
            details: activityDetails
          };
        });
      } else {
        // 处理时间段格式（旧的后端格式）
        const timeSlots = ['breakfast', 'morning', 'lunch', 'afternoon', 'dinner', 'evening'];
        const timeSlotNames = {
          breakfast: '早餐',
          morning: '上午',
          lunch: '午餐', 
          afternoon: '下午',
          dinner: '晚餐',
          evening: '晚上'
        };
        
        timeSlots.forEach((slot, slotIndex) => {
          if (day[slot] && day[slot].name) {
            const activityDetails = {
              openTime: day[slot].openTime || day[slot].open_time,
              ticketPrice: day[slot].ticketPrice || day[slot].ticket_price,
              specialties: day[slot].specialties || day[slot].recommended_dishes,
              features: day[slot].features,
              tips: day[slot].tips
            };
            

            
            activities.push({
              id: `${dayIndex}-${slotIndex}`,
              timeSlot: timeSlotNames[slot],
              time: day[slot].time || getDefaultTime(slot),
              title: day[slot].name,
              description: day[slot].description || '',
              location: day[slot].address || day[slot].location || '待定',
              cost: day[slot].cost || 0,
              category: getCategoryFromTimeSlot(slot),
              details: activityDetails
            });
          }
        });
      }
      
      return {
        day: dayIndex + 1,
        date: day.date || '',
        theme: day.theme || `第${dayIndex + 1}天`,
        activities
      };
    });
  };

  const getDefaultTime = (slot: string) => {
    const times: { [key: string]: string } = {
      breakfast: '08:00',
      morning: '09:30',
      lunch: '12:00',
      afternoon: '14:00', 
      dinner: '18:00',
      evening: '20:00'
    };
    return times[slot] || '09:00';
  };
  
  const getCategoryFromTimeSlot = (slot: string) => {
    if (slot === 'breakfast' || slot === 'lunch' || slot === 'dinner') return '美食';
    if (slot === 'morning' || slot === 'afternoon') return '文化';
    return '娱乐';
  };

  const getTimeSlotFromActivity = (activityName: string) => {
    const name = activityName.toLowerCase();
    if (name.includes('早餐') || name.includes('breakfast')) return '早餐';
    if (name.includes('午餐') || name.includes('lunch')) return '午餐';
    if (name.includes('晚餐') || name.includes('dinner')) return '晚餐';
    if (name.includes('上午') || name.includes('morning')) return '上午';
    if (name.includes('下午') || name.includes('afternoon')) return '下午';
    if (name.includes('晚上') || name.includes('evening')) return '晚上';
    return '全天';
  };

  const getCategoryFromActivity = (activityName: string) => {
    if (activityName.includes('博物馆') || activityName.includes('文化') || activityName.includes('历史')) return '文化';
    if (activityName.includes('美食') || activityName.includes('餐厅') || activityName.includes('小吃')) return '美食';
    if (activityName.includes('购物') || activityName.includes('商场') || activityName.includes('市场')) return '购物';
    if (activityName.includes('公园') || activityName.includes('户外') || activityName.includes('自然')) return '户外';
    return '娱乐';
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      '文化': <Building className="w-4 h-4" />,
      '美食': <Utensils className="w-4 h-4" />,
      '购物': <ShoppingBag className="w-4 h-4" />,
      '娱乐': <Music className="w-4 h-4" />,
      '户外': <TreePine className="w-4 h-4" />
    };
    return icons[category] || <Star className="w-4 h-4" />;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-64 h-64 sm:w-96 sm:h-96 bg-gradient-to-br from-purple-200/30 to-pink-200/30 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-64 h-64 sm:w-96 sm:h-96 bg-gradient-to-br from-blue-200/30 to-cyan-200/30 rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
        
        <div className="relative z-10 container mx-auto px-3 sm:px-4 py-4 sm:py-6 lg:py-8">
          <div className="max-w-4xl mx-auto">
            {/* 加载骨架屏 - 头部 */}
            <div className="bg-white/80 backdrop-blur-lg rounded-2xl sm:rounded-3xl shadow-2xl p-4 sm:p-6 lg:p-8 mb-4 sm:mb-6 lg:mb-8 border border-white/50 animate-pulse">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-4 sm:mb-6 space-y-3 sm:space-y-0">
                <div className="flex-1 pr-0 sm:pr-4">
                  <div className="h-8 sm:h-10 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg mb-2"></div>
                  <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-1/2"></div>
                </div>
                <div className="h-10 w-32 bg-gradient-to-r from-purple-200 to-pink-200 rounded-2xl"></div>
              </div>
              
              <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 lg:gap-4 mb-4 sm:mb-6">
                {[1,2,3,4].map(i => (
                  <div key={i} className="bg-gradient-to-br from-blue-50 to-cyan-50 p-3 sm:p-4 rounded-xl border border-blue-100">
                    <div className="h-4 bg-gradient-to-r from-blue-200 to-cyan-200 rounded mb-2"></div>
                    <div className="h-6 bg-gradient-to-r from-blue-300 to-cyan-300 rounded"></div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* 加载骨架屏 - 行程 */}
            <div className="bg-white/80 backdrop-blur-lg rounded-2xl sm:rounded-3xl shadow-2xl p-4 sm:p-6 lg:p-8 border border-white/50 animate-pulse">
              <div className="h-6 sm:h-8 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg mb-6 w-1/3"></div>
              
              <div className="space-y-6">
                {[1,2,3].map(i => (
                  <div key={i} className="flex space-x-3 sm:space-x-4">
                    <div className="flex flex-col items-center flex-shrink-0">
                      <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-violet-200 to-pink-200 rounded-full"></div>
                      {i < 3 && <div className="w-1 h-12 sm:h-16 bg-gradient-to-b from-violet-200 to-pink-200 mt-2 rounded-full"></div>}
                    </div>
                    
                    <div className="flex-1 pb-4 sm:pb-6 lg:pb-8">
                      <div className="bg-gradient-to-br from-white to-gray-50/50 rounded-xl sm:rounded-2xl p-3 sm:p-4 lg:p-5 border border-gray-100/50">
                        <div className="h-5 bg-gradient-to-r from-gray-200 to-gray-300 rounded mb-2"></div>
                        <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-2/3 mb-2"></div>
                        <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-1/2"></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!planData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-bold text-gray-800 mb-2">计划不存在</h2>
          <p className="text-gray-600">请检查计划ID是否正确</p>
        </div>
      </div>
    );
  }

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      '文化': 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 border border-blue-200',
      '美食': 'bg-gradient-to-r from-orange-100 to-red-100 text-orange-800 border border-orange-200',
      '购物': 'bg-gradient-to-r from-pink-100 to-rose-100 text-pink-800 border border-pink-200',
      '娱乐': 'bg-gradient-to-r from-purple-100 to-violet-100 text-purple-800 border border-purple-200',
      '户外': 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200'
    };
    return colors[category] || 'bg-gradient-to-r from-gray-100 to-slate-100 text-gray-800 border border-gray-200';
  };

  return (
    <Layout>
      <style>{`
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes slide-in-left {
          from {
            opacity: 0;
            transform: translateX(-30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        .animate-fade-in-up {
          animation: fade-in-up 0.6s ease-out forwards;
          opacity: 0;
        }
        
        .animate-slide-in-left {
          animation: slide-in-left 0.5s ease-out forwards;
          opacity: 0;
        }
        
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        .line-clamp-3 {
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
      
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden">
      {/* 背景装饰 */}
      <div className="absolute top-0 left-0 w-64 h-64 sm:w-96 sm:h-96 bg-gradient-to-br from-purple-200/30 to-pink-200/30 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
      <div className="absolute bottom-0 right-0 w-64 h-64 sm:w-96 sm:h-96 bg-gradient-to-br from-blue-200/30 to-cyan-200/30 rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
      
      <div className="relative z-10 container mx-auto px-3 sm:px-4 py-4 sm:py-6 lg:py-8">
        <div className="max-w-4xl mx-auto">
        {/* 计划头部信息 */}
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl sm:rounded-3xl shadow-2xl p-4 sm:p-6 lg:p-8 mb-4 sm:mb-6 lg:mb-8 border border-white/50">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-4 sm:mb-6 space-y-3 sm:space-y-0">
            <div className="flex-1 pr-0 sm:pr-4">
              <h1 className="text-xl sm:text-2xl lg:text-3xl xl:text-4xl font-bold text-gray-800 mb-2 leading-tight">{planData.title}</h1>
              <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-2 sm:space-y-0 text-gray-600">
                <div className="flex items-center space-x-1">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm sm:text-base">{planData.location}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm sm:text-base">{planData.date}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="w-4 h-4" />
                  <span className="text-sm sm:text-base">{planData.participants}人</span>
                </div>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
              <button 
                onClick={handleSharePlan}
                disabled={shareStatus === 'copying'}
                className="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 hover:from-blue-600 hover:via-indigo-600 hover:to-purple-600 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 text-white px-3 py-2 sm:px-4 sm:py-2.5 rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 text-xs sm:text-sm shadow-lg hover:shadow-xl hover:scale-105 border border-white/20 backdrop-blur-sm disabled:hover:scale-100 disabled:cursor-not-allowed"
              >
                {shareStatus === 'copying' ? (
                  <Loader2 className="w-3 h-3 sm:w-4 sm:h-4 animate-spin" />
                ) : shareStatus === 'copied' ? (
                  <Check className="w-3 h-3 sm:w-4 sm:h-4" />
                ) : (
                  <Share2 className="w-3 h-3 sm:w-4 sm:h-4" />
                )}
                <span>
                  {shareStatus === 'copying' ? '复制中...' : shareStatus === 'copied' ? '已复制!' : '分享计划'}
                </span>
              </button>
              <button 
                onClick={handleShareCollaboration}
                disabled={shareCollabStatus === 'copying'}
                className="bg-gradient-to-r from-orange-500 via-red-500 to-pink-500 hover:from-orange-600 hover:via-red-600 hover:to-pink-600 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 text-white px-3 py-2 sm:px-4 sm:py-2.5 rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 text-xs sm:text-sm shadow-lg hover:shadow-xl hover:scale-105 border border-white/20 backdrop-blur-sm disabled:hover:scale-100 disabled:cursor-not-allowed"
              >
                {shareCollabStatus === 'copying' ? (
                  <Loader2 className="w-3 h-3 sm:w-4 sm:h-4 animate-spin" />
                ) : shareCollabStatus === 'copied' ? (
                  <Check className="w-3 h-3 sm:w-4 sm:h-4" />
                ) : (
                  <Users className="w-3 h-3 sm:w-4 sm:h-4" />
                )}
                <span>
                  {shareCollabStatus === 'copying' ? '复制中...' : shareCollabStatus === 'copied' ? '已复制!' : '分享协作'}
                </span>
              </button>
            </div>
          </div>
          
          {/* 天气概览卡片 */}
          <div className="mb-4 sm:mb-6">
            <WeatherOverview weatherData={weatherData} />
          </div>
          
          <div className="grid grid-cols-1 xs:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mb-6 sm:mb-8">
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 sm:p-5 rounded-xl border border-blue-100 hover:shadow-lg transition-all duration-300 hover:scale-105">
              <div className="flex items-center space-x-2 mb-2">
                <Calendar className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
                <span className="text-xs sm:text-sm font-medium text-blue-800">出发日期</span>
              </div>
              <p className="text-sm sm:text-base font-bold text-blue-900 truncate">{planData.date}</p>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 sm:p-5 rounded-xl border border-green-100 hover:shadow-lg transition-all duration-300 hover:scale-105">
              <div className="flex items-center space-x-2 mb-2">
                <Clock className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />
                <span className="text-xs sm:text-sm font-medium text-green-800">行程天数</span>
              </div>
              <p className="text-sm sm:text-base font-bold text-green-900">{planData.totalDays}天</p>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 sm:p-5 rounded-xl border border-purple-100 hover:shadow-lg transition-all duration-300 hover:scale-105">
              <div className="flex items-center space-x-2 mb-2">
                <Users className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
                <span className="text-xs sm:text-sm font-medium text-purple-800">人数</span>
              </div>
              <p className="text-sm sm:text-base font-bold text-purple-900">{planData.participants}人</p>
            </div>
            <div className="bg-gradient-to-br from-orange-50 to-red-50 p-4 sm:p-5 rounded-xl border border-orange-100 hover:shadow-lg transition-all duration-300 hover:scale-105">
              <div className="flex items-center space-x-2 mb-2">
                <DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-orange-600" />
                <span className="text-xs sm:text-sm font-medium text-orange-800">预算</span>
              </div>
              <p className="text-sm sm:text-base font-bold text-orange-900">¥{planData.totalCost}</p>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 via-teal-50 to-cyan-50 rounded-2xl border border-emerald-100/50 shadow-inner">
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-gray-800">计划状态</span>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              planData.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {planData.status === 'confirmed' ? '✅ 已确认' : '⏳ 待确认'}
            </div>
          </div>
        </div>

        {/* 行程时间轴 - 按天分组 */}
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl sm:rounded-3xl shadow-2xl p-4 sm:p-6 lg:p-8 mb-4 sm:mb-6 lg:mb-8 border border-white/50">
          <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-800 mb-3 sm:mb-4 lg:mb-6 flex items-center space-x-2">
            <Clock className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
            <span>详细行程</span>
          </h2>
          
          <div className="space-y-8">
            {planData.itinerary.map((dayData: any, dayIndex: number) => (
              <DayItinerary key={dayIndex} dayData={dayData} dayIndex={dayIndex} getCategoryColor={getCategoryColor} getCategoryIcon={getCategoryIcon} weatherData={weatherData} />
            ))}
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="mt-8 flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
          <button 
            onClick={handleEditPlan}
            className="flex-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 hover:from-blue-600 hover:via-indigo-600 hover:to-purple-600 text-white font-bold py-4 px-6 rounded-2xl transition-all duration-300 text-sm sm:text-base shadow-xl hover:shadow-2xl hover:scale-105 border border-white/20 backdrop-blur-sm group"
          >
            <div className="flex items-center justify-center space-x-2">
              <Edit3 className="w-5 h-5 group-hover:rotate-12 transition-transform duration-300" />
              <span>编辑计划</span>
            </div>
          </button>
          <button 
            onClick={() => navigate(`/collaborate/${planData.id}`)}
            className="flex-1 bg-gradient-to-r from-orange-500 via-red-500 to-pink-500 hover:from-orange-600 hover:via-red-600 hover:to-pink-600 text-white font-bold py-4 px-6 rounded-2xl transition-all duration-300 text-sm sm:text-base shadow-xl hover:shadow-2xl hover:scale-105 border border-white/20 backdrop-blur-sm group"
          >
            <div className="flex items-center justify-center space-x-2">
              <Users className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
              <span>协作计划</span>
            </div>
          </button>
          <button 
            onClick={handleInviteFriends}
            disabled={inviteStatus === 'sharing'}
            className="flex-1 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-600 hover:via-teal-600 hover:to-cyan-600 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 text-white font-bold py-4 px-6 rounded-2xl transition-all duration-300 text-sm sm:text-base shadow-xl hover:shadow-2xl hover:scale-105 border border-white/20 backdrop-blur-sm group disabled:hover:scale-100 disabled:cursor-not-allowed"
          >
            <div className="flex items-center justify-center space-x-2">
              {inviteStatus === 'sharing' ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : inviteStatus === 'shared' ? (
                <Check className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
              ) : (
                <UserPlus className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" />
              )}
              <span>
                {inviteStatus === 'sharing' ? '分享中...' : inviteStatus === 'shared' ? '已分享!' : '邀请好友'}
              </span>
            </div>
          </button>
        </div>
        </div>
      </div>
    </div>
    </Layout>
  );
};

export default PlanDetail;