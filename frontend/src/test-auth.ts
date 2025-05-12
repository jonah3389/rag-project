/**
 * 认证功能测试脚本
 * 
 * 这个脚本用于测试前端与后端的认证功能联动
 * 可以在浏览器控制台中运行
 */

import api from './shared/services/api';
import { login, register, getCurrentUser } from './modules/auth/services/authService';

// 测试注册功能
async function testRegister() {
  try {
    console.log('测试注册功能...');
    const testUser = {
      username: `test_user_${Date.now()}`,
      email: `test_${Date.now()}@example.com`,
      password: 'Password123!',
      full_name: '测试用户',
    };
    
    console.log('注册用户:', testUser);
    const user = await register(testUser);
    console.log('注册成功:', user);
    return testUser;
  } catch (error) {
    console.error('注册失败:', error);
    throw error;
  }
}

// 测试登录功能
async function testLogin(credentials: { username: string; password: string }) {
  try {
    console.log('测试登录功能...');
    console.log('登录凭据:', credentials);
    const result = await login(credentials);
    console.log('登录成功:', result);
    return result;
  } catch (error) {
    console.error('登录失败:', error);
    throw error;
  }
}

// 测试获取当前用户信息
async function testGetCurrentUser() {
  try {
    console.log('测试获取当前用户信息...');
    const user = await getCurrentUser();
    console.log('获取用户信息成功:', user);
    return user;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    throw error;
  }
}

// 运行所有测试
async function runTests() {
  try {
    // 测试注册
    const testUser = await testRegister();
    
    // 测试登录
    const loginResult = await testLogin({
      username: testUser.username,
      password: testUser.password,
    });
    
    // 测试获取当前用户信息
    const currentUser = await testGetCurrentUser();
    
    console.log('所有测试通过!');
    return { testUser, loginResult, currentUser };
  } catch (error) {
    console.error('测试失败:', error);
    throw error;
  }
}

// 导出测试函数，可以在浏览器控制台中调用
export {
  testRegister,
  testLogin,
  testGetCurrentUser,
  runTests,
};

// 默认导出所有测试函数
export default {
  testRegister,
  testLogin,
  testGetCurrentUser,
  runTests,
};
