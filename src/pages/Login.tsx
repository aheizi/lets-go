import React from 'react';
import Layout from '../components/Layout';

const Login: React.FC = () => {
  return (
    <Layout>
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-400 to-blue-400">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Let'sGo</h1>
          <p className="text-gray-600">来次够，不再鸽！</p>
        </div>
        
        <div className="space-y-4">
          <button className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-4 rounded-xl transition-colors duration-200 flex items-center justify-center space-x-2">
            <span>🚀</span>
            <span>微信快速登录</span>
          </button>
          
          <div className="text-center text-sm text-gray-500">
            登录即表示同意用户协议和隐私政策
          </div>
        </div>
      </div>
    </div>
    </Layout>
  );
};

export default Login;