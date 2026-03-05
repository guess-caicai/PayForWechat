<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>💰 PayForWechat</h2>
          <p>开发者支付管理平台</p>
        </div>
      </template>

      <el-form
        :model="loginForm"
        :rules="rules"
        ref="loginFormRef"
        label-width="80px"
        class="login-form"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="loginForm.email"
            placeholder="请输入邮箱"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>

        <div class="register-link">
          还没有账号？<el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const loginFormRef = ref(null)
    const loading = ref(false)

    const loginForm = reactive({
      email: '',
      password: ''
    })

    const rules = {
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ]
    }

    const handleLogin = () => {
      loginFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true
          try {
            const res = await login(loginForm)
            localStorage.setItem('token', res.access_token)
            ElMessage.success('登录成功')
            router.push('/dashboard')
          } catch (error) {
            ElMessage.error(error.response?.data?.detail || '登录失败')
          } finally {
            loading.value = false
          }
        }
      })
    }

    return {
      loginForm,
      rules,
      loginFormRef,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f6f7f9;
}

.login-card {
  width: 400px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #fff;
  box-shadow: 0 2px 8px rgba(17, 24, 39, 0.04);
}

.card-header {
  text-align: center;
  padding: 20px;
}

.card-header h2 {
  color: #111827;
  margin: 0;
  font-size: 24px;
}

.card-header p {
  color: #6b7280;
  margin: 10px 0 0;
  font-size: 14px;
}

.login-form {
  padding: 20px;
}

.register-link {
  text-align: center;
  margin-top: 15px;
}
</style>
