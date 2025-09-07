// 测试计划创建和行程生成的完整流程
const testPlanCreation = async () => {
  try {
    console.log('🧪 开始测试计划创建流程...');
    
    // 1. 创建计划
    const createResponse = await fetch('http://localhost:3001/api/plans/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        destination: '东京',
        start_date: '2024-03-01',
        end_date: '2024-03-05',
        group_size: 2,
        budget_level: '舒适型',
        travel_style: '文化探索',
        interests: ['美食', '历史']
      })
    });
    
    if (!createResponse.ok) {
      throw new Error(`创建计划失败: ${createResponse.status}`);
    }
    
    const createResult = await createResponse.json();
    console.log('✅ 计划创建成功:', createResult);
    
    const planId = createResult.plan_id;
    if (!planId) {
      throw new Error('❌ 未获取到plan_id');
    }
    
    console.log(`📋 获取到计划ID: ${planId}`);
    
    // 2. 触发行程生成
    const generateResponse = await fetch(`http://localhost:3001/api/plans/generate/${planId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!generateResponse.ok) {
      throw new Error(`启动行程生成失败: ${generateResponse.status}`);
    }
    
    const generateResult = await generateResponse.json();
    console.log('✅ 行程生成已启动:', generateResult);
    
    // 3. 检查状态
    const statusResponse = await fetch(`http://localhost:3001/api/plans/status/${planId}`);
    if (!statusResponse.ok) {
      throw new Error(`获取状态失败: ${statusResponse.status}`);
    }
    
    const statusResult = await statusResponse.json();
    console.log('📊 计划状态:', statusResult);
    
    console.log('🎉 测试完成！所有步骤都成功执行。');
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
  }
};

// 运行测试
testPlanCreation();