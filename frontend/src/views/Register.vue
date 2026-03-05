<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>💰 注册账号</h2>
          <p>开发者支付管理平台</p>
        </div>
      </template>

      <el-form
        :model="registerForm"
        :rules="rules"
        ref="registerFormRef"
        label-width="80px"
        class="login-form"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '立即注册' }}
          </el-button>
        </el-form-item>

        <div class="login-link">
          已有账号？<el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const registerFormRef = ref(null)
    const loading = ref(false)

    const registerForm = reactive({
      email: '',
      password: '',
      confirmPassword: ''
    })

    const rules = {
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== registerForm.password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    const handleRegister = () => {
      registerFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true
          try {
            await register(registerForm)
            ElMessage.success('注册成功，请登录')
            router.push('/login')
          } catch (error) {
            ElMessage.error(error.response?.data?.detail || '注册失败')
          } finally {
            loading.value = false
          }
        }
      })
    }

    return {
      registerForm,
      rules,
      registerFormRef,
      loading,
      handleRegister
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

.login-link {
  text-align: center;
  margin-top: 15px;
}
</style>
