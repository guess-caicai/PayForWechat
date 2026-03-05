<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <h2>PayForWechat</h2>
        </div>
        <el-menu :default-active="$route.path" router class="menu">
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="/pay/create">
            <el-icon><Plus /></el-icon>
            <span>创建订单</span>
          </el-menu-item>
          <el-menu-item index="/orders">
            <el-icon><List /></el-icon>
            <span>全部订单</span>
          </el-menu-item>
          <el-menu-item index="/orders/success">
            <el-icon><CircleCheck /></el-icon>
            <span>成功订单</span>
          </el-menu-item>
          <el-menu-item index="/wallet">
            <el-icon><Wallet /></el-icon>
            <span>钱包</span>
          </el-menu-item>
          <el-menu-item index="/withdraw">
            <el-icon><Money /></el-icon>
            <span>提现</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-icon class="hamburger" @click="toggleSidebar"><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
          </div>
          <div class="header-right">
            <el-dropdown>
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ userInfo.email }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleProfile">个人中心</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { getProfile } from '@/api'

export default {
  name: 'MainLayout',
  setup() {
    const router = useRouter()
    const isCollapse = ref(false)
    const userInfo = reactive({
      email: '',
      payKey: ''
    })

    const toggleSidebar = () => {
      isCollapse.value = !isCollapse.value
    }

    const fetchProfile = async () => {
      try {
        const res = await getProfile()
        userInfo.email = res.email
        userInfo.payKey = res.pay_key
      } catch (error) {
        console.error('获取用户信息失败', error)
      }
    }

    const handleProfile = () => {
      router.push('/profile')
    }

    const handleLogout = () => {
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        localStorage.removeItem('token')
        router.push('/login')
      })
    }

    onMounted(() => {
      fetchProfile()
    })

    return {
      isCollapse,
      userInfo,
      toggleSidebar,
      handleProfile,
      handleLogout
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background: #f6f7f9;
}

.sidebar {
  background: #ffffff;
  height: 100vh;
  transition: width 0.3s;
  border-right: 1px solid #e5e7eb;
  box-shadow: none;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.logo h2 {
  color: #111827;
  font-size: 18px;
  margin: 0;
}

.menu {
  border-right: none;
  background: transparent;
}

.menu :deep(.el-menu-item) {
  color: #374151;
  border-radius: 8px;
  margin: 6px 10px;
}

.menu :deep(.el-menu-item:hover) {
  background-color: #f3f4f6 !important;
  color: #111827 !important;
}

.menu :deep(.el-menu-item.is-active) {
  background: #eef2ff !important;
  color: #111827 !important;
  font-weight: 600;
}

.el-header {
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #e2e8f0;
}

.header-left {
  display: flex;
  align-items: center;
}

.hamburger {
  font-size: 20px;
  cursor: pointer;
  color: #4b5563;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #374151;
}

.el-main {
  background: transparent;
  padding: 16px;
}

.main-content {
  overflow-y: auto;
}

@media (max-width: 900px) {
  .sidebar {
    width: 72px !important;
  }

  .logo h2 {
    font-size: 14px;
  }

  .menu :deep(.el-menu-item span) {
    display: none;
  }

  .el-main {
    padding: 10px;
  }
}
</style>
