let captchaCode = "";

// 从服务端获取验证码
async function generateCaptcha() {
  try {
    const response = await fetch('/api/captcha');
    const data = await response.json();
    
    if (data.success) {
      captchaCode = data.captcha;
      displayCaptcha(captchaCode);
    } else {
      console.error('获取验证码失败:', data.message);
      showError('获取验证码失败，请刷新页面重试');
    }
  } catch (error) {
    console.error('获取验证码失败:', error);
    showError('网络错误，请检查连接');
  }
}

// 显示验证码
function displayCaptcha(code) {
  const canvas = document.getElementById("captchaCanvas");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.font = "24px Arial";
  ctx.fillStyle = "#333";
  ctx.fillText(code, 15, 28);

  // 添加干扰线
  for (let i = 0; i < 3; i++) {
    ctx.strokeStyle = "#"+Math.floor(Math.random()*16777215).toString(16);
    ctx.beginPath();
    ctx.moveTo(Math.random() * 100, Math.random() * 40);
    ctx.lineTo(Math.random() * 100, Math.random() * 40);
    ctx.stroke();
  }
}

// 显示加载状态
function showLoading(button, text = "登录中...") {
  button.disabled = true;
  button.textContent = text;
}

// 隐藏加载状态
function hideLoading(button, text = "登录") {
  button.disabled = false;
  button.textContent = text;
}

// 显示错误消息
function showError(message) {
  // 创建错误提示元素
  let errorDiv = document.getElementById("error-message");
  if (!errorDiv) {
    errorDiv = document.createElement("div");
    errorDiv.id = "error-message";
    errorDiv.style.cssText = `
      background-color: #f8d7da;
      color: #721c24;
      padding: 10px;
      margin: 10px 0;
      border: 1px solid #f5c6cb;
      border-radius: 4px;
      text-align: center;
    `;
    document.getElementById("loginForm").insertBefore(errorDiv, document.getElementById("loginForm").firstChild);
  }
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

// 隐藏错误消息
function hideError() {
  const errorDiv = document.getElementById("error-message");
  if (errorDiv) {
    errorDiv.style.display = "none";
  }
}

// 登录API调用
async function loginUser(username, password, captcha) {
  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        password: password,
        captcha: captcha
      })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('登录请求失败:', error);
    return {
      success: false,
      message: '网络连接失败，请检查服务器状态'
    };
  }
}

document.getElementById("refreshCaptcha").addEventListener("click", generateCaptcha);

document.getElementById("loginForm").addEventListener("submit", async function(e) {
  e.preventDefault();
  hideError();
  
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const inputCode = document.getElementById("captchaInput").value.trim().toUpperCase();
  const submitButton = document.querySelector('button[type="submit"]');

  // 基本验证
  if (!username || !password) {
    showError("请输入用户名和密码");
    return;
  }

  // 验证码验证（现在使用服务端验证码）
  if (inputCode !== captchaCode) {
    showError("验证码错误，请重新输入！");
    generateCaptcha();
    return;
  }

  // 显示加载状态
  showLoading(submitButton);

  try {
    // 调用登录API
    const result = await loginUser(username, password, inputCode);
    
    if (result.success) {
      // 登录成功，跳转到仪表板
      window.location.href = result.redirect_url || '/dashboard';
    } else {
      // 登录失败，显示错误信息
      showError(result.message || "登录失败");
      generateCaptcha(); // 刷新验证码
    }
  } catch (error) {
    console.error('登录过程出错:', error);
    showError("登录过程中发生错误，请重试");
    generateCaptcha();
  } finally {
    // 恢复按钮状态
    hideLoading(submitButton);
  }
});

// 检查是否已经登录
async function checkAuthStatus() {
  try {
    const response = await fetch('/api/check-auth');
    const data = await response.json();
    
    if (data.authenticated) {
      // 如果已经登录，跳转到仪表板
      window.location.href = '/dashboard';
    }
  } catch (error) {
    console.log('认证检查失败:', error);
  }
}

// 页面加载时检查认证状态
window.onload = function() {
  generateCaptcha();
  checkAuthStatus();
};
