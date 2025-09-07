import { create } from 'zustand';

interface Participant {
  id: string;
  userId: string; // 用户唯一标识，用于协作功能
  name: string;
  email: string;
  avatar?: string;
  status: 'confirmed' | 'declined' | 'pending';
  role: 'organizer' | 'participant';
  feedback?: string;
}

interface PlanDetails {
  destination: string;
  startDate: string;
  endDate: string;
  participants: number;
  budget: string;
  travelStyle: string;
  interests: string[];
}

interface Plan {
  id: string;
  title: string;
  description?: string;
  details: PlanDetails;
  participants: Participant[];
  status: 'draft' | 'planning' | 'confirmed' | 'completed' | 'cancelled';
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  itinerary?: {
    day: number;
    activities: {
      time: string;
      activity: string;
      location: string;
      cost?: number;
    }[];
  }[];
}

interface PlanState {
  plans: Plan[];
  currentPlan: Plan | null;
  isLoading: boolean;
  isGenerating: boolean;
  
  // Actions
  setPlans: (plans: Plan[]) => void;
  addPlan: (plan: Plan) => void;
  updatePlan: (id: string, updates: Partial<Plan>) => void;
  deletePlan: (id: string) => void;
  setCurrentPlan: (plan: Plan | null) => void;
  
  // Plan creation and generation
  createPlan: (details: PlanDetails) => Promise<string>;
  generateItinerary: (planId: string) => Promise<void>;
  fetchPlans: () => Promise<void>;
  fetchPlanById: (planId: string) => Promise<Plan | null>;
  
  // Collaboration
  inviteParticipant: (planId: string, email: string) => Promise<void>;
  updateParticipantStatus: (planId: string, participantId: string, status: Participant['status'], feedback?: string) => void;
  
  // Loading states
  setLoading: (loading: boolean) => void;
  setGenerating: (generating: boolean) => void;
}

// Transform function to convert backend data to frontend format
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
        
        // 调试信息：打印原始数据和转换后的details
        console.log(`[DEBUG] Day ${dayIndex + 1} Activity ${activityIndex} 原始数据:`, activity);
        console.log(`[DEBUG] Day ${dayIndex + 1} Activity ${activityIndex} details:`, activityDetails);
        
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
          
          // 调试信息：打印原始数据和转换后的details
          console.log(`[DEBUG] Day ${dayIndex + 1} ${slot} 原始数据:`, day[slot]);
          console.log(`[DEBUG] Day ${dayIndex + 1} ${slot} details:`, activityDetails);
          
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

// 根据活动名称推断时间段
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

// 根据活动名称推断分类
const getCategoryFromActivity = (activityName: string) => {
  const name = activityName.toLowerCase();
  if (name.includes('餐') || name.includes('食') || name.includes('吃') || name.includes('restaurant') || name.includes('dining')) {
    return 'dining';
  }
  if (name.includes('景点') || name.includes('游览') || name.includes('参观') || name.includes('sightseeing') || name.includes('visit')) {
    return 'sightseeing';
  }
  if (name.includes('购物') || name.includes('商场') || name.includes('shopping')) {
    return 'shopping';
  }
  return 'other';
};

export const usePlanStore = create<PlanState>((set, get) => ({
  plans: [
    {
      id: 'sample-plan-1',
      title: '北京三日游',
      description: '探索古都北京的历史文化',
      details: {
        destination: '北京',
        startDate: '2024-03-15',
        endDate: '2024-03-17',
        participants: 4,
        budget: 'medium',
        travelStyle: ['文化', '历史'],
        interests: ['故宫', '长城', '胡同']
      },
      participants: [
        {
          id: 'current_user',
          userId: 'current_user',
          name: '我',
          email: 'user@example.com',
          avatar: '👨‍💼',
          status: 'confirmed',
          role: 'organizer'
        },
        {
          id: 'participant_1',
          userId: 'participant_1',
          name: '小明',
          email: 'xiaoming@example.com',
          avatar: '👨',
          status: 'pending',
          role: 'participant',
          feedback: '期待这次旅行！'
        },
        {
          id: 'participant_2',
          userId: 'participant_2',
          name: '小红',
          email: 'xiaohong@example.com',
          avatar: '👩',
          status: 'confirmed',
          role: 'participant'
        },
        {
          id: 'participant_3',
          userId: 'participant_3',
          name: '小李',
          email: 'xiaoli@example.com',
          avatar: '👨‍🎓',
          status: 'declined',
          role: 'participant',
          feedback: '时间冲突，无法参加'
        }
      ],
      status: 'planning',
      createdBy: 'current_user',
      createdAt: '2024-01-15T10:00:00.000Z',
      updatedAt: '2024-01-15T10:00:00.000Z',
      itinerary: [
        {
          day: 1,
          activities: [
            {
              id: '1-1',
              timeSlot: '上午',
              time: '09:00',
              title: '故宫博物院',
              description: '参观紫禁城，了解明清两代皇宫历史',
              location: '北京市东城区景山前街4号',
              cost: 60,
              category: 'sightseeing'
            },
            {
              id: '1-2',
              timeSlot: '下午',
              time: '14:00',
              title: '天安门广场',
              description: '游览世界最大的城市广场',
              location: '北京市东城区东长安街',
              cost: 0,
              category: 'sightseeing'
            }
          ]
        },
        {
          day: 2,
          activities: [
            {
              id: '2-1',
              timeSlot: '上午',
              time: '08:00',
              title: '八达岭长城',
              description: '登长城，体验万里长城的雄伟',
              location: '北京市延庆区八达岭镇',
              cost: 45,
              category: 'sightseeing'
            }
          ]
        }
      ]
    },
    {
      id: 'sample-plan-2',
      title: '上海周末游',
      description: '感受魔都的现代魅力',
      details: {
        destination: '上海',
        startDate: '2024-03-20',
        endDate: '2024-03-22',
        participants: 3,
        budget: 'high',
        travelStyle: ['现代', '购物'],
        interests: ['外滩', '迪士尼', '美食']
      },
      participants: [
        {
          id: 'current_user',
          userId: 'current_user',
          name: '我',
          email: 'user@example.com',
          avatar: '👨‍💼',
          status: 'confirmed',
          role: 'organizer'
        },
        {
          id: 'participant_4',
          userId: 'participant_4',
          name: '小王',
          email: 'xiaowang@example.com',
          avatar: '👩‍💻',
          status: 'confirmed',
          role: 'participant',
          feedback: '很期待去迪士尼！'
        },
        {
          id: 'participant_5',
          userId: 'participant_5',
          name: '小张',
          email: 'xiaozhang@example.com',
          avatar: '👨‍🎨',
          status: 'pending',
          role: 'participant'
        }
      ],
      status: 'draft',
      createdBy: 'current_user',
      createdAt: '2024-01-16T10:00:00.000Z',
      updatedAt: '2024-01-16T10:00:00.000Z'
    }
  ],
  currentPlan: null,
  isLoading: false,
  isGenerating: false,

  setPlans: (plans) => set({ plans }),
  
  addPlan: (plan) => set((state) => ({
    plans: [...state.plans, plan]
  })),
  
  updatePlan: async (id, updates) => {
    set({ isLoading: true });
    
    try {
      // 准备更新数据，只发送需要更新的字段
      const updateData: any = {};
      
      // 映射前端字段到后端字段
      if (updates.details) {
        const details = updates.details;
        if (details.destination) updateData.destination = details.destination;
        if (details.startDate) updateData.start_date = details.startDate;
        if (details.endDate) updateData.end_date = details.endDate;
        if (details.participants) updateData.group_size = details.participants;
        if (details.budget) updateData.budget_level = details.budget;
        if (details.travelStyle) {
          updateData.travel_style = Array.isArray(details.travelStyle) 
            ? details.travelStyle.join(', ') 
            : details.travelStyle;
        }
        if (details.interests) updateData.interests = details.interests;
      }
      
      // 如果有其他直接字段更新
      if (updates.title) updateData.title = updates.title;
      if (updates.status) updateData.status = updates.status;
      
      console.log('Updating plan with data:', updateData);
      
      // 调用后端API更新计划
      const response = await fetch(`http://localhost:3001/api/plans/update/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Update error response:', errorText);
        let errorMessage = `更新失败: HTTP ${response.status}`;
        
        try {
          const errorData = JSON.parse(errorText);
          if (errorData.detail) {
            errorMessage = `更新失败: ${errorData.detail}`;
          }
        } catch (e) {
          errorMessage += ` - ${errorText}`;
        }
        
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      console.log('Plan updated successfully:', result);
      
      // 更新本地状态
      set((state) => ({
        plans: state.plans.map(plan => 
          plan.id === id ? { ...plan, ...updates, updatedAt: new Date().toISOString() } : plan
        ),
        currentPlan: state.currentPlan?.id === id 
          ? { ...state.currentPlan, ...updates, updatedAt: new Date().toISOString() }
          : state.currentPlan
      }));
      
      return result;
    } catch (error) {
      console.error('Failed to update plan:', error);
      throw error;
    } finally {
      set({ isGenerating: false });
    }
  },
  
  deletePlan: (id) => set((state) => ({
    plans: state.plans.filter(plan => plan.id !== id),
    currentPlan: state.currentPlan?.id === id ? null : state.currentPlan
  })),
  
  setCurrentPlan: (plan) => set({ currentPlan: plan }),
  
  createPlan: async (details) => {
    set({ isGenerating: true });
    
    try {
      const requestData = {
        destination: details.destination,
        start_date: details.startDate,
        end_date: details.endDate,
        group_size: details.participants,
        budget_level: details.budget,
        travel_style: Array.isArray(details.travelStyle) ? details.travelStyle.join(', ') : details.travelStyle,
        interests: details.interests
      };
      
      console.log('Creating plan with NeMo Agent:', requestData);
      
      const response = await fetch('http://localhost:3001/api/nemo-plans/quick-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        try {
          const errorData = JSON.parse(errorText);
          if (errorData.detail) {
            errorMessage += ` - ${JSON.stringify(errorData.detail)}`;
          }
        } catch (e) {
          errorMessage += ` - ${errorText}`;
        }
        
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      console.log('Plan created with NeMo Agent:', result);
      
      // 使用后端返回的plan_id，而不是前端生成
      const planId = result.plan_id;
      
      // Transform NeMo result to our format
      const transformedItinerary = result.itinerary ? transformItinerary(result.itinerary) : undefined;
      
      // Create local plan object with mock participants
      const newPlan: Plan = {
        id: planId,
        title: `${details.destination}之旅`,
        details,
        participants: [
          {
            id: 'current_user',
            userId: 'current_user',
            name: '我',
            email: 'user@example.com',
            avatar: '👨‍💼',
            status: 'confirmed',
            role: 'organizer'
          },
          {
            id: 'participant_1',
            userId: 'participant_1',
            name: '小明',
            email: 'xiaoming@example.com',
            avatar: '👨',
            status: 'pending',
            role: 'participant',
            feedback: '期待这次旅行！'
          },
          {
            id: 'participant_2',
            userId: 'participant_2',
            name: '小红',
            email: 'xiaohong@example.com',
            avatar: '👩',
            status: 'confirmed',
            role: 'participant'
          },
          {
            id: 'participant_3',
            userId: 'participant_3',
            name: '小李',
            email: 'xiaoli@example.com',
            avatar: '👨‍🎓',
            status: 'maybe',
            role: 'participant',
            feedback: '需要确认一下时间安排'
          }
        ],
        status: transformedItinerary ? 'planning' : 'draft',
        createdBy: 'current_user',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        itinerary: transformedItinerary
      };
      
      get().addPlan(newPlan);
      // Refresh the plans list to ensure it's up to date
      await get().fetchPlans();
      return planId;
    } catch (error) {
      console.error('Failed to create plan:', error);
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },
  
  generateItinerary: async (planId) => {
    set({ isGenerating: true });
    
    try {
      // Get plan details for NeMo generation
      const plan = get().plans.find(p => p.id === planId);
      if (!plan) {
        throw new Error('Plan not found');
      }
      
      // Start the itinerary generation process with NeMo
      const generateResponse = await fetch(`http://localhost:3001/api/nemo-plans/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          destination: plan.details.destination,
          start_date: plan.details.startDate,
          end_date: plan.details.endDate,
          group_size: plan.details.participants,
          budget_level: plan.details.budget,
          travel_style: Array.isArray(plan.details.travelStyle) ? plan.details.travelStyle.join(', ') : plan.details.travelStyle,
          interests: plan.details.interests
        })
      });
      
      if (!generateResponse.ok) {
        throw new Error(`Failed to start NeMo generation: ${generateResponse.status}`);
      }
      
      const generateResult = await generateResponse.json();
      const taskId = generateResult.task_id;
      
      // Poll for status until completion
      let isCompleted = false;
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes timeout
      
      while (!isCompleted && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
        
        const statusResponse = await fetch(`http://localhost:3001/api/nemo-plans/status/${taskId}`);
        if (!statusResponse.ok) {
          throw new Error(`Failed to check NeMo status: ${statusResponse.status}`);
        }
        
        const statusData = await statusResponse.json();
        
        if (statusData.status === 'completed') {
          isCompleted = true;
          
          // Get the generated result
          const resultResponse = await fetch(`http://localhost:3001/api/nemo-plans/result/${taskId}`);
          if (!resultResponse.ok) {
            throw new Error(`Failed to get result: ${resultResponse.status}`);
          }
          
          const resultData = await resultResponse.json();
          
          // Transform the result to match our frontend format
          const rawItinerary = resultData.itinerary || [];
          const transformedItinerary = transformItinerary(rawItinerary);
          
          get().updatePlan(planId, { 
            itinerary: transformedItinerary,
            status: 'planning'
          });
        } else if (statusData.status === 'failed') {
          throw new Error('Itinerary generation failed');
        }
        
        attempts++;
      }
      
      if (!isCompleted) {
        throw new Error('Itinerary generation timed out');
      }
    } catch (error) {
      console.error('Failed to generate itinerary:', error);
      // Optionally show error to user
      throw error;
    } finally {
      set({ isGenerating: false });
    }
  },
  
  inviteParticipant: async (planId, email) => {
    // Mock invitation logic
    const participantId = `participant_${Date.now()}`;
    const newParticipant: Participant = {
      id: participantId,
      userId: participantId,
      name: email.split('@')[0],
      email,
      avatar: '👤',
      status: 'pending',
      role: 'participant'
    };
    
    const plan = get().plans.find(p => p.id === planId);
    if (plan) {
      get().updatePlan(planId, {
        participants: [...plan.participants, newParticipant]
      });
    }
  },
  
  updateParticipantStatus: async (planId, participantId, status, feedback) => {
    const plan = get().plans.find(p => p.id === planId);
    if (plan) {
      // 先更新本地状态
      const updatedParticipants = plan.participants.map(p => 
        p.id === participantId 
          ? { ...p, status, feedback: feedback || p.feedback }
          : p
      );
      get().updatePlan(planId, { participants: updatedParticipants });
      
      // 同步到后端
      try {
        const response = await fetch(`http://localhost:3001/api/plans/collaborate/${planId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            action: 'update_status',
            participant_id: participantId,
            status: status,
            feedback: feedback
          })
        });
        
        if (!response.ok) {
          console.error('Failed to sync participant status to backend:', response.status);
          // 可以选择回滚本地状态或显示错误提示
        }
      } catch (error) {
        console.error('Error syncing participant status:', error);
        // 可以选择回滚本地状态或显示错误提示
      }
    }
  },
  
  setLoading: (isLoading) => set({ isLoading }),
  setGenerating: (isGenerating) => set({ isGenerating }),
  
  fetchPlans: async () => {
    set({ isLoading: true });
    
    try {
      console.log('开始调用后端API获取计划列表...');
      const response = await fetch('http://localhost:3001/api/plans/list', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch plans: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('后端返回的计划数据:', data);
      
      // Transform backend data to frontend format
      const transformedPlans: Plan[] = [];
      
      // Process active plans
      if (data.active_plans && Array.isArray(data.active_plans)) {
        data.active_plans.forEach((planData: any) => {
          const plan: Plan = {
            id: planData.plan_id,
            title: planData.destination ? `${planData.destination}之旅` : '未命名计划',
            details: {
              destination: planData.destination || '',
              startDate: planData.start_date || '',
              endDate: planData.end_date || '',
              participants: planData.participants || 1,
              budget: planData.budget || '',
              travelStyle: planData.travel_style || '',
              interests: planData.interests || []
            },
            participants: [
              {
                id: 'current_user',
                userId: 'current_user',
                name: '我',
                email: 'user@example.com',
                avatar: '👨‍💼',
                status: 'confirmed',
                role: 'organizer'
              }
            ],
            status: planData.status === 'completed' ? 'completed' : 'planning',
            createdBy: 'current_user',
            createdAt: planData.created_at || new Date().toISOString(),
            updatedAt: planData.updated_at || new Date().toISOString(),
            itinerary: planData.itinerary ? transformItinerary(planData.itinerary) : undefined
          };
          transformedPlans.push(plan);
        });
      }
      
      // Process completed plans
      if (data.completed_plans && Array.isArray(data.completed_plans)) {
        data.completed_plans.forEach((planData: any) => {
          const plan: Plan = {
            id: planData.plan_id,
            title: planData.destination ? `${planData.destination}之旅` : '未命名计划',
            details: {
              destination: planData.destination || '',
              startDate: planData.start_date || '',
              endDate: planData.end_date || '',
              participants: planData.participants || 1,
              budget: planData.budget || '',
              travelStyle: planData.travel_style || '',
              interests: planData.interests || []
            },
            participants: [
              {
                id: 'current_user',
                userId: 'current_user',
                name: '我',
                email: 'user@example.com',
                avatar: '👨‍💼',
                status: 'confirmed',
                role: 'organizer'
              }
            ],
            status: 'completed',
            createdBy: 'current_user',
            createdAt: planData.created_at || new Date().toISOString(),
            updatedAt: planData.updated_at || new Date().toISOString(),
            itinerary: planData.itinerary ? transformItinerary(planData.itinerary) : undefined
          };
          transformedPlans.push(plan);
        });
      }
      
      set({ plans: transformedPlans });
      console.log('转换后的计划列表:', transformedPlans);
      console.log('Plans fetched successfully:', transformedPlans);
    } catch (error) {
      console.error('Failed to fetch plans:', error);
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  fetchPlanById: async (planId: string) => {
    set({ isLoading: true });
    
    try {
      console.log('开始获取单个计划数据:', planId);
      const response = await fetch(`http://localhost:3001/api/plans/${planId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log('计划不存在:', planId);
          return null;
        }
        throw new Error(`Failed to fetch plan: ${response.status}`);
      }
      
      const planData = await response.json();
      console.log('后端返回的单个计划数据:', planData);
      
      // Transform backend data to frontend format
      const plan: Plan = {
        id: planData.plan_id,
        title: planData.destination ? `${planData.destination}之旅` : '未命名计划',
        details: {
          destination: planData.destination || '',
          startDate: planData.start_date || '',
          endDate: planData.end_date || '',
          participants: planData.participants || 1,
          budget: planData.budget || '',
          travelStyle: planData.travel_style || '',
          interests: planData.interests || []
        },
        participants: [
          {
            id: 'current_user',
            userId: 'current_user',
            name: '我',
            email: 'user@example.com',
            avatar: '👨‍💼',
            status: 'confirmed',
            role: 'organizer'
          }
        ],
        status: planData.status === 'completed' ? 'completed' : 'planning',
        createdBy: 'current_user',
        createdAt: planData.created_at || new Date().toISOString(),
        updatedAt: planData.updated_at || new Date().toISOString(),
        itinerary: planData.itinerary ? transformItinerary(planData.itinerary) : undefined
      };
      
      // 将获取到的计划添加到plans数组中（如果不存在的话）
      const existingPlan = get().plans.find(p => p.id === planId);
      if (!existingPlan) {
        set((state) => ({
          plans: [...state.plans, plan]
        }));
      }
      
      console.log('转换后的计划数据:', plan);
      return plan;
    } catch (error) {
      console.error('Failed to fetch plan by id:', error);
      throw error;
    } finally {
      set({ isLoading: false });
    }
  }
}));